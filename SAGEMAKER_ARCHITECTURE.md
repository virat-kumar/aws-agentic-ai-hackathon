# AWS SageMaker Integration for LangChain Module

## Architecture Overview

This document outlines how to move the LangChain functionality to AWS SageMaker for scalable, production-ready deployment.

### Current Architecture
```
Streamlit App (app.py)
    ↓
LangChain Module (langchain_module.py)
    ↓
AWS Bedrock (LLM) + DuckDuckGo (Web Search)
```

### New SageMaker Architecture
```
Streamlit App (app.py)
    ↓
SageMaker Endpoint (sagemaker_module.py)
    ↓
SageMaker Model Endpoint
    ├── LangChain Processing
    ├── AWS Bedrock (LLM)
    └── DuckDuckGo (Web Search)
```

## Components

### 1. SageMaker Inference Script (`inference.py`)
- Containerizes the LangChain logic
- Runs in a SageMaker endpoint
- Handles search + LLM synthesis

### 2. SageMaker Endpoint Client (`sagemaker_module.py`)
- Replaces direct LangChain module
- Calls SageMaker endpoint
- Manages request/response handling

### 3. Deployment Script (`deploy_sagemaker.py`)
- Creates SageMaker model
- Deploys to endpoint
- Manages scaling

## Benefits

✅ **Scalability**: Auto-scales based on load
✅ **Cost Optimization**: Pay only for usage
✅ **Reliability**: Built-in redundancy
✅ **Security**: IAM-based access control
✅ **Monitoring**: CloudWatch metrics
✅ **Decoupling**: App and ML logic separated

## Deployment Steps

### Step 1: Create Inference Script
Create `deployment/inference.py` with the LangChain logic

### Step 2: Build Docker Container
```bash
docker build -t langchain-sagemaker .
```

### Step 3: Push to ECR
```bash
aws ecr create-repository --repository-name langchain-sagemaker
docker tag langchain-sagemaker:latest <account>.dkr.ecr.<region>.amazonaws.com/langchain-sagemaker:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/langchain-sagemaker:latest
```

### Step 4: Deploy to SageMaker
Use `deploy_sagemaker.py` to create and deploy the endpoint

### Step 5: Update App
Update `app.py` to use SageMaker client instead of local LangChain

## Cost Estimation

- **SageMaker Instance**: ~$0.10-0.50/hour (depending on instance type)
- **Usage**: Only charged when endpoint is running
- **Storage**: Container image stored in ECR (~$0.10/GB-month)

## Security Considerations

1. IAM Roles for SageMaker execution
2. VPC configuration for private endpoints
3. Encryption at rest and in transit
4. CloudWatch logging

## Next Steps

See `deployment/` folder for implementation files.
