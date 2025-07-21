"""
Specialized Agent Pools - Domain-specific AI agents
Healthcare, Financial, Sports, Business, and General purpose agents
"""

import logging
import json
from typing import Dict, List, Any
from datetime import datetime
import re

from financial_integrations import FinancialIntegrationManager
from healthcare_analysis import HealthcareAnalyzer
from sports_betting import SportsBettingAnalyzer
from business_automation import BusinessAutomationManager

logger = logging.getLogger(__name__)

class SpecializedAgentPools:
    """Manages specialized agent pools for different domains"""
    
    def __init__(self, ai_provider_manager):
        self.ai_provider = ai_provider_manager
        
        # Initialize domain-specific managers
        self.financial_manager = FinancialIntegrationManager(ai_provider_manager)
        self.healthcare_analyzer = HealthcareAnalyzer(ai_provider_manager)
        self.sports_analyzer = SportsBettingAnalyzer(ai_provider_manager)
        self.business_manager = BusinessAutomationManager(ai_provider_manager)
        
        logger.info("Specialized agent pools initialized")
    
    def process_healthcare_task(self, query: str) -> str:
        """Process healthcare-related tasks"""
        try:
            # Determine the type of healthcare query
            query_type = self._classify_healthcare_query(query)
            
            if query_type == 'diagnosis':
                return self.healthcare_analyzer.analyze_symptoms(query)
            elif query_type == 'medication':
                return self.healthcare_analyzer.medication_analysis(query)
            elif query_type == 'insurance':
                return self.healthcare_analyzer.insurance_navigation(query)
            elif query_type == 'wellness':
                return self.healthcare_analyzer.wellness_coaching(query)
            else:
                return self.healthcare_analyzer.general_health_advice(query)
                
        except Exception as e:
            logger.error(f"Error processing healthcare task: {e}")
            return f"I apologize, but I encountered an error while processing your healthcare query. Error: {str(e)}"
    
    def process_financial_task(self, query: str) -> str:
        """Process financial-related tasks"""
        try:
            # Determine the type of financial query
            query_type = self._classify_financial_query(query)
            
            if query_type == 'market_data':
                return self.financial_manager.get_market_analysis(query)
            elif query_type == 'portfolio':
                return self.financial_manager.portfolio_optimization(query)
            elif query_type == 'banking':
                return self.financial_manager.banking_analysis(query)
            elif query_type == 'investment':
                return self.financial_manager.investment_advice(query)
            elif query_type == 'planning':
                return self.financial_manager.financial_planning(query)
            else:
                return self.financial_manager.general_financial_advice(query)
                
        except Exception as e:
            logger.error(f"Error processing financial task: {e}")
            return f"I apologize, but I encountered an error while processing your financial query. Error: {str(e)}"
    
    def process_sports_task(self, query: str) -> str:
        """Process sports-related tasks"""
        try:
            # Determine the type of sports query
            query_type = self._classify_sports_query(query)
            
            if query_type == 'betting':
                return self.sports_analyzer.betting_analysis(query)
            elif query_type == 'arbitrage':
                return self.sports_analyzer.arbitrage_opportunities(query)
            elif query_type == 'predictions':
                return self.sports_analyzer.game_predictions(query)
            elif query_type == 'fantasy':
                return self.sports_analyzer.fantasy_advice(query)
            elif query_type == 'stats':
                return self.sports_analyzer.statistical_analysis(query)
            else:
                return self.sports_analyzer.general_sports_analysis(query)
                
        except Exception as e:
            logger.error(f"Error processing sports task: {e}")
            return f"I apologize, but I encountered an error while processing your sports query. Error: {str(e)}"
    
    def process_business_task(self, query: str) -> str:
        """Process business-related tasks"""
        try:
            # Determine the type of business query
            query_type = self._classify_business_query(query)
            
            if query_type == 'automation':
                return self.business_manager.process_automation(query)
            elif query_type == 'workflow':
                return self.business_manager.workflow_optimization(query)
            elif query_type == 'project':
                return self.business_manager.project_management(query)
            elif query_type == 'strategy':
                return self.business_manager.strategic_planning(query)
            elif query_type == 'operations':
                return self.business_manager.operations_analysis(query)
            else:
                return self.business_manager.general_business_advice(query)
                
        except Exception as e:
            logger.error(f"Error processing business task: {e}")
            return f"I apologize, but I encountered an error while processing your business query. Error: {str(e)}"
    
    def process_general_task(self, query: str) -> str:
        """Process general-purpose tasks"""
        try:
            # Use the AI provider for general assistance
            system_prompt = """You are a helpful AI assistant capable of providing information, 
            analysis, and assistance across a wide range of topics. Provide accurate, helpful, 
            and well-structured responses."""
            
            response = self.ai_provider.get_completion(
                query,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing general task: {e}")
            return f"I apologize, but I encountered an error while processing your query. Error: {str(e)}"
    
    def _classify_healthcare_query(self, query: str) -> str:
        """Classify healthcare queries into specific types"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['symptom', 'pain', 'diagnosis', 'feel', 'hurt']):
            return 'diagnosis'
        elif any(word in query_lower for word in ['medication', 'drug', 'prescription', 'pill']):
            return 'medication'
        elif any(word in query_lower for word in ['insurance', 'coverage', 'claim', 'copay']):
            return 'insurance'
        elif any(word in query_lower for word in ['wellness', 'exercise', 'diet', 'lifestyle']):
            return 'wellness'
        else:
            return 'general'
    
    def _classify_financial_query(self, query: str) -> str:
        """Classify financial queries into specific types"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['stock', 'market', 'ticker', 'price', 'chart']):
            return 'market_data'
        elif any(word in query_lower for word in ['portfolio', 'diversification', 'allocation']):
            return 'portfolio'
        elif any(word in query_lower for word in ['bank', 'account', 'balance', 'transaction']):
            return 'banking'
        elif any(word in query_lower for word in ['invest', 'investment', 'buy', 'sell']):
            return 'investment'
        elif any(word in query_lower for word in ['retirement', 'planning', 'budget', 'savings']):
            return 'planning'
        else:
            return 'general'
    
    def _classify_sports_query(self, query: str) -> str:
        """Classify sports queries into specific types"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['bet', 'betting', 'odds', 'wager']):
            return 'betting'
        elif any(word in query_lower for word in ['arbitrage', 'arb', 'surebet']):
            return 'arbitrage'
        elif any(word in query_lower for word in ['predict', 'prediction', 'forecast', 'outcome']):
            return 'predictions'
        elif any(word in query_lower for word in ['fantasy', 'lineup', 'draft']):
            return 'fantasy'
        elif any(word in query_lower for word in ['stats', 'statistics', 'performance', 'data']):
            return 'stats'
        else:
            return 'general'
    
    def _classify_business_query(self, query: str) -> str:
        """Classify business queries into specific types"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['automate', 'automation', 'automatic']):
            return 'automation'
        elif any(word in query_lower for word in ['workflow', 'process', 'procedure']):
            return 'workflow'
        elif any(word in query_lower for word in ['project', 'management', 'timeline', 'milestone']):
            return 'project'
        elif any(word in query_lower for word in ['strategy', 'strategic', 'planning', 'goal']):
            return 'strategy'
        elif any(word in query_lower for word in ['operations', 'efficiency', 'productivity']):
            return 'operations'
        else:
            return 'general'
    
    def get_pool_capabilities(self, pool_name: str) -> List[str]:
        """Get capabilities for a specific agent pool"""
        capabilities = {
            'healthcare': [
                'Medical symptom analysis',
                'Medication recommendations',
                'Insurance navigation',
                'Wellness coaching',
                'Clinical decision support'
            ],
            'financial': [
                'Market data analysis',
                'Portfolio optimization',
                'Banking integration',
                'Investment advice',
                'Financial planning'
            ],
            'sports': [
                'Sports betting analysis',
                'Arbitrage detection',
                'Game predictions',
                'Fantasy sports advice',
                'Statistical analysis'
            ],
            'business': [
                'Process automation',
                'Workflow optimization',
                'Project management',
                'Strategic planning',
                'Operations analysis'
            ],
            'general': [
                'General assistance',
                'Research and analysis',
                'Writing and content creation',
                'Problem solving',
                'Information synthesis'
            ]
        }
        
        return capabilities.get(pool_name, [])
    
    def get_pool_status(self) -> Dict[str, Dict]:
        """Get status of all agent pools"""
        return {
            'healthcare': {
                'active': True,
                'capabilities': self.get_pool_capabilities('healthcare'),
                'integrations': ['HealthcareAnalyzer']
            },
            'financial': {
                'active': True,
                'capabilities': self.get_pool_capabilities('financial'),
                'integrations': ['Plaid', 'AlphaVantage', 'Banking APIs']
            },
            'sports': {
                'active': True,
                'capabilities': self.get_pool_capabilities('sports'),
                'integrations': ['SportsBettingAnalyzer', 'Sports APIs']
            },
            'business': {
                'active': True,
                'capabilities': self.get_pool_capabilities('business'),
                'integrations': ['BusinessAutomationManager']
            },
            'general': {
                'active': True,
                'capabilities': self.get_pool_capabilities('general'),
                'integrations': ['AI Providers']
            }
        }
