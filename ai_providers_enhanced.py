"""
Enhanced AI Provider management with OpenAI Assistants API integration
Supports both traditional Chat Completions and persistent Assistant conversations
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Union, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
from openai import OpenAI

# The newest Anthropic model is "claude-sonnet-4-20250514", not "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022" nor "claude-3-sonnet-20240229". 
# If the user doesn't specify a model, always prefer using "claude-sonnet-4-20250514" as it is the latest model.
from anthropic import Anthropic

from app import db
from models import AssistantThread, AssistantRun, AssistantConfiguration

logger = logging.getLogger(__name__)

class AssistantMode(Enum):
    """Modes for AI interaction"""
    CHAT_COMPLETION = "chat_completion"
    ASSISTANT = "assistant"
    AUTO = "auto"  # Automatically choose based on context

class AssistantTools:
    """Available tools for OpenAI Assistants"""
    
    @staticmethod
    def get_tools_for_domain(domain: str) -> List[Dict[str, Any]]:
        """Get tools configuration for specific domain"""
        
        base_tools = [
            {"type": "code_interpreter"}
        ]
        
        if domain == "healthcare":
            return base_tools + [
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "get_medical_information",
                        "description": "Get medical information and drug interactions",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Medical query"},
                                "drug_name": {"type": "string", "description": "Drug name for interaction check"}
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]
        
        elif domain == "financial":
            return base_tools + [
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "get_market_data",
                        "description": "Get real-time market data and financial analysis",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {"type": "string", "description": "Stock symbol"},
                                "analysis_type": {"type": "string", "enum": ["price", "fundamentals", "technical", "news"]}
                            },
                            "required": ["symbol", "analysis_type"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "calculate_financial_metrics",
                        "description": "Calculate financial ratios and investment metrics",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "calculation_type": {"type": "string", "enum": ["roi", "npv", "irr", "compound_interest"]},
                                "parameters": {"type": "object", "description": "Calculation parameters"}
                            },
                            "required": ["calculation_type", "parameters"]
                        }
                    }
                }
            ]
        
        elif domain == "sports":
            return base_tools + [
                {
                    "type": "function",
                    "function": {
                        "name": "get_sports_data",
                        "description": "Get sports statistics and betting information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "sport": {"type": "string", "description": "Sport type"},
                                "team": {"type": "string", "description": "Team name"},
                                "data_type": {"type": "string", "enum": ["stats", "odds", "schedule", "news"]}
                            },
                            "required": ["sport", "data_type"]
                        }
                    }
                }
            ]
        
        elif domain == "business":
            return base_tools + [
                {"type": "file_search"},
                {
                    "type": "function",
                    "function": {
                        "name": "business_analytics",
                        "description": "Perform business analysis and automation tasks",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "analysis_type": {"type": "string", "enum": ["workflow", "efficiency", "roi", "market_analysis"]},
                                "data": {"type": "object", "description": "Business data for analysis"}
                            },
                            "required": ["analysis_type", "data"]
                        }
                    }
                }
            ]
        
        else:  # general
            return base_tools

class EnhancedAIProviderManager:
    """Enhanced AI Provider Manager with OpenAI Assistants API support"""
    
    def __init__(self):
        self.providers = {}
        self.usage_stats = {}
        self.assistants = {}  # Domain -> Assistant ID mapping
        
        # Initialize OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.providers['openai'] = OpenAI(api_key=openai_key)
            self.usage_stats['openai'] = {'requests': 0, 'tokens': 0, 'assistant_runs': 0}
            logger.info("OpenAI provider initialized with Assistants API support")
        
        # Initialize Anthropic
        # The newest Anthropic model is "claude-sonnet-4-20250514"
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.providers['anthropic'] = Anthropic(api_key=anthropic_key)
            self.usage_stats['anthropic'] = {'requests': 0, 'tokens': 0}
            logger.info("Anthropic provider initialized")
        
        # Default models
        self.default_models = {
            'openai': 'gpt-4o',  # the newest OpenAI model is "gpt-4o"
            'anthropic': 'claude-sonnet-4-20250514'
        }
        
        # Initialize assistants
        self._initialize_assistants()
    
    def _initialize_assistants(self):
        """Initialize domain-specific OpenAI Assistants"""
        if 'openai' not in self.providers:
            return
        
        domains = {
            'healthcare': {
                'name': 'Healthcare AI Assistant',
                'instructions': """You are a specialized healthcare AI assistant with expertise in medical analysis, symptom assessment, and healthcare guidance. 

