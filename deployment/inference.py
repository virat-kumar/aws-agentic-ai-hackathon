"""
SageMaker Inference Script for LangChain Module
This script runs in a SageMaker endpoint and handles LangChain processing
"""
import os
import json
import sys
from typing import Dict, Any

# Add the parent directory to path to import langchain_module
sys.path.insert(0, '/opt/ml/code')

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage
import boto3
import re

class LangChainEndpointHandler:
    """Handler for SageMaker inference requests"""
    
    def __init__(self):
        """Initialize the handler with LangChain components"""
        self.search = DuckDuckGoSearchRun()
        self.llm = self._init_bedrock_llm()
    
    def _init_bedrock_llm(self):
        """Initialize AWS Bedrock LLM"""
        try:
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
            
            # Use SageMaker execution role for Bedrock access
            bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=aws_region
            )
            
            llm = ChatBedrock(
                client=bedrock_client,
                model_id=model_id,
                temperature=0.7
            )
            print(f"Successfully initialized AWS Bedrock with model: {model_id}")
            return llm
        except Exception as e:
            print(f"Error initializing AWS Bedrock: {e}")
            return None
    
    def _extract_sources(self, search_results: str):
        """Extract URLs from search results"""
        sources = []
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, search_results)
        
        seen = set()
        for url in urls:
            url = url.rstrip('.,;)')
            if url not in seen and len(sources) < 5:
                seen.add(url)
                sources.append(url)
        return sources
    
    def _remove_thinking_process(self, text: str) -> str:
        """Remove thinking process from response"""
        thinking_patterns = [
            r'(?i)^we (must|need to|should).*$',
            r'(?i)^let\'s.*$',
            r'(?i)^there\'s (only )?one.*result.*$',
            r'(?i)^provide (practical )?advice:.*$',
            r'(?i)^instructions? (to|for).*$',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            is_thinking = False
            for pattern in thinking_patterns:
                if re.search(pattern, line.strip()):
                    is_thinking = True
                    break
            
            if not is_thinking:
                cleaned_lines.append(line)
        
        # Remove backticks around URLs
        result = '\n'.join(cleaned_lines).strip()
        result = re.sub(r'`(https?://[^`]+)`', r'\1', result)
        
        return result
    
    def process_query(self, query: str, category: str) -> Dict[str, Any]:
        """Process a user query and return response"""
        try:
            # Perform web search
            search_query = f"international students Dallas Texas {query}"
            search_results = self.search.run(search_query)
            
            # Extract sources
            sources = self._extract_sources(search_results)
            
            if self.llm:
                # Build system prompt
                system_prompt = f"""You are a helpful assistant for international students in Dallas, Texas.
Category: {category}

CRITICAL RULES:
1. ONLY output the final answer. Do NOT include thinking, planning, notes, or instructions.
2. Do NOT write phrases like "We need to answer...", "There's only one result...".
3. Start directly with the answer - be concise and useful.
4. When mentioning specific information, add inline citations like [1], [2], etc."""

                prompt = f"""Search Results:
{search_results}

User Question: {query}

Provide a helpful answer based on the search results above with inline citations [1], [2], etc."""

                # Generate response
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                generated_text = response.content if hasattr(response, 'content') else str(response)
                
                # Post-process
                generated_text = self._remove_thinking_process(generated_text)
                
                # Add references
                if sources:
                    generated_text += "\n\n**References:**\n"
                    for idx, source in enumerate(sources, 1):
                        link_display = source if len(source) < 80 else source[:77] + "..."
                        generated_text += f"[{idx}] [{link_display}]({source})\n"
                
                return {
                    "response": generated_text,
                    "sources": sources,
                    "status": "success"
                }
            else:
                return {
                    "response": search_results,
                    "sources": sources,
                    "status": "fallback"
                }
                
        except Exception as e:
            return {
                "response": f"I encountered an error: {str(e)}",
                "sources": [],
                "status": "error",
                "error": str(e)
            }


# Singleton handler
_handler = None

def model_fn(model_dir):
    """Load the model for SageMaker"""
    global _handler
    if _handler is None:
        _handler = LangChainEndpointHandler()
    return _handler

def input_fn(request_body, content_type='application/json'):
    """Parse input data"""
    if content_type == 'application/json':
        data = json.loads(request_body)
        return data
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    """Make predictions"""
    query = input_data.get('query', '')
    category = input_data.get('category', 'General')
    return model.process_query(query, category)

def output_fn(prediction, accept='application/json'):
    """Format output"""
    if accept == 'application/json':
        return json.dumps(prediction), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")
