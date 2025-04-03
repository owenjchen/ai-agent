# Setting up an Agent using OpenAI Agent SDK and Azure OpenAI Service

This comprehensive guide will walk you through the process of setting up an intelligent agent using the OpenAI Agent SDK integrated with Azure OpenAI Service. By following these instructions, you'll be able to create powerful AI agents that leverage Azure's enterprise-grade security, compliance, and scalability features.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Azure OpenAI Service Setup](#azure-openai-service-setup)
5. [OpenAI Agent SDK Configuration](#openai-agent-sdk-configuration)
6. [Integration Steps](#integration-steps)
7. [Advanced Features](#advanced-features)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Troubleshooting](#troubleshooting)
10. [References](#references)

## Introduction

The OpenAI Agent SDK provides a lightweight, powerful framework for building AI agents with very few abstractions. When combined with Azure OpenAI Service, you can create production-ready AI applications that benefit from Azure's security, compliance, and enterprise capabilities.

Key benefits of this integration include:

- Enterprise-grade security and compliance through Azure OpenAI
- Scalable deployment options in Azure
- Monitoring and observability through Azure Application Insights
- Cost management and resource governance
- Integration with other Azure services

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or later
- An Azure account with an active subscription
- An Azure OpenAI resource with deployed models
- Basic familiarity with Python programming
- Understanding of AI concepts and prompt engineering

## Installation

### 1. Set up a Python virtual environment

```bash
# Create a new directory for your project
mkdir my_agent_project
cd my_agent_project

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

### 2. Install the required packages

```bash
# Install the OpenAI Agents SDK
pip install openai-agents

# Install the Azure OpenAI client library
pip install azure-identity openai
```

## Azure OpenAI Service Setup

### 1. Create an Azure OpenAI resource

If you haven't already created an Azure OpenAI resource:

1. Sign in to the [Azure portal](https://portal.azure.com)
2. Search for "Azure OpenAI" and select "Azure OpenAI"
3. Click "Create" and follow the prompts to create a new resource
4. Choose an appropriate region, pricing tier, and other settings
5. Review and create the resource

### 2. Deploy models

1. Navigate to your Azure OpenAI resource in the Azure portal
2. Select "Model deployments" from the left menu
3. Click "Create new deployment"
4. Select a model (e.g., GPT-4o, GPT-4o mini, or GPT-3.5-Turbo)
5. Give your deployment a name (you'll need this later)
6. Configure other settings as needed and create the deployment

### 3. Get your API credentials

You'll need the following information to connect to your Azure OpenAI resource:

1. Navigate to your Azure OpenAI resource in the Azure portal
2. Select "Keys and Endpoint" from the left menu
3. Note down the following:
   - Endpoint URL (e.g., `https://your-resource-name.openai.azure.com/`)
   - API key (either KEY1 or KEY2)

## OpenAI Agent SDK Configuration

The OpenAI Agent SDK provides several key components:

- **Agents**: LLMs equipped with instructions and tools
- **Handoffs**: Allow agents to delegate to other agents for specific tasks
- **Guardrails**: Enable input validation for agents
- **Tools**: Functions that agents can use to perform actions

### Basic Agent Setup

Here's a simple example of creating an agent:

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant that provides concise and accurate information."
)

result = Runner.run_sync(agent, "What is the capital of France?")
print(result.final_output)
```

## Integration Steps

To integrate the OpenAI Agent SDK with Azure OpenAI Service, you need to create an Azure OpenAI client and pass it to the Agent. Here's how to do it:

### 1. Set up environment variables

Create a `.env` file in your project directory with the following content:

```
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-05-01-preview
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

### 2. Load environment variables

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

### 3. Create an Azure OpenAI client

There are two authentication methods you can use:

#### Option 1: API Key Authentication

```python
from openai import AsyncAzureOpenAI

# Create the Azure OpenAI client
azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
```

#### Option 2: Microsoft Entra ID Authentication (Recommended for production)

```python
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI

# Create a token provider using DefaultAzureCredential
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), 
    "https://cognitiveservices.azure.com/.default"
)

# Create the Azure OpenAI client with token authentication
azure_openai_client = AsyncAzureOpenAI(
    azure_ad_token_provider=token_provider,
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)
```

### 4. Configure the Agent to use Azure OpenAI

```python
import os
import asyncio
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled

# Disable tracing if not needed
set_tracing_disabled(disabled=True)

# Create the Azure OpenAI client
azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Configure the agent with Azure OpenAI
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=OpenAIChatCompletionsModel(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        openai_client=azure_openai_client
    )
)

# Run the agent
async def main():
    result = await Runner.run(agent, "Write a haiku about cloud computing.")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### Adding Tools to Your Agent

Tools allow your agent to perform actions like searching the web, accessing files, or calling external APIs.

```python
from agents import Agent, Runner, function_tool
from typing_extensions import TypedDict

class Location(TypedDict):
    lat: float
    long: float

@function_tool
async def fetch_weather(location: Location) -> str:
    """Fetch the weather for a given location.
    
    Args:
        location: The location to fetch the weather for.
    """
    # In a real implementation, you would call a weather API here
    return "sunny"

# Create an agent with the tool
agent = Agent(
    name="Weather Assistant",
    instructions="You help users check the weather.",
    tools=[fetch_weather]
)
```

### Implementing Handoffs Between Agents

Handoffs allow agents to delegate tasks to specialized agents.

```python
from agents import Agent, Runner

# Create specialized agents
math_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step."
)

history_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly."
)

# Create a triage agent that can hand off to specialized agents
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's question",
    handoffs=[math_agent, history_agent]
)

# Run the triage agent
async def main():
    result = await Runner.run(triage_agent, "What is the Pythagorean theorem?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Adding Guardrails

Guardrails allow you to validate user inputs and ensure your agent behaves appropriately.

```python
from agents import Agent, Runner, GuardrailFunctionOutput, InputGuardrail
from pydantic import BaseModel

class HomeworkOutput(BaseModel):
    is_homework: bool
    reasoning: str

# Create a guardrail agent
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about homework.",
    output_type=HomeworkOutput
)

# Define the guardrail function
async def homework_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_homework,
    )

# Create an agent with the guardrail
agent = Agent(
    name="Homework Helper",
    instructions="You help with homework questions.",
    input_guardrails=[InputGuardrail(homework_guardrail)]
)
```

## Monitoring and Observability

You can monitor your agents using Azure Application Insights through OpenTelemetry integration.

### Setting up monitoring

```python
import os
import logfire
from openai import AsyncAzureOpenAI
from agents import set_default_openai_client, set_tracing_disabled

# Create the Azure OpenAI client
azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Configure OpenAI Agents SDK
set_default_openai_client(azure_openai_client)
set_tracing_disabled(False)  # Enable tracing

# Configure OpenTelemetry endpoint
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "http://0.0.0.0:4318/v1/traces"

# Configure Logfire for distributed tracing
logfire.configure(
    service_name='my-agent-service',
    send_to_logfire=False,
    distributed_tracing=True
)

# Instrument OpenAI Agents
logfire.instrument_openai_agents()
```

## Troubleshooting

### Common Issues and Solutions

1. **Authentication Errors**
   - Ensure your API key or Microsoft Entra ID credentials are correct
   - Check that your Azure OpenAI resource is properly provisioned

2. **Model Deployment Issues**
   - Verify that you've deployed the correct model in Azure OpenAI
   - Ensure you're using the deployment name, not the model name

3. **Integration Problems**
   - Make sure you're using compatible versions of the OpenAI and Azure OpenAI libraries
   - Check that you're passing the Azure OpenAI client correctly to the Agent

4. **Performance Concerns**
   - Consider using async methods for better performance
   - Monitor your agent's performance using Azure Application Insights

## References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI Assistants Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/assistants-quickstart)
- [OpenAI Developer Community](https://community.openai.com/)
- [Microsoft Tech Community](https://techcommunity.microsoft.com/)