Key responsibilities:
- Provide evidence-based medical information
- Assess symptoms and suggest appropriate care levels
- Explain medical procedures and treatments
- Offer medication guidance and interaction checks
- Maintain patient privacy and confidentiality

Important disclaimers:
- Always remind users that you are not a substitute for professional medical advice
- Encourage users to consult healthcare providers for serious concerns
- Provide educational information, not diagnostic conclusions""",
                'model': 'gpt-4o'
            },
            'financial': {
                'name': 'Financial AI Assistant',
                'instructions': """You are a specialized financial AI assistant with expertise in market analysis, investment strategies, and financial planning.

Key responsibilities:
- Analyze market trends and financial data
- Provide investment insights and portfolio recommendations
- Perform financial calculations and modeling
- Explain financial concepts and instruments
- Assess risk and return profiles

Important disclaimers:
- Investment advice is for educational purposes only
- Past performance does not guarantee future results
- Users should consult financial advisors for personalized advice
- Consider individual risk tolerance and financial situations""",
                'model': 'gpt-4o'
            },
            'sports': {
                'name': 'Sports Analytics AI Assistant',
                'instructions': """You are a specialized sports analytics AI assistant with expertise in sports statistics, performance analysis, and sports betting education.

Key responsibilities:
- Analyze sports statistics and team performance
- Provide insights on player and team dynamics
- Explain betting concepts and odds (educational only)
- Track sports trends and historical data
- Offer performance predictions based on data

Important disclaimers:
- Betting information is for educational purposes only
- Gambling can be addictive; promote responsible gambling
- Statistical analysis does not guarantee outcomes
- Sports involve unpredictable elements""",
                'model': 'gpt-4o'
            },
            'business': {
                'name': 'Business Automation AI Assistant', 
                'instructions': """You are a specialized business AI assistant with expertise in process automation, workflow optimization, and business intelligence.

Key responsibilities:
- Analyze business processes and identify inefficiencies
- Suggest automation opportunities and solutions
- Perform business calculations and ROI analysis
- Create workflow diagrams and process documentation
- Provide market analysis and competitive insights

Focus areas:
- Process optimization and automation
- Data analysis and business intelligence
- Strategic planning and decision support
- Cost-benefit analysis and financial modeling
- Integration with business tools and APIs""",
                'model': 'gpt-4o'
            },
            'general': {
                'name': 'General AI Assistant',
                'instructions': """You are a versatile AI assistant capable of handling a wide range of queries and tasks.

Key responsibilities:
- Provide accurate and helpful information across various topics
- Assist with writing, analysis, and problem-solving
- Offer creative solutions and insights
- Help with research and learning
- Maintain a helpful, professional, and engaging tone

