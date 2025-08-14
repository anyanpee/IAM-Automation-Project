# IAM Automation Tool - Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   Developer/    │───▶│   AWS Lambda     │───▶│   AWS IAM       │
│   Admin User    │    │   Function       │    │   Service       │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│                 │    │                  │    │                 │
│   AWS CLI /     │    │   CloudWatch     │    │   Users, Roles  │
│   Console       │    │   Logs           │    │   & Policies    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘

Components:
- AWS Lambda: Python 3.9 runtime with IAM permissions
- AWS IAM: Target service for automation
- CloudWatch: Logging and monitoring
- Boto3: AWS SDK for Python
- JSON: Configuration and response format
```