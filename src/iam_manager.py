"""
IAM Manager - Core IAM operations handler
"""

import boto3
import json
# import yaml  # Not available in Lambda by default
import logging
from botocore.exceptions import ClientError
from typing import List, Dict, Any, Optional
from utils.policy_templates import PolicyTemplateManager

logger = logging.getLogger(__name__)

class IAMManager:
    def __init__(self, region: str = 'us-east-1', profile: str = 'default', dry_run: bool = False):
        """Initialize IAM Manager with AWS session"""
        self.region = region
        self.profile = profile
        self.dry_run = dry_run
        
        # Initialize AWS session (Lambda uses IAM role, no profile needed)
        if profile == 'default':
            # In Lambda, use default session without profile
            self.iam_client = boto3.client('iam', region_name=region)
            self.sts_client = boto3.client('sts', region_name=region)
        else:
            # For local development with profiles
            session = boto3.Session(profile_name=profile)
            self.iam_client = session.client('iam', region_name=region)
            self.sts_client = session.client('sts', region_name=region)
        
        # Initialize policy template manager
        self.policy_manager = PolicyTemplateManager()
        
        logger.info(f"IAM Manager initialized - Region: {region}, Profile: {profile}, Dry Run: {dry_run}")

    def create_user(self, username: str, groups: List[str] = None, policies: List[str] = None) -> Dict[str, Any]:
        """Create IAM user with optional groups and policies"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create user: {username}")
                return {"status": "dry_run", "username": username}
            
            # Create user
            response = self.iam_client.create_user(UserName=username)
            logger.info(f"Created user: {username}")
            
            result = {"status": "success", "username": username, "arn": response['User']['Arn']}
            
            # Add to groups if specified
            if groups:
                for group in groups:
                    try:
                        self.iam_client.add_user_to_group(GroupName=group, UserName=username)
                        logger.info(f"Added user {username} to group {group}")
                    except ClientError as e:
                        logger.error(f"Failed to add user to group {group}: {e}")
            
            # Attach policies if specified
            if policies:
                for policy in policies:
                    try:
                        self.iam_client.attach_user_policy(UserName=username, PolicyArn=policy)
                        logger.info(f"Attached policy {policy} to user {username}")
                    except ClientError as e:
                        logger.error(f"Failed to attach policy {policy}: {e}")
            
            return result
            
        except ClientError as e:
            logger.error(f"Failed to create user {username}: {e}")
            return {"status": "error", "message": str(e)}

    def create_role(self, role_name: str, trust_policy_file: str, policies: List[str] = None) -> Dict[str, Any]:
        """Create IAM role with trust policy"""
        try:
            # Load trust policy
            with open(trust_policy_file, 'r') as f:
                trust_policy = json.load(f)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create role: {role_name}")
                return {"status": "dry_run", "role_name": role_name}
            
            # Create role
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy)
            )
            
            logger.info(f"Created role: {role_name}")
            result = {"status": "success", "role_name": role_name, "arn": response['Role']['Arn']}
            
            # Attach policies if specified
            if policies:
                for policy in policies:
                    try:
                        self.iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy)
                        logger.info(f"Attached policy {policy} to role {role_name}")
                    except ClientError as e:
                        logger.error(f"Failed to attach policy {policy}: {e}")
            
            return result
            
        except (ClientError, FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to create role {role_name}: {e}")
            return {"status": "error", "message": str(e)}

    def create_policy(self, policy_name: str, policy_file: str) -> Dict[str, Any]:
        """Create IAM policy from file"""
        try:
            # Load policy document
            with open(policy_file, 'r') as f:
                policy_document = json.load(f)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would create policy: {policy_name}")
                return {"status": "dry_run", "policy_name": policy_name}
            
            # Create policy
            response = self.iam_client.create_policy(
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
            
            logger.info(f"Created policy: {policy_name}")
            return {"status": "success", "policy_name": policy_name, "arn": response['Policy']['Arn']}
            
        except (ClientError, FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to create policy {policy_name}: {e}")
            return {"status": "error", "message": str(e)}

    def audit_permissions(self, output_file: str) -> Dict[str, Any]:
        """Audit IAM permissions and generate report"""
        try:
            audit_results = {
                "users": [],
                "roles": [],
                "policies": [],
                "summary": {}
            }
            
            # Audit users
            paginator = self.iam_client.get_paginator('list_users')
            for page in paginator.paginate():
                for user in page['Users']:
                    user_info = self._audit_user(user['UserName'])
                    audit_results["users"].append(user_info)
            
            # Audit roles
            paginator = self.iam_client.get_paginator('list_roles')
            for page in paginator.paginate():
                for role in page['Roles']:
                    role_info = self._audit_role(role['RoleName'])
                    audit_results["roles"].append(role_info)
            
            # Generate summary
            audit_results["summary"] = {
                "total_users": len(audit_results["users"]),
                "total_roles": len(audit_results["roles"]),
                "users_with_policies": len([u for u in audit_results["users"] if u["attached_policies"]]),
                "roles_with_policies": len([r for r in audit_results["roles"] if r["attached_policies"]])
            }
            
            # Save results
            with open(output_file, 'w') as f:
                json.dump(audit_results, f, indent=2, default=str)
            
            logger.info(f"Audit completed. Results saved to {output_file}")
            return {"status": "success", "output_file": output_file}
            
        except ClientError as e:
            logger.error(f"Audit failed: {e}")
            return {"status": "error", "message": str(e)}

    def _audit_user(self, username: str) -> Dict[str, Any]:
        """Audit individual user permissions"""
        try:
            user_info = {
                "username": username,
                "attached_policies": [],
                "groups": [],
                "inline_policies": []
            }
            
            # Get attached policies
            try:
                response = self.iam_client.list_attached_user_policies(UserName=username)
                user_info["attached_policies"] = [p['PolicyArn'] for p in response['AttachedPolicies']]
            except ClientError:
                pass
            
            # Get groups
            try:
                response = self.iam_client.list_groups_for_user(UserName=username)
                user_info["groups"] = [g['GroupName'] for g in response['Groups']]
            except ClientError:
                pass
            
            # Get inline policies
            try:
                response = self.iam_client.list_user_policies(UserName=username)
                user_info["inline_policies"] = response['PolicyNames']
            except ClientError:
                pass
            
            return user_info
            
        except ClientError as e:
            logger.error(f"Failed to audit user {username}: {e}")
            return {"username": username, "error": str(e)}

    def _audit_role(self, role_name: str) -> Dict[str, Any]:
        """Audit individual role permissions"""
        try:
            role_info = {
                "role_name": role_name,
                "attached_policies": [],
                "inline_policies": []
            }
            
            # Get attached policies
            try:
                response = self.iam_client.list_attached_role_policies(RoleName=role_name)
                role_info["attached_policies"] = [p['PolicyArn'] for p in response['AttachedPolicies']]
            except ClientError:
                pass
            
            # Get inline policies
            try:
                response = self.iam_client.list_role_policies(RoleName=role_name)
                role_info["inline_policies"] = response['PolicyNames']
            except ClientError:
                pass
            
            return role_info
            
        except ClientError as e:
            logger.error(f"Failed to audit role {role_name}: {e}")
            return {"role_name": role_name, "error": str(e)}

    def bulk_create_from_config(self, config_file: str) -> Dict[str, Any]:
        """Create multiple IAM resources from configuration file"""
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    raise Exception("YAML files not supported in Lambda. Use JSON instead.")
                else:
                    config = json.load(f)
            
            results = {"users": [], "roles": [], "policies": []}
            
            # Create users
            if 'users' in config:
                for user_config in config['users']:
                    result = self.create_user(
                        user_config['name'],
                        groups=user_config.get('groups', []),
                        policies=user_config.get('policies', [])
                    )
                    results["users"].append(result)
            
            # Create roles
            if 'roles' in config:
                for role_config in config['roles']:
                    result = self.create_role(
                        role_config['name'],
                        role_config['trust_policy_file'],
                        policies=role_config.get('policies', [])
                    )
                    results["roles"].append(result)
            
            # Create policies
            if 'policies' in config:
                for policy_config in config['policies']:
                    result = self.create_policy(
                        policy_config['name'],
                        policy_config['policy_file']
                    )
                    results["policies"].append(result)
            
            return {"status": "success", "results": results}
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to process config file {config_file}: {e}")
            return {"status": "error", "message": str(e)}