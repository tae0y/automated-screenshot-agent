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
_user_prompt = ""


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


class JobRequest:
    """
    Job request data structure.
    """
    def __init__(self, status: JobStatus = JobStatus.INIT, user_prompt: str = ""):
        self.status = status
        self.user_prompt = user_prompt


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
    async def do_test(self, request: JobRequest, ctx: WorkflowContext[str]) -> None:
        if request.status == JobStatus.COMPLETED:
            _logger.debug(f"WorkerExecutor completed the task successfully.")
            _logger.debug(f"WorkerExecutor yielding output: {self._result}")
            await ctx.yield_output(f"Task completed successfully. {self._result}")

        elif request.status == JobStatus.INIT:
            prompt = f"""
            You are a QA engineer for UI testing.
            You will process the task based on three steps: ASSUMPTION, REASON(METHODOLOGY and TASK), RESULT.
            Answer in the format below:
            ---
            ASSUMPTION: <your assumption>
            REASON: <your reasoning including methodology and task>
            RESULT: <your result>
            ---

            user request is:
            {request.user_prompt}
            """
            _logger.debug(f"WorkerExecutor sending prompt: {prompt}")
            self._result = AgentExecutorRequest(
                messages=[
                    ChatMessage(role=Role.USER, content=prompt)
                ],
                should_respond=True
            )
            _logger.debug(f"WorkerExecutor sending AgentExecutorRequest: {self._result}")
            await ctx.send_message(self._result)

        else:
            prompt = f"""
            The previous task was not completed successfully due to: {request.status.name}.
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
            {request.user_prompt}
            """
            _logger.debug(f"WorkerExecutor sending prompt: {prompt}")
            self._result = AgentExecutorRequest(
                messages=[
                    ChatMessage(role=Role.USER, content=prompt)
                ],
                should_respond=True
            )
            _logger.debug(f"WorkerExecutor sending AgentExecutorRequest: {self._result}")
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
    async def submit_task(self, response: str, ctx: WorkflowContext[str]) -> None:
        #response_text = response.agent_run_response.text.strip()
        response_text = response
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
    async def parse_response(self, response: AgentExecutorResponse, ctx: WorkflowContext[JobRequest]) -> None:
        global _user_prompt
        response_text = response.agent_run_response.text.strip().upper()
        try:
            if response_text in JobStatus.__members__:
                ctx.set_output(JobRequest(status=JobStatus[response_text], user_prompt=_user_prompt)) # TODO: sustain user_prompt through workflow... how?
            else:
                ctx.set_output(JobRequest(status=JobStatus.JOBSTATUS_CANNOT_PARSED, user_prompt=_user_prompt))  # I_DONT_KNOW_WHY_BUT_JUST_RETRY
        except Exception as e:
            _logger.error(f"Error parsing response: {e}")
            ctx.set_output(JobRequest(status=JobStatus.JOBSTATUS_CANNOT_PARSED, user_prompt=_user_prompt))


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
        self.worker_executor = WorkerExecutor(id="worker_agent")
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
            .set_start_executor(self.worker_executor)
            .build()
        )
        pass

    async def get_response(self, user_prompt: str, max_iterations: int = 10) -> str:
        global _user_prompt
        _user_prompt = user_prompt
        iterations = 0
        result = ""
        async for event in self.workflow.run_stream(JobRequest(status=JobStatus.INIT, user_prompt=user_prompt)):
            if iterations >= max_iterations:
                _logger.warning("Max iterations reached, terminating workflow.")
                result = str(event.data) if isinstance(event, WorkflowOutputEvent) else "Max iterations reached."
                break
            if isinstance(event, ExecutorCompletedEvent) and event.executor_id == self.worker_executor.id:
                _logger.debug(f"WorkerExecutor completed event received.")
                iterations += 1
            elif isinstance(event, WorkflowOutputEvent):
                _logger.debug(f"Workflow output event received: {event.data}")
                result = event.data
        _logger.debug(f"Total iterations: {iterations} times.")
        return result
