## Terraform Files for creating an ECR and an S3.

This is the first Terraform folder that should be run before the terraform-etl-iterator folder.


### Requirements:

One missing component is a terraform.tfvars file.

It **must** contain:
- `ETL_ECR_NAME` = "Name of choice for an ECR that will hold the ETL process image"
- `TRANSFER_DATA_ECR_NAME` = "Name of choice for an ECR that will hold the Long Term Storage process image"

- `BUCKET` = "Bucket Name for Long Term Data to be sent to"