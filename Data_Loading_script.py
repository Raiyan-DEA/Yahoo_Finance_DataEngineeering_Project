import requests
import boto3
import json
import os
import time
from datetime import datetime
from botocore.exceptions import BotoCoreError, NoCredentialsError, ClientError

def debug_credentials():
    """
    Debug AWS credentials.
    """
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            print("AWS credentials found.")
            print("Access Key:", credentials.access_key)
        else:
            print("No AWS credentials found.")
    except Exception as e:
        print(f"Error debugging credentials: {e}")

debug_credentials()

def fetch_secret(secret_name):
    """
    Fetch secret value from AWS Secrets Manager.
    """
    try:
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        print(f"Error fetching secret: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error fetching secret: {e}")
        raise

def fetch_stock_data(symbols, api_key, retries=3):
    """
    Fetch stock data from Yahoo Finance API with retry logic for rate limiting.
    """
    url = f"https://yfapi.net/v6/finance/quote?region=US&lang=en&symbols={','.join(symbols)}"
    
    headers = {"X-API-KEY": api_key}
    
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            print("This is response",response)
            if response.status_code == 429:  # Too many requests
                print(f"Rate limit hit. Retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            if attempt == retries - 1:
                raise
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            if attempt == retries - 1:
                raise

def write_to_s3(bucket_name, data, key_prefix):
    """
    Write data to S3 bucket.
    """
    try:
        s3 = boto3.client('s3')
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        key = f"{key_prefix}/stock_data_{timestamp}.json"
        s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data, indent=2))
        print(f"Data successfully written to S3: {bucket_name}/{key}")
    except BotoCoreError as e:
        print(f"Error writing to S3: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error writing to S3: {e}")
        raise

if __name__ == "__main__":
    # Environment variables
    secret_name = os.getenv("SECRET_NAME", "Yahoo_Finance_Api")  # AWS Secrets Manager secret name
    bucket_name = os.getenv("S3_BUCKET", "finance-stock-data-dea")  # S3 bucket name
    symbols = os.getenv("STOCK_SYMBOLS", "AAPL,MSFT,GOOGL").split(",")  # Stock symbols
    try:
        # Fetch API key from AWS Secrets Manager
        secrets = fetch_secret(secret_name)
        api_key = secrets['yahoo_finance_api_key']

        # Fetch stock data
        print("Fetching stock data...")
        stock_data = fetch_stock_data(symbols, api_key)
        print("Fetched Stock Data:", stock_data)

        # Write data to S3
        print("Writing data to S3...")
        write_to_s3(bucket_name, stock_data, "raw")

        print("Stock data ingestion completed successfully.")

    except NoCredentialsError:
        print("AWS credentials not found. Ensure credentials are configured.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise