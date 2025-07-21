"""
Sports Betting and Analytics Engine - Advanced sports analysis and betting insights
Responsible gambling with educational focus and compliance monitoring
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class SportsBettingAnalyzer:
    """Advanced sports analytics and responsible betting education"""
    
    def __init__(self, ai_provider_manager):
        self.ai_provider = ai_provider_manager
        
        # Sports API keys
        self.sports_api_key = os.environ.get('SPORTS_API_KEY', 'demo_key')
        self.odds_api_key = os.environ.get('ODDS_API_KEY', 'demo_key')
        
        # Responsible gambling disclaimer
        self.responsible_gambling_notice = """
        RESPONSIBLE GAMBLING NOTICE: Sports betting involves risk and should only be done by adults in jurisdictions where it is legal. 
        Never bet more than you can afford to lose. Gambling can be addictive. If you or someone you know has a gambling problem, 
        seek help immediately. National Problem Gambling Helpline: 1-800-522-4700 or visit ncpgambling.org.
        This analysis is for educational purposes only and does not constitute gambling advice.
        """
        
        logger.info("Sports Betting Analyzer initialized")
    
    def betting_analysis(self, query: str) -> str:
        """Provide educational sports betting analysis"""
        try:
            # Extract sports and teams from query
            sports_context = self._extract_sports_context(query)
            
            betting_prompt = f"""
            {self.responsible_gambling_notice}
            
            Provide educational sports betting analysis for the following query:
            
            Query: {query}
            Sports Context: {sports_context}
            
            Please provide comprehensive educational information on:
            
            1. BETTING FUNDAMENTALS:
            - Types of bets and how they work
            - Understanding odds and probability
            - Bankroll management principles
            - Value betting concepts
            
            2. ANALYTICAL APPROACH:
            - Key statistics to consider
            - Team and player performance metrics
            - Situational factors (injuries, weather, etc.)
            - Historical trends and patterns
            
            3. RISK ASSESSMENT:
            - Probability evaluation
            - Expected value calculations
            - Variance and standard deviation
            - Risk vs. reward analysis
            
            4. MARKET ANALYSIS:
            - Line movement interpretation
            - Market efficiency concepts
            - Sharp vs. public money
            - Arbitrage opportunities (if applicable)
            
            5. RESPONSIBLE PRACTICES:
            - Bankroll management strategies
            - Emotional control and discipline
            - Record keeping importance
            - When to take breaks
            
            Always emphasize responsible gambling practices and legal compliance.
            """
            
            response = self.ai_provider.get_completion(
                betting_prompt,
                system_prompt="You are a sports analytics expert focused on education and responsible gambling practices. Always emphasize risk management and legal compliance.",
                temperature=0.3
            )
            
            return f"{self.responsible_gambling_notice}\n\n{response}"
            
        except Exception as e:
            logger.error(f"Error in betting analysis: {e}")
            return f"{self.responsible_gambling_notice}\n\nI apologize, but I encountered an error while providing betting analysis. Please ensure you're gambling responsibly and within legal limits."
    
    def arbitrage_opportunities(self, query: str) -> str:
        """Analyze arbitrage opportunities in sports betting"""
        try:
            arbitrage_prompt = f"""
            {self.responsible_gambling_notice}
            
            Provide educational information about sports betting arbitrage based on the following query:
            
            Query: {query}
            
            Please explain:
            
            1. ARBITRAGE FUNDAMENTALS:
            - What is sports betting arbitrage
            - How arbitrage opportunities arise
            - Mathematical principles behind arbitrage
            - Risk-free profit concept
            
            2. IDENTIFICATION METHODS:
            - How to find arbitrage opportunities
            - Tools and resources for detection
            - Market inefficiencies to look for
            - Timing considerations
            
            3. CALCULATION TECHNIQUES:
            - Arbitrage formulas and calculations
            - Stake distribution methods
            - Profit margin determination
            - Break-even analysis
            
            4. PRACTICAL CONSIDERATIONS:
            - Account management across sportsbooks
            - Bet limits and restrictions
            - Processing times and settlements
            - Legal and regulatory compliance
            
            5. RISKS AND LIMITATIONS:
            - Account closure risks
            - Line movement during placement
            - Human error possibilities
            - Limited profit margins
            
            Emphasize that arbitrage requires significant capital, time, and carries operational risks.
            """
            
            response = self.ai_provider.get_completion(
                arbitrage_prompt,
                system_prompt="You are a quantitative analyst specializing in sports betting mathematics and arbitrage theory. Focus on education while emphasizing practical limitations and risks.",
                temperature=0.2
            )
            
            return f"{self.responsible_gambling_notice}\n\n{response}"
            
        except Exception as e:
            logger.error(f"Error in arbitrage analysis: {e}")
            return f"{self.responsible_gambling_notice}\n\nI apologize, but I encountered an error while analyzing arbitrage opportunities."
    
    def game_predictions(self, query: str) -> str:
        """Provide game predictions and analysis"""
        try:
            # Get recent sports data if available
            sports_data = self._get_sports_data(query)
            
            prediction_prompt = f"""
            Provide comprehensive sports game analysis and educational prediction methodology for the following query:
            
            Query: {query}
            
            Available Data: {json.dumps(sports_data, indent=2) if sports_data else "Limited data available"}
            
            Please provide analysis covering:
            
            1. TEAM ANALYSIS:
            - Current form and recent performance
            - Key player availability and injuries
            - Home/away performance splits
            - Head-to-head historical records
            
            2. STATISTICAL MODELING:
            - Relevant performance metrics
            - Offensive and defensive ratings
            - Advanced analytics (if applicable)
            - Situational statistics
            
            3. CONTEXTUAL FACTORS:
            - Weather conditions (if relevant)
            - Rest and travel considerations
            - Motivation and playoff implications
            - Coaching matchups and strategies
            
            4. PREDICTION METHODOLOGY:
            - How to weight different factors
            - Probability assessment techniques
            - Model building concepts
            - Uncertainty quantification
            
            5. EDUCATIONAL INSIGHTS:
            - Common prediction pitfalls
            - Importance of sample sizes
            - Regression to the mean concepts
            - Value vs. outcome distinction
            
            Focus on the analytical process rather than definitive predictions.
            """
            
            response = self.ai_provider.get_completion(
                prediction_prompt,
                system_prompt="You are a sports statistician and analyst focused on teaching prediction methodologies and analytical thinking. Emphasize process over outcomes.",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in game predictions: {e}")
            return "I apologize, but I encountered an error while providing game analysis. Sports predictions should always be viewed as educational and entertainment purposes only."
    
    def fantasy_advice(self, query: str) -> str:
        """Provide fantasy sports advice and strategy"""
        try:
            fantasy_prompt = f"""
            Provide comprehensive fantasy sports strategy and advice based on the following query:
            
            Query: {query}
            
            Please provide guidance on:
            
            1. PLAYER EVALUATION:
            - Statistical analysis and projections
            - Matchup analysis and game scripts
            - Injury reports and player news
            - Usage trends and opportunity assessment
            
            2. ROSTER CONSTRUCTION:
            - Salary cap optimization
            - Lineup building strategies
            - Stack and correlation concepts
            - Risk/reward balance
            
            3. GAME THEORY CONCEPTS:
            - Tournament vs. cash game strategies
            - Ownership projections and leverage
            - Contrarian play identification
            - Late swap strategies
            
            4. RESEARCH METHODOLOGY:
            - Data sources and analysis
            - News monitoring and interpretation
            - Weather and situational factors
            - Line movement implications
            
            5. BANKROLL MANAGEMENT:
            - Entry selection strategies
            - Risk allocation principles
            - Variance understanding
            - Long-term profitability focus
            
            Emphasize skill development and analytical thinking in fantasy sports.
            """
            
            response = self.ai_provider.get_completion(
                fantasy_prompt,
                system_prompt="You are a fantasy sports expert with deep knowledge of strategy, analytics, and game theory. Focus on educational content and skill development.",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in fantasy advice: {e}")
            return "I apologize, but I encountered an error while providing fantasy sports advice."
    
    def statistical_analysis(self, query: str) -> str:
        """Provide advanced sports statistical analysis"""
        try:
            stats_prompt = f"""
            Provide advanced statistical analysis for the following sports query:
            
            Query: {query}
            
            Please provide comprehensive analysis including:
            
            1. DESCRIPTIVE STATISTICS:
            - Central tendency measures
            - Variability and distribution analysis
            - Trend identification
            - Seasonal patterns
            
            2. PREDICTIVE ANALYTICS:
            - Regression analysis concepts
            - Machine learning applications
            - Model validation techniques
            - Feature importance assessment
            
            3. ADVANCED METRICS:
            - Efficiency ratings and advanced stats
            - Context-adjusted metrics
            - Player impact measurements
            - Team chemistry indicators
            
            4. COMPARATIVE ANALYSIS:
            - Peer group comparisons
            - Historical context and benchmarking
            - Cross-era adjustments
            - League average baselines
            
            5. STATISTICAL INTERPRETATION:
            - Significance testing concepts
            - Sample size considerations
            - Correlation vs. causation
            - Confidence intervals and uncertainty
            
            Focus on teaching statistical literacy and analytical thinking.
            """
            
            response = self.ai_provider.get_completion(
                stats_prompt,
                system_prompt="You are a sports statistician with expertise in advanced analytics, machine learning, and statistical modeling. Focus on education and methodology.",
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {e}")
            return "I apologize, but I encountered an error while providing statistical analysis."
    
    def general_sports_analysis(self, query: str) -> str:
        """Provide general sports analysis and insights"""
        try:
            sports_prompt = f"""
            Provide comprehensive sports analysis and insights for the following query:
            
            Query: {query}
            
            Please provide analysis covering relevant aspects such as:
            - Performance evaluation and trends
            - Strategic and tactical analysis
            - Player and team comparisons
            - Historical context and significance
            - Future outlook and projections
            
            Focus on educational content and analytical thinking.
            """
            
            response = self.ai_provider.get_completion(
                sports_prompt,
                system_prompt="You are a knowledgeable sports analyst with expertise across multiple sports and analytical methodologies.",
                temperature=0.5
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in general sports analysis: {e}")
            return "I apologize, but I encountered an error while providing sports analysis."
    
    def _extract_sports_context(self, text: str) -> Dict:
        """Extract sports-related information from text"""
        text_lower = text.lower()
        
        # Sports leagues
        leagues = {
            'nfl': ['nfl', 'football', 'super bowl', 'playoffs'],
            'nba': ['nba', 'basketball', 'playoffs', 'finals'],
            'mlb': ['mlb', 'baseball', 'world series'],
            'nhl': ['nhl', 'hockey', 'stanley cup'],
            'ncaa': ['college', 'march madness', 'bowl game'],
            'soccer': ['soccer', 'mls', 'premier league', 'champions league']
        }
        
        # Team names (simplified)
        teams = [
            'patriots', 'cowboys', 'packers', 'steelers', 'giants', '49ers',
            'lakers', 'celtics', 'warriors', 'bulls', 'heat', 'spurs',
            'yankees', 'red sox', 'dodgers', 'giants', 'astros', 'mets'
        ]
        
        context = {
            'leagues': [],
            'teams': [],
            'betting_types': []
        }
        
        # Identify leagues
        for league, keywords in leagues.items():
            if any(keyword in text_lower for keyword in keywords):
                context['leagues'].append(league)
        
        # Identify teams
        for team in teams:
            if team in text_lower:
                context['teams'].append(team)
        
        # Identify betting types
        betting_keywords = ['spread', 'moneyline', 'over', 'under', 'prop', 'parlay', 'teaser']
        for keyword in betting_keywords:
            if keyword in text_lower:
                context['betting_types'].append(keyword)
        
        return context
    
    def _get_sports_data(self, query: str) -> Optional[Dict]:
        """Get sports data from APIs (simplified implementation)"""
        try:
            # This is a placeholder for actual sports API integration
            # In a real implementation, you would integrate with sports data APIs
            
            context = self._extract_sports_context(query)
            
            # Return mock structure for demonstration
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'leagues_identified': context['leagues'],
                'teams_identified': context['teams'],
                'data_source': 'Limited - API integration required for full functionality',
                'note': 'This is a demonstration response. Real implementation would fetch live sports data.'
            }
            
        except Exception as e:
            logger.error(f"Error getting sports data: {e}")
            return None
    
    def get_compliance_info(self) -> Dict:
        """Get gambling compliance and responsible gambling information"""
        return {
            'responsible_gambling': {
                'national_helpline': '1-800-522-4700',
                'website': 'ncpgambling.org',
                'chat': 'ncpgambling.org/chat',
                'text': 'Text GAMBLER to 53342'
            },
            'age_verification': {
                'minimum_age': 21,
                'note': 'Age requirements vary by jurisdiction'
            },
            'legal_notice': 'Sports betting is only legal in certain jurisdictions. Always verify local laws and regulations.',
            'resources': {
                'gamblers_anonymous': 'gamblersanonymous.org',
                'problem_gambling': 'problemgambling.ca',
                'responsible_gambling_council': 'responsiblegambling.org'
            }
        }
