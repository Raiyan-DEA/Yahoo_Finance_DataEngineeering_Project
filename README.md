**Project Overview:**

 This project focuses on building a robust and scalable Data Engineering pipeline to ingest, transform, and analyze stock market data from the Yahoo Finance API. The primary goal is to create a system that gathers real-time stock information for various companies, processes it to generate meaningful insights, and stores it in a data warehouse for further analysis. By implementing this pipeline, we aim to enable businesses and analysts to monitor stock trends, compare company performance, and make data-driven investment decisions. The project also ensures data integrity and reliability and incorporates a failure notification mechanism for monitoring the pipeline.

 **Architechture Diagram**
 
 ![end_to_end_project drawio](https://github.com/user-attachments/assets/63ccb2ae-26ca-406b-a5e8-3d899be8fa7d)

**Architecture:**

 The pipeline begins with AWS Batch, which orchestrates the ingestion process by running a Python script to fetch stock data from the Yahoo Finance API. The raw data is stored in Amazon S3 in a structured format. Within the same AWS Batch workflow, the pipeline includes a transformation step to clean and enrich the data, ensuring it meets analytical needs. The transformed data is saved into a designated folder in S3 which can be used for analytical Needs. A failure notification mechanism using CloudWatch and SNS ensures pipeline reliability by alerting stakeholders in case of errors, making the system resilient and user-friendly.
