"""
Service for redacting sensitive information from transcripts
"""
import re
from typing import List, Tuple
from app.config import settings


class RedactionService:
    """Service for detecting and redacting sensitive data"""
    
    def __init__(self):
        # Common patterns for sensitive information
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            "api_key": r'[Aa][Pp][Ii][_-]?[Kk][Ee][Yy][:\s=]+[\w\-]{20,}',
            "password": r'[Pp]assword[:\s=]+[\w\-!@#$%^&*()]{6,}',
            "token": r'[Tt]oken[:\s=]+[\w\-]{20,}',
        }
    
    def redact(self, text: str) -> Tuple[str, List[str]]:
        """
        Redact sensitive information from text
        
        Args:
            text: Input text to redact
        
        Returns:
            Tuple of (redacted_text, list_of_redacted_items)
        """
        if not settings.ENABLE_DATA_REDACTION:
            return text, []
        
        redacted_text = text
        redacted_items = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                redacted_items.append({
                    "type": pattern_name,
                    "value": match.group(0),
                    "position": match.start()
                })
                redacted_text = redacted_text.replace(
                    match.group(0),
                    f"[REDACTED_{pattern_name.upper()}]"
                )
        
        return redacted_text, redacted_items
    
    def check_sensitivity(self, text: str) -> bool:
        """Check if text contains potentially sensitive information"""
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        return False


# Singleton instance
redaction_service = RedactionService()

