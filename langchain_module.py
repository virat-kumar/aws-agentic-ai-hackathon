"""
LangChain Module for Dallas Student Navigator
Handles web search and query validation for international students using AWS Bedrock
"""

import os
import re
from typing import List, Dict
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage, HumanMessage
import boto3

load_dotenv()


class StudentQueryValidator:
    """Validates user queries to ensure they're relevant to international student topics"""
    
    ALLOWED_CATEGORIES = [
        "Housing",
        "Groceries", 
        "Transportation",
        "Legal Info",
        "Cultural Tips",
        "Financial"
    ]
    
    CATEGORY_KEYWORDS = {
        "Housing": ["apartment", "housing", "rent", "room", "accommodation", "hostel", "dorm", "lease", "landlord", "flat", "rental", "living", "stay", "residence"],
        "Groceries": ["grocery", "food", "market", "store", "shopping", "supermarket", "ingredients", "restaurant", "eat", "buy", "purchase", "shop"],
        "Transportation": ["bus", "train", "metro", "transport", "uber", "lyft", "taxi", "driving", "route", "transit", "get around", "commute", "travel", "public transit", "dart"],
        "Legal Info": ["visa", "work permit", "legal", "immigration", "document", "status", "f1", "f2", "j1", "cpt", "opt", "curricular practical training", "optional practical training", "application", "apply", "process", "authorization", "sevis", "ds-160", "i-20", "work authorization", "permit", "international student", "advice", "guide"],
        "Cultural Tips": ["culture", "etiquette", "custom", "tradition", "festival", "holiday", "local", "community", "social", "people", "make friends", "events"],
        "Financial": ["financial", "money", "bank", "budget", "advice", "finance", "payment", "tuition", "scholarship", "funding", "cost", "price"]
    }
    
    def is_relevant_query(self, query: str) -> Dict[str, any]:
        """
        Check if the query is relevant to international student topics
        
        Returns:
            Dict with 'is_relevant' (bool) and 'matched_categories' (List[str])
        """
        query_lower = query.lower()
        
        matched_categories = []
        relevance_score = 0
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if category not in matched_categories:
                        matched_categories.append(category)
                    relevance_score += 1
                    break
        
        # Check if query contains student-related terms
        student_terms = ["student", "international", "study", "university", "dallas", "texas", "apply", "application", "process", "help", "need"]
        has_student_context = any(term in query_lower for term in student_terms)
        
        # Also check for question words that indicate it might be relevant
        question_indicators = ["how", "what", "where", "when", "why", "can i", "do i", "should i", "need to", "can you", "give me"]
        has_question_format = any(term in query_lower for term in question_indicators)
        
        # Be very permissive - allow all queries that seem like legitimate questions
        # Only reject obvious irrelevant queries (very short or spam-like)
        is_clearly_irrelevant = (
            len(query.strip()) < 3 or
            query_lower in ["hi", "hello", "hey"]
        )
        
        is_relevant = not is_clearly_irrelevant and (
            len(matched_categories) > 0 or 
            has_student_context or
            has_question_format or
            "dallas" in query_lower or
            "texas" in query_lower or
            len(query.split()) >= 2  # Allow multi-word queries
        )
        
        return {
            'is_relevant': is_relevant,
            'matched_categories': matched_categories,
            'relevance_score': relevance_score,
            'has_student_context': has_student_context
        }


