"""
Deploy LangChain module to AWS SageMaker
"""
import boto3
import sagemaker
from sagemaker.pytorch import PyTorchModel
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
REGION = os.getenv('AWS_REGION', 'us-east-1')
ENDPOINT_NAME = os.getenv('SAGEMAKER_ENDPOINT_NAME', 'langchain-endpoint')
INSTANCE_TYPE = os.getenv('SAGEMAKER_INSTANCE_TYPE', 'ml.t3.medium')
ROLE_NAME = os.getenv('SAGEMAKER_ROLE_NAME', 'SageMakerExecutionRole')

def get_sagemaker_role():
    """Get or create SageMaker execution role"""
    iam = boto3.client('iam', region_name=REGION)
    
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
        
        print(f"Created role: {role['Role']['Arn']}")
        return role['Role']['Arn']


def deploy_model(ecr_image_uri: str):
    """Deploy model to SageMaker endpoint"""
    session = sagemaker.Session()
    role = get_sagemaker_role()
    
    print(f"Deploying model from ECR: {ecr_image_uri}")
    print(f"Endpoint name: {ENDPOINT_NAME}")
    print(f"Instance type: {INSTANCE_TYPE}")
    
    # Create model
    model = PyTorchModel(
        image_uri=ecr_image_uri,
        role=role,
        entry_point='inference.py',
        framework_version='2.0.0',
        py_version='py310'
    )
    
    # Deploy to endpoint
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type=INSTANCE_TYPE,
        endpoint_name=ENDPOINT_NAME
    )
    
    print(f"✅ Endpoint deployed successfully: {ENDPOINT_NAME}")
    print(f"Endpoint ARN: {predictor.endpoint_arn}")
    
    return predictor


def update_endpoint_config():
    """Update endpoint configuration for auto-scaling"""
    client = boto3.client('sagemaker', region_name=REGION)
    
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
    import json
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python deploy_sagemaker.py <ECR_IMAGE_URI>")
        print("Example: python deploy_sagemaker.py 123456789.dkr.ecr.us-east-1.amazonaws.com/langchain-sagemaker:latest")
        sys.exit(1)
    
    ecr_image_uri = sys.argv[1]
    deploy_model(ecr_image_uri)
