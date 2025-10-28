# SageMaker Deployment Guide

## Overview

This guide walks you through deploying the LangChain module to AWS SageMaker for production use.

## Prerequisites

1. **AWS CLI configured** with appropriate credentials
2. **Docker** installed locally
3. **SageMaker permissions** in your AWS account
4. **ECR repository** for storing container images

## Step-by-Step Deployment

### Step 1: Create ECR Repository

```bash
aws ecr create-repository --repository-name langchain-sagemaker --region us-east-1
```

Note the repository URI (e.g., `123456789.dkr.ecr.us-east-1.amazonaws.com/langchain-sagemaker`)

### Step 2: Build Docker Image

```bash
cd deployment
docker build -t langchain-sagemaker .
```

### Step 3: Tag and Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag image
docker tag langchain-sagemaker:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/langchain-sagemaker:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/langchain-sagemaker:latest
```

### Step 4: Deploy to SageMaker

```bash
cd ..
python deployment/deploy_sagemaker.py <ECR_IMAGE_URI>
```

Or manually using AWS CLI:

```bash
aws sagemaker create-model \
  --model-name langchain-model \
  --execution-role-arn arn:aws:iam::<account-id>:role/SageMakerExecutionRole \
  --primary-container Image=<ECR_IMAGE_URI>

aws sagemaker create-endpoint-config \
  --endpoint-config-name langchain-endpoint-config \
  --production-variants VariantName=AllTraffic,ModelName=langchain-model,InitialInstanceCount=1,InstanceType=ml.t3.medium

aws sagemaker create-endpoint \
  --endpoint-name langchain-endpoint \
  --endpoint-config-name langchain-endpoint-config
```

### Step 5: Update Environment Variables

In your `.env` file:

```bash
SAGEMAKER_ENDPOINT_NAME=langchain-endpoint
SAGEMAKER_INSTANCE_TYPE=ml.t3.medium
AWS_REGION=us-east-1
```

### Step 6: Update app.py

Change the import in `app.py`:

```python
# OLD
from langchain_module import get_web_search_agent

# NEW
from sagemaker_module import get_sagemaker_agent

# And update the function call
agent = get_sagemaker_agent()
```

### Step 7: Restart Service

```bash
sudo systemctl restart dallas-student-navigator.service
```

## Configuration Options

### Instance Types

| Instance Type | vCPU | RAM | Best For |
|---------------|------|-----|----------|
| ml.t3.medium  | 2    | 4GB | Development/Testing |
| ml.t3.large   | 2    | 8GB | Production (light) |
| ml.m5.large   | 2    | 8GB | Production (balanced) |
| ml.c5.large   | 2    | 4GB | Production (CPU-bound) |

### Auto-Scaling

To enable auto-scaling:

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace sagemaker \
  --resource-id endpoint/langchain-endpoint/variant/AllTraffic \
  --scalable-dimension sagemaker:variant:DesiredInstanceCount \
  --min-capacity 1 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --service-namespace sagemaker \
  --resource-id endpoint/langchain-endpoint/variant/AllTraffic \
  --scalable-dimension sagemaker:variant:DesiredInstanceCount \
  --policy-name langchain-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration TargetValue=70.0,PredefinedMetricSpecification={PredefinedMetricType=SageMakerVariantInvocationsPerInstance}
```

## Monitoring

### CloudWatch Metrics

Monitor:
- `Invocations`: Number of requests
- `ModelLatency`: Response time
- `ErrorRate`: Error percentage
- `CPUUtilization`: CPU usage

### CloudWatch Dashboard

```bash
aws cloudwatch put-dashboard \
  --dashboard-name SageMakerLangChain \
  --dashboard-body file://monitoring/dashboard.json
```

## Troubleshooting

### Endpoint Creation Failed

Check logs:
```bash
aws logs tail /aws/sagemaker/Endpoints/langchain-endpoint --follow
```

### High Latency

- Use larger instance types (ml.m5.xlarge)
- Enable async invocation
- Implement caching

### Cost Optimization

- Stop endpoint when not in use:
  ```bash
  aws sagemaker stop-endpoint --endpoint-name langchain-endpoint
  ```

- Use serverless inference for sporadic usage
- Implement request batching

## Cost Estimates

**ml.t3.medium** (Development):
- $0.052/hour ≈ $37/month (if running 24/7)
- Pay-per-use with auto-scaling

**ml.t3.large** (Production):
- $0.104/hour ≈ $75/month

## Next Steps

1. Test endpoint with sample queries
2. Monitor CloudWatch metrics
3. Set up alerts for errors
4. Configure auto-scaling
5. Implement caching layer
