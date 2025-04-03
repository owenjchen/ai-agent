"""
Agent with Guardrails Example - Integrating OpenAI Agent SDK with Azure OpenAI

This example demonstrates how to create an agent with guardrails using the OpenAI Agent SDK
with Azure OpenAI as the underlying model provider.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, GuardrailFunctionOutput, InputGuardrail, set_tracing_disabled
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Disable tracing for simplicity
set_tracing_disabled(disabled=True)

# Define output models for guardrails
class ContentSafetyOutput(BaseModel):
    is_safe: bool
    reasoning: str

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

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

    # Create guardrail agents
    content_safety_agent = Agent(
        name="Content Safety Check",
        instructions="""You evaluate if user input contains harmful, offensive, or inappropriate content.
                       Respond with is_safe=True only if the content is completely safe and appropriate.
                       Respond with is_safe=False if the content contains any harmful, offensive, or inappropriate elements.
                       Provide clear reasoning for your decision.""",
        output_type=ContentSafetyOutput,
        model=model_config
    )
    
    homework_agent = Agent(
        name="Homework Check",
        instructions="""You evaluate if the user is asking for direct homework answers or trying to cheat on assignments.
                       Respond with is_homework=True if the query appears to be asking for direct homework answers.
                       Respond with is_homework=False if the query is asking for general knowledge or understanding.
                       Provide clear reasoning for your decision.""",
        output_type=HomeworkOutput,
        model=model_config
    )

    # Define guardrail functions
    async def content_safety_guardrail(ctx, agent, input_data):
        result = await Runner.run(content_safety_agent, input_data, context=ctx.context)
        final_output = result.final_output_as(ContentSafetyOutput)
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=not final_output.is_safe,
            message=f"Content safety check: {final_output.reasoning}" if not final_output.is_safe else None
        )

    async def homework_guardrail(ctx, agent, input_data):
        result = await Runner.run(homework_agent, input_data, context=ctx.context)
        final_output = result.final_output_as(HomeworkOutput)
        return GuardrailFunctionOutput(
            output_info=final_output,
            tripwire_triggered=final_output.is_homework,
            message=f"Homework policy: {final_output.reasoning}" if final_output.is_homework else None
        )

    # Create the main agent with guardrails
    education_agent = Agent(
        name="Education Assistant",
        instructions="""You are an educational assistant that helps students learn and understand concepts.
                       Provide explanations that promote understanding rather than giving direct answers.
                       Use examples to illustrate concepts and encourage critical thinking.""",
        input_guardrails=[
            InputGuardrail(content_safety_guardrail),
            InputGuardrail(homework_guardrail)
        ],
        model=model_config
    )

    # Example queries to test guardrails
    queries = [
        "Can you explain how photosynthesis works?",
        "Do my homework for me: solve x^2 + 5x + 6 = 0",
        "What are the key themes in Shakespeare's Macbeth?"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        print("Processing...")
        
        try:
            result = await Runner.run(education_agent, query)
            print(f"Agent: {result.final_output}")
        except Exception as e:
            print(f"Guardrail triggered: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
