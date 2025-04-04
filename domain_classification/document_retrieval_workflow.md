# Document Retrieval Workflow Implementation

## Search Endpoint Integration

### 1. Domain-Specific Search Endpoints

Each domain should have a dedicated search endpoint that can be queried for relevant documents:

```
{base_url}/search/{domain}?query={encoded_query}
```

For example:
- Github search endpoint: `{base_url}/search/github?query=how%20to%20create%20pull%20request`
- Jenkins search endpoint: `{base_url}/search/jenkins?query=pipeline%20configuration`

### 2. Search API Client

```python
import requests
import urllib.parse

class DomainSearchClient:
    def __init__(self, base_url):
        self.base_url = base_url
        
    def search_domain(self, domain, query, max_results=5):
        """
        Search for documents in a specific domain.
        
        Args:
            domain (str): The domain to search in (e.g., 'github', 'jenkins')
            query (str): The search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of document objects with 'id', 'title', and 'snippet' fields
        """
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}/search/{domain.lower()}?query={encoded_query}&max_results={max_results}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('documents', [])
        except requests.exceptions.RequestException as e:
            print(f"Error searching {domain}: {e}")
            return []
    
    def get_document_content(self, domain, doc_id):
        """
        Retrieve the full content of a document.
        
        Args:
            domain (str): The domain the document belongs to
            doc_id (str): The document ID
            
        Returns:
            str: The full document content
        """
        url = f"{self.base_url}/document/{domain.lower()}/{doc_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('content', '')
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving document {doc_id}: {e}")
            return ""
```

## Relevance Assessment

### 1. Document Relevance Scoring

Use the LLM to assess the relevance of retrieved documents to the original question:

```python
def assess_document_relevance(llm_client, question, document_content, threshold=0.7):
    """
    Assess the relevance of a document to the original question.
    
    Args:
        llm_client: The LLM client (e.g., OpenAI client)
        question (str): The original user question
        document_content (str): The content of the retrieved document
        threshold (float): Minimum relevance score to consider document relevant
        
    Returns:
        tuple: (is_relevant, relevance_score)
    """
    # Truncate document content if too long
    max_content_length = 4000  # Adjust based on model context limits
    truncated_content = document_content[:max_content_length] + "..." if len(document_content) > max_content_length else document_content
    
    prompt = f"""
    On a scale of 0 to 1, rate how relevant the following document is to answering this question:
    
    Question: {question}
    
    Document:
    {truncated_content}
    
    Return only a number between 0 and 1, where 0 means completely irrelevant and 1 means perfectly relevant.
    """
    
    response = llm_client.generate(prompt)
    
    try:
        relevance_score = float(response.strip())
        is_relevant = relevance_score >= threshold
        return is_relevant, relevance_score
    except ValueError:
        # If the LLM doesn't return a valid number, assume not relevant
        return False, 0.0
```

### 2. Batch Document Assessment

For efficiency, assess multiple documents in a single LLM call:

```python
def batch_assess_documents(llm_client, question, documents, threshold=0.7):
    """
    Assess the relevance of multiple documents to the original question.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        documents (list): List of document objects with 'id' and 'content' fields
        threshold (float): Minimum relevance score to consider document relevant
        
    Returns:
        list: List of (document, is_relevant, relevance_score) tuples, sorted by relevance
    """
    if not documents:
        return []
    
    # Create a prompt that asks for relevance scores for all documents
    prompt = f"Question: {question}\n\n"
    
    for i, doc in enumerate(documents):
        # Truncate each document content
        max_content_length = 1000  # Shorter for batch assessment
        truncated_content = doc['content'][:max_content_length] + "..." if len(doc['content']) > max_content_length else doc['content']
        prompt += f"Document {i+1}:\n{truncated_content}\n\n"
    
    prompt += "For each document, rate its relevance to the question on a scale of 0 to 1, where 0 means completely irrelevant and 1 means perfectly relevant.\n"
    prompt += "Return a JSON array of numbers representing the relevance score for each document, in the same order."
    
    response = llm_client.generate(prompt)
    
    try:
        # Parse the response as a list of scores
        import json
        scores = json.loads(response.strip())
        
        # Ensure we have the right number of scores
        if len(scores) != len(documents):
            scores = [0.0] * len(documents)
        
        # Create result tuples and sort by relevance
        results = [(doc, score >= threshold, score) for doc, score in zip(documents, scores)]
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results
    except (ValueError, json.JSONDecodeError):
        # If parsing fails, assume all documents are not relevant
        return [(doc, False, 0.0) for doc in documents]
```

## Domain Fallback Mechanism

### 1. Sequential Domain Search

