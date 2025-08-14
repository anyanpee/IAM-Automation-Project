"""
AWS Lambda handler for IAM automation tool
"""

import json
import logging
from iam_manager import IAMManager
from utils.logger import setup_logger

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    Lambda function handler for IAM automation
    
    Expected event structure:
    {
        "action": "create_user|create_role|create_policy|audit",
        "parameters": {
            // Action-specific parameters
        }
    }
    """
    try:
        # Initialize IAM Manager
        iam_manager = IAMManager(
            region=event.get('region', 'us-east-1'),
            dry_run=event.get('dry_run', False)
        )
        
        action = event.get('action')
        parameters = event.get('parameters', {})
        
        if action == 'create_user':
            result = iam_manager.create_user(
                username=parameters['username'],
                groups=parameters.get('groups', []),
                policies=parameters.get('policies', [])
            )
        
        elif action == 'create_role':
            # For Lambda, trust policy should be provided in parameters
            trust_policy = parameters.get('trust_policy')
            if not trust_policy:
                raise ValueError("Trust policy is required for role creation")
            
            # Create temporary file for trust policy
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(trust_policy, f)
                trust_policy_file = f.name
            
            try:
                result = iam_manager.create_role(
                    role_name=parameters['role_name'],
                    trust_policy_file=trust_policy_file,
                    policies=parameters.get('policies', [])
                )
            finally:
                # Clean up temporary file
                import os
                os.unlink(trust_policy_file)
        
        elif action == 'create_policy':
            # For Lambda, policy document should be provided in parameters
            policy_document = parameters.get('policy_document')
            if not policy_document:
                raise ValueError("Policy document is required for policy creation")
            
            # Create temporary file for policy document
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(policy_document, f)
                policy_file = f.name
            
            try:
                result = iam_manager.create_policy(
                    policy_name=parameters['policy_name'],
                    policy_file=policy_file
                )
            finally:
                # Clean up temporary file
                import os
                os.unlink(policy_file)
        
        elif action == 'audit':
            # For Lambda, return audit results directly instead of saving to file
            result = iam_manager.audit_permissions('/tmp/audit_results.json')
            
            # Read the audit results and include in response
            if result['status'] == 'success':
                with open('/tmp/audit_results.json', 'r') as f:
                    audit_data = json.load(f)
                result['audit_data'] = audit_data
        
        else:
            raise ValueError(f"Unsupported action: {action}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }

# Example event structures for testing
EXAMPLE_EVENTS = {
    "create_user": {
        "action": "create_user",
        "parameters": {
            "username": "lambda-test-user",
            "groups": ["developers"],
            "policies": ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
        }
    },
    "create_role": {
        "action": "create_role",
        "parameters": {
            "role_name": "lambda-test-role",
            "trust_policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "policies": ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
        }
    },
    "audit": {
        "action": "audit",
        "parameters": {}
    }
}