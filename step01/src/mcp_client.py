import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic #TODO: Ollama, Azure AI Foundry로 변경
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    """
    커스텀 로그인이 필요할땐 자체 Playwright MCP를
    그외에는 일반 Playwright MCP를 사용
    자체 Playwright MCP 내부에선 tool_call 메서드 호출로 로그인한 다음 
    브라우저 컨텍스트를 전달함
    """
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        print("Connected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                result = await self.session.call_tool(content.name, content.input)
                final_text.append(result.content)

        return "\n".join(final_text)
