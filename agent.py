# agent.py
import os
from smolagents import ToolCallingAgent, ToolCollection, LiteLLMModel
from mcp import StdioServerParameters
from dotenv import load_dotenv
load_dotenv()

# Use OpenAI API (ensure OPENAI_API_KEY is set in your environment)
model = LiteLLMModel(
    model_id="openai/gpt-4",  # or "openai/gpt-3.5-turbo"
    api_base="https://api.openai.com/v1",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Define how to launch the MCP tool server
server_parameters = StdioServerParameters(
    command="python",
    args=["server.py"],
    env={"PYTHONUNBUFFERED": "1"},
)

# Run agent with tools from MCP
with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    print("🛠️  Tools received from server:")
    for tool in tool_collection.tools:
        print(f"- {tool.name}")

    agent = ToolCallingAgent(tools=[*tool_collection.tools], model=model)
    agent.run("Can you find me an etf similar in sector weight distribution to the index fund VTSAX ")
