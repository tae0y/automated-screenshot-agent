import asyncio
from enum import Enum

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatMessage,
    Executor,
    ExecutorCompletedEvent,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowOutputEvent,
    handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential

from src.agent_tools import (
    new_session,
    navigate,
    screenshot,
    click,
    fill,
    evaluate,
    click_text,
    get_text_content,
    get_html_content,
    get_visible_html,
)
from src.config import ConfigManager
from src.logger import get_logger

_logger = get_logger(__name__)
_config = ConfigManager()


class JobStatus(Enum):
    """
    Job status enumeration.
    - There are three steps in Job: ASSUMPTION, REASON(METHODOLOGY and TASK), RESULT
    - Each step has three status: INCORRECT, INCOMPLETE, CORRECT_AND_COMPLETED
    - Final "Result" has three status: UNREASONABLE itself, INCONSISTENCY with REASON, CORRECT_AND_COMPLETED
    - There is exception status: I_DONT_KNOW_WHY_BUT_JUST_RETRY
    """
    INIT = "INIT"
    UNREASONABLE_RESULT = "UNREASONABLE_RESULT"
    INCONSISTENCY_BETWEEN_REASON_AND_RESULT = "INCONSISTENCY_BETWEEN_REASON_AND_RESULT"
    INCORRECT_TASK = "INCORRECT_TASK"
    INCOMPLETE_TASK = "INCOMPLETE_TASK"
    INCORRECT_METHODOLOGY = "INCORRECT_METHODOLOGY"
    INCOMPLETE_METHODOLOGY = "INCOMPLETE_METHODOLOGY"
    INCORRECT_ASSUMPTION = "INCORRECT_ASSUMPTION"
    INCOMPLETE_ASSUMPTION = "INCOMPLETE_ASSUMPTION"
    I_DONT_KNOW_WHY_BUT_JUST_RETRY = "I_DONT_KNOW_WHY_BUT_JUST_RETRY"
    JOBSTATUS_CANNOT_PARSED = "JOBSTATUS_CANNOT_PARSED"
    COMPLETED = "COMPLETED"


class WorkerExecutor(Executor):
    """
    Worker executor to perform UI tests based on user input.
    """

    def __init__(self, id: str):
        """Initialize the WorkerExecutor"""
        tools = [
            new_session,
            navigate,
            screenshot,
            click,
            fill,
            evaluate,
            click_text,
            get_text_content,
            get_html_content,
            get_visible_html
        ]
        super().__init__(
            id=id or "worker_agent",
            tools=tools
        )

    @handler
    async def do_test(self, feedback: JobStatus, user_prompt: str, ctx: WorkflowContext[str, str]) -> None:
        if feedback == JobStatus.COMPLETED:
            await ctx.yield_output(f"Task completed successfully. {self._result}")

        elif feedback == JobStatus.INIT:
            prompt = """
            You are a QA engineer for UI testing.
            You will process the task based on three steps: ASSUMPTION, REASON(METHODOLOGY and TASK), RESULT.
            Answer in the format below:
            ---
            ASSUMPTION: <your assumption>
            REASON: <your reasoning including methodology and task>
            RESULT: <your result>
            ---

            user request is:
            {user_prompt}
            """
            self._result = AgentExecutorRequest(
                messages=[
                    ChatMessage(role=Role.USER, content=prompt)
                ],
                should_respond=True
            )
            await ctx.send_message(self._result)

        else:
            prompt = f"""
            The previous task was not completed successfully due to: {feedback.name}.
            Please review and try again.

            You are a QA engineer for UI testing.
            You will process the task based on three steps: ASSUMPTION, REASON(METHODOLOGY and TASK), RESULT.
            Answer in the format below:
            ---
            ASSUMPTION: <your assumption>
            REASON: <your reasoning including methodology and task>
            RESULT: <your result>
            ---

            original user request was:
            {user_prompt}
            """
            prompt = user_prompt
            self._result = AgentExecutorRequest(
                messages=[
                    ChatMessage(role=Role.USER, content=prompt)
                ],
                should_respond=True
            )
            await ctx.send_message(self._result)
        pass


