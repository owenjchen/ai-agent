# Implementation Examples

## Code Samples

### 1. Complete System Implementation

```python
# main.py
import os
import argparse
from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key, model="gpt-4"):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key (str): OpenAI API key
            model (str): Model to use for generation
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
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
            response = self.client.chat.completions.create(
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

class DomainSearchClient:
    def __init__(self, base_url):
        """
        Initialize the domain search client.
        
        Args:
            base_url (str): Base URL for domain search endpoints
        """
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
        import requests
        import urllib.parse
        
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
        import requests
        
        url = f"{self.base_url}/document/{domain.lower()}/{doc_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json().get('content', '')
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving document {doc_id}: {e}")
            return ""

class DomainQASystem:
    def __init__(self, llm_client, search_client):
        """
        Initialize the Domain QA System.
        
        Args:
            llm_client: The LLM client (e.g., OpenAI client)
            search_client: The domain search client
        """
        self.llm_client = llm_client
        self.search_client = search_client
        
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
    
    def classify_question(self, question):
        """
        Classify a question into a domain with confidence score.
        
        Args:
            question (str): The question to classify
            
        Returns:
            tuple: (domain, confidence)
        """
        # Build the classification prompt
        prompt = "Given the following domains related to software development:\n\n"
        
        for domain in self.domains:
            description = self.domain_descriptions.get(domain, "")
            prompt += f"- {domain}: {description}\n"
        
        prompt += f"\nClassify the following question into the most relevant domain:\n{question}\n\n"
        prompt += "Return the domain name followed by a confidence score between 0 and 1, separated by a colon.\n"
        prompt += "Example: \"Github:0.92\""
        
        # Generate the classification
        response = self.llm_client.generate(prompt)
        
        try:
            # Parse the response
            domain, confidence_str = response.split(":", 1)
            domain = domain.strip()
            confidence = float(confidence_str.strip())
            
            # Validate the domain
            if domain not in self.domains:
                # Find the closest matching domain
                import difflib
                closest_domain = difflib.get_close_matches(domain, self.domains, n=1, cutoff=0.6)
                
                if closest_domain:
                    domain = closest_domain[0]
                else:
                    domain = self.domains[0]  # Default to first domain
                    confidence = 0.1  # Low confidence
            
            return domain, confidence
        except Exception as e:
            print(f"Error parsing classification: {e}")
            return self.domains[0], 0.1  # Default to first domain with low confidence
    
    def classify_question_multi_label(self, question, max_domains=3):
        """
        Classify a question into multiple domains.
        
        Args:
            question (str): The question to classify
            max_domains (int): Maximum number of domains to return
            
        Returns:
            list: List of domain names
        """
        # Build the classification prompt
        prompt = "Given the following domains related to software development:\n\n"
        
        for domain in self.domains:
            description = self.domain_descriptions.get(domain, "")
            prompt += f"- {domain}: {description}\n"
        
        prompt += f"\nClassify the following question into the most relevant domains (up to {max_domains}):\n{question}\n\n"
        prompt += "Return the domain names in order of relevance, separated by commas, without any explanation."
        
        # Generate the classification
        response = self.llm_client.generate(prompt)
        
        try:
            # Parse the response
            domains = [domain.strip() for domain in response.split(",")]
            
            # Validate the domains
            valid_domains = []
            for domain in domains:
                if domain in self.domains:
                    valid_domains.append(domain)
                else:
                    # Find the closest matching domain
                    import difflib
                    closest_domain = difflib.get_close_matches(domain, self.domains, n=1, cutoff=0.6)
                    
                    if closest_domain and closest_domain[0] not in valid_domains:
                        valid_domains.append(closest_domain[0])
            
            # Limit to max_domains
            valid_domains = valid_domains[:max_domains]
            
            # If no valid domains, return the first domain
            if not valid_domains:
                valid_domains = [self.domains[0]]
            
            return valid_domains
        except Exception as e:
            print(f"Error parsing multi-label classification: {e}")
            return [self.domains[0]]  # Default to first domain
    
    def get_expanded_domains(self, primary_domain):
        """
        Get expanded domains for a primary domain.
        
        Args:
            primary_domain (str): The primary domain
            
        Returns:
            list: List of related domains
        """
        domain_expansions = {
            'Github': ['API'],
            'Jenkins': ['AWS', 'Azure'],
            'Artifactory': ['Secret Management'],
            'SonarScan': ['Cloud Security'],
            'API': ['Github', 'AWS', 'Azure'],
            'Terraform': ['AWS', 'Azure', 'EKS'],
            'EKS': ['AWS'],
            'AWS': ['Cloud Security', 'Terraform', 'EKS'],
            'Azure': ['Cloud Security', 'Terraform'],
            'Cloud Security': ['AWS', 'Azure', 'Secret Management'],
            'Secret Management': ['Cloud Security', 'AWS', 'Azure'],
            'ALMx': ['Github', 'Jenkins', 'Artifactory']
        }
        
        return domain_expansions.get(primary_domain, [])
    
    def build_domain_queue(self, question, primary_domain, confidence, max_domains=3):
        """
        Build a queue of domains to search.
        
        Args:
            question (str): The original question
            primary_domain (str): The primary domain
            confidence (float): Confidence in the primary domain
            max_domains (int): Maximum number of domains to include
            
        Returns:
            list: Ordered list of domains to search
        """
        # Initialize domain queue with primary domain
        domain_queue = [primary_domain]
        
        # If confidence is low, add alternative domains
        if confidence < 0.7:
            alternative_domains = self.classify_question_multi_label(question)
            for domain in alternative_domains:
                if domain not in domain_queue and len(domain_queue) < max_domains:
                    domain_queue.append(domain)
        
        # Add expanded domains for the primary domain
        expanded_domains = self.get_expanded_domains(primary_domain)
        for domain in expanded_domains:
            if domain not in domain_queue and len(domain_queue) < max_domains:
                domain_queue.append(domain)
        
        return domain_queue
    
    def assess_document_relevance(self, question, document_content, threshold=0.7):
        """
        Assess the relevance of a document to the original question.
        
        Args:
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
        
        response = self.llm_client.generate(prompt)
        
        try:
            relevance_score = float(response.strip())
            is_relevant = relevance_score >= threshold
            return is_relevant, relevance_score
        except ValueError:
            # If the LLM doesn't return a valid number, assume not relevant
            return False, 0.0
    
    def search_domains_sequentially(self, question, domain_queue, max_docs_per_domain=5, relevance_threshold=0.7):
        """
        Search domains sequentially until relevant documents are found.
        
        Args:
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
            documents = self.search_client.search_domain(domain, question, max_results=max_docs_per_domain)
            
            # If no documents found, continue to next domain
            if not documents:
                continue
            
            # Retrieve full content for each document
            for doc in documents:
                doc['content'] = self.search_client.get_document_content(domain, doc['id'])
            
            # Assess document relevance
            for doc in documents:
                is_relevant, relevance_score = self.assess_document_relevance(question, doc['content'], threshold=relevance_threshold)
                
                if is_relevant:
                    doc['relevance_score'] = relevance_score
                    doc['domain'] = domain
                    relevant_documents.append(doc)
            
            # If relevant documents found, stop searching
            if relevant_documents:
                break
        
        return relevant_documents, searched_domains
    
    def is_generic_software_question(self, question):
        """
        Determine if a question is a generic software development question.
        
        Args:
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
        
        response = self.llm_client.generate(prompt).strip().upper()
        return response == "YES"
    
    def generate_answer_from_documents(self, question, relevant_documents):
        """
        Generate an answer based on the question and relevant documents.
        
        Args:
            question (str): The original user question
            relevant_documents (list): List of relevant document objects
            
        Returns:
            str: Generated answer
        """
        # Prepare document context
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
        
        return self.llm_client.generate(prompt, max_tokens=1500)
    
    def generate_generic_answer(self, question):
        """
        Generate an answer based on generic software development knowledge.
        
        Args:
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
        
        return self.llm_client.generate(prompt, max_tokens=1500)
    
    def generate_clarification_request(self, question, searched_domains):
        """
        Generate a response requesting clarification when no relevant documents are found.
        
        Args:
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
        
        return self.llm_client.generate(prompt)
    
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
            primary_domain, confidence = self.classify_question(question)
            print(f"Primary domain: {primary_domain} (confidence: {confidence:.2f})")
            
            # Step 2: Build domain queue for searching
            domain_queue = self.build_domain_queue(question, primary_domain, confidence)
            print(f"Domain queue: {domain_queue}")
            
            # Step 3: Search for relevant documents
            relevant_documents, searched_domains = self.search_domains_sequentially(question, domain_queue)
            print(f"Searched domains: {searched_domains}")
            print(f"Found {len(relevant_documents)} relevant documents")
            
            # Step 4: Generate answer
            if relevant_documents:
                answer = self.generate_answer_from_documents(question, relevant_documents)
                source_info = []
                for doc in relevant_documents:
                    source_info.append({
                        "title": doc.get("title", "Untitled"),
                        "domain": doc.get("domain", "Unknown"),
                        "id": doc.get("id", ""),
                        "relevance_score": doc.get("relevance_score", 0.0)
                    })
                
                return {
                    "answer": answer,
                    "sources": source_info,
                    "primary_domain": primary_domain,
                    "confidence": confidence,
                    "searched_domains": searched_domains,
                    "status": "answered_with_documents"
                }
            
            # Step 5: Check if it's a generic question
            is_generic = self.is_generic_software_question(question)
            print(f"Is generic question: {is_generic}")
            
            if is_generic:
                answer = self.generate_generic_answer(question)
                
                return {
                    "answer": answer,
                    "sources": [],
                    "primary_domain": primary_domain,
                    "confidence": confidence,
                    "searched_domains": searched_domains,
                    "status": "answered_with_general_knowledge"
                }
            
            # Step 6: Generate clarification request
            clarification = self.generate_clarification_request(question, searched_domains)
            
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
            print(error_message)
            return {
                "answer": "I encountered an error while processing your question. Please try again.",
                "error": error_message,
                "status": "error"
            }

def main():
    parser = argparse.ArgumentParser(description='Domain QA System')
    parser.add_argument('--api_key', type=str, help='OpenAI API key')
    parser.add_argument('--search_url', type=str, default='https://api.example.com', help='Search API base URL')
    parser.add_argument('--question', type=str, help='Question to process')
    
    args = parser.parse_args()
    
    # Use environment variable if API key not provided
    api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: OpenAI API key is required. Provide it with --api_key or set OPENAI_API_KEY environment variable.")
        return
    
    # Initialize clients
    llm_client = OpenAIClient(api_key=api_key)
    search_client = DomainSearchClient(base_url=args.search_url)
    
    # Initialize QA system
    qa_system = DomainQASystem(llm_client=llm_client, search_client=search_client)
    
    # Process question if provided
    if args.question:
        result = qa_system.process_question(args.question)
        print("\nAnswer:")
        print(result["answer"])
        print("\nStatus:", result["status"])
    else:
        # Interactive mode
        print("Domain QA System (type 'exit' to quit)")
        while True:
            question = input("\nEnter your question: ")
            
            if question.lower() in ['exit', 'quit']:
                break
            
            result = qa_system.process_question(question)
            print("\nAnswer:")
            print(result["answer"])
            print("\nStatus:", result["status"])

if __name__ == "__main__":
    main()
```

