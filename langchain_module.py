"""
LangChain Module for Dallas Student Navigator
Handles web search and query validation for international students using Azure OpenAI
"""

import os
from typing import List, Dict
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()


class StudentQueryValidator:
    """Validates user queries to ensure they're relevant to international student topics"""
    
    ALLOWED_CATEGORIES = [
        "Housing",
        "Groceries", 
        "Transportation",
        "Legal Info",
        "Cultural Tips"
    ]
    
    CATEGORY_KEYWORDS = {
        "Housing": ["apartment", "housing", "rent", "room", "accommodation", "hostel", "dorm", "lease", "landlord", "flat"],
        "Groceries": ["grocery", "food", "market", "store", "shopping", "supermarket", "ingredients", "restaurant"],
        "Transportation": ["bus", "train", "metro", "transport", "uber", "lyft", "taxi", "driving", "route", "transit"],
        "Legal Info": ["visa", "work permit", "legal", "immigration", "document", "status", "f1", "f2", "j1"],
        "Cultural Tips": ["culture", "etiquette", "custom", "tradition", "festival", "holiday", "local", "community"]
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
        student_terms = ["student", "international", "study", "university", "dallas", "texas"]
        has_student_context = any(term in query_lower for term in student_terms)
        
        is_relevant = (
            len(matched_categories) > 0 or 
            has_student_context or
            "dallas" in query_lower or
            "texas" in query_lower
        )
        
        return {
            'is_relevant': is_relevant,
            'matched_categories': matched_categories,
            'relevance_score': relevance_score,
            'has_student_context': has_student_context
        }


class WebSearchAgent:
    """Agent that performs web search and uses Azure OpenAI to synthesize responses"""
    
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
        self.validator = StudentQueryValidator()
        self.llm = self._init_azure_llm()
    
    def _init_azure_llm(self):
        """Initialize Azure OpenAI LLM"""
        try:
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            azure_api_key = os.getenv('AZURE_OPENAI_API_KEY')
            azure_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
            model_name = os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o')
            
            if azure_endpoint and azure_api_key:
                llm = AzureChatOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=azure_api_key,
                    api_version=azure_api_version,
                    model=model_name,
                    temperature=0.7
                )
                return llm
            else:
                print("Warning: Azure OpenAI credentials not found. Using web search only.")
                return None
        except Exception as e:
            print(f"Error initializing Azure OpenAI: {e}")
            return None
        
    def search_and_respond(self, query: str, conversation_history: List[Dict] = None) -> str:
        """
        Perform web search and use Azure OpenAI to synthesize responses
        
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
                "🌍 **Cultural Tips** - Local customs and community\n\n"
                "Could you ask something related to these topics?"
            )
        
        # If relevant, perform search and synthesize with LLM
        try:
            # Add context for better search results
            search_query = f"international students Dallas Texas {query}"
            search_results = self.search.run(search_query)
            
            # Use Azure OpenAI to synthesize the response if available
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

                # Generate response using Azure OpenAI
                messages_langchain = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages_langchain)
                generated_text = response.content if hasattr(response, 'content') else str(response)
                
                return f"{generated_text}\n\n---\n*Sources: Web search results*"
            
            else:
                # Fallback to simple response if LLM not available
                categories = validation['matched_categories']
                category_str = ", ".join(categories) if categories else "General"
                
                response = f"**Category**: {category_str}\n\n"
                response += f"**Question**: {query}\n\n"
                response += "**Answer**:\n\n"
                response += search_results
                response += "\n\n---\n*Search results from DuckDuckGo*"
                
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