Capabilities:
- Text analysis and writing assistance
- Code interpretation and debugging
- Data analysis and visualization
- Research and information synthesis
- Creative problem-solving""",
                'model': 'gpt-4o'
            }
        }
        
        # Create or update assistants
        for domain, config in domains.items():
            try:
                assistant_config = db.session.query(AssistantConfiguration).filter_by(domain=domain).first()
                
                if not assistant_config:
                    # Create new assistant
                    assistant = self.providers['openai'].beta.assistants.create(
                        name=config['name'],
                        instructions=config['instructions'],
                        model=config['model'],
                        tools=AssistantTools.get_tools_for_domain(domain)
                    )
                    
                    # Save configuration to database
                    assistant_config = AssistantConfiguration(
                        domain=domain,
                        assistant_id=assistant.id,
                        name=config['name'],
                        instructions=config['instructions'],
                        model=config['model'],
                        tools=AssistantTools.get_tools_for_domain(domain)
                    )
                    db.session.add(assistant_config)
                    logger.info(f"Created new assistant for {domain}: {assistant.id}")
                
                self.assistants[domain] = assistant_config.assistant_id
                
            except Exception as e:
                logger.error(f"Error initializing assistant for {domain}: {e}")
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving assistant configurations: {e}")
    
    def get_completion(self, prompt: str, provider: str = 'auto', 
                      model: str = None, system_prompt: str = None,
                      max_tokens: int = 1000, temperature: float = 0.7,
                      mode: AssistantMode = AssistantMode.AUTO,
                      domain: str = 'general', user_id: int = None,
                      session_id: int = None, thread_id: str = None) -> Dict[str, Any]:
        """Get completion from specified AI provider with assistant support"""
        
        if provider == 'auto':
            provider = self._select_optimal_provider(prompt, domain)
        
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available")
        
        # Determine mode
        if mode == AssistantMode.AUTO:
            mode = self._select_optimal_mode(prompt, domain, session_id)
        
        # Use OpenAI Assistants for supported domains and complex conversations
        if (mode == AssistantMode.ASSISTANT and provider == 'openai' and 
            domain in self.assistants):
            return self._get_assistant_completion(
                prompt, domain, user_id, session_id, thread_id
            )
        
        # Fall back to traditional chat completion
        return self._get_chat_completion(
            prompt, provider, model, system_prompt, max_tokens, temperature
        )
    
    def _get_assistant_completion(self, prompt: str, domain: str, 
                                 user_id: int = None, session_id: int = None,
                                 thread_id: str = None) -> Dict[str, Any]:
        """Get completion using OpenAI Assistants API"""
        
        try:
            assistant_id = self.assistants[domain]
            client = self.providers['openai']
            
            # Get or create thread
            if thread_id:
                # Use existing thread
                thread_record = db.session.query(AssistantThread).filter_by(
                    thread_id=thread_id
                ).first()
                if not thread_record:
                    raise ValueError(f"Thread {thread_id} not found")
                thread = client.beta.threads.retrieve(thread_id)
            else:
                # Create new thread
                thread = client.beta.threads.create()
                
                # Save thread to database
                thread_record = AssistantThread(
                    thread_id=thread.id,
                    assistant_id=assistant_id,
                    domain=domain,
                    user_id=user_id,
                    session_id=session_id
                )
                db.session.add(thread_record)
                db.session.commit()
            
            # Add message to thread
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Create run
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )
            
            # Save run to database
            run_record = AssistantRun(
                run_id=run.id,
                thread_id=thread_record.id,
                status=run.status,
                model=run.model,
                instructions=run.instructions,
                tools=run.tools
            )
            db.session.add(run_record)
            
            # Poll for completion
            start_time = time.time()
            max_wait_time = 60  # Maximum 60 seconds wait
            
            while run.status in ['queued', 'in_progress', 'requires_action']:
                if time.time() - start_time > max_wait_time:
                    run_record.status = 'expired'
                    db.session.commit()
                    raise TimeoutError("Assistant run timed out")
                
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                run_record.status = run.status
                
                # Handle function calls if needed
                if run.status == 'requires_action':
                    run = self._handle_required_action(client, thread.id, run)
            
            # Update run record
            run_record.completed_at = datetime.utcnow()
            if run.usage:
                run_record.usage_tokens = run.usage.total_tokens
                self.usage_stats['openai']['tokens'] += run.usage.total_tokens
            
            self.usage_stats['openai']['assistant_runs'] += 1
            
            # Get response
            if run.status == 'completed':
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id,
                    order='desc',
                    limit=1
                )
                
                if messages.data:
                    response_content = messages.data[0].content[0].text.value
                    
                    # Update thread activity
                    thread_record.last_activity = datetime.utcnow()
                    thread_record.message_count += 1
                    
                    db.session.commit()
                    
                    return {
                        'content': response_content,
                        'provider': 'openai',
                        'mode': 'assistant',
                        'domain': domain,
                        'thread_id': thread.id,
                        'run_id': run.id,
                        'tokens_used': run_record.usage_tokens,
                        'model': run.model
                    }
            
            # Handle failed runs
            run_record.failed_at = datetime.utcnow()
            run_record.error_code = run.last_error.code if run.last_error else 'unknown'
            run_record.error_message = run.last_error.message if run.last_error else 'Unknown error'
            db.session.commit()
            
            # Fall back to chat completion
            logger.warning(f"Assistant run failed, falling back to chat completion: {run.status}")
            return self._get_chat_completion(prompt, 'openai')
            
        except Exception as e:
            logger.error(f"Error in assistant completion: {e}")
            db.session.rollback()
            # Fall back to chat completion
            return self._get_chat_completion(prompt, 'openai')
    
    def _handle_required_action(self, client, thread_id: str, run) -> any:
        """Handle function calls and other required actions"""
        try:
            if run.required_action.type == "submit_tool_outputs":
                tool_outputs = []
                
                for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                    # Handle function calls
                    if tool_call.type == "function":
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        # Execute function (implement specific handlers)
                        output = self._execute_function(function_name, function_args)
                        
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(output)
                        })
                
                # Submit tool outputs
                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            
            return run
            
        except Exception as e:
            logger.error(f"Error handling required action: {e}")
            return run
    
    def _execute_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute assistant function calls"""
        try:
            if function_name == "get_market_data":
                # Implement financial data retrieval
                return {"status": "success", "data": "Market data placeholder"}
            
            elif function_name == "get_medical_information":
                # Implement medical information lookup
                return {"status": "success", "data": "Medical information placeholder"}
            
            elif function_name == "get_sports_data":
                # Implement sports data retrieval
                return {"status": "success", "data": "Sports data placeholder"}
            
            elif function_name == "business_analytics":
                # Implement business analytics
                return {"status": "success", "data": "Business analytics placeholder"}
            
            else:
                return {"status": "error", "message": f"Unknown function: {function_name}"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _get_chat_completion(self, prompt: str, provider: str = 'openai',
                           model: str = None, system_prompt: str = None,
                           max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Get completion using traditional chat API"""
        
        if model is None:
            model = self.default_models.get(provider)
        
        try:
            if provider == 'openai':
                response = self._get_openai_completion(
                    prompt, model, system_prompt, max_tokens, temperature
                )
                return {
                    'content': response,
                    'provider': 'openai',
                    'mode': 'chat_completion',
                    'model': model
                }
            
            elif provider == 'anthropic':
                response = self._get_anthropic_completion(
                    prompt, model, system_prompt, max_tokens, temperature
                )
                return {
                    'content': response,
                    'provider': 'anthropic',
                    'mode': 'chat_completion',
                    'model': model
                }
            
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        except Exception as e:
            logger.error(f"Error getting chat completion: {e}")
            raise
    
    def _get_openai_completion(self, prompt: str, model: str, system_prompt: str = None,
                              max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Get completion from OpenAI using Chat Completions API"""
        
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
        if response.usage:
            self.usage_stats['openai']['tokens'] += response.usage.total_tokens
        
        return response.choices[0].message.content
    
    def _get_anthropic_completion(self, prompt: str, model: str, system_prompt: str = None,
                                 max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """Get completion from Anthropic Claude"""
        
        # Build the message
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}"
        else:
            full_prompt = f"Human: {prompt}"
        
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
    
    def _select_optimal_provider(self, prompt: str, domain: str = 'general') -> str:
        """Select the best provider based on prompt and domain"""
        
        # Use OpenAI for domains that benefit from assistants and tools
        if domain in ['financial', 'healthcare', 'business'] and 'openai' in self.providers:
            return 'openai'
        
        # Use Anthropic for complex reasoning and analysis
        anthropic_indicators = ['analyze', 'reasoning', 'complex', 'detailed analysis']
        if any(indicator in prompt.lower() for indicator in anthropic_indicators) and 'anthropic' in self.providers:
            return 'anthropic'
        
        # Default to OpenAI
        return 'openai' if 'openai' in self.providers else 'anthropic'
    
    def _select_optimal_mode(self, prompt: str, domain: str, session_id: int = None) -> AssistantMode:
        """Select the optimal mode based on context"""
        
        # Use assistants for domains with specialized tools
        if domain in ['financial', 'healthcare', 'sports', 'business']:
            return AssistantMode.ASSISTANT
        
        # Use assistants for multi-turn conversations
        if session_id:
            return AssistantMode.ASSISTANT
        
        # Use assistants for complex tasks
        complex_indicators = ['analyze', 'calculate', 'step by step', 'detailed', 'comprehensive']
        if any(indicator in prompt.lower() for indicator in complex_indicators):
            return AssistantMode.ASSISTANT
        
        # Default to chat completion for simple queries
        return AssistantMode.CHAT_COMPLETION
    
    def get_thread_history(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get message history from an assistant thread"""
        
        if 'openai' not in self.providers:
            return []
        
        try:
            messages = self.providers['openai'].beta.threads.messages.list(
                thread_id=thread_id,
                order='desc',
                limit=limit
            )
            
            history = []
            for message in reversed(messages.data):
                history.append({
                    'role': message.role,
                    'content': message.content[0].text.value if message.content else '',
                    'created_at': message.created_at
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting thread history: {e}")
            return []
    
    def cleanup_inactive_threads(self, days_inactive: int = 30):
        """Clean up inactive assistant threads"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        try:
            inactive_threads = db.session.query(AssistantThread).filter(
                AssistantThread.last_activity < cutoff_date,
                AssistantThread.is_active == True
            ).all()
            
            for thread in inactive_threads:
                try:
                    # Delete from OpenAI
                    if 'openai' in self.providers:
                        self.providers['openai'].beta.threads.delete(thread.thread_id)
                    
                    # Mark as inactive in database
                    thread.is_active = False
                    logger.info(f"Cleaned up inactive thread: {thread.thread_id}")
                    
                except Exception as e:
                    logger.error(f"Error cleaning up thread {thread.thread_id}: {e}")
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error during thread cleanup: {e}")
            db.session.rollback()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        
        # Get database stats
        total_threads = db.session.query(AssistantThread).filter_by(is_active=True).count()
        total_runs = db.session.query(AssistantRun).count()
        
        # Get per-domain stats
        domain_stats = {}
        for domain in ['healthcare', 'financial', 'sports', 'business', 'general']:
            domain_threads = db.session.query(AssistantThread).filter_by(
                domain=domain, is_active=True
            ).count()
            domain_stats[domain] = {
                'active_threads': domain_threads,
                'assistant_id': self.assistants.get(domain)
            }
        
        return {
            'providers': self.usage_stats,
            'assistants': {
                'total_active_threads': total_threads,
                'total_runs': total_runs,
                'domain_breakdown': domain_stats
            }
        }

# Global instance - will be initialized in app context
enhanced_ai_provider = None

def initialize_enhanced_ai_provider():
    """Initialize the enhanced AI provider within Flask app context"""
    global enhanced_ai_provider
    if enhanced_ai_provider is None:
        enhanced_ai_provider = EnhancedAIProviderManager()
    return enhanced_ai_provider