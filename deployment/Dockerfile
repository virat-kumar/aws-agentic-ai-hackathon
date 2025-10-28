FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for SageMaker
WORKDIR /opt/ml/code

# Copy requirements and install dependencies
COPY requirements-sagemaker.txt /opt/ml/code/
RUN pip install --no-cache-dir -r /opt/ml/code/requirements-sagemaker.txt

# Copy inference script
COPY inference.py /opt/ml/code/

# Set environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV SAGEMAKER_PROGRAM=inference.py

# Set the entrypoint
ENTRYPOINT ["python"]
