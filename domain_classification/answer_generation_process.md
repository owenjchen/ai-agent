# Answer Generation Process

## Context Integration

### 1. Document Context Preparation

```python
def prepare_document_context(relevant_documents, max_context_length=8000):
    """
    Prepare document context for answer generation.
    
    Args:
        relevant_documents (list): List of relevant document objects
        max_context_length (int): Maximum context length to include
        
    Returns:
        str: Formatted document context
    """
    context = ""
    current_length = 0
    
    # Sort documents by relevance score (highest first)
    sorted_docs = sorted(relevant_documents, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    for doc in sorted_docs:
        # Format document with metadata
        doc_text = f"Document Title: {doc.get('title', 'Untitled')}\n"
        doc_text += f"Domain: {doc.get('domain', 'Unknown')}\n"
        doc_text += f"Content:\n{doc.get('content', '')}\n\n"
        
        # Check if adding this document would exceed the max context length
        if current_length + len(doc_text) > max_context_length:
            # If this is the first document, truncate it
            if current_length == 0:
                truncated_text = doc_text[:max_context_length] + "..."
                context += truncated_text
                break
            # Otherwise, stop adding documents
            else:
                break
        
        # Add document to context
        context += doc_text
        current_length += len(doc_text)
    
    return context
```

### 2. Context Chunking for Large Documents

For cases where the relevant documents are too large to fit in a single LLM context window:

```python
def chunk_document_context(relevant_documents, chunk_size=4000, overlap=500):
    """
    Split document context into overlapping chunks.
    
    Args:
        relevant_documents (list): List of relevant document objects
        chunk_size (int): Maximum size of each chunk
        overlap (int): Overlap between chunks
        
    Returns:
        list: List of context chunks
    """
    # Prepare full context first
    full_context = prepare_document_context(relevant_documents, max_context_length=float('inf'))
    
    # Split into chunks
    chunks = []
    start = 0
    
    while start < len(full_context):
        end = min(start + chunk_size, len(full_context))
        
        # If this is not the first chunk, include overlap from previous chunk
        if start > 0:
            start = start - overlap
        
        chunks.append(full_context[start:end])
        start = end
    
    return chunks
```

## Answer Generation with LLM

### 1. Single-Context Answer Generation

```python
def generate_answer(llm_client, question, document_context):
    """
    Generate an answer based on the question and document context.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        document_context (str): The prepared document context
        
    Returns:
        str: Generated answer
    """
    prompt = f"""
    You are an AI assistant that helps answer software development questions based on internal documentation.
    
    User Question: {question}
    
    Based on the following internal documentation, provide a precise and accurate answer to the user's question.
    If the documentation doesn't contain enough information to answer the question completely, clearly state what information is missing.
    
    Internal Documentation:
    {document_context}
    
    Answer:
    """
    
    return llm_client.generate(prompt)
```

### 2. Multi-Chunk Answer Generation

For handling large document contexts that need to be processed in chunks:

```python
def generate_answer_from_chunks(llm_client, question, context_chunks):
    """
    Generate an answer by processing multiple context chunks and synthesizing the results.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        context_chunks (list): List of context chunks
        
    Returns:
        str: Generated answer
    """
    if not context_chunks:
        return "No relevant information found to answer the question."
    
    # If only one chunk, use single-context generation
    if len(context_chunks) == 1:
        return generate_answer(llm_client, question, context_chunks[0])
    
    # Process each chunk to extract relevant information
    chunk_insights = []
    
    for i, chunk in enumerate(context_chunks):
        prompt = f"""
        You are analyzing a portion of internal documentation to answer this question: "{question}"
        
        Document Chunk {i+1}/{len(context_chunks)}:
        {chunk}
        
        Extract only the key information from this document chunk that is relevant to answering the question.
        Focus on facts, procedures, and specific details. Be concise but complete.
        """
        
        insight = llm_client.generate(prompt)
        chunk_insights.append(insight)
    
    # Synthesize insights into a final answer
    combined_insights = "\n\n".join([f"Insight {i+1}:\n{insight}" for i, insight in enumerate(chunk_insights)])
    
    synthesis_prompt = f"""
    You are synthesizing information to answer this question: "{question}"
    
    Below are insights extracted from multiple documents. Use these insights to create a comprehensive, precise answer.
    If there are contradictions between insights, note them in your answer.
    
    {combined_insights}
    
    Synthesized Answer:
    """
    
    return llm_client.generate(synthesis_prompt)
```

