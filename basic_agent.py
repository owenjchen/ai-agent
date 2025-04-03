"""
Basic Agent Example - Integrating OpenAI Agent SDK with Azure OpenAI

This example demonstrates how to create a simple agent using the OpenAI Agent SDK
with Azure OpenAI as the underlying model provider.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled

# Load environment variables
load_dotenv()

# Disable tracing for simplicity
set_tracing_disabled(disabled=True)

async def main():
    # Create the Azure OpenAI client
    azure_openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Configure the agent with Azure OpenAI
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant that provides concise and accurate information.",
        model=OpenAIChatCompletionsModel(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            openai_client=azure_openai_client
        )
    )

    # Run the agent
    user_input = "What are the benefits of cloud computing?"
    print(f"User: {user_input}")
    
    result = await Runner.run(agent, user_input)
    print(f"Agent: {result.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