class WebSearchAgent:
    """Agent that performs web search and uses AWS Bedrock LLM to synthesize responses"""
    
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
        self.validator = StudentQueryValidator()
        self.llm = self._init_bedrock_llm()
    
    def _init_bedrock_llm(self):
        """Initialize AWS Bedrock LLM"""
        try:
            # Get AWS credentials from environment
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_REGION', 'us-east-1')
            model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            
            if aws_access_key and aws_secret_key:
                # Create boto3 client with credentials
                bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                
                # Initialize Bedrock LLM with reasoning disabled
                llm = ChatBedrock(
                    client=bedrock_client,
                    model_id=model_id,
                    temperature=0.7,
                    model_kwargs={
                        "trace": False,
                        "return_thoughts": False,
                        "enableTrace": False
                    }
                )
                print(f"Successfully initialized AWS Bedrock with model: {model_id}")
                return llm
            else:
                print("Warning: AWS Bedrock credentials not found. Using web search only.")
                return None
        except Exception as e:
            print(f"Error initializing AWS Bedrock: {e}")
            return None
    
    def _extract_sources(self, search_results: str) -> List[str]:
        """Extract URLs and sources from search results"""
        sources = []
        
        # Try to find URLs in the search results
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, search_results)
        
        # Get unique URLs
        seen = set()
        for url in urls:
            # Clean up URL (remove trailing punctuation)
            url = url.rstrip('.,;)')
            if url not in seen:
                seen.add(url)
                sources.append(url)
        
        # Limit to top 5 sources
        return sources[:5]
    
    def _remove_thinking_process(self, text: str) -> str:
        """Remove thinking process and internal notes from response"""
        # Common patterns that indicate thinking process - more comprehensive list
        thinking_patterns = [
            r'(?i)^we (must|need to|should).*$',
            r'(?i)^let\'s.*$',
            r'(?i)^let me.*$',
            r'(?i)^i (need to|should|will).*$',
            r'(?i)^internal note.*$',
            r'(?i)^thinking:.*$',
            r'(?i)^reasoning:.*$',
            r'(?i)^there\'s (only )?one.*result.*snippet.*$',
            r'(?i)^provide (practical )?advice:.*$',
            r'(?i)^also mention.*$',
            r'(?i)^provide tips? about.*$',
            r'(?i)^provide friendly tone.*$',
            r'(?i)^below are.*$',
            r'(?i)^instructions? (to|for).*$',
            r'(?i)^use \[1\].*snippet.*$',
            r'(?i)^reminder:.*$',
            r'(?i)^concluding sentence.*$',
            r'(?i)^a concluding.*$',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        skip_count = 0  # Track how many lines to skip
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line matches thinking patterns
            is_thinking = False
            for pattern in thinking_patterns:
                if re.search(pattern, line.strip()):
                    is_thinking = True
                    break
            
            if is_thinking:
                # Skip this line and the next few lines (bullets or follow-ups)
                skip_count = 10  # Skip up to 10 lines after thinking
                i += 1
                continue
            
            # If we're in skip mode, skip this line
            if skip_count > 0:
                # If we hit a blank line or heading, stop skipping
                if line.strip() == '' or re.match(r'^#+\s+', line):
                    skip_count = 0
                else:
                    skip_count -= 1
                    i += 1
                    continue
            
            cleaned_lines.append(line)
            i += 1
        
        result = '\n'.join(cleaned_lines).strip()
        
        # Additional cleanup: remove paragraphs that start with "We need to answer"
        result = re.sub(r'We need to answer.*?\.\s*', '', result, flags=re.DOTALL | re.IGNORECASE)
        
        return result
        
    def search_and_respond(self, query: str, conversation_history: List[Dict] = None) -> str:
        """
        Perform web search and use AWS Bedrock LLM to synthesize responses
        
        Args:
            query: User's question
            conversation_history: Previous conversation messages
            
        Returns:
            Response string with synthesized search results
        """
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
        
        # If relevant, perform search and synthesize with LLM
        try:
            # Add context for better search results
            search_query = f"international students Dallas Texas {query}"
            search_results = self.search.run(search_query)
            
            # Use AWS Bedrock LLM to synthesize the response if available
            if self.llm:
                categories = validation['matched_categories']
                category_str = ", ".join(categories) if categories else "General"
                
                # Build prompt for LLM
                system_prompt = f"""You are a helpful assistant for international students in Dallas, Texas.
You help with: Housing, Groceries, Transportation, Legal Info, and Cultural Tips.

The user asked about: {query}
Category: {category_str}

Use the following search results to provide a comprehensive, accurate answer.
Be friendly, empathetic, and provide practical, actionable advice.
Focus on information relevant to international students."""

                prompt = f"""{system_prompt}

Search Results:
{search_results}

User Question: {query}

Provide a helpful answer based on the search results above."""

                # Extract URLs from search results for citations
                sources = self._extract_sources(search_results)
                
                # Add instruction for inline citations
                system_prompt_with_citations = f"""You are a helpful assistant for international students in Dallas, Texas.
You help with: Housing, Groceries, Transportation, Legal Info, and Cultural Tips.

The user asked about: {query}
Category: {category_str}

Use the following search results to provide a comprehensive, accurate answer.
Be friendly, empathetic, and provide practical, actionable advice.
Focus on information relevant to international students.

IMPORTANT: When mentioning specific information from the search results, add inline citations like [1], [2], etc. in your response.

CRITICAL RULES:
1. ONLY output the final answer to the user. Do NOT include thinking, planning, notes, or instructions to yourself.
2. Do NOT write phrases like "We need to answer...", "There's only one result...", "Provide advice...", "Also mention...", etc.
3. Do NOT include backticks or code formatting around URLs in your response.
4. Start directly with the answer - be concise and useful.
5. Do not explain what you're about to do - just do it."""
                
                prompt_with_citations = f"""Search Results:
{search_results}

User Question: {query}

Provide a helpful answer based on the search results above with inline citations [1], [2], etc.

Remember: Only provide the final answer. Do not include any thinking process, internal notes, or reasoning in your response."""

                # Generate response using AWS Bedrock LLM
                messages_langchain = [
                    SystemMessage(content=system_prompt_with_citations),
                    HumanMessage(content=prompt_with_citations)
                ]
                
                response = self.llm.invoke(messages_langchain)
                generated_text = response.content if hasattr(response, 'content') else str(response)
                
                # Post-process to remove thinking process and internal notes
                generated_text = self._remove_thinking_process(generated_text)
                
                # Clean up backticks around URLs - convert `http://url` to plain URL
                generated_text = re.sub(r'`(https?://[^`]+)`', r'\1', generated_text)
                
                # Append sources if available
                if sources:
                    generated_text += "\n\n**References:**\n"
                    for idx, source in enumerate(sources, 1):
                        # Format as markdown link - the link text is the URL itself
                        # This will be converted to HTML with target="_blank" by app.py
                        link_display = source if len(source) < 80 else source[:77] + "..."
                        generated_text += f"[{idx}] [{link_display}]({source})\n"
                
                return generated_text
            
            else:
                # Fallback to simple response if LLM not available
                categories = validation['matched_categories']
                category_str = ", ".join(categories) if categories else "General"
                
                response = f"**Category**: {category_str}\n\n"
                response += f"**Question**: {query}\n\n"
                response += "**Answer**:\n\n"
                response += search_results
                
                return response
            
        except Exception as e:
            return f"I encountered an error while processing your request. Please try again. Error: {str(e)}"
    
    def get_matched_categories(self, query: str) -> List[str]:
        """Get categories that match the query"""
        validation = self.validator.is_relevant_query(query)
        return validation['matched_categories']


# Singleton instance
_web_search_agent = None

def get_web_search_agent():
    """Get or create the web search agent instance"""
    global _web_search_agent
    if _web_search_agent is None:
        _web_search_agent = WebSearchAgent()
    return _web_search_agent


if __name__ == "__main__":
    # Test the module
    agent = get_web_search_agent()
    
    test_queries = [
        "Where can I find affordable housing near UT Dallas?",
        "What are the best Asian grocery stores in Dallas?",
        "How do I apply for a work permit on F1 visa?",
        "What is the weather today?"
    ]
    
    print("Testing Web Search Agent:\n")
    for query in test_queries:
        print(f"Query: {query}")
        result = agent.search_and_respond(query)
        print(f"Result: {result[:200]}...")
        print("-" * 80)

