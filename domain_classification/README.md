# README: LLM Domain Classification and Document Retrieval System

This repository contains a comprehensive solution for using Large Language Models (LLMs) such as OpenAI's GPT models to perform domain classification of user questions, retrieve relevant internal knowledge documents, and generate precise answers.

## Repository Contents

1. **Analysis and Design**
   - `domain_analysis.md` - Analysis of domain classification requirements
   - `classification_system_design.md` - Design of the LLM classification system
   - `document_retrieval_workflow.md` - Implementation of document retrieval workflow
   - `answer_generation_process.md` - Design of answer generation process
   - `solution_architecture.md` - Complete solution architecture with diagrams

2. **Implementation**
   - `implementation_examples.md` - Code samples, example prompts, and workflow examples

3. **Summary**
   - `executive_summary.md` - High-level overview of the complete solution
   - `todo.md` - Project task list (all tasks completed)

## System Overview

The solution consists of five main components:

1. **Domain Classification**: Uses LLMs to classify user questions into the most relevant software development domains
2. **Document Retrieval**: Searches domain-specific endpoints for relevant internal knowledge documents
3. **Relevance Assessment**: Evaluates the relevance of retrieved documents to the original question
4. **Answer Generation**: Creates precise answers based on relevant documents or falls back to general knowledge
5. **Error Handling and Monitoring**: Ensures system reliability and provides insights into performance

## Getting Started

To implement this solution:

1. Review the `executive_summary.md` for a high-level overview
2. Examine the detailed design documents to understand each component
3. Use the code samples in `implementation_examples.md` as a starting point
4. Customize the implementation to fit your specific requirements

## Implementation Requirements

- Python 3.8+
- OpenAI API key
- Access to domain-specific search endpoints
- Required Python packages:
  - openai
  - requests
  - flask (for mock API)

## Usage Example

```python
# Initialize the system
from domain_qa_system import OpenAIClient, DomainSearchClient, DomainQASystem

# Set up clients
llm_client = OpenAIClient(api_key="your-openai-api-key")
search_client = DomainSearchClient(base_url="https://your-search-api.com")

# Initialize QA system
qa_system = DomainQASystem(llm_client=llm_client, search_client=search_client)

# Process a question
result = qa_system.process_question("How do I create a pull request in Github?")

# Display the answer
print(result["answer"])
```

## Customization

The system is designed to be modular and extensible. Key areas for customization include:

- Adding or modifying domains
- Adjusting confidence thresholds
- Implementing custom search clients
- Enhancing answer generation prompts
- Adding additional fallback mechanisms

## Next Steps

For production deployment, consider:

1. Implementing caching for frequently asked questions
2. Setting up monitoring and logging
3. Adding user feedback mechanisms
4. Fine-tuning models for improved classification accuracy
5. Implementing vector database integration for better document retrieval

## License

This project is provided as a reference implementation. Please ensure compliance with OpenAI's usage policies when implementing this solution.
