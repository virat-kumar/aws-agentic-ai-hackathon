"""
Deploy LangChain module to AWS SageMaker
"""
import boto3
import json
import sagemaker
import os
import sys
from dotenv import load_dotenv
from sagemaker.model import Model
from sagemaker.predictor import Predictor

load_dotenv()

# Configuration - will be updated if region detected from ECR URI
_config_region = os.getenv('AWS_REGION', 'us-east-1')

def get_region():
    """Get current region"""
    return _config_region

def set_region(region):
    """Set region"""
    global _config_region
    _config_region = region

ENDPOINT_NAME = os.getenv('SAGEMAKER_ENDPOINT_NAME', 'langchain-endpoint')
INSTANCE_TYPE = os.getenv('SAGEMAKER_INSTANCE_TYPE', 'ml.t3.medium')
ROLE_NAME = os.getenv('SAGEMAKER_ROLE_NAME', 'SageMakerExecutionRole')

def get_sagemaker_role():
    """Get or create SageMaker execution role"""
    iam = boto3.client('iam', region_name=get_region())
    
    try:
        role = iam.get_role(RoleName=ROLE_NAME)
        return role['Role']['Arn']
    except iam.exceptions.NoSuchEntityException:
        print(f"Creating new IAM role: {ROLE_NAME}")
        
        # Create role
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sagemaker.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        role = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for SageMaker LangChain endpoint"
        )
        
        # Attach policies
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'
        )
        
        iam.attach_role_policy(
            RoleName=ROLE_NAME,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        
        # Add Bedrock access
        bedrock_policy = {
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
        
        try:
            iam.put_role_policy(
                RoleName=ROLE_NAME,
                PolicyName="BedrockAccess",
                PolicyDocument=json.dumps(bedrock_policy)
            )
            print("   ✓ Added Bedrock access policy")
        except Exception as e:
            print(f"   ⚠ Could not add Bedrock policy: {e}")
        
        print(f"Created role: {role['Role']['Arn']}")
        return role['Role']['Arn']


def deploy_model(ecr_image_uri: str):
    """Deploy model to SageMaker endpoint"""
    print(f"🚀 Starting SageMaker deployment...")
    print(f"ECR Image URI: {ecr_image_uri}")
    print(f"Endpoint name: {ENDPOINT_NAME}")
    print(f"Instance type: {INSTANCE_TYPE}")
    print(f"Region: {get_region()}")
    print("")
    
    # Get role
    print("📝 Getting/creating IAM role...")
    role = get_sagemaker_role()
    print(f"✓ Using IAM role: {role}")
    print("")
    
    # Create SageMaker session
    print("🔧 Creating SageMaker session...")
    session = sagemaker.Session(boto_session=boto3.Session(region_name=get_region()))
    print(f"✓ Session created")
    print("")
    
    # Create model
    print("📦 Creating SageMaker model...")
    print("   This may take a few minutes...")
    
    model = Model(
        image_uri=ecr_image_uri,
        role=role,
        entry_point='inference.py',
        name=ENDPOINT_NAME
    )
    
    print("✓ Model created")
    print("")
    
    # Deploy to endpoint
    print("🚀 Deploying endpoint...")
    print("   ⏳ This will take 5-10 minutes...")
    print("   You can monitor progress in AWS Console")
    print("")
    
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
        endpoint_name=ENDPOINT_NAME,
        wait=True  # Wait for deployment to complete
    )
    
    print("")
    print(f"✅ Endpoint deployed successfully!")
    print(f"   Endpoint Name: {ENDPOINT_NAME}")
    print(f"   Endpoint ARN: {predictor.endpoint_arn}")
    print(f"   Endpoint URL: https://runtime.sagemaker.{get_region()}.amazonaws.com/endpoints/{ENDPOINT_NAME}")
    print("")
    
    return predictor


def update_endpoint_config():
    """Update endpoint configuration for auto-scaling"""
    client = boto3.client('sagemaker', region_name=get_region())
    
    config_name = f"{ENDPOINT_NAME}-config"
    
    # Create new endpoint config
    client.create_endpoint_config(
        EndpointConfigName=config_name,
        ProductionVariants=[{
            'VariantName': 'AllTraffic',
            'ModelName': ENDPOINT_NAME,
            'InitialInstanceCount': 1,
            'InstanceType': INSTANCE_TYPE,
            'InitialVariantWeight': 1
        }]
    )
    
    # Update endpoint
    client.update_endpoint(
        EndpointName=ENDPOINT_NAME,
        EndpointConfigName=config_name
    )
    
    print(f"✅ Updated endpoint configuration")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_sagemaker.py <ECR_IMAGE_URI>")
        print("Example: python deploy_sagemaker.py 642384808711.dkr.ecr.us-west-2.amazonaws.com/langchain-sagemaker:latest")
        sys.exit(1)
    
    ecr_image_uri = sys.argv[1]
    
    # Extract region from ECR URI if not set
    if '.dkr.ecr.' in ecr_image_uri:
        parts = ecr_image_uri.split('.dkr.ecr.')
        if len(parts) > 1:
            region_part = parts[1].split('.')[0]
            set_region(region_part)
            print(f"📍 Detected region from ECR URI: {region_part}")
    
    try:
        deploy_model(ecr_image_uri)
    except KeyboardInterrupt:
        print("\n⚠ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during deployment: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