class SubmitToManagerAgent(Executor):
    """
    Submit to Manager agent for handling task submissions to the manager.
    """

    def __init__(self, manager_agent_id: str, id: str):
        """Initialize the SubmitToManagerAgent"""
        super().__init__(
            id=id or "submit_to_manager"
        )
        self.manager_agent_id = manager_agent_id

    @handler
    async def submit_task(self, response: AgentExecutorResponse, ctx: WorkflowContext[int, str]) -> None:
        response_text = response.agent_run_response.text.strip()
        prompt = f"""
        You are a QA senior manager overseeing a UI testing worker.
        The worker has processed the task based on three steps: ASSUMPTION, REASON(METHODOLOGY and TASK), RESULT.
        Each step has three status: INCORRECT, INCOMPLETE, CORRECT_AND_COMPLETED.
        The final "Result" has three status: UNREASONABLE itself, INCONSISTENCY with REASON, CORRECT_AND_COMPLETED.
        
        The worker has provided the following response:
        {response_text}

        Based on this response, determine whether the task has been completed successfully or not.
        Provide your decision strictly as one of the following statuses:
            - UNREASONABLE_RESULT
            - INCONSISTENCY_BETWEEN_REASON_AND_RESULT
            - INCORRECT_TASK
            - INCOMPLETE_TASK
            - INCORRECT_METHODOLOGY
            - INCOMPLETE_METHODOLOGY
            - INCORRECT_ASSUMPTION
            - INCOMPLETE_ASSUMPTION
            - I_DONT_KNOW_WHY_BUT_JUST_RETRY
            - COMPLETED
        """

        await ctx.send_message(
            AgentExecutorRequest(
                messages=[
                    ChatMessage(role=Role.USER, content=prompt)
                ],
                should_respond=True
            ),
            target_id=self.manager_agent_id
        )


class ParseManagerResponse(Executor):
    """
    Parse the response from the Manager to determine next steps.
    """
    @handler
    async def parse_response(self, response: AgentExecutorResponse, ctx: WorkflowContext[JobStatus]) -> None:
        response_text = response.agent_run_response.text.strip().upper()
        try:
            if response_text in JobStatus.__members__:
                ctx.set_output(JobStatus[response_text])
            else:
                ctx.set_output(JobStatus.JOBSTATUS_CANNOT_PARSED)  # I_DONT_KNOW_WHY_BUT_JUST_RETRY
        except Exception as e:
            _logger.error(f"Error parsing response: {e}")
            ctx.set_output(JobStatus.JOBSTATUS_CANNOT_PARSED)


class AgentWorkflow:
    """
    Simple Loop workflow
    
    What it does:
    - Worker performs a UI test based on user input.
    - Manager oversees the Worker and ensures task completion.
    - If Manager detects incomplete tasks, it prompts the Worker to retry until successful.
    - If Manager requests Worker to perform a task, Worker can disagree.
    - If Manager and Worker disagree, Manager will decide the final outcome.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentWorkflow, cls).__new__(cls)
            cls._instance._initialize_workflow()
        return cls._instance
    
    def _initialize_workflow(self):
        # Create executors
        chat_client = AzureOpenAIChatClient(
            api_key=_config.AZURE_AI_FOUNDRY_API_KEY,
            endpoint=_config.AZURE_AI_FOUNDRY_ENDPOINT,
            deployment_name=_config.AZURE_AI_FOUNDRY_DEPLOYMENT_NAME
        )
        self.worker_executor = WorkerExecutor()
        self.manager_executor = AgentExecutor(
            chat_client.create_agent(
                instructions=(
                    """
                    You strictly respond with one of:
                        - UNREASONABLE_RESULT
                        - INCONSISTENCY_BETWEEN_REASON_AND_RESULT
                        - INCORRECT_TASK
                        - INCOMPLETE_TASK
                        - INCORRECT_METHODOLOGY
                        - INCOMPLETE_METHODOLOGY
                        - INCORRECT_ASSUMPTION
                        - INCOMPLETE_ASSUMPTION
                        - I_DONT_KNOW_WHY_BUT_JUST_RETRY
                        - COMPLETED
                    """
                )
            ),
            id="manager_agent",
        )
        self.submit_to_manager_agent = SubmitToManagerAgent(manager_agent_id=self.manager_executor.id, id="submit_to_manager")
        self.parse_manager_response = ParseManagerResponse(id="parse_manager")

        # Build workflow
        self.workflow = (
            WorkflowBuilder()
            .add_edge(self.worker_executor, self.submit_to_manager_agent)
            .add_edge(self.submit_to_manager_agent, self.manager_executor)
            .add_edge(self.manager_executor, self.parse_manager_response)
            .add_edge(self.parse_manager_response, self.worker_executor)
            .build()
        )
        pass

    async def get_response(self, user_prompt: str, max_iterations: int = 5) -> str:
        iterations = 0
        result = ""
        async for event in self.workflow.run_stream(JobStatus.INIT, prompt=user_prompt):
            if iterations >= max_iterations:
                _logger.warning("Max iterations reached, terminating workflow.")
                result = str(event.data) if isinstance(event, WorkflowOutputEvent) else "Max iterations reached."
                break
            if isinstance(event, ExecutorCompletedEvent) and event.executor_id == self.worker_executor.id:
                iterations += 1
            elif isinstance(event, WorkflowOutputEvent):
                print(f"Final result: {event.data}")
                result = event.data
        print(f"Total iterations: {iterations} times.")
        return result
