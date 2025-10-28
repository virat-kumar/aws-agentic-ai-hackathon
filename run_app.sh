#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run Streamlit app on all interfaces
streamlit run app.py --server.address 0.0.0.0 --server.port 8501

