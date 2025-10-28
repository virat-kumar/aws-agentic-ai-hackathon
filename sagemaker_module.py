"""
SageMaker Module for Dallas Student Navigator
Replaces langchain_module.py to call SageMaker endpoint instead
"""
import os
import json
import boto3
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class SageMakerClient:
    """Client to call SageMaker endpoint for LangChain processing"""
    
    def __init__(self, endpoint_name: str = None):
        self.endpoint_name = endpoint_name or os.getenv('SAGEMAKER_ENDPOINT_NAME', 'langchain-endpoint')
        self.client = boto3.client('sagemaker-runtime', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    
    def invoke(self, query: str, category: str = "General") -> str:
        """Invoke SageMaker endpoint with query"""
        try:
            # Prepare payload
            payload = {
                "query": query,
                "category": category
            }
            
            # Invoke endpoint
            response = self.client.invoke_endpoint(
                EndpointName=self.endpoint_name,
                ContentType='application/json',
                Accept='application/json',
                Body=json.dumps(payload)
            )
            
            # Parse response
            result = json.loads(response['Body'].read().decode())
            
            # Check for errors
            if result.get('status') == 'error':
                return f"I encountered an error: {result.get('error', 'Unknown error')}"
            
            # Return response
            return result.get('response', 'No response generated')
            
        except Exception as e:
            print(f"Error calling SageMaker endpoint: {e}")
            return f"Error calling SageMaker endpoint: {str(e)}"


class SageMakerAgent:
    """Simplified agent that uses SageMaker instead of local LangChain"""
    
    def __init__(self):
        self.sagemaker = SageMakerClient()
        self.validator = self._load_validator()
    
    def _load_validator(self):
        """Load query validator (keep validation logic local)"""
        from langchain_module import StudentQueryValidator
        return StudentQueryValidator()
    
    def search_and_respond(self, query: str, conversation_history: List[Dict] = None) -> str:
        """Search and respond using SageMaker endpoint"""
        # Validate query
        validation = self.validator.is_relevant_query(query)
        
        if not validation['is_relevant']:
            return (
                "I'm here to help international students in Dallas with:\n\n"
                "🏠 **Housing** - Finding apartments, rooms, and accommodations\n"
                "🛒 **Groceries** - Locating stores and shopping advice\n"
                "🚌 **Transportation** - Public transit, rideshare, and routes\n"
                "⚖️ **Legal Info** - Visa, work permits, and immigration\n"
                "🌍 **Cultural Tips** - Local customs and community\n"
                "💰 **Financial** - Financial advice, budgeting, and payments\n\n"
                "Could you ask something related to these topics?"
            )
        
        # Get category
        categories = validation['matched_categories']
        category = categories[0] if categories else "General"
        
        # Call SageMaker endpoint
        response = self.sagemaker.invoke(query, category)
        
        return response


# Singleton instance
_sagemaker_agent = None

def get_sagemaker_agent():
    """Get or create the SageMaker agent instance"""
    global _sagemaker_agent
    if _sagemaker_agent is None:
        _sagemaker_agent = SageMakerAgent()
    return _sagemaker_agent
