# Complete Solution Architecture

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                           User Interface                                │
│                                                                         │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         Question Processing                             │
│                                                                         │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                       Domain Classification                             │
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │   Zero-Shot     │    │    Few-Shot     │    │   Multi-Label   │     │
│  │ Classification  │    │  Classification  │    │  Classification  │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                       Document Retrieval                                │
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │  Domain Search  │    │    Relevance    │    │Domain Fallback  │     │
│  │    Endpoints    │◄───┤    Assessment   │◄───┤   Mechanism     │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                        Answer Generation                                │
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐     │
│  │    Context      │    │     Answer      │    │   Fallback      │     │
│  │   Integration   │───►│   Synthesis     │───►│   Strategies    │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘     │
│                                                                         │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                         Response Delivery                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Interactions

### 1. Main System Flow

```python
class DomainQASystem:
    def __init__(self, llm_client, search_base_url):
        """
        Initialize the Domain QA System.
        
        Args:
            llm_client: The LLM client (e.g., OpenAI client)
            search_base_url (str): Base URL for domain search endpoints
        """
        self.llm_client = llm_client
        self.search_client = DomainSearchClient(search_base_url)
        
        # Define the list of supported domains
        self.domains = [
            "Github", "Jenkins", "Artifactory", "SonarScan", "API", 
            "Terraform", "EKS", "AWS", "Azure", "Cloud Security", 
            "Secret Management", "ALMx"
        ]
        
        # Domain descriptions for classification
        self.domain_descriptions = {
            "Github": "Version control, repositories, pull requests, issues, actions",
            "Jenkins": "CI/CD pipelines, builds, automation",
            "Artifactory": "Binary repository management, artifact storage",
            "SonarScan": "Code quality, static analysis, security scanning",
            "API": "API development, documentation, testing, management",
            "Terraform": "Infrastructure as code, provisioning",
            "EKS": "Amazon Elastic Kubernetes Service, container orchestration",
            "AWS": "Amazon Web Services, cloud infrastructure",
            "Azure": "Microsoft's cloud platform",
            "Cloud Security": "Security practices for cloud environments",
            "Secret Management": "Managing credentials, keys, certificates",
            "ALMx": "Application Lifecycle Management"
        }
    
    def process_question(self, question):
        """
        Process a user question and generate an answer.
        
        Args:
            question (str): The user's question
            
        Returns:
            dict: Result containing answer and metadata
        """
        try:
            # Step 1: Classify the question into domains
            primary_domain, confidence = self._classify_question(question)
            
            # Step 2: Build domain queue for searching
            domain_queue = self._build_domain_queue(question, primary_domain, confidence)
            
            # Step 3: Search for relevant documents
            relevant_documents, searched_domains = self._search_domains(question, domain_queue)
            
            # Step 4: Generate answer
            if relevant_documents:
                answer = self._generate_answer_from_documents(question, relevant_documents)
                source_info = self._extract_source_info(relevant_documents)
                
                return {
                    "answer": answer,
                    "sources": source_info,
                    "primary_domain": primary_domain,
                    "confidence": confidence,
                    "searched_domains": searched_domains,
                    "status": "answered_with_documents"
                }
            
            # Step 5: Check if it's a generic question
            is_generic = self._is_generic_software_question(question)
            
            if is_generic:
                answer = self._generate_generic_answer(question)
                
                return {
                    "answer": answer,
                    "sources": [],
                    "primary_domain": primary_domain,
                    "confidence": confidence,
                    "searched_domains": searched_domains,
                    "status": "answered_with_general_knowledge"
                }
            
            # Step 6: Generate clarification request
            clarification = self._generate_clarification_request(question, searched_domains)
            
            return {
                "answer": clarification,
                "sources": [],
                "primary_domain": primary_domain,
                "confidence": confidence,
                "searched_domains": searched_domains,
                "status": "clarification_needed"
            }
        
        except Exception as e:
            # Handle errors
            error_message = f"Error processing question: {str(e)}"
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "error": error_message,
                "status": "error"
            }
    
    def _classify_question(self, question):
        """Implementation of domain classification"""
        # This would call the classification functions defined earlier
        pass
    
    def _build_domain_queue(self, question, primary_domain, confidence):
        """Implementation of domain queue building"""
        # This would call the domain queue building functions defined earlier
        pass
    
    def _search_domains(self, question, domain_queue):
        """Implementation of domain searching"""
        # This would call the document retrieval functions defined earlier
        pass
    
    def _generate_answer_from_documents(self, question, relevant_documents):
        """Implementation of answer generation from documents"""
        # This would call the answer generation functions defined earlier
        pass
    
    def _is_generic_software_question(self, question):
        """Implementation of generic question detection"""
        # This would call the generic question detection function defined earlier
        pass
    
    def _generate_generic_answer(self, question):
        """Implementation of generic answer generation"""
        # This would call the generic answer generation function defined earlier
        pass
    
    def _generate_clarification_request(self, question, searched_domains):
        """Implementation of clarification request generation"""
        # This would call the clarification request generation function defined earlier
        pass
    
    def _extract_source_info(self, relevant_documents):
        """Extract source information from relevant documents"""
        sources = []
        for doc in relevant_documents:
            sources.append({
                "title": doc.get("title", "Untitled"),
                "domain": doc.get("domain", "Unknown"),
                "id": doc.get("id", ""),
                "relevance_score": doc.get("relevance_score", 0.0)
            })
        return sources
```