### 2. Mock Search API for Testing

```python
# mock_search_api.py
from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Mock document database
documents = {
    "github": [
        {
            "id": "github-001",
            "title": "Creating Pull Requests in Github",
            "snippet": "Learn how to create and manage pull requests in Github...",
            "content": """
            # Creating Pull Requests in Github
            
            Pull requests let you tell others about changes you've pushed to a branch in a repository on GitHub. 
            Once a pull request is opened, you can discuss and review the potential changes with collaborators 
            and add follow-up commits before your changes are merged into the base branch.
            
            ## Creating a Pull Request
            
            1. Navigate to the repository you want to contribute to
            2. Click on the "Pull requests" tab
            3. Click the green "New pull request" button
            4. Select the branch you made your changes in as the "compare" branch
            5. Select the branch you want your changes to be merged into as the "base" branch
            6. Give your pull request a title and description
            7. Click "Create pull request"
            
            ## Best Practices
            
            - Keep pull requests small and focused on a single issue
            - Write clear descriptions of what the changes do
            - Reference related issues using the # symbol
            - Request reviews from appropriate team members
            """
        },
        {
            "id": "github-002",
            "title": "Github Actions Workflow Guide",
            "snippet": "Comprehensive guide to setting up CI/CD with Github Actions...",
            "content": """
            # Github Actions Workflow Guide
            
            GitHub Actions help you automate tasks within your software development life cycle. 
            GitHub Actions are event-driven, meaning that you can run a series of commands after a specified event has occurred.
            
            ## Setting Up a Basic Workflow
            
            1. Create a `.github/workflows` directory in your repository
            2. Add a YAML file (e.g., `main.yml`) to define your workflow
            3. Define the events that trigger the workflow
            4. Specify the jobs and steps to run
            
            Example workflow:
            
            ```yaml
            name: CI
            
            on:
              push:
                branches: [ main ]
              pull_request:
                branches: [ main ]
            
            jobs:
              build:
                runs-on: ubuntu-latest
                
                steps:
                - uses: actions/checkout@v2
                - name: Set up Python
                  uses: actions/setup-python@v2
                  with:
                    python-version: 3.8
                - name: Install dependencies
                  run: |
                    python -m pip install --upgrade pip
                    pip install flake8 pytest
                    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
                - name: Lint with flake8
                  run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                - name: Test with pytest
                  run: pytest
            ```
            
            ## Advanced Features
            
            - Use matrix builds to test across multiple versions
            - Cache dependencies to speed up workflows
            - Deploy to production environments
            - Create custom actions for reusable components
            """
        }
    ],
    "jenkins": [
        {
            "id": "jenkins-001",
            "title": "Jenkins Pipeline Configuration",
            "snippet": "Guide to setting up Jenkins pipelines for CI/CD...",
            "content": """
            # Jenkins Pipeline Configuration
            
            Jenkins Pipeline is a suite of plugins that supports implementing and integrating continuous delivery pipelines into Jenkins.
            
            ## Creating a Jenkinsfile
            
            A Jenkinsfile is a text file that contains the definition of a Jenkins Pipeline and is checked into source control.
            
            ```groovy
            pipeline {
                agent any
                
                stages {
                    stage('Build') {
                        steps {
                            echo 'Building..'
                            sh 'mvn clean package'
                        }
                    }
                    stage('Test') {
                        steps {
                            echo 'Testing..'
                            sh 'mvn test'
                        }
                    }
                    stage('Deploy') {
                        steps {
                            echo 'Deploying....'
                            sh 'mvn deploy'
                        }
                    }
                }
                
                post {
                    always {
                        junit '**/target/surefire-reports/TEST-*.xml'
                        archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
                    }
                    success {
                        echo 'Pipeline completed successfully!'
                    }
                    failure {
                        echo 'Pipeline failed!'
                    }
                }
            }
            ```
            
            ## Pipeline Syntax
            
            - `pipeline`: The pipeline block defines a Pipeline
            - `agent`: Where the Pipeline will execute
            - `stages`: Contains all the stages of the Pipeline
            - `stage`: A block defining a stage of the Pipeline
            - `steps`: The steps to be executed in a stage
            - `post`: Actions to be performed after the Pipeline execution
            
            ## Best Practices
            
            - Keep the Jenkinsfile in the root of your repository
            - Use declarative pipeline syntax for better readability
            - Parameterize your pipeline for flexibility
            - Use shared libraries for common functionality
            """
        }
    ],
    "aws": [
        {
            "id": "aws-001",
            "title": "AWS S3 Bucket Configuration",
            "snippet": "Guide to configuring S3 buckets with proper security...",
            "content": """
            # AWS S3 Bucket Configuration
            
            Amazon S3 (Simple Storage Service) is an object storage service that offers industry-leading scalability, data availability, security, and performance.
            
            ## Creating a Secure S3 Bucket
            
            1. Sign in to the AWS Management Console
            2. Navigate to the S3 service
            3. Click "Create bucket"
            4. Enter a unique bucket name
            5. Select the AWS Region
            6. Configure bucket settings:
               - Block all public access (recommended)
               - Enable bucket versioning
               - Enable server-side encryption
            7. Click "Create bucket"
            
            ## Security Best Practices
            
            - Use IAM policies to control access
            - Enable S3 access logging
            - Use presigned URLs for temporary access
            - Implement lifecycle policies for cost optimization
            - Use bucket policies to enforce encryption
            
            ## Example Bucket Policy
            
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowSSLRequestsOnly",
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            "arn:aws:s3:::your-bucket-name",
                            "arn:aws:s3:::your-bucket-name/*"
                        ],
                        "Condition": {
                            "Bool": {
                                "aws:SecureTransport": "false"
                            }
                        }
                    }
                ]
            }
            ```
            """
        }
    ]
}

@app.route('/search/<domain>')
def search(domain):
    query = request.args.get('query', '')
    max_results = int(request.args.get('max_results', 5))
    
    if domain.lower() not in documents:
        return jsonify({"error": f"Domain '{domain}' not found", "documents": []})
    
    # In a real implementation, this would perform actual search
    # Here we just return all documents for the domain
    domain_docs = documents.get(domain.lower(), [])
    
    # Limit to max_results
    result_docs = domain_docs[:max_results]
    
    # Remove content field from results (will be fetched separately)
    for doc in result_docs:
        doc_copy = doc.copy()
        if 'content' in doc_copy:
            del doc_copy['content']
        
    return jsonify({"documents": result_docs})

@app.route('/document/<domain>/<doc_id>')
def get_document(domain, doc_id):
    if domain.lower() not in documents:
        return jsonify({"error": f"Domain '{domain}' not found", "content": ""})
    
    # Find the document with the matching ID
    for doc in documents.get(domain.lower(), []):
        if doc['id'] == doc_id:
            return jsonify({"content": doc.get('content', '')})
    
    return jsonify({"error": f"Document '{doc_id}' not found", "content": ""})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Example Prompts

### 1. Domain Classification Prompt

```
Given the following domains related to software development:
- Github: Version control, repositories, pull requests, issues, actions
- Jenkins: CI/CD pipelines, builds, automation
- Artifactory: Binary repository management, artifact storage
- SonarScan: Code quality, static analysis, security scanning
- API: API development, documentation, testing, management
- Terraform: Infrastructure as code, provisioning
- EKS: Amazon Elastic Kubernetes Service, container orchestration
- AWS: Amazon Web Services, cloud infrastructure
- Azure: Microsoft's cloud platform
- Cloud Security: Security practices for cloud environments
- Secret Management: Managing credentials, keys, certificates
- ALMx: Application Lifecycle Management

Classify the following question into the most relevant domain:
How do I create a pull request in Github for my feature branch?

Return the domain name followed by a confidence score between 0 and 1, separated by a colon.
Example: "Github:0.92"
```

Expected response:
```
Github:0.95
```

### 2. Multi-Label Classification Prompt

```
Given the following domains related to software development:
- Github: Version control, repositories, pull requests, issues, actions
- Jenkins: CI/CD pipelines, builds, automation
- Artifactory: Binary repository management, artifact storage
- SonarScan: Code quality, static analysis, security scanning
- API: API development, documentation, testing, management
- Terraform: Infrastructure as code, provisioning
- EKS: Amazon Elastic Kubernetes Service, container orchestration
- AWS: Amazon Web Services, cloud infrastructure
- Azure: Microsoft's cloud platform
- Cloud Security: Security practices for cloud environments
- Secret Management: Managing credentials, keys, certificates
- ALMx: Application Lifecycle Management

Classify the following question into the most relevant domains (up to 3):
How do I set up a Jenkins pipeline that deploys to AWS using Terraform?

Return the domain names in order of relevance, separated by commas, without any explanation.
```

Expected response:
```
Jenkins, AWS, Terraform
```

### 3. Document Relevance Assessment Prompt

```
On a scale of 0 to 1, rate how relevant the following document is to answering this question:

Question: How do I create a pull request in Github?

Document:
# Creating Pull Requests in Github

Pull requests let you tell others about changes you've pushed to a branch in a repository on GitHub. 
Once a pull request is opened, you can discuss and review the potential changes with collaborators 
and add follow-up commits before your changes are merged into the base branch.

## Creating a Pull Request

1. Navigate to the repository you want to contribute to
2. Click on the "Pull requests" tab
3. Click the green "New pull request" button
4. Select the branch you made your changes in as the "compare" branch
5. Select the branch you want your changes to be merged into as the "base" branch
6. Give your pull request a title and description
7. Click "Create pull request"

## Best Practices

- Keep pull requests small and focused on a single issue
- Write clear descriptions of what the changes do
- Reference related issues using the # symbol
- Request reviews from appropriate team members

Return only a number between 0 and 1, where 0 means completely irrelevant and 1 means perfectly relevant.
```

Expected response:
```
0.98
```

### 4. Answer Generation Prompt

```
You are an AI assistant that helps answer software development questions based on internal documentation.

User Question: How do I create a pull request in Github?

Based on the following internal documentation, provide a precise and accurate answer to the user's question.
Include citations to the source documents using the format [n] where n is the document number.
If the documentation doesn't contain enough information to answer the question completely, clearly state what information is missing.

Internal Documentation:
[1] Document Title: Creating Pull Requests in Github
Domain: Github
Content:
# Creating Pull Requests in Github

Pull requests let you tell others about changes you've pushed to a branch in a repository on GitHub. 
Once a pull request is opened, you can discuss and review the potential changes with collaborators 
and add follow-up commits before your changes are merged into the base branch.

## Creating a Pull Request

1. Navigate to the repository you want to contribute to
2. Click on the "Pull requests" tab
3. Click the green "New pull request" button
4. Select the branch you made your changes in as the "compare" branch
5. Select the branch you want your changes to be merged into as the "base" branch
6. Give your pull request a title and description
7. Click "Create pull request"

## Best Practices

- Keep pull requests small and focused on a single issue
- Write clear descriptions of what the changes do
- Reference related issues using the # symbol
- Request reviews from appropriate team members

Answer (with citations):
```

Expected response:
```
To create a pull request in Github, follow these steps:

1. Navigate to the repository you want to contribute to
2. Click on the "Pull requests" tab
3. Click the green "New pull request" button
4. Select the branch you made your changes in as the "compare" branch
5. Select the branch you want your changes to be merged into as the "base" branch
6. Give your pull request a title and description
7. Click "Create pull request" [1]

When creating pull requests, it's recommended to follow these best practices:
- Keep pull requests small and focused on a single issue
- Write clear descriptions of what the changes do
- Reference related issues using the # symbol
- Request reviews from appropriate team members [1]

Pull requests are an important part of the collaboration workflow in Github, allowing you to discuss and review potential changes with collaborators before merging them into the base branch. [1]
```

### 5. Generic Question Detection Prompt

```
Determine if the following question is a generic software development question that can be answered with general knowledge, 
without requiring specific internal documentation or proprietary information.

Question: What is the difference between Git and Github?

Return only "YES" if it's a generic software development question or "NO" if it requires specific internal documentation.
```

Expected response:
```
YES
```

## Complete Workflow Examples

### Example 1: Domain-Specific Question with Relevant Documents

**User Question:** "How do I create a pull request in Github?"

**Step 1: Domain Classification**
- Primary domain: Github (confidence: 0.95)
- Domain queue: [Github, API]

**Step 2: Document Retrieval**
- Search Github domain
- Find document "Creating Pull Requests in Github" (relevance: 0.98)
- Document is relevant, stop searching

**Step 3: Answer Generation**
- Generate answer based on the relevant document
- Include citations to the source document

**Final Answer:**
```
To create a pull request in Github, follow these steps:

1. Navigate to the repository you want to contribute to
2. Click on the "Pull requests" tab
3. Click the green "New pull request" button
4. Select the branch you made your changes in as the "compare" branch
5. Select the branch you want your changes to be merged into as the "base" branch
6. Give your pull request a title and description
7. Click "Create pull request" [1]

When creating pull requests, it's recommended to follow these best practices:
- Keep pull requests small and focused on a single issue
- Write clear descriptions of what the changes do
- Reference related issues using the # symbol
- Request reviews from appropriate team members [1]

Pull requests are an important part of the collaboration workflow in Github, allowing you to discuss and review potential changes with collaborators before merging them into the base branch. [1]
```

### Example 2: Multi-Domain Question with Relevant Documents

**User Question:** "How do I set up a Jenkins pipeline that deploys to AWS?"

**Step 1: Domain Classification**
- Primary domain: Jenkins (confidence: 0.85)
- Domain queue: [Jenkins, AWS, Cloud Security]

**Step 2: Document Retrieval**
- Search Jenkins domain
- Find document "Jenkins Pipeline Configuration" (relevance: 0.90)
- Document is relevant, but may need additional information
- Search AWS domain
- Find document "AWS S3 Bucket Configuration" (relevance: 0.60)
- Document is somewhat relevant but not directly related to the question

**Step 3: Answer Generation**
- Generate answer based on the relevant documents
- Include citations to the source documents
- Note that additional information might be needed

**Final Answer:**
```
To set up a Jenkins pipeline that deploys to AWS, you'll need to create a Jenkinsfile that defines your pipeline stages, including a deployment stage for AWS.

Here's how to create a basic Jenkins pipeline:

1. Create a Jenkinsfile in the root of your repository
2. Define your pipeline using the declarative syntax
3. Set up stages for building, testing, and deploying your application [1]

A basic pipeline structure would look like this:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                echo 'Building..'
                sh 'mvn clean package'
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                sh 'mvn test'
            }
        }
        stage('Deploy to AWS') {
            steps {
                echo 'Deploying to AWS....'
                // AWS deployment commands would go here
            }
        }
    }
    
    post {
        always {
            junit '**/target/surefire-reports/TEST-*.xml'
            archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
        }
    }
}
```

For the AWS deployment stage, you would typically use AWS CLI commands or a plugin like AWS Steps Plugin to interact with AWS services. [1]

While the documentation provides information about Jenkins pipelines [1] and some AWS configuration details [2], it doesn't contain specific instructions for integrating Jenkins with AWS deployment. You would likely need to:

1. Install the AWS CLI on your Jenkins server
2. Configure AWS credentials in Jenkins (using credentials binding plugin)
3. Use those credentials in your pipeline to authenticate with AWS
4. Add specific AWS deployment commands to your pipeline script

For best practices, keep your Jenkinsfile in the root of your repository and use declarative pipeline syntax for better readability. [1]
```

### Example 3: Generic Question with No Relevant Documents

**User Question:** "What is the difference between Git and Github?"

**Step 1: Domain Classification**
- Primary domain: Github (confidence: 0.80)
- Domain queue: [Github, API]

**Step 2: Document Retrieval**
- Search Github domain
- No directly relevant documents found
- Search API domain
- No directly relevant documents found

**Step 3: Generic Question Detection**
- Determine if it's a generic software development question
- Result: YES (it's a generic question)

**Step 4: Generic Answer Generation**
- Generate answer based on general knowledge

**Final Answer:**
```
Git and Github are related but distinct tools in the software development ecosystem:

Git:
- Git is a distributed version control system
- It was created by Linus Torvalds in 2005
- Git is installed locally on your computer
- Git allows you to track changes to files, create branches, and merge code
- Git is open-source software
- Git can be used without any online service or internet connection

Github:
- Github is a web-based hosting service for Git repositories
- It was founded in 2008 and later acquired by Microsoft in 2018
- Github provides a centralized location to store Git repositories
- Github adds collaboration features on top of Git, such as:
  - Pull requests
  - Issues and project tracking
  - Code review tools
  - Actions for CI/CD
  - Wiki pages
  - Access control and team management
- Github requires an internet connection to use

In simple terms, Git is the version control tool itself, while Github is a service that hosts Git repositories and adds collaboration features. Other alternatives to Github include GitLab, Bitbucket, and Azure DevOps, all of which provide hosting for Git repositories with their own sets of additional features.
```

### Example 4: Specific Question with No Relevant Documents

**User Question:** "How do I configure the secret rotation policy in our company's Secret Management system?"

**Step 1: Domain Classification**
- Primary domain: Secret Management (confidence: 0.88)
- Domain queue: [Secret Management, Cloud Security, AWS]

**Step 2: Document Retrieval**
- Search Secret Management domain
- No relevant documents found
- Search Cloud Security domain
- No relevant documents found
- Search AWS domain
- No relevant documents found

**Step 3: Generic Question Detection**
- Determine if it's a generic software development question
- Result: NO (it requires specific internal documentation)

**Step 4: Clarification Request Generation**
- Generate a clarification request

**Final Answer:**
```
I couldn't find specific information about configuring the secret rotation policy in your company's Secret Management system. This appears to be a question that requires company-specific documentation that isn't available in the knowledge base I searched (Secret Management, Cloud Security, AWS).

To help you better, I would need additional information:

1. Which specific Secret Management system is your company using? (e.g., HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, CyberArk)
2. Are you looking to configure automatic rotation or manual rotation policies?
3. Are there specific types of secrets you're trying to rotate (e.g., database credentials, API keys, certificates)?

Alternatively, you might want to:
- Check your company's internal documentation portal for Secret Management guides
- Consult with your Security or DevOps team who might have established procedures
- Look for configuration files or existing rotation policies in your infrastructure code repositories

If you can provide more details about your specific environment and requirements, I can try to provide more targeted assistance.
```
