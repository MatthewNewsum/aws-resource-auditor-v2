# aws-resource-auditor-v2


# AWS Resource Auditor

A comprehensive AWS infrastructure auditing tool that collects and reports on resources across multiple regions and services.

## Preface

- If you try to use this app its at your own risk
- There is no support whatsoever
- There is no warranty express or implied
- I would appreciate suggestions to improve it so if you have ideas to help me make it better send them please
- If theres a service you want I have not yet added let me know and ill see what i can do 

## Known Issues
- Some services will not produce any output at all if theres nothing to report on (EMR and Organizations are 2 examples).  I have created and tested these resources and they worked as I expected.

## Features

- Multi-region resource discovery
- Parallel processing for faster auditing
- Detailed Excel and JSON reports
- Supports auditing of:
  - EC2 instances and EIPs
  - RDS instances
  - VPC resources (VPCs, Subnets, IGWs, NAT Gateways)
  - IAM resources (Users, Roles, Groups)
  - S3 buckets
  - Lambda functions
  - DynamoDB tables
  - Bedrock models
  - AWS Config

## Requirements

```
boto3
pandas
xlsxwriter
```

## Installation

```bash
pip install boto3 pandas xlsxwriter
git clone [repository-url]
cd aws-resource-auditor
```

## Usage

Basic usage:
```bash
python main.py
```

Specific regions:
```bash
python main.py --regions us-east-1,us-west-2
```

Specific services:
```bash
python main.py --services ec2,rds,vpc
```

Custom output directory:
```bash
python main.py --output-dir /path/to/output
```

## Output

The tool generates two reports:
1. Excel report (aws_inventory_[timestamp].xlsx) with sheets for:
   - Resource counts
   - Region summary
   - Regional resource details
   - Service-specific details
   - Resource usage by region matrix

2. JSON report (aws_inventory_[timestamp].json) containing raw audit data

## AWS Credentials

Configure AWS credentials using:
- AWS CLI (`aws configure`)
- Environment variables
- IAM role if running on AWS

Required permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "rds:Describe*",
                "iam:List*",
                "iam:Get*",
                "s3:List*",
                "s3:GetBucket*",
                "lambda:List*",
                "lambda:Get*",
                "dynamodb:List*",
                "dynamodb:Describe*",
                "bedrock:List*",
                "bedrock:Get*",
                "config:Describe*",
                "lightsail:GetInstances",
                "lightsail:GetRelationalDatabases",
                "lightsail:GetContainerServices"
            ],
            "Resource": "*"
        }
    ]
}
```