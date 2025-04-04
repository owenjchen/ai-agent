# LLM Classification System Design

## Prompt Engineering Techniques

### 1. Zero-Shot Classification Prompt

The most straightforward approach is to use a zero-shot classification prompt that instructs the LLM to classify the question into one of the predefined domains:

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
[USER QUESTION]

Return only the domain name without any explanation.
```

### 2. Few-Shot Classification Prompt

For better accuracy, provide examples of questions and their classifications:

```
Given the following domains related to software development:
[DOMAIN LIST WITH DESCRIPTIONS]

Here are some examples of questions and their classifications:
- "How do I create a pull request in Github?" -> Github
- "What's the best way to set up a Jenkins pipeline?" -> Jenkins
- "How can I upload artifacts to Artifactory?" -> Artifactory
- "How do I configure SonarScan for my Java project?" -> SonarScan

Classify the following question into the most relevant domain:
[USER QUESTION]

Return only the domain name without any explanation.
```

### 3. Multi-Label Classification Prompt

For questions that span multiple domains:

```
Given the following domains related to software development:
[DOMAIN LIST WITH DESCRIPTIONS]

Classify the following question into the most relevant domains (up to 3):
[USER QUESTION]

Return the domain names in order of relevance, separated by commas, without any explanation.
```

### 4. Confidence-Based Classification Prompt

To get confidence scores for better fallback mechanisms:

```
Given the following domains related to software development:
[DOMAIN LIST WITH DESCRIPTIONS]

Classify the following question into the most relevant domain:
[USER QUESTION]

Return the domain name followed by a confidence score between 0 and 1, separated by a colon.
Example: "Github:0.92"
```

## Classification Algorithm

1. **Input Processing**:
   - Clean and normalize the user question
   - Extract key terms and concepts

2. **Primary Classification**:
   - Send the question to the LLM with the confidence-based classification prompt
   - Parse the response to get the primary domain and confidence score

3. **Confidence Threshold Check**:
   - If confidence score > 0.7, proceed with the primary domain
   - If confidence score <= 0.7, perform multi-label classification

4. **Multi-Label Classification** (if needed):
   - Send the question to the LLM with the multi-label classification prompt
   - Parse the response to get multiple potential domains

5. **Domain Prioritization**:
   - Create a queue of domains to search, starting with the highest confidence domain
   - If multi-label classification was used, add all identified domains to the queue

## Handling Ambiguous Classifications

1. **Iterative Search Strategy**:
   - Start with the highest confidence domain
   - If no relevant documents are found, move to the next domain in the queue

2. **Domain Expansion**:
   - For questions that might be too specific, expand to parent domains
   - Example: If "EKS" yields no results, try "AWS"

3. **Keyword Extraction Fallback**:
   - If LLM classification yields low confidence across all domains, extract keywords from the question
   - Map keywords to domains using a predefined dictionary
   - Search based on keyword-domain mappings

4. **Generic Knowledge Fallback**:
   - If no relevant documents are found across all domains, check if the question is a generic software development question
   - If yes, generate an answer based on the LLM's pretrained knowledge

5. **Clarification Request**:
   - As a last resort, generate a response that asks for clarification
   - Suggest potential domains the question might relate to
