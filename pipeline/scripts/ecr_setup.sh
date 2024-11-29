
cd ..

python create_schemas.py

cd ../terraform/terraform-ecr-and-s3

terraform init
terraform apply