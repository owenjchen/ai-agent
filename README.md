# README.md - OpenAI Agent SDK with Azure OpenAI Integration Guide

This repository contains a comprehensive guide and code examples for setting up an intelligent agent using the OpenAI Agent SDK integrated with Azure OpenAI Service.

## Contents

- [Setup Guide](setup_guide.md) - Detailed documentation on how to integrate OpenAI Agent SDK with Azure OpenAI
- [Code Examples](code_examples/) - Working examples demonstrating different integration scenarios

### Code Examples

1. [Basic Agent](code_examples/basic_agent.py) - Simple agent setup with Azure OpenAI
2. [Agent with Tools](code_examples/agent_with_tools.py) - Adding function tools to your agent
3. [Agent with Handoffs](code_examples/agent_with_handoffs.py) - Creating specialized agents with handoff capabilities
4. [Agent with Guardrails](code_examples/agent_with_guardrails.py) - Implementing input validation and safety checks

## Getting Started

1. Clone this repository
2. Create a `.env` file with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_VERSION=2024-05-01-preview
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```
3. Install the required packages:
   ```
   pip install openai-agents azure-identity openai python-dotenv
   ```
4. Explore the setup guide and code examples

## Prerequisites

- Python 3.8 or later
- An Azure account with an active subscription
- An Azure OpenAI resource with deployed models

## Key Features

- Enterprise-grade security and compliance through Azure OpenAI
- Scalable deployment options in Azure
- Monitoring and observability through Azure Application Insights
- Cost management and resource governance
- Integration with other Azure services

## References

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure OpenAI Assistants Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/assistants-quickstart)

