# Base Python image
FROM python:3.8-slim

# Install necessary Python dependencies
RUN pip install boto3 requests

# Copy both scripts (ingestion and transformation)
COPY Data_Loading_script.py /app/Data_Loading_script.py
COPY transform_script.py /app/transform_script.py

# Set the working directory
WORKDIR /app

# Default command to execute both scripts sequentially
CMD ["sh", "-c", "python Data_Loading_script.py && python transform_script.py"]
