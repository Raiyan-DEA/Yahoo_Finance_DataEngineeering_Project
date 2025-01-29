## command to create a repository in AWS ECR With name Stock-data-ingestion

aws ecr create-repository --repository-name stock-data-ingestion

## command  to buld the Docker Container Image (dont forget the dot at the end)

docker build -t stock-data-ingestion .

## Command to give the tag Lastest to the Docker Image

docker tag stock-data-ingestion:latest 980921724429.dkr.ecr.us-east-1.amazonaws.com/stock-data-ingestion:latest

##you can get above URI from AWS ECR console

## Command to connect to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 980921724429.dkr.ecr.us-east-1.amazonaws.com

## replace this 980921724429.dkr.ecr.us-east-1.amazonaws.com with your URI from AWS ECR console

## Command to Push the latest Image to AWS ECR

docker push 980921724429.dkr.ecr.us-east-1.amazonaws.com/stock-data-ingestion:latest


