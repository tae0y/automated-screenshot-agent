import asyncio
from dataclasses import dataclass
from enum import Enum

from agent_framework import (
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    ChatAgent,
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
from src.kernel_agent import KernelAgent

_logger = get_logger(__name__)
_config = ConfigManager()
_user_prompt = ""
_previous_result = None
# _agent = KernelAgent() # for tool call test

class JobStatus(Enum):
    """
    Job status enumeration.
    - There are three steps in Job: ASSUMPTION, REASON(METHODOLOGY and TASK), RESULT
    - Each step has three status: INCORRECT, INCOMPLETE, CORRECT_AND_COMPLETED
    - Final "Result" has three status: UNREASONABLE itself, INCONSISTENCY with REASON, CORRECT_AND_COMPLETED
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
    # I_DONT_KNOW_WHY_BUT_JUST_RETRY = "I_DONT_KNOW_WHY_BUT_JUST_RETRY"
    JOBSTATUS_CANNOT_PARSED = "JOBSTATUS_CANNOT_PARSED"
    COMPLETED = "COMPLETED"


@dataclass
class UserRequest:
    """
    User request data structure.
    """
    status: JobStatus
    user_prompt: str
    previous_result: str = None


# @dataclass
# class ParsedUserRequest:
#     """
#     Parsed user request data structure.
#     """
#     target_url: str
#     desired_actions: str
#     acceptance_criteria: str


class SubmitToWorkerExecutor(Executor):
    """
    Worker executor to perform UI tests based on user input.
    """
    def __init__(self, id: str, worker_executor_id: str = "worker_agent"):
        """Initialize the WorkerExecutor"""
        super().__init__(
            id=id or "submit_to_worker"
        )
        self.worker_executor_id = worker_executor_id

    @handler
    async def do_test(self, request: UserRequest, ctx: WorkflowContext[AgentExecutorResponse]) -> None:
        if request.status == JobStatus.COMPLETED:
            _logger.debug(f"WorkerExecutor completed the task successfully.")
            _logger.debug(f"WorkerExecutor yielding output: {request.previous_result}")
            await ctx.yield_output(f"Task completed successfully. Result: {request.previous_result}")

        elif request.status == JobStatus.INIT:
            prompt = f"""
            Parse the user's request carefully and use the tools to fulfill the request.

            USER'S UI test request:
            {request.user_prompt}

            Above is the user's UI test request. Perform the test using the available tools.
            """
            _logger.debug(f"WorkerExecutor sending prompt: {prompt}")
            await ctx.send_message(
                AgentExecutorRequest(
                    messages=[
                        ChatMessage(role=Role.USER, content=prompt)
                    ],
                    should_respond=True
                ),
                target_id=self.worker_executor_id
            )
   
        else:
            prompt = f"""
            The previous task was not completed successfully due to: 
            {request.status.name}.
            
            Please review and try again.
            Parse the user's request carefully and use the tools to fulfill the request step by step.
            After performing the test, provide a detailed report of the results.

            USER'S UI test request:
            {request.user_prompt}

            Above is the user's UI test request. Perform the test using the available tools.
            """
            _logger.debug(f"WorkerExecutor sending prompt: {prompt}")
            await ctx.send_message(
                AgentExecutorRequest(
                    messages=[
                        ChatMessage(role=Role.USER, content=prompt)
                    ],
                    should_respond=True
                ),
                target_id=self.worker_executor_id
            )


class SubmitToManagerAgent(Executor):
    """
    Submit to Manager agent for handling task submissions to the manager.
    """

    def __init__(self, id: str, manager_agent_id: str = "manager_agent"):
        """Initialize the SubmitToManagerAgent"""
        super().__init__(
            id=id or "submit_to_manager"
        )
        self.manager_agent_id = manager_agent_id

    @handler
    async def submit_task(self, response: AgentExecutorResponse, ctx: WorkflowContext[str]) -> None:
        global _previous_result, _user_prompt
        response_text = response.agent_run_response.text.strip()
        _previous_result = response_text
        prompt = f"""
        You are a QA senior manager overseeing a UI testing worker.
        
        Review the WORKER'S RESPONSE and determine the USER'S UI test request was fulfilled the UI test request.                                

        USER'S UI test request:
        {_user_prompt}

        WORKER'S RESPONSE:
        {response_text}

        Based on this response, determine whether UI test has been completed successfully or not.
        """

        _logger.debug(f"SubmitToManagerAgent sending prompt: {prompt}")
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
    async def parse_response(self, response: AgentExecutorResponse, ctx: WorkflowContext[UserRequest]) -> None:
        global _user_prompt, _previous_result
        response_text = response.agent_run_response.text.strip().upper()
        _logger.debug(f"ParseManagerResponse received response: {response_text}")
        try:
            if response_text in JobStatus.__members__:
                await ctx.send_message(UserRequest(status=JobStatus[response_text], user_prompt=_user_prompt, previous_result=_previous_result))
            else:
                await ctx.send_message(UserRequest(status=JobStatus.JOBSTATUS_CANNOT_PARSED, user_prompt=_user_prompt, previous_result=_previous_result))  # I_DONT_KNOW_WHY_BUT_JUST_RETRY
        except Exception as e:
            _logger.error(f"Error parsing response: {e}")
            await ctx.send_message(UserRequest(status=JobStatus.JOBSTATUS_CANNOT_PARSED, user_prompt=_user_prompt, previous_result=_previous_result))


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
        chat_client = AzureOpenAIChatClient(
            api_key=_config.AZURE_AI_FOUNDRY_API_KEY,
            endpoint=_config.AZURE_AI_FOUNDRY_ENDPOINT,
            deployment_name=_config.AZURE_AI_FOUNDRY_DEPLOYMENT_NAME,
            api_version="2024-12-01-preview" # for o4-mini
        )

        self.worker_executor = AgentExecutor(
            chat_client.create_agent(
                instructions=(
                    """
                    You are a QA engineer for UI testing.
                    Answer to the user's UI testing request by performing the test using the available tools.
                    Always use the tools to interact with the web page as needed.
                    """
                ),
                # TODO: tool 목록 전체를 보내기
                tools=tools
            ),
            id="worker_agent",
        )
        self.submit_to_worker_agent = SubmitToWorkerExecutor(id="submit_to_worker", worker_executor_id=self.worker_executor.id)
        self.manager_executor = AgentExecutor(
            chat_client.create_agent(
                instructions=(
                    """
                    Respond strictly with one of the following statuses only:
                        - UNREASONABLE_RESULT
                        - INCONSISTENCY_BETWEEN_REASON_AND_RESULT
                        - INCORRECT_TASK
                        - INCOMPLETE_TASK
                        - INCORRECT_METHODOLOGY
                        - INCOMPLETE_METHODOLOGY
                        - INCORRECT_ASSUMPTION
                        - INCOMPLETE_ASSUMPTION
                        - COMPLETED
                    """
                )
            ),
            id="manager_agent",
        )
        self.submit_to_manager_agent = SubmitToManagerAgent(id="submit_to_manager", manager_agent_id=self.manager_executor.id)
        self.parse_manager_response_agent = ParseManagerResponse(id="parse_manager")

        # Build workflow
        self.workflow = (
            WorkflowBuilder()
            .add_edge(self.submit_to_worker_agent, self.worker_executor)
            .add_edge(self.worker_executor, self.submit_to_manager_agent)
            .add_edge(self.submit_to_manager_agent, self.manager_executor)
            .add_edge(self.manager_executor, self.parse_manager_response_agent)
            .add_edge(self.parse_manager_response_agent, self.submit_to_worker_agent)
            .set_start_executor(self.submit_to_worker_agent)
            .build()
        )
        pass

    async def get_response(self, user_prompt: str, max_iterations: int = 2) -> str:
        global _user_prompt, _previous_result
        _user_prompt = user_prompt
        iterations = 0
        result = ""
        async for event in self.workflow.run_stream(UserRequest(status=JobStatus.INIT, user_prompt=user_prompt, previous_result=None)):
            if iterations >= max_iterations:
                _logger.warning("Max iterations reached, terminating workflow.")
                result = str(event.data) if isinstance(event, WorkflowOutputEvent) else "Max iterations reached."
                break
            if isinstance(event, ExecutorCompletedEvent) and event.executor_id == self.worker_executor.id:
                iterations += 1
            elif isinstance(event, WorkflowOutputEvent):
                _logger.debug(f"Workflow final results: {event.data}")
                result = event.data
        _logger.debug(f"Total iterations: {iterations} times.")
        return str(_previous_result)
