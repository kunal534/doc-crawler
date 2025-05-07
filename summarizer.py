from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict, List
import logging
import tiktoken
import re
load_dotenv()
logging.basicConfig(level=logging.INFO)

class DescriptionGenerator:
    def __init__(self, model="gpt-3.5-turbo"):
        api_key = os.getenv("OPENAI_API_KEY")
        logging.info(f"Loaded API key: {api_key[:10]}...")  # Print first 10 chars
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.context = []
        self.encoder = tiktoken.encoding_for_model(model)
    
    def add_context(self, page_title: str, url: str):
        """Add page context for better summarization"""
        self.context.append(f"Page: {page_title} ({url})")
        if len(self.context) > 5:
            self.context.pop(0)
    
    def generate_description(self, content: str) -> str:
        """Generate concise module description"""
        try:
            if not content.strip():
                return "No description available"
            
            # Clean content first
            content = self._preprocess_content(content)
            
            # Truncate content to fit token limit
            max_tokens = 3000
            content_tokens = self.encoder.encode(content)
            if len(content_tokens) > max_tokens:
                content = self.encoder.decode(content_tokens[:max_tokens])
            
            prompt = (
                "You are a technical documentation analyzer. "
                "Generate a concise 1-2 sentence description summarizing "
                "the key purpose and functionality of this documentation section.\n\n"
                f"Context:\n{'\n'.join(self.context)}\n\n"
                f"Content:\n{content}\n\n"
                "Description:"
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            return self._postprocess_description(response.choices[0].message.content.strip())
        except Exception as e:
            logging.error(f"Error generating description: {e}")
            return self._fallback_description(content)
    
    def _preprocess_content(self, text: str) -> str:
        """Clean content before summarization"""
        text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
        text = re.sub(r'(\n\n)+', '\n\n', text)  # Normalize newlines
        text = text.replace('\u00a0', ' ')  # Replace non-breaking spaces
        return text.strip()
    
    def _postprocess_description(self, text: str) -> str:
        """Clean up generated description"""
        text = re.sub(r'^Description:\s*', '', text)  # Remove prefix if present
        text = text.replace('"', "'")  # Normalize quotes
        if not text.endswith('.'):
            text += '.'  # Ensure proper sentence ending
        return text
    
    def _fallback_description(self, content: str) -> str:
        """Generate description without API"""
        sentences = [s.strip() for s in re.split(r'[.!?]', content) if s.strip()]
        if sentences:
            # Take first meaningful sentence
            for sentence in sentences:
                if len(sentence.split()) > 5 and not self._is_citation(sentence):
                    return sentence[:200] + ('...' if len(sentence) > 200 else '')
        return "Description not available"
    
    def _is_citation(self, text: str) -> bool:
        """Check if text is citation/reference"""
        return bool(re.search(r'\[\d+\]|\([A-Za-z]+,?\s*\d{4}\)', text))