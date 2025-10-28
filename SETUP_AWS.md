# AWS Bedrock Setup Guide

This guide explains how to configure AWS Bedrock for the Dallas Student Navigator application.

## Prerequisites

1. AWS Account with Bedrock access enabled
2. IAM user with appropriate permissions
3. Bedrock model access (for Claude models)

## Where to Put AWS Secrets

### 1. Create/Edit `.env` file

Create a `.env` file in the project root directory (same location as `env.example`):

```bash
cd /home/ubuntu/aws-agentic-ai-hackathon
cp env.example .env
```

### 2. Edit `.env` file

Open the `.env` file and add your AWS credentials:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_actual_access_key_here
AWS_SECRET_ACCESS_KEY=your_actual_secret_key_here

# AWS Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=4096

# Application Settings
APP_TITLE=Dallas Student Navigator
APP_THEME=light
```

### 3. How to Get AWS Credentials

#### Option A: Using AWS Console

1. Log in to AWS Console: https://console.aws.amazon.com/
2. Go to **IAM** service
3. Click **Users** → Your username
4. Click **Security credentials** tab
5. Click **Create access key**
6. Copy the **Access Key ID** and **Secret Access Key**

#### Option B: Using AWS CLI

If you have AWS CLI configured locally:

```bash
# View current credentials
cat ~/.aws/credentials

# Or set up AWS CLI
aws configure
```

## Required IAM Permissions

Your IAM user needs the following permissions to use Bedrock:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels",
                "bedrock:GetFoundationModel"
            ],
            "Resource": "*"
        }
    ]
}
```

## Enabling Bedrock Models

1. Go to **AWS Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. Click on **Model access** (left sidebar)
3. Click **Request access** for the models you want to use:
   - **Claude 3 Sonnet** (recommended)
   - **Claude 3 Haiku** (fast & cheap)
   - **Claude 3.5 Sonnet** (latest)

## Available Bedrock Models

Update `BEDROCK_MODEL_ID` in `.env` file to use different models:

## Latest & Best (2025)

- **Claude 4 Sonnet**: `anthropic.claude-sonnet-4-20250514-v1:0` (Latest)
- **Claude 3.7 Sonnet**: `anthropic.claude-3-7-sonnet-20250219-v1:0`
- **Claude 3.5 Sonnet**: `anthropic.claude-3-5-sonnet-20241022-v2:0` ⭐ **Recommended**
- **Claude 4 Opus**: `anthropic.claude-opus-4-20250514-v1:0` (Most Powerful)

## Cost-Effective Options

- **Claude 3.5 Haiku**: `anthropic.claude-3-5-haiku-20241022-v1:0` (Fast & Cheap)
- **Claude 3 Haiku**: `anthropic.claude-3-haiku-20240307-v1:0` (Very Fast & Cheap)

## ⚠️ DO NOT USE (End of Life)

- ~~`anthropic.claude-3-sonnet-20240229-v1:0`~~ (END OF LIFE)
- ~~`anthropic.claude-v2`~~ (END OF LIFE)

## Security Best Practices

### 1. Never commit `.env` file

The `.env` file is already in `.gitignore` to prevent accidental commits.

### 2. Use IAM roles on EC2

If running on AWS EC2, use IAM roles instead of access keys:

```python
# The code will automatically use IAM role if no credentials are provided
# Remove AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from .env
```

### 3. Rotate credentials regularly

Update your credentials every 90 days for security.

### 4. Use least privilege principle

Only grant the minimum permissions needed for Bedrock.

## Testing the Setup

After configuring credentials, restart the service:

```bash
sudo systemctl restart dallas-student-navigator.service
sudo systemctl status dallas-student-navigator.service
```

Check the logs for successful initialization:

```bash
sudo journalctl -u dallas-student-navigator.service -f
```

You should see: `Successfully initialized AWS Bedrock with model: anthropic.claude-3-sonnet-20240229-v1:0`

## Troubleshooting

### Error: "AWS Bedrock credentials not found"
- Ensure `.env` file exists in the project root
- Check that `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
- Verify credentials are correct (no extra spaces or quotes)

### Error: "Access Denied"
- Check IAM permissions for the user
- Verify Bedrock model access is enabled in AWS Console
- Ensure region is correct (us-east-1, us-west-2, etc.)

### Error: "Model not available"
- Enable model access in AWS Bedrock Console
- Use an alternative model ID from the list above
- Check if the model is available in your AWS region

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [LangChain AWS Integration](https://python.langchain.com/docs/integrations/platforms/aws)
- [Claude Models on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
