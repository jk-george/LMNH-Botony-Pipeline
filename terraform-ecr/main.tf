provider "aws" {
  region = "eu-west-2"  # Specify the AWS region (modify as needed)
}

# Create an ECR repository
resource "aws_ecr_repository" "my_ecr_repo" {
  name                 = var.ECR_NAME  # The name of the ECR repository
  image_tag_mutability = "MUTABLE"        # Options: MUTABLE or IMMUTABLE
  image_scanning_configuration {
    scan_on_push = true  
  }

  lifecycle {
    prevent_destroy = false  
  }
}
