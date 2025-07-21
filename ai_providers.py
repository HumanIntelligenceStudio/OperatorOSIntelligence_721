"""
AI Providers - Integration with multiple AI services
Supports OpenAI, Anthropic, and other AI providers with intelligent routing
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
import anthropic
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AIProviderManager:
    """Manages multiple AI providers with intelligent routing"""
    
    def __init__(self):
        self.providers = {}
        self.usage_stats = {}
        
        # Initialize OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.providers['openai'] = OpenAI(api_key=openai_key)
            self.usage_stats['openai'] = {'requests': 0, 'tokens': 0}
            logger.info("OpenAI provider initialized")
        
        # Initialize Anthropic
        # The newest Anthropic model is "claude-sonnet-4-20250514", not "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022" nor "claude-3-sonnet-20240229". 
        # If the user doesn't specify a model, always prefer using "claude-sonnet-4-20250514" as it is the latest model.
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.providers['anthropic'] = Anthropic(api_key=anthropic_key)
            self.usage_stats['anthropic'] = {'requests': 0, 'tokens': 0}
            logger.info("Anthropic provider initialized")
        
        # Default models
        self.default_models = {
            'openai': 'gpt-4o',  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            'anthropic': 'claude-sonnet-4-20250514'
        }
    
    def get_completion(self, prompt: str, provider: str = 'auto', 
                      model: str = None, system_prompt: str = None,
                      max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Get completion from specified AI provider"""
        
        if provider == 'auto':
            provider = self._select_optimal_provider(prompt)
        
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        if model is None:
            model = self.default_models.get(provider)
        
        try:
            if provider == 'openai':
                return self._get_openai_completion(
                    prompt, model, system_prompt, max_tokens, temperature
                )
            elif provider == 'anthropic':
                return self._get_anthropic_completion(
                    prompt, model, system_prompt, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        except Exception as e:
            logger.error(f"Error getting completion from {provider}: {e}")
            # Fallback to other provider
            if provider == 'openai' and 'anthropic' in self.providers:
                return self._get_anthropic_completion(
                    prompt, self.default_models['anthropic'], 
                    system_prompt, max_tokens, temperature
                )
            elif provider == 'anthropic' and 'openai' in self.providers:
                return self._get_openai_completion(
                    prompt, self.default_models['openai'],
                    system_prompt, max_tokens, temperature
                )
            else:
                raise e
    
    def _get_openai_completion(self, prompt: str, model: str, 
                              system_prompt: str, max_tokens: int, 
                              temperature: float) -> str:
        """Get completion from OpenAI"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.providers['openai'].chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        self.usage_stats['openai']['requests'] += 1
        if hasattr(response, 'usage'):
            self.usage_stats['openai']['tokens'] += response.usage.total_tokens
        
        return response.choices[0].message.content
    
    def _get_anthropic_completion(self, prompt: str, model: str,
                                 system_prompt: str, max_tokens: int,
                                 temperature: float) -> str:
        """Get completion from Anthropic"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
        else:
            full_prompt = f"Human: {prompt}\n\nAssistant:"
        
        response = self.providers['anthropic'].messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        self.usage_stats['anthropic']['requests'] += 1
        if hasattr(response, 'usage'):
            self.usage_stats['anthropic']['tokens'] += response.usage.input_tokens + response.usage.output_tokens
        
        return response.content[0].text
    
    def _select_optimal_provider(self, prompt: str) -> str:
        """Select optimal provider based on prompt characteristics"""
        # Simple heuristics for provider selection
        prompt_lower = prompt.lower()
        
        # Anthropic is better for analysis and reasoning
        if any(word in prompt_lower for word in [
            'analyze', 'analysis', 'reasoning', 'logic', 'critical thinking',
            'medical', 'healthcare', 'clinical', 'diagnosis'
        ]):
            if 'anthropic' in self.providers:
                return 'anthropic'
        
        # OpenAI is better for creative tasks and general assistance
        if any(word in prompt_lower for word in [
            'create', 'generate', 'write', 'creative', 'story', 'code'
        ]):
            if 'openai' in self.providers:
                return 'openai'
        
        # Default to the first available provider
        if 'openai' in self.providers:
            return 'openai'
        elif 'anthropic' in self.providers:
            return 'anthropic'
        else:
            raise ValueError("No AI providers available")
    
    def get_structured_response(self, prompt: str, schema: Dict,
                               provider: str = 'auto') -> Dict:
        """Get structured response from AI provider"""
        schema_prompt = f"""
        Please respond with a JSON object that matches this schema:
        {json.dumps(schema, indent=2)}
        
        Query: {prompt}
        
        Response (JSON only):
        """
        
        response = self.get_completion(
            schema_prompt, 
            provider=provider,
            temperature=0.3  # Lower temperature for structured responses
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("Could not parse structured response")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics for all providers"""
        return self.usage_stats.copy()
    
    def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health = {}
        
        for provider_name, provider in self.providers.items():
            try:
                # Simple test query
                if provider_name == 'openai':
                    response = provider.chat.completions.create(
                        model=self.default_models[provider_name],
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5
                    )
                    health[provider_name] = bool(response.choices[0].message.content)
                
                elif provider_name == 'anthropic':
                    response = provider.messages.create(
                        model=self.default_models[provider_name],
                        max_tokens=5,
                        messages=[{"role": "user", "content": "Hello"}]
                    )
                    health[provider_name] = bool(response.content[0].text)
                
            except Exception as e:
                logger.error(f"Health check failed for {provider_name}: {e}")
                health[provider_name] = False
        
        return health