### 2. OpenAI Client Implementation

```python
class OpenAIClient:
    def __init__(self, api_key, model="gpt-4"):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key (str): OpenAI API key
            model (str): Model to use for generation
        """
        self.api_key = api_key
        self.model = model
        
        # Import OpenAI library
        import openai
        openai.api_key = api_key
        self.openai = openai
    
    def generate(self, prompt, max_tokens=1000, temperature=0.0):
        """
        Generate text using the OpenAI API.
        
        Args:
            prompt (str): The prompt to generate from
            max_tokens (int): Maximum tokens to generate
            temperature (float): Temperature for generation
            
        Returns:
            str: Generated text
        """
        try:
            response = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that provides accurate and precise information about software development."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""
    
    def classify_with_confidence(self, question, domains, domain_descriptions):
        """
        Classify a question into a domain with confidence score.
        
        Args:
            question (str): The question to classify
            domains (list): List of domain names
            domain_descriptions (dict): Dictionary mapping domain names to descriptions
            
        Returns:
            tuple: (domain, confidence)
        """
        # Build the classification prompt
        prompt = "Given the following domains related to software development:\n\n"
        
        for domain in domains:
            description = domain_descriptions.get(domain, "")
            prompt += f"- {domain}: {description}\n"
        
        prompt += f"\nClassify the following question into the most relevant domain:\n{question}\n\n"
        prompt += "Return the domain name followed by a confidence score between 0 and 1, separated by a colon.\n"
        prompt += "Example: \"Github:0.92\""
        
        # Generate the classification
        response = self.generate(prompt)
        
        try:
            # Parse the response
            domain, confidence_str = response.split(":", 1)
            domain = domain.strip()
            confidence = float(confidence_str.strip())
            
            # Validate the domain
            if domain not in domains:
                # Find the closest matching domain
                import difflib
                closest_domain = difflib.get_close_matches(domain, domains, n=1, cutoff=0.6)
                
                if closest_domain:
                    domain = closest_domain[0]
                else:
                    domain = domains[0]  # Default to first domain
                    confidence = 0.1  # Low confidence
            
            return domain, confidence
        except Exception as e:
            print(f"Error parsing classification: {e}")
            return domains[0], 0.1  # Default to first domain with low confidence
```

### 3. System Initialization and Usage

```python
def initialize_qa_system(openai_api_key, search_base_url):
    """
    Initialize the QA system.
    
    Args:
        openai_api_key (str): OpenAI API key
        search_base_url (str): Base URL for domain search endpoints
        
    Returns:
        DomainQASystem: Initialized QA system
    """
    # Initialize OpenAI client
    llm_client = OpenAIClient(api_key=openai_api_key)
    
    # Initialize QA system
    qa_system = DomainQASystem(llm_client=llm_client, search_base_url=search_base_url)
    
    return qa_system

def process_user_question(qa_system, question):
    """
    Process a user question and return the answer.
    
    Args:
        qa_system (DomainQASystem): The QA system
        question (str): The user's question
        
    Returns:
        dict: Result containing answer and metadata
    """
    # Process the question
    result = qa_system.process_question(question)
    
    # Format the result for display
    formatted_result = {
        "answer": result["answer"],
        "metadata": {
            "primary_domain": result["primary_domain"],
            "confidence": result["confidence"],
            "status": result["status"],
            "searched_domains": result["searched_domains"]
        }
    }
    
    # Add sources if available
    if result.get("sources"):
        formatted_result["sources"] = result["sources"]
    
    return formatted_result
```

