import boto3
import json
import os
from datetime import datetime

def read_from_s3(bucket_name, prefix):
    """
    Read the latest file from the given S3 bucket and prefix.
    """
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if "Contents" not in response:
        raise FileNotFoundError(f"No files found in bucket {bucket_name} with prefix {prefix}")

    # Get the latest file
    files = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)
    latest_file = files[0]["Key"]

    print(f"Reading data from: {bucket_name}/{latest_file}")
    file_obj = s3.get_object(Bucket=bucket_name, Key=latest_file)
    return json.loads(file_obj["Body"].read().decode("utf-8"))

def transform_data(data):
    """
    Perform the necessary transformations on the stock data.
    """
    transformed_data = []
    for stock in data["quoteResponse"]["result"]:
        transformed_stock = {
            "company_id": stock.get("symbol"),
            "company_name": stock.get("longName"),
            "currency": stock.get("currency"),
            "current_price": stock.get("regularMarketPrice"),
            "day_low": stock.get("regularMarketDayLow"),
            "day_high": stock.get("regularMarketDayHigh"),
        }
        transformed_data.append(transformed_stock)

    print(f"Transformed {len(transformed_data)} records.")
    return transformed_data

def write_to_s3(bucket_name, data, key_prefix):
    """
    Write transformed data back to S3 in JSON format.
    """
    s3 = boto3.client("s3")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    key = f"{key_prefix}/transformed_stock_data_{timestamp}.json"
    s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(data, indent=2))
    print(f"Transformed data written to S3: {bucket_name}/{key}")

if __name__ == "__main__":
    # Environment variables
    raw_bucket = os.getenv("RAW_BUCKET", "finance-stock-data-dea")  # Raw data S3 bucket
    transformed_bucket = os.getenv("TRANSFORMED_BUCKET", "finance-stock-data-dea")  # Transformed data S3 bucket
    raw_prefix = os.getenv("RAW_PREFIX", "raw/")  # Prefix for raw data in S3
    transformed_prefix = os.getenv("TRANSFORMED_PREFIX", "transformed/")  # Prefix for transformed data in S3

    try:
        # Step 1: Read raw data from S3
        print("Reading raw data from S3...")
        raw_data = read_from_s3(raw_bucket, raw_prefix)

        # Step 2: Transform the data
        print("Transforming data...")
        transformed_data = transform_data(raw_data)

        # Step 3: Write transformed data to S3
        print("Writing transformed data to S3...")
        write_to_s3(transformed_bucket, transformed_data, transformed_prefix)

        print("Data transformation completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise
