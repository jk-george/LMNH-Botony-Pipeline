## Terraform Files for creating an ECR and an S3.

This is the **first** Terraform folder that should be run before the terraform-etl-iterator folder.

It will create two ECRs and one S3. The ECR will hold images that will be used in task definitions. Whilst the S3 will hold long term storage data produced by one of these tasks.

### Requirements:

One missing component is a terraform.tfvars file.

It **must** contain:
- `ETL_ECR_NAME` = "Name of choice for an ECR that will hold the ETL process image"
- `TRANSFER_DATA_ECR_NAME` = "Name of choice for an ECR that will hold the Long Term Storage process image"

- `BUCKET` = "Bucket Name for Long Term Data to be sent to"


After creating this terraform.tfvars file, you must include `ETL_ECR_NAME`, `TRANSFER_DATA_ECR_NAME` and `BUCKET` in the terraform.tfvars file inside of the terraform-etl-iterator file.