## Error Handling

### 1. Exception Handling Strategy

```python
def safe_execute(func, default_return=None, error_message="An error occurred"):
    """
    Safely execute a function with exception handling.
    
    Args:
        func: Function to execute
        default_return: Default return value if function fails
        error_message: Error message to log
        
    Returns:
        Result of function or default_return if function fails
    """
    try:
        return func()
    except Exception as e:
        print(f"{error_message}: {str(e)}")
        return default_return
```

### 2. Retry Mechanism for API Calls

```python
def retry_api_call(func, max_retries=3, backoff_factor=2):
    """
    Retry an API call with exponential backoff.
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retries
        backoff_factor: Backoff factor for retry delay
        
    Returns:
        Result of function or raises the last exception
    """
    import time
    
    retries = 0
    last_exception = None
    
    while retries < max_retries:
        try:
            return func()
        except Exception as e:
            last_exception = e
            retries += 1
            
            if retries < max_retries:
                # Calculate delay with exponential backoff
                delay = backoff_factor ** retries
                print(f"Retry {retries}/{max_retries} after {delay} seconds...")
                time.sleep(delay)
    
    # If we've exhausted all retries, raise the last exception
    raise last_exception
```

### 3. Graceful Degradation

```python
class DomainQASystem:
    # ... (previous implementation) ...
    
    def process_question_with_degradation(self, question):
        """
        Process a user question with graceful degradation.
        
        Args:
            question (str): The user's question
            
        Returns:
            dict: Result containing answer and metadata
        """
        try:
            # Try the full pipeline first
            return self.process_question(question)
        except Exception as e:
            print(f"Full pipeline failed: {e}")
            
            try:
                # Fallback to classification only
                primary_domain, confidence = self._classify_question(question)
                
                # Try generic answer generation
                answer = self._generate_generic_answer(question)
                
                return {
                    "answer": answer,
                    "sources": [],
                    "primary_domain": primary_domain,
                    "confidence": confidence,
                    "searched_domains": [primary_domain],
                    "status": "degraded_service_generic_answer"
                }
            except Exception as e2:
                print(f"Degraded service failed: {e2}")
                
                # Last resort fallback
                return {
                    "answer": "I'm currently experiencing technical difficulties and cannot process your question. Please try again later.",
                    "status": "service_unavailable"
                }
```

### 4. Monitoring and Logging

```python
class QASystemLogger:
    def __init__(self, log_file=None):
        """
        Initialize the logger.
        
        Args:
            log_file (str): Path to log file
        """
        self.log_file = log_file
        
        # Initialize logging
        import logging
        
        self.logger = logging.getLogger("qa_system")
        self.logger.setLevel(logging.INFO)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        
        # Add file handler if log file specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            self.logger.addHandler(file_handler)
    
    def log_question(self, question, user_id=None):
        """Log a user question"""
        self.logger.info(f"Question received: {question} (User: {user_id or 'anonymous'})")
    
    def log_classification(self, question, domain, confidence):
        """Log a classification result"""
        self.logger.info(f"Classification: '{question}' -> {domain} (confidence: {confidence:.2f})")
    
    def log_document_retrieval(self, domain, query, num_documents):
        """Log document retrieval"""
        self.logger.info(f"Retrieved {num_documents} documents from {domain} for query: {query}")
    
    def log_answer_generation(self, status, answer_length):
        """Log answer generation"""
        self.logger.info(f"Generated answer ({status}): {answer_length} characters")
    
    def log_error(self, stage, error):
        """Log an error"""
        self.logger.error(f"Error in {stage}: {error}")
```

### 5. Input Validation

```python
def validate_question(question):
    """
    Validate a user question.
    
    Args:
        question (str): The user's question
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check if question is empty
    if not question or question.strip() == "":
        return False, "Question cannot be empty"
    
    # Check if question is too short
    if len(question.strip()) < 5:
        return False, "Question is too short"
    
    # Check if question is too long
    if len(question) > 1000:
        return False, "Question is too long (maximum 1000 characters)"
    
    # Check if question ends with a question mark or is imperative
    if not (question.strip().endswith("?") or any(question.lower().startswith(cmd) for cmd in ["how", "what", "why", "when", "where", "who", "which", "show", "tell", "explain", "describe", "list", "find", "get"])):
        return True, "Note: Your input doesn't appear to be a question. I'll try to interpret it as a request for information."
    
    return True, ""
```
