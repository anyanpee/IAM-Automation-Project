# Terraform Infrastructure for IAM Automation

This directory contains Terraform configuration to deploy the IAM automation tool infrastructure on AWS.

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with appropriate permissions
- AWS credentials with IAM permissions

## Quick Start

1. **Initialize Terraform**:
   ```bash
   cd terraform
   terraform init
   ```

2. **Configure Variables**:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your settings
   ```

3. **Plan Deployment**:
   ```bash
   terraform plan
   ```

4. **Deploy Infrastructure**:
   ```bash
   terraform apply
   ```

## Configuration Options

### Basic Configuration
```hcl
aws_region   = "us-east-1"
project_name = "iam-automation"
log_level    = "INFO"
```

### Optional Features
```hcl
create_s3_bucket       = true
enable_scheduled_audit = true
audit_schedule        = "rate(7 days)"
```

## Resources Created

- **Lambda Function**: Main IAM automation function
- **IAM Role**: Lambda execution role with IAM permissions
- **CloudWatch Log Group**: For Lambda function logs
- **S3 Bucket**: (Optional) For storing audit results
- **EventBridge Rule**: (Optional) For scheduled audits

## Usage After Deployment

### Invoke Lambda Function
```bash
aws lambda invoke \
  --function-name iam-automation-function \
  --payload '{"action":"audit","parameters":{}}' \
  response.json
```

### View Logs
```bash
aws logs tail /aws/lambda/iam-automation-function --follow
```

### Access S3 Audit Results
```bash
aws s3 ls s3://iam-automation-audit-results-xxxxx/
```

## Cleanup

```bash
terraform destroy
```

## Security Considerations

- Lambda function has IAM permissions - review and adjust as needed
- S3 bucket is encrypted by default
- CloudWatch logs have retention policy
- Consider using least privilege principles

## Customization

- Modify `variables.tf` to add new configuration options
- Update `main.tf` to add additional AWS resources
- Use `ec2.tf` for EC2-based deployment (uncomment as needed)