import requests
import boto3
import json
import os
import time
from datetime import datetime
from botocore.exceptions import BotoCoreError,NoCredentialsError,ClientError


def debug_credentials():
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            print("AWS Credentials Found")
            print("Access Key:",credentials.access_key)
        else:
            print("No AWS Credentials Found")

    except Exception as e:
        print(f"Error Debuging Credentials: {e}")

debug_credentials()

def fetch_secret(secret_name):
    try:
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretID =secret_name)

        return json.loads(response['SecretString'])

    except ClientError as e:
        print(f"Error Fetching Secret:{e}")
        raise
    except Exception as e:
        print(f"Unexpected error fetching secret:{e}")
        raise
def fetch_stock_details(symbols,api_key,retries=3):

    url = f"https://yfapi.net/v6/finance/quote?region=US&lang=en&symbols={','.join(symbols)}"
    
    headers = {"X-API-KEY": api_key}

    for attempt in range(retries):
        try:
            response = requests.get(url,headers=headers)
            print("This is resppinse",response)
            if response.status_code == 429:
                print(f"Rate limit hit. Retrying in {2 ** attempt} seconds...")
                time.sleep(2**attempt)
                continue
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            if attempt == retries - 1:
                raise
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            if attempt == retries - 1:
                raise
def write_to_s3(bucket_name,data,key_prefix):
    try:
        s3 =boto3.client('s3')
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        key = f"{key_prefix}/stock_data_{timestamp}.json"

        s3.put_object(Bucket=bucket_name,Key=key,Body=json.dumps(data,indent=2))
        print(f"Data Sucessfuly written to S3: {bucket_name}/{key}")

    except BotoCoreError as e:
        print(f"Error writing to S3: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error writing to S3: {e}")
        raise

if __name__ == "__main__":
    secret_name = os.getenv("SECRET_NAME","Yahoo_Finance_Api")

    bucket_name= os.getenv("S3_BUCKET","finace-stock-data-dea")

    symbols = os.getenv("STOCK_SYMBOLS","AAPL,MSFT,GOOGL").split(",")


    try:
        secrets =  fetch_secret(secret_name)
        api_key = secrets['Yahoo_finance_api_key']

        stock_data = fetch_stock_details(symbols,api_key)

        write_to_s3(bucket_name,stock_data,"raw")

    except NoCredentialsError:
        print("AWS credentials not found. Ensure credentials are configured.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
        


