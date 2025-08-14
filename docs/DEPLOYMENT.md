# IAM Automation Tool - Deployment Guide

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate permissions
- Docker (for containerized deployment)
- AWS account with IAM permissions

## Local Development Setup

### 1. Quick Setup (Windows)
```bash
# Run the setup script
scripts\setup.bat
```

### 2. Manual Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Configure AWS credentials
aws configure
```

### 3. Test Installation
```bash
python src\main.py --help
python src\main.py --dry-run create-user test-user
```

## Deployment Options

### Option 1: Terraform Infrastructure (Recommended)

**Best for**: Production deployments, infrastructure as code, team environments

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your settings

# Plan and apply
terraform plan
terraform apply

# Get outputs
terraform output
```

**Features**:
- Lambda function with IAM permissions
- CloudWatch logging
- Optional S3 bucket for audit results
- Optional scheduled audits via EventBridge
- Proper IAM roles and policies

### Option 2: Local CLI Tool

**Best for**: Development, testing, one-off operations

```bash
# Activate environment
venv\Scripts\activate

# Run commands
python src\main.py create-user developer-1 --groups developers
python src\main.py audit --output-file audit_results.json
python src\main.py bulk-create config\bulk_config_example.yaml
```

### Option 3: AWS Lambda (Serverless)

**Best for**: Event-driven automation, cost-effective scaling

```bash
# Deploy using the script
cd scripts
python deploy_lambda.py

# Or manually create Lambda function with:
# - Runtime: Python 3.9
# - Handler: lambda_handler.lambda_handler
# - Role: IAMAutomationLambdaRole (with IAM permissions)
```

**Lambda Event Examples**:
```json
{
  "action": "create_user",
  "parameters": {
    "username": "new-user",
    "groups": ["developers"],
    "policies": ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
  }
}
```

### Option 4: Docker Container

**Best for**: Consistent environments, CI/CD pipelines

```bash
# Build and run with Docker Compose
docker-compose up -d

# Execute commands in container
docker-compose exec iam-automation python src/main.py --help

# Or build manually
docker build -t iam-automation .
docker run -v ~/.aws:/home/appuser/.aws:ro iam-automation python src/main.py --help
```

### Option 5: EC2 Instance

**Best for**: Long-running operations, scheduled tasks

```bash
# On EC2 instance:
git clone <your-repo>
cd iam-automation-project
python -m venv venv
source venv/bin/activate  # Linux
pip install -r requirements.txt

# Setup cron jobs for scheduled operations
crontab -e
# Add: 0 2 * * * /path/to/venv/bin/python /path/to/src/main.py audit
```

## Configuration

### Environment Variables
```bash
AWS_REGION=us-east-1
AWS_PROFILE=default
LOG_LEVEL=INFO
DRY_RUN=false
```

### AWS Permissions Required

**Minimum IAM Policy**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateUser",
                "iam:CreateRole",
                "iam:CreatePolicy",
                "iam:AttachUserPolicy",
                "iam:AttachRolePolicy",
                "iam:AddUserToGroup",
                "iam:ListUsers",
                "iam:ListRoles",
                "iam:ListPolicies",
                "iam:GetUser",
                "iam:GetRole",
                "iam:GetPolicy",
                "iam:ListAttachedUserPolicies",
                "iam:ListAttachedRolePolicies",
                "iam:ListUserPolicies",
                "iam:ListRolePolicies",
                "iam:GetGroupsForUser"
            ],
            "Resource": "*"
        }
    ]
}
```

## Usage Examples

### Create Single User
```bash
python src\main.py create-user john-doe --groups developers --policies arn:aws:iam::aws:policy/PowerUserAccess
```

### Create Role with Trust Policy
```bash
python src\main.py create-role EC2-S3-Role config\trust_policies.json --policies arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### Bulk Operations
```bash
python src\main.py bulk-create config\bulk_config_example.yaml
```

### Audit Permissions
```bash
python src\main.py audit --output-file my_audit.json
```

### Dry Run Mode
```bash
python src\main.py --dry-run create-user test-user
```

## Monitoring and Logging

- Logs are output to console with color coding
- Set `LOG_LEVEL` environment variable (DEBUG, INFO, WARNING, ERROR)
- For production, consider forwarding logs to CloudWatch

## Security Best Practices

1. **Use IAM roles instead of access keys when possible**
2. **Apply principle of least privilege**
3. **Enable CloudTrail for audit logging**
4. **Regularly rotate access keys**
5. **Use dry-run mode for testing**
6. **Store sensitive data in AWS Secrets Manager**

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**
   ```bash
   aws configure
   # or set AWS_PROFILE environment variable
   ```

2. **Permission Denied**
   - Check IAM permissions for your user/role
   - Verify AWS region settings

3. **Module Import Errors**
   ```bash
   pip install -r requirements.txt
   # Ensure virtual environment is activated
   ```

4. **Lambda Deployment Issues**
   - Check Lambda execution role permissions
   - Verify deployment package size limits
   - Use Lambda layers for large dependencies

## Next Steps

1. **Customize policy templates** in `templates/` directory
2. **Add custom business logic** to IAM operations
3. **Integrate with CI/CD pipelines**
4. **Set up monitoring and alerting**
5. **Create web interface** for non-technical users