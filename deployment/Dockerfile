FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /opt/ml/code

# Copy requirements and install dependencies
COPY requirements-sagemaker.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy inference script
COPY inference.py .

# Set environment variables
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# SageMaker requirements
ENV SAGEMAKER_PROGRAM=inference.py

# Run the entry point
CMD ["python", "inference.py"]
