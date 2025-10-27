from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from src.config import ConfigManager
from src.kernel_plugins import WebNavigationPlugin

_config = ConfigManager()

class KernelAgent:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KernelAgent, cls).__new__(cls)
            cls._instance._initialize_agent()
        return cls._instance

    def _initialize_agent(self):
        self.agent = ChatCompletionAgent(
            service=AzureChatCompletion(
                api_key=_config.AZURE_AI_FOUNDRY_API_KEY,
                endpoint=_config.AZURE_AI_FOUNDRY_ENDPOINT,
                deployment_name=_config.AZURE_AI_FOUNDRY_DEPLOYMENT_NAME,
            ),
            name="SK-Assistant",
            instructions="You are a helpful assistant.",
            plugins=[WebNavigationPlugin()],
        )

    async def get_response(self, messages):
        response = await self.agent.get_response(messages=messages)
        return response.content

# Example usage:
# agent_singleton = KernelAgentSingleton()
# result = asyncio.run(agent_singleton.get_response("Write a haiku about Semantic Kernel."))
# print(result)

# Output:
# Language's essence,
# Semantic threads intertwine,
# Meaning's core revealed.