### 3. Answer with Citations

For answers that include citations to the source documents:

```python
def generate_answer_with_citations(llm_client, question, relevant_documents):
    """
    Generate an answer with citations to source documents.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        relevant_documents (list): List of relevant document objects
        
    Returns:
        str: Generated answer with citations
    """
    # Prepare context with document indices for citation
    context = ""
    
    for i, doc in enumerate(relevant_documents):
        context += f"[{i+1}] Document Title: {doc.get('title', 'Untitled')}\n"
        context += f"Domain: {doc.get('domain', 'Unknown')}\n"
        context += f"Content:\n{doc.get('content', '')}\n\n"
    
    prompt = f"""
    You are an AI assistant that helps answer software development questions based on internal documentation.
    
    User Question: {question}
    
    Based on the following internal documentation, provide a precise and accurate answer to the user's question.
    Include citations to the source documents using the format [n] where n is the document number.
    If the documentation doesn't contain enough information to answer the question completely, clearly state what information is missing.
    
    Internal Documentation:
    {context}
    
    Answer (with citations):
    """
    
    return llm_client.generate(prompt)
```

## Handling Cases with No Relevant Documents

### 1. Generic Knowledge Fallback

```python
def generate_generic_answer(llm_client, question):
    """
    Generate an answer based on generic software development knowledge.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        
    Returns:
        str: Generated answer
    """
    prompt = f"""
    You are an AI assistant that helps answer software development questions based on general knowledge.
    
    User Question: {question}
    
    This question appears to be about general software development concepts that don't require specific internal documentation.
    Provide a helpful answer based on general software development knowledge.
    
    Make sure to:
    1. Be accurate and precise
    2. Provide practical information when applicable
    3. Clarify if certain details might vary based on specific implementations
    
    Answer:
    """
    
    return llm_client.generate(prompt)
```

### 2. Clarification Request

```python
def generate_clarification_request(llm_client, question, searched_domains):
    """
    Generate a response requesting clarification when no relevant documents are found.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        searched_domains (list): List of domains that were searched
        
    Returns:
        str: Generated clarification request
    """
    domains_str = ", ".join(searched_domains)
    
    prompt = f"""
    You are an AI assistant that helps answer software development questions based on internal documentation.
    
    User Question: {question}
    
    You searched the following domains but couldn't find relevant information: {domains_str}
    
    Generate a response that:
    1. Acknowledges that you couldn't find relevant information
    2. Suggests possible clarifications or additional details the user could provide
    3. Offers alternative domains or topics that might be more relevant
    
    Clarification Request:
    """
    
    return llm_client.generate(prompt)
```

### 3. Complete Answer Generation Workflow

```python
def complete_answer_workflow(llm_client, search_client, question):
    """
    Complete workflow for generating answers to user questions.
    
    Args:
        llm_client: The LLM client
        search_client: The domain search client
        question (str): The original user question
        
    Returns:
        str: Final answer to the user's question
    """
    # Step 1: Retrieve relevant documents
    relevant_documents, is_generic_question = retrieve_relevant_documents(search_client, llm_client, question)
    
    # Step 2: If relevant documents found, generate answer based on them
    if relevant_documents:
        # Check if we need to chunk the context
        total_content_length = sum(len(doc.get('content', '')) for doc in relevant_documents)
        
        if total_content_length > 6000:  # Threshold for chunking
            context_chunks = chunk_document_context(relevant_documents)
            return generate_answer_from_chunks(llm_client, question, context_chunks)
        else:
            document_context = prepare_document_context(relevant_documents)
            return generate_answer(llm_client, question, document_context)
    
    # Step 3: If no relevant documents but it's a generic question, use generic knowledge
    elif is_generic_question:
        return generate_generic_answer(llm_client, question)
    
    # Step 4: If no relevant documents and not a generic question, request clarification
    else:
        # Get the list of domains that were searched
        primary_domain, _ = classify_question_with_confidence(llm_client, question)
        domain_queue = [primary_domain] + get_expanded_domains(primary_domain)
        
        # Limit to domains that were actually searched
        searched_domains = domain_queue[:3]  # Assuming we searched at most 3 domains
        
        return generate_clarification_request(llm_client, question, searched_domains)
```
