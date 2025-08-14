# Getting Started with IAM Automation Project

## Overview

This project provides a comprehensive IAM automation solution with multiple deployment options:

- **CLI Tool**: Local command-line interface
- **Lambda Function**: Serverless AWS deployment
- **Docker Container**: Containerized deployment
- **Terraform Infrastructure**: Infrastructure as Code

## Quick Setup (5 minutes)

### 1. Prerequisites
- Python 3.8+
- AWS CLI configured (`aws configure`)
- Terraform (for infrastructure deployment)

### 2. Setup Project
```bash
# Clone/download project
cd "IAM automation project"

# Quick setup (Windows)
scripts\setup.bat

# Or manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

### 3. Test Installation
```bash
# Test CLI
python src\main.py --help

# Test with dry-run
python src\main.py --dry-run create-user test-user
```

## Deployment Options

### 🚀 Recommended: Terraform Infrastructure

```bash
cd terraform
terraform init
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform apply
```

**What you get**:
- Lambda function for IAM operations
- Proper IAM roles and permissions
- CloudWatch logging
- Optional S3 bucket for audit results
- Optional scheduled audits

### 🖥️ Local CLI Usage

```bash
# Create user
python src\main.py create-user john-doe --groups developers

# Create role
python src\main.py create-role MyRole config\trust_policies.json

# Run audit
python src\main.py audit --output-file my_audit.json

# Bulk operations
python src\main.py bulk-create config\bulk_config_example.yaml
```

### 🐳 Docker Deployment

```bash
docker-compose up -d
docker-compose exec iam-automation python src/main.py --help
```

## Key Features

### ✅ User Management
- Create IAM users with groups and policies
- Bulk user creation from YAML/JSON config
- Dry-run mode for testing

### ✅ Role Management
- Create roles with trust policies
- Attach managed and custom policies
- Template-based role creation

### ✅ Policy Management
- Create custom policies from templates
- Jinja2 templating support
- Common policy templates included

### ✅ Auditing & Reporting
- Comprehensive IAM permission audit
- JSON output for further processing
- User and role permission analysis

### ✅ Automation Features
- Scheduled audits (with Terraform)
- Bulk operations from config files
- Lambda-based serverless execution

## Project Structure

```
├── src/                    # Core application code
│   ├── main.py            # CLI entry point
│   ├── iam_manager.py     # Core IAM operations
│   ├── lambda_handler.py  # Lambda function handler
│   └── utils/             # Utility modules
├── terraform/             # Infrastructure as Code
├── config/               # Configuration files
├── templates/            # IAM policy templates
├── scripts/              # Deployment scripts
├── tests/                # Unit tests
└── docs/                 # Documentation
```

## Common Use Cases

### 1. Onboard New Developer
```bash
python src\main.py create-user new-developer \
  --groups developers \
  --policies arn:aws:iam::aws:policy/PowerUserAccess
```

### 2. Create Service Role
```bash
python src\main.py create-role ServiceRole \
  config\trust_policies.json \
  --policies arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### 3. Audit All Permissions
```bash
python src\main.py audit --output-file audit_$(date +%Y%m%d).json
```

### 4. Bulk User Creation
```yaml
# config/new_team.yaml
users:
  - name: "alice"
    groups: ["developers"]
    policies: ["arn:aws:iam::aws:policy/ReadOnlyAccess"]
  - name: "bob"
    groups: ["admins"]
    policies: ["arn:aws:iam::aws:policy/PowerUserAccess"]
```

```bash
python src\main.py bulk-create config\new_team.yaml
```

## Security Best Practices

- ✅ Use dry-run mode for testing
- ✅ Apply principle of least privilege
- ✅ Regular permission audits
- ✅ Use IAM roles instead of access keys
- ✅ Enable CloudTrail logging
- ✅ Store sensitive data in AWS Secrets Manager

## Next Steps

1. **Customize Templates**: Edit files in `templates/` for your policies
2. **Add Business Logic**: Extend `iam_manager.py` for custom operations
3. **Set Up Monitoring**: Configure CloudWatch alerts
4. **Integrate CI/CD**: Use in your deployment pipelines
5. **Web Interface**: Deploy the optional web UI

## Support

- Check `docs/DEPLOYMENT.md` for detailed deployment instructions
- Review `terraform/README.md` for infrastructure details
- Run tests with `python -m pytest tests/`
- Use `--dry-run` flag for safe testing

## Makefile Commands

```bash
make help              # Show available commands
make setup             # Setup development environment
make deploy-terraform  # Deploy with Terraform
make test             # Run tests
make audit            # Run IAM audit
```