"""
Financial Integration Manager - Comprehensive financial services integration
Plaid, Alpha Vantage, banking APIs, and investment analysis
"""

import os
import logging
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class FinancialIntegrationManager:
    """Manages financial data integrations and analysis"""
    
    def __init__(self, ai_provider_manager):
        self.ai_provider = ai_provider_manager
        
        # API Keys from environment
        self.plaid_client_id = os.environ.get('PLAID_CLIENT_ID', 'demo_client_id')
        self.plaid_secret = os.environ.get('PLAID_SECRET', 'demo_secret')
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY', 'demo_key')
        self.polygon_key = os.environ.get('POLYGON_API_KEY', 'demo_key')
        
        # API Base URLs
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.polygon_base = "https://api.polygon.io"
        
        logger.info("Financial Integration Manager initialized")
    
    def get_market_analysis(self, query: str) -> str:
        """Analyze market conditions and provide insights"""
        try:
            # Extract ticker symbols from query if any
            tickers = self._extract_tickers(query)
            
            market_data = {}
            
            # Get market data for identified tickers
            for ticker in tickers[:5]:  # Limit to 5 tickers to avoid rate limits
                try:
                    data = self._get_stock_data(ticker)
                    if data:
                        market_data[ticker] = data
                except Exception as e:
                    logger.warning(f"Failed to get data for {ticker}: {e}")
            
            # Get general market overview
            market_overview = self._get_market_overview()
            
            # Generate AI analysis
            analysis_prompt = f"""
            Provide comprehensive financial market analysis based on the following data:
            
            Query: {query}
            
            Market Data: {json.dumps(market_data, indent=2) if market_data else "No specific ticker data available"}
            
            Market Overview: {json.dumps(market_overview, indent=2)}
            
            Please provide:
            1. Current market conditions analysis
            2. Specific stock insights (if applicable)
            3. Investment recommendations
            4. Risk assessment
            5. Market trends and outlook
            
            Format the response in a clear, professional manner suitable for financial decision-making.
            """
            
            response = self.ai_provider.get_completion(
                analysis_prompt,
                system_prompt="You are a professional financial analyst with expertise in market analysis, investment strategy, and risk management.",
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return f"I apologize, but I encountered an error while analyzing market conditions. Please try again or contact support if the issue persists."
    
    def portfolio_optimization(self, query: str) -> str:
        """Provide portfolio optimization recommendations"""
        try:
            optimization_prompt = f"""
            Provide comprehensive portfolio optimization advice based on the following request:
            
            Query: {query}
            
            Please analyze and provide recommendations for:
            1. Asset allocation strategies
            2. Risk diversification approaches
            3. Rebalancing recommendations
            4. Performance optimization techniques
            5. Tax-efficient strategies
            6. Timeline and goal-based planning
            
            Consider modern portfolio theory, risk tolerance assessment, and current market conditions.
            Provide specific, actionable recommendations.
            """
            
            response = self.ai_provider.get_completion(
                optimization_prompt,
                system_prompt="You are an expert portfolio manager and investment advisor with deep knowledge of modern portfolio theory, asset allocation, and risk management.",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {e}")
            return f"I apologize, but I encountered an error while analyzing your portfolio optimization request."
    
    def banking_analysis(self, query: str) -> str:
        """Analyze banking and account information"""
        try:
            # Note: In a real implementation, this would integrate with Plaid for actual account data
            banking_prompt = f"""
            Provide comprehensive banking and financial account analysis based on the following request:
            
            Query: {query}
            
            Please provide insights on:
            1. Account management strategies
            2. Banking product recommendations
            3. Fee optimization opportunities
            4. Credit improvement strategies
            5. Savings and investment account options
            6. Cash flow management
            
            Provide practical, actionable advice for personal and business banking needs.
            """
            
            response = self.ai_provider.get_completion(
                banking_prompt,
                system_prompt="You are a banking and financial services expert with knowledge of personal and business banking, credit management, and financial products.",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in banking analysis: {e}")
            return f"I apologize, but I encountered an error while analyzing your banking request."
    
    def investment_advice(self, query: str) -> str:
        """Provide investment recommendations and analysis"""
        try:
            # Get current market conditions
            market_conditions = self._get_market_sentiment()
            
            investment_prompt = f"""
            Provide comprehensive investment advice based on the following request:
            
            Query: {query}
            
            Current Market Conditions: {market_conditions}
            
            Please analyze and provide advice on:
            1. Investment opportunities and strategies
            2. Risk assessment and management
            3. Diversification recommendations
            4. Timeline and goal alignment
            5. Tax implications and optimization
            6. Market timing considerations
            7. Alternative investment options
            
            Provide specific, actionable investment recommendations with clear reasoning.
            """
            
            response = self.ai_provider.get_completion(
                investment_prompt,
                system_prompt="You are a certified financial advisor and investment strategist with expertise in securities analysis, investment planning, and wealth management.",
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in investment advice: {e}")
            return f"I apologize, but I encountered an error while generating investment advice."
    
    def financial_planning(self, query: str) -> str:
        """Comprehensive financial planning assistance"""
        try:
            planning_prompt = f"""
            Provide comprehensive financial planning guidance based on the following request:
            
            Query: {query}
            
            Please create a detailed financial plan addressing:
            1. Goal setting and prioritization
            2. Budgeting and cash flow management
            3. Emergency fund planning
            4. Debt management strategies
            5. Retirement planning
            6. Tax planning and optimization
            7. Insurance needs assessment
            8. Estate planning considerations
            
            Provide a structured, actionable financial plan with specific steps and timelines.
            """
            
            response = self.ai_provider.get_completion(
                planning_prompt,
                system_prompt="You are a certified financial planner (CFP) with expertise in comprehensive financial planning, retirement planning, tax strategy, and wealth management.",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in financial planning: {e}")
            return f"I apologize, but I encountered an error while creating your financial plan."
    
    def general_financial_advice(self, query: str) -> str:
        """General financial guidance and advice"""
        try:
            advice_prompt = f"""
            Provide comprehensive financial guidance based on the following question:
            
            Query: {query}
            
            Please provide clear, actionable financial advice covering relevant aspects such as:
            - Personal finance management
            - Investment strategies
            - Risk management
            - Financial product recommendations
            - Market insights
            - Planning strategies
            
            Ensure the advice is practical, well-reasoned, and appropriate for the user's apparent needs.
            """
            
            response = self.ai_provider.get_completion(
                advice_prompt,
                system_prompt="You are a knowledgeable financial advisor with broad expertise in personal finance, investments, and financial planning.",
                temperature=0.5
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in general financial advice: {e}")
            return f"I apologize, but I encountered an error while providing financial advice."
    
    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock ticker symbols from text"""
        import re
        
        # Common stock ticker patterns
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        potential_tickers = re.findall(ticker_pattern, text.upper())
        
        # Filter out common words that aren't tickers
        common_words = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}
        
        tickers = [t for t in potential_tickers if t not in common_words and len(t) <= 5]
        
        return tickers[:10]  # Return max 10 tickers
    
    def _get_stock_data(self, ticker: str) -> Dict:
        """Get stock data from Alpha Vantage"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': ticker,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(self.alpha_vantage_base, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': quote.get('01. Symbol', ticker),
                    'price': quote.get('05. Price', '0'),
                    'change': quote.get('09. Change', '0'),
                    'change_percent': quote.get('10. Change Percent', '0%'),
                    'high': quote.get('03. High', '0'),
                    'low': quote.get('04. Low', '0'),
                    'volume': quote.get('06. Volume', '0')
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting stock data for {ticker}: {e}")
            return {}
    
    def _get_market_overview(self) -> Dict:
        """Get general market overview"""
        try:
            # Get major indices data
            indices = ['SPY', 'QQQ', 'DIA']  # S&P 500, NASDAQ, Dow Jones ETFs
            market_data = {}
            
            for index in indices:
                data = self._get_stock_data(index)
                if data:
                    market_data[index] = data
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'indices': market_data,
                'market_status': 'open' if self._is_market_open() else 'closed'
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {'error': str(e)}
    
    def _get_market_sentiment(self) -> str:
        """Get current market sentiment analysis"""
        try:
            # Simple market sentiment based on major indices
            indices_data = self._get_market_overview()
            
            sentiment_factors = []
            
            if 'indices' in indices_data:
                for symbol, data in indices_data['indices'].items():
                    try:
                        change_percent = float(data['change_percent'].replace('%', ''))
                        sentiment_factors.append(change_percent)
                    except (ValueError, KeyError):
                        continue
            
            if sentiment_factors:
                avg_change = sum(sentiment_factors) / len(sentiment_factors)
                if avg_change > 1:
                    return "Bullish - Market showing strong positive momentum"
                elif avg_change > 0:
                    return "Moderately Bullish - Market trending upward"
                elif avg_change > -1:
                    return "Neutral - Market showing mixed signals"
                elif avg_change > -2:
                    return "Moderately Bearish - Market under pressure"
                else:
                    return "Bearish - Market showing significant weakness"
            
            return "Neutral - Unable to determine clear market sentiment"
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return "Neutral - Market sentiment analysis unavailable"
    
    def _is_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        try:
            now = datetime.utcnow()
            # Simple check - US market is open 9:30 AM - 4:00 PM EST, Monday-Friday
            # This is a simplified implementation
            weekday = now.weekday()  # 0 = Monday, 6 = Sunday
            
            if weekday > 4:  # Weekend
                return False
            
            # Convert to EST (simplified - doesn't account for DST properly)
            est_hour = (now.hour - 5) % 24
            
            return 9 <= est_hour < 16  # 9:30 AM to 4:00 PM EST (simplified)
            
        except Exception:
            return False
    
    def get_integration_status(self) -> Dict:
        """Get status of financial integrations"""
        status = {
            'plaid': {
                'configured': bool(self.plaid_client_id and self.plaid_client_id != 'demo_client_id'),
                'status': 'ready' if self.plaid_client_id != 'demo_client_id' else 'demo_mode'
            },
            'alpha_vantage': {
                'configured': bool(self.alpha_vantage_key and self.alpha_vantage_key != 'demo_key'),
                'status': 'ready' if self.alpha_vantage_key != 'demo_key' else 'demo_mode'
            },
            'polygon': {
                'configured': bool(self.polygon_key and self.polygon_key != 'demo_key'),
                'status': 'ready' if self.polygon_key != 'demo_key' else 'demo_mode'
            }
        }
        
        return status
