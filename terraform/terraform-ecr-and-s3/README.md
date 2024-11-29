## Terraform Files for creating an ECR and an S3.

### Requirements:

One missing component is a terraform.tfvars file.

It **must** contain:
- `ECR_NAME` = "AWS Repository Name"
- `BUCKET` = "Bucket Name for Loaded Data to be sent to"