"""
Agent with Handoffs Example - Integrating OpenAI Agent SDK with Azure OpenAI

This example demonstrates how to create agents with handoff capabilities using the OpenAI Agent SDK
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
    
    # Create model configuration with Azure OpenAI
    model_config = OpenAIChatCompletionsModel(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_client=azure_openai_client
    )

    # Create specialized agents
    math_agent = Agent(
        name="Math Tutor",
        handoff_description="Specialist agent for math questions and calculations",
        instructions="""You are a math tutor who helps students understand mathematical concepts and solve problems.
                       Explain your reasoning step by step and provide clear explanations.
                       Focus only on mathematics topics.""",
        model=model_config
    )

    history_agent = Agent(
        name="History Tutor",
        handoff_description="Specialist agent for historical questions and information",
        instructions="""You are a history tutor who helps students understand historical events, figures, and contexts.
                       Provide accurate information with relevant dates and explain historical significance.
                       Focus only on history topics.""",
        model=model_config
    )

    science_agent = Agent(
        name="Science Tutor",
        handoff_description="Specialist agent for science questions and explanations",
        instructions="""You are a science tutor who helps students understand scientific concepts and phenomena.
                       Explain scientific principles clearly and relate them to real-world applications.
                       Focus only on science topics.""",
        model=model_config
    )

    # Create a triage agent that can hand off to specialized agents
    triage_agent = Agent(
        name="Education Assistant",
        instructions="""You are an education assistant who helps direct students to the appropriate specialized tutor.
                       For math questions (algebra, calculus, geometry, etc.), hand off to the Math Tutor.
                       For history questions (events, figures, civilizations, etc.), hand off to the History Tutor.
                       For science questions (physics, chemistry, biology, etc.), hand off to the Science Tutor.
                       If a question spans multiple domains, choose the most relevant specialist.""",
        handoffs=[math_agent, history_agent, science_agent],
        model=model_config
    )

    # Example questions to demonstrate handoffs
    questions = [
        "Can you help me solve this equation: 3x + 7 = 22?",
        "What were the main causes of World War I?",
        "How does photosynthesis work in plants?"
    ]
    
    for question in questions:
        print(f"\nUser: {question}")
        print("Processing...")
        
        result = await Runner.run(triage_agent, question)
        
        print(f"Agent: {result.final_output}")
        
        # Display handoff information if available
        if hasattr(result, 'handoff_history') and result.handoff_history:
            handoffs = result.handoff_history
            print("\nHandoff Path:")
            for i, handoff in enumerate(handoffs):
                print(f"  {i+1}. {handoff.from_agent.name} → {handoff.to_agent.name}")

if __name__ == "__main__":
    asyncio.run(main())
