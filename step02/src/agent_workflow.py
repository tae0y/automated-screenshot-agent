from azure.identity import AzureCliCredential

from agent_framework.azure import AzureChatClient
from agent_framework import SequentialBuilder
from agent_framework import ChatMessage, WorkflowCompletedEvent

from src.config import ConfigManager
from src.logger import get_logger

_logger = get_logger(__name__)
_config = ConfigManager()

# Observer
# Decider
# Executor
# Supervisor
# Recorder
# ㄴ Context Memory


class AgentWorkflow:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentWorkflow, cls).__new__(cls)
            cls._instance._initialize_workflow()
        return cls._instance
    
    def _initialize_workflow(self):
        pass
    
    async def get_response(self, messages):
        pass
