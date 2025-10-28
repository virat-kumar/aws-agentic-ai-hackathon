# Create IAM Role Manually (Required)

## Problem
Your AWS user doesn't have permission to create IAM roles automatically.

## Solution: Create the role manually in AWS Console

### Step 1: Go to IAM Console
https://console.aws.amazon.com/iam/

### Step 2: Create Role
1. Click "Roles" → "Create role"
2. Select "SageMaker" as trusted entity
3. Click "Next"

### Step 3: Attach Policies
Search and attach these policies:
- `AmazonSageMakerFullAccess`
- `AmazonS3FullAccess`

### Step 4: Create Custom Policy for Bedrock
1. Click "Add permissions" → "Create inline policy"
2. Click "JSON" tab
3. Paste this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        }
    ]
}
```

4. Name: `BedrockAccess`
5. Click "Create policy"

### Step 5: Name the Role
- Name: `SageMakerExecutionRole`
- Description: "Role for SageMaker LangChain endpoint"
- Click "Create role"

## Step 6: Retry Deployment

Once the role exists, run:

```bash
python deployment/deploy_sagemaker.py 642384808711.dkr.ecr.us-west-2.amazonaws.com/langchain-sagemaker:latest
```

## Alternative: Use Existing Role

If you already have a SageMaker role, update the script:

Set in `.env`:
```bash
SAGEMAKER_ROLE_NAME=your-existing-role-name
```
