

python create_schemas.py

aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 129033205317.dkr.ecr.eu-west-2.amazonaws.com

docker build --platform linux/amd64 -f etl.dockerfile -t connect4-etl-ecr .

docker tag connect4-etl-ecr:latest 129033205317.dkr.ecr.eu-west-2.amazonaws.com/connect4-etl-ecr:latest

docker push 129033205317.dkr.ecr.eu-west-2.amazonaws.com/connect4-etl-ecr:latest


cd ../../terraform/terraform-etl-iterator
terraform init
terraform apply