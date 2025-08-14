#!/usr/bin/env python3
"""
Deploy IAM automation tool as AWS Lambda function
"""

import boto3
import zipfile
import os
import json
from pathlib import Path

def create_deployment_package():
    """Create deployment package for Lambda"""
    print("Creating deployment package...")
    
    # Create zip file
    with zipfile.ZipFile('iam_automation_lambda.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add source files
        src_dir = Path('../src')
        for file_path in src_dir.rglob('*.py'):
            zipf.write(file_path, file_path.relative_to(src_dir.parent))
        
        # Add requirements (you'll need to install them in a lambda-compatible way)
        # This is a simplified version - in production, use Lambda layers or docker
        print("Note: For production deployment, use Lambda layers for dependencies")
    
    print("Deployment package created: iam_automation_lambda.zip")
    return 'iam_automation_lambda.zip'

def create_lambda_function(function_name: str, role_arn: str, zip_file: str):
    """Create Lambda function"""
    lambda_client = boto3.client('lambda')
    
    try:
        with open(zip_file, 'rb') as f:
            zip_content = f.read()
        
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role=role_arn,
            Handler='lambda_handler.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='IAM Automation Tool',
            Timeout=300,
            MemorySize=512,
            Environment={
                'Variables': {
                    'LOG_LEVEL': 'INFO'
                }
            }
        )
        
        print(f"Lambda function created: {response['FunctionArn']}")
        return response
        
    except Exception as e:
        print(f"Failed to create Lambda function: {e}")
        return None

def create_lambda_role():
    """Create IAM role for Lambda function"""
    iam_client = boto3.client('iam')
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        # Create role
        role_response = iam_client.create_role(
            RoleName='IAMAutomationLambdaRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for IAM Automation Lambda function'
        )
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/IAMFullAccess'  # Adjust permissions as needed
        ]
        
        for policy in policies:
            iam_client.attach_role_policy(
                RoleName='IAMAutomationLambdaRole',
                PolicyArn=policy
            )
        
        print(f"Lambda role created: {role_response['Role']['Arn']}")
        return role_response['Role']['Arn']
        
    except Exception as e:
        print(f"Failed to create Lambda role: {e}")
        return None

if __name__ == '__main__':
    print("Deploying IAM Automation Tool to AWS Lambda...")
    
    # Create Lambda execution role
    role_arn = create_lambda_role()
    if not role_arn:
        exit(1)
    
    # Wait for role to be available
    print("Waiting for role to be available...")
    import time
    time.sleep(10)
    
    # Create deployment package
    zip_file = create_deployment_package()
    
    # Deploy Lambda function
    function_name = 'iam-automation-tool'
    result = create_lambda_function(function_name, role_arn, zip_file)
    
    if result:
        print("Deployment completed successfully!")
        print(f"Function ARN: {result['FunctionArn']}")
    else:
        print("Deployment failed!")
        exit(1)