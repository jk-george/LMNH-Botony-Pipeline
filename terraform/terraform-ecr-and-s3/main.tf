provider "aws" {
  region = "eu-west-2"
}

# ECR to hold the image that runs the short -> long term data transfer
resource "aws_ecr_repository" "ecr_for_long_term_storage" {
  name                 = var.TRANSFER_DATA_ECR_NAME
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true  
  }

  lifecycle {
    prevent_destroy = false  
  }
}



# ECR to hold the image that runs the etl process
resource "aws_ecr_repository" "ecr_for_etl" {
  name                 = var.ETL_ECR_NAME  
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true  
  }

  lifecycle {
    prevent_destroy = false  
  }
}



# S3: Long term storage solution
resource "aws_s3_bucket" "long_term_storage_bucket" {
  bucket = var.BUCKET
  force_destroy = true
}


resource "aws_s3_bucket_public_access_block" "block_public_access" {
  bucket = aws_s3_bucket.long_term_storage_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}