"""
Whisper service for speech-to-text conversion
Supports both local Whisper and OpenAI Whisper API
"""
import os
import whisper
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
from app.config import settings
import openai
from openai import OpenAI


class WhisperService:
    """Service for transcribing audio using Whisper"""
    
    def __init__(self):
        self.local_model = None
        self.use_local = settings.USE_LOCAL_WHISPER or settings.ENABLE_LOCAL_MODE
        
        if self.use_local:
            # Load local Whisper model
            model_name = settings.WHISPER_MODEL
            print(f"Loading local Whisper model: {model_name}")
            self.local_model = whisper.load_model(model_name)
        elif settings.OPENAI_API_KEY:
            # Use OpenAI Whisper API
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError(
                "Either USE_LOCAL_WHISPER must be True or OPENAI_API_KEY must be set"
            )
    
    def transcribe(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es')
            task: 'transcribe' or 'translate'
        
        Returns:
            Dictionary with transcript and metadata
        """
        if self.use_local:
            return self._transcribe_local(audio_file_path, language, task)
        else:
            return self._transcribe_api(audio_file_path, language, task)
    
    def _transcribe_local(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """Transcribe using local Whisper model"""
        if not self.local_model:
            raise RuntimeError("Local Whisper model not loaded")
        
        result = self.local_model.transcribe(
            audio_file_path,
            language=language,
            task=task,
            verbose=True
        )
        
        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", []),
            "full_result": result
        }
    
    def _transcribe_api(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API"""
        if not hasattr(self, 'client'):
            raise RuntimeError("OpenAI client not initialized")
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
        
        return {
            "text": transcript.text,
            "language": transcript.language if hasattr(transcript, 'language') else "unknown",
            "segments": getattr(transcript, 'segments', []),
            "full_result": transcript.dict() if hasattr(transcript, 'dict') else {}
        }


# Singleton instance
whisper_service = WhisperService() if settings.USE_LOCAL_WHISPER or settings.OPENAI_API_KEY else None

