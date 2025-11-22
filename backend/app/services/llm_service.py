"""
LLM service for extracting action items from transcripts
Supports Groq API, OpenAI API (optional), and local models via Ollama
"""
import json
import re
from typing import List, Dict, Any, Optional
from app.config import settings
from groq import Groq
import os

# Optional OpenAI support for backward compatibility
try:
    from openai import OpenAI as OpenAIClient
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMService:
    """Service for extracting action items using LLM (Groq by default)"""
    
    def __init__(self):
        self.client = None
        self.model = settings.LLM_MODEL
        self.provider = None
        
        if settings.GROQ_API_KEY:
            # Use Groq API (recommended)
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.provider = "groq"
            # Default Groq models if not specified
            if not settings.LLM_MODEL or settings.LLM_MODEL.startswith("gpt-"):
                self.model = "llama-3.1-70b-versatile"
        elif settings.OPENAI_API_KEY and OPENAI_AVAILABLE:
            # Fallback to OpenAI API
            self.client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
            self.provider = "openai"
            self.model = settings.LLM_MODEL or "gpt-4o-mini"
        elif settings.ENABLE_LOCAL_MODE:
            # Try to use local Ollama if available
            if OPENAI_AVAILABLE:
                self.client = OpenAIClient(
                    base_url="http://localhost:11434/v1",
                    api_key="ollama"  # Not used but required
                )
                self.provider = "ollama"
                self.model = "llama3.2"  # Default local model
            else:
                raise ValueError("OpenAI library required for local Ollama mode. Install: pip install openai")
        else:
            raise ValueError("LLM service requires GROQ_API_KEY, OPENAI_API_KEY, or ENABLE_LOCAL_MODE")
    
    def extract_action_items(self, transcript: str) -> Dict[str, Any]:
        """
        Extract action items from meeting transcript
        
        Args:
            transcript: Meeting transcript text
        
        Returns:
            Dictionary with extracted tasks in the required format
        """
        prompt = self._build_extraction_prompt(transcript)
        
        try:
            if self.client:
                # Prepare request parameters
                request_params = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an expert at analyzing meeting transcripts and extracting action items.
                            Extract all action items, tasks, and to-dos mentioned in the meeting.
                            For each item, identify:
                            - The task description
                            - The responsible person (if mentioned)
                            - The due date or deadline (if mentioned)
                            - Priority level (low, medium, high, critical)
                            - Your confidence in the extraction (0.0 to 1.0)
                            
                            Return only valid JSON in this exact format:
                            {
                                "tasks": [
                                    {
                                        "description": "...",
                                        "owner": "...",
                                        "deadline": "YYYY-MM-DD" or null,
                                        "priority": "low|medium|high|critical",
                                        "confidence": 0.92
                                    }
                                ]
                            }
                            
                            If no action items are found, return: {"tasks": []}
                            Be thorough but accurate. Only extract clear action items."""
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                }
                
                # Groq and OpenAI both support JSON mode, but syntax differs slightly
                if self.provider == "groq":
                    # Groq uses response_format
                    request_params["response_format"] = {"type": "json_object"}
                elif self.provider == "openai":
                    # OpenAI uses response_format
                    request_params["response_format"] = {"type": "json_object"}
                # Ollama doesn't support structured output the same way
                
                response = self.client.chat.completions.create(**request_params)
                
                content = response.choices[0].message.content
                result = json.loads(content)
                return result
            else:
                # Fallback: Simple regex-based extraction
                return self._extract_simple(transcript)
        
        except Exception as e:
            print(f"Error extracting action items with {self.provider}: {e}")
            # Fallback to simple extraction
            return self._extract_simple(transcript)
    
    def _build_extraction_prompt(self, transcript: str) -> str:
        """Build the prompt for action item extraction"""
        return f"""Analyze the following meeting transcript and extract all action items:

{transcript}

Extract all tasks, action items, and to-dos. For each item, identify the responsible person (if mentioned), deadline (if mentioned), and priority level."""
    
    def _extract_simple(self, transcript: str) -> Dict[str, Any]:
        """Fallback simple extraction using regex patterns"""
        tasks = []
        
        # Look for common patterns
        action_patterns = [
            r"(?:need to|will|should|must|have to)\s+([^.!?]+(?:\.|!|\?))",
            r"action item[:\s]+([^.!?]+(?:\.|!|\?))",
            r"todo[:\s]+([^.!?]+(?:\.|!|\?))",
            r"task[:\s]+([^.!?]+(?:\.|!|\?))",
        ]
        
        for pattern in action_patterns:
            matches = re.finditer(pattern, transcript, re.IGNORECASE)
            for match in matches:
                description = match.group(1).strip()
                if len(description) > 10:  # Filter out too short matches
                    tasks.append({
                        "description": description,
                        "owner": None,
                        "deadline": None,
                        "priority": "medium",
                        "confidence": 0.5
                    })
        
        return {"tasks": tasks[:10]}  # Limit to 10 tasks


# Singleton instance
llm_service = LLMService() if (settings.GROQ_API_KEY or settings.OPENAI_API_KEY or settings.ENABLE_LOCAL_MODE) else None