```python
def search_domains_sequentially(search_client, llm_client, question, domain_queue, max_docs_per_domain=5, relevance_threshold=0.7):
    """
    Search domains sequentially until relevant documents are found.
    
    Args:
        search_client: The domain search client
        llm_client: The LLM client
        question (str): The original user question
        domain_queue (list): Ordered list of domains to search
        max_docs_per_domain (int): Maximum documents to retrieve per domain
        relevance_threshold (float): Minimum relevance score to consider document relevant
        
    Returns:
        tuple: (relevant_documents, searched_domains)
    """
    relevant_documents = []
    searched_domains = []
    
    for domain in domain_queue:
        searched_domains.append(domain)
        
        # Search the current domain
        documents = search_client.search_domain(domain, question, max_results=max_docs_per_domain)
        
        # If no documents found, continue to next domain
        if not documents:
            continue
        
        # Retrieve full content for each document
        for doc in documents:
            doc['content'] = search_client.get_document_content(domain, doc['id'])
        
        # Assess document relevance
        assessed_docs = batch_assess_documents(llm_client, question, documents, threshold=relevance_threshold)
        
        # Filter for relevant documents
        domain_relevant_docs = [(doc, score) for doc, is_relevant, score in assessed_docs if is_relevant]
        
        # If relevant documents found, add them to the result
        if domain_relevant_docs:
            for doc, score in domain_relevant_docs:
                doc['relevance_score'] = score
                doc['domain'] = domain
                relevant_documents.append(doc)
            
            # Stop searching if we found relevant documents
            break
    
    return relevant_documents, searched_domains
```

### 2. Domain Expansion Strategy

```python
def get_expanded_domains(primary_domain):
    """
    Get expanded domains for a primary domain.
    
    Args:
        primary_domain (str): The primary domain
        
    Returns:
        list: List of related domains
    """
    domain_expansions = {
        'github': ['api'],
        'jenkins': ['ci/cd', 'aws', 'azure'],
        'artifactory': ['secret_management'],
        'sonarscan': ['cloud_security'],
        'api': ['github', 'aws', 'azure'],
        'terraform': ['aws', 'azure', 'eks'],
        'eks': ['aws', 'kubernetes'],
        'aws': ['cloud_security', 'terraform', 'eks'],
        'azure': ['cloud_security', 'terraform'],
        'cloud_security': ['aws', 'azure', 'secret_management'],
        'secret_management': ['cloud_security', 'aws', 'azure'],
        'almx': ['github', 'jenkins', 'artifactory']
    }
    
    return domain_expansions.get(primary_domain.lower(), [])
```

### 3. Complete Fallback Workflow

```python
def retrieve_relevant_documents(search_client, llm_client, question, max_domains=3):
    """
    Complete document retrieval workflow with fallback mechanisms.
    
    Args:
        search_client: The domain search client
        llm_client: The LLM client
        question (str): The original user question
        max_domains (int): Maximum number of domains to search
        
    Returns:
        tuple: (relevant_documents, is_generic_question)
    """
    # Step 1: Classify the question into domains
    primary_domain, confidence = classify_question_with_confidence(llm_client, question)
    
    # Initialize domain queue with primary domain
    domain_queue = [primary_domain]
    
    # Step 2: If confidence is low, add alternative domains
    if confidence < 0.7:
        alternative_domains = classify_question_multi_label(llm_client, question)
        for domain in alternative_domains:
            if domain not in domain_queue:
                domain_queue.append(domain)
    
    # Step 3: Add expanded domains for the primary domain
    expanded_domains = get_expanded_domains(primary_domain)
    for domain in expanded_domains:
        if domain not in domain_queue and len(domain_queue) < max_domains:
            domain_queue.append(domain)
    
    # Step 4: Search domains sequentially
    relevant_documents, searched_domains = search_domains_sequentially(
        search_client, llm_client, question, domain_queue
    )
    
    # Step 5: If no relevant documents found, check if it's a generic question
    is_generic_question = False
    if not relevant_documents:
        is_generic_question = is_generic_software_question(llm_client, question)
    
    return relevant_documents, is_generic_question
```

### 4. Generic Question Detection

```python
def is_generic_software_question(llm_client, question):
    """
    Determine if a question is a generic software development question.
    
    Args:
        llm_client: The LLM client
        question (str): The original user question
        
    Returns:
        bool: True if the question is generic, False otherwise
    """
    prompt = f"""
    Determine if the following question is a generic software development question that can be answered with general knowledge, 
    without requiring specific internal documentation or proprietary information.
    
    Question: {question}
    
    Return only "YES" if it's a generic software development question or "NO" if it requires specific internal documentation.
    """
    
    response = llm_client.generate(prompt).strip().upper()
    return response == "YES"
```
