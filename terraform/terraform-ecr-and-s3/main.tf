provider "aws" {
  region = "eu-west-2"
}


resource "aws_ecr_repository" "my_ecr_repo" {
  name                 = var.ECR_NAME  
  image_tag_mutability = "MUTABLE"  
  image_scanning_configuration {
    scan_on_push = true  
  }

  lifecycle {
    prevent_destroy = false  
  }
}


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