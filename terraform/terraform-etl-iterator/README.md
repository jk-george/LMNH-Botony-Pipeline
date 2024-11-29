## Terraform Files for creating an ETL Iterator.

**Every minute, whatever image is inside the ecr created beforehand will continue to get run as a Task.**

## Dependencies:

**You must have the following in your terraform.tfvars file before you can use the terraform:**

The following **must** be the same as from the `terraform-ecr-and-s3` folder:
- `ETL_ECR_NAME` 
- `TRANSFER_DATA_ECR_NAME` 

The following are pre-requisites for this script to run:
- `VPC_ID` : You must have a VPC and present its ID for use.
- `ECS_CLUSTER_NAME` : You must have created an ECS Cluster. 
- `SUBNET_IDS` : Within your VPC you must have created public subnet. Present chosen public subnets in a list - ["Public Subnet 1","Public Subnet 2","Public Subnet 3"].


## What architecture been used?

- `Task Definition` : A task definiton was used to define a task from the image inside the specified ECR.
- `EventBridge Scheduler Schedule` : A schedule was created using a cron expression that will run every minute.
- `Security Groups,IAM Roles and Policies` : Necessary IAM Roles and policies were created along with the correct security groups so that the scheduler and the task definition had the correct permissions and access.