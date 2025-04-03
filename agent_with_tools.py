"""
Agent with Tools Example - Integrating OpenAI Agent SDK with Azure OpenAI

This example demonstrates how to create an agent with tools using the OpenAI Agent SDK
with Azure OpenAI as the underlying model provider.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from typing_extensions import TypedDict

# Load environment variables
load_dotenv()

# Disable tracing for simplicity
set_tracing_disabled(disabled=True)

# Define tool input types
class Location(TypedDict):
    city: str
    country: str

class SearchQuery(TypedDict):
    query: str

# Define tools as functions
@function_tool
async def fetch_weather(location: Location) -> str:
    """Fetch the current weather for a given location.
    
    Args:
        location: The location to fetch the weather for, including city and country.
    """
    # In a real implementation, you would call a weather API here
    return f"The weather in {location['city']}, {location['country']} is currently sunny with a temperature of 22°C."

@function_tool
async def search_web(query: SearchQuery) -> str:
    """Search the web for information.
    
    Args:
        query: The search query string.
    """
    # In a real implementation, you would call a search API here
    return f"Here are the top results for '{query['query']}':\n1. Example result 1\n2. Example result 2\n3. Example result 3"

@function_tool
async def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate.
    """
    try:
        # Warning: eval can be dangerous in production code
        # Use a safer alternative in real applications
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

async def main():
    # Create the Azure OpenAI client
    azure_openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Configure the agent with Azure OpenAI and tools
    agent = Agent(
        name="Research Assistant",
        instructions="""You are a helpful research assistant that can search for information, 
                       check the weather, and perform calculations. Use the appropriate tool 
                       based on the user's request.""",
        model=OpenAIChatCompletionsModel(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_client=azure_openai_client
        ),
        tools=[fetch_weather, search_web, calculate]
    )

    # Run the agent with different queries
    queries = [
        "What's the weather like in London, UK?",
        "Search for information about renewable energy",
        "Calculate 15 * 24 + 7"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        result = await Runner.run(agent, query)
        print(f"Agent: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
