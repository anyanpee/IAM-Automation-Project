#!/usr/bin/env python3
"""
IAM Automation Tool - Main Entry Point
"""

import click
import os
from dotenv import load_dotenv
from iam_manager import IAMManager
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

@click.group()
@click.option('--region', default=os.getenv('AWS_REGION', 'us-east-1'), help='AWS region')
@click.option('--profile', default=os.getenv('AWS_PROFILE', 'default'), help='AWS profile')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def cli(ctx, region, profile, dry_run):
    """IAM Automation Tool - Manage AWS IAM resources at scale"""
    ctx.ensure_object(dict)
    ctx.obj['region'] = region
    ctx.obj['profile'] = profile
    ctx.obj['dry_run'] = dry_run
    
    # Setup logging
    setup_logger()
    
    # Initialize IAM Manager
    ctx.obj['iam_manager'] = IAMManager(region=region, profile=profile, dry_run=dry_run)

@cli.command()
@click.argument('username')
@click.option('--groups', multiple=True, help='Groups to add user to')
@click.option('--policies', multiple=True, help='Policies to attach')
@click.pass_context
def create_user(ctx, username, groups, policies):
    """Create a new IAM user"""
    iam_manager = ctx.obj['iam_manager']
    result = iam_manager.create_user(username, groups=list(groups), policies=list(policies))
    click.echo(f"User creation result: {result}")

@cli.command()
@click.argument('role_name')
@click.argument('trust_policy_file')
@click.option('--policies', multiple=True, help='Policies to attach')
@click.pass_context
def create_role(ctx, role_name, trust_policy_file, policies):
    """Create a new IAM role"""
    iam_manager = ctx.obj['iam_manager']
    result = iam_manager.create_role(role_name, trust_policy_file, policies=list(policies))
    click.echo(f"Role creation result: {result}")

@cli.command()
@click.argument('policy_name')
@click.argument('policy_file')
@click.pass_context
def create_policy(ctx, policy_name, policy_file):
    """Create a new IAM policy"""
    iam_manager = ctx.obj['iam_manager']
    result = iam_manager.create_policy(policy_name, policy_file)
    click.echo(f"Policy creation result: {result}")

@cli.command()
@click.option('--output-file', default='iam_audit.json', help='Output file for audit results')
@click.pass_context
def audit(ctx, output_file):
    """Audit IAM permissions and generate report"""
    iam_manager = ctx.obj['iam_manager']
    result = iam_manager.audit_permissions(output_file)
    click.echo(f"Audit completed. Results saved to: {output_file}")

@cli.command()
@click.argument('config_file')
@click.pass_context
def bulk_create(ctx, config_file):
    """Create multiple IAM resources from configuration file"""
    iam_manager = ctx.obj['iam_manager']
    result = iam_manager.bulk_create_from_config(config_file)
    click.echo(f"Bulk creation completed: {result}")

if __name__ == '__main__':
    cli()