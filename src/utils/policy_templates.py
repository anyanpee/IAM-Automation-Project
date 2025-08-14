"""
IAM Policy Template Manager
"""

import json
import os
# from jinja2 import Template, Environment, FileSystemLoader  # Not available in Lambda
from typing import Dict, Any

class PolicyTemplateManager:
    def __init__(self, templates_dir: str = None):
        """Initialize policy template manager"""
        if templates_dir is None:
            # Default to templates directory relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'templates')
        
        self.templates_dir = templates_dir
        # self.env = Environment(loader=FileSystemLoader(templates_dir))  # Disabled for Lambda
    
    def generate_policy(self, template_name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Generate policy from template with variables (simplified for Lambda)"""
        # For Lambda, return pre-defined policies instead of templating
        common_policies = self.get_common_policies()
        if template_name in common_policies:
            return common_policies[template_name]
        else:
            raise Exception(f"Template {template_name} not found. Available: {list(common_policies.keys())}")
    
    def get_common_policies(self) -> Dict[str, Dict[str, Any]]:
        """Get common pre-defined policies"""
        return {
            "s3_read_only": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:ListBucket"
                        ],
                        "Resource": "*"
                    }
                ]
            },
            "ec2_read_only": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ec2:Describe*",
                            "ec2:List*"
                        ],
                        "Resource": "*"
                    }
                ]
            },
            "lambda_basic_execution": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "arn:aws:logs:*:*:*"
                    }
                ]
            }
        }
    
    def get_trust_policies(self) -> Dict[str, Dict[str, Any]]:
        """Get common trust policies"""
        return {
            "ec2_trust": {
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
            "lambda_trust": {
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
            },
            "cross_account_trust": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::ACCOUNT_ID:root"
                        },
                        "Action": "sts:AssumeRole",
                        "Condition": {
                            "StringEquals": {
                                "sts:ExternalId": "EXTERNAL_ID"
                            }
                        }
                    }
                ]
            }
        }