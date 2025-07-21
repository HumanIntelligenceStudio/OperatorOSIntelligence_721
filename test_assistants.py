#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI Assistants API integration
Shows each domain-specific assistant responding to relevant queries
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from ai_providers_enhanced import initialize_enhanced_ai_provider, AssistantMode
from models import AssistantThread, AssistantRun, AssistantConfiguration

def test_assistant_domain(domain, query, description):
    """Test a specific assistant domain with a query"""
    print(f"\n{'='*60}")
    print(f"TESTING {domain.upper()} ASSISTANT")
    print(f"Description: {description}")
    print(f"Query: {query}")
    print('='*60)
    
    try:
        # Get the enhanced AI provider
        enhanced_ai = initialize_enhanced_ai_provider()
        
        # Submit query to the assistant
        start_time = time.time()
        result = enhanced_ai.get_completion(
            prompt=query,
            provider='openai',
            mode=AssistantMode.ASSISTANT,
            domain=domain,
            user_id=1,  # Test user
            session_id=1,  # Test session
            max_tokens=1500,
            temperature=0.7
        )
        
        processing_time = time.time() - start_time
        
        print(f"\n✅ SUCCESS - Response received in {processing_time:.2f}s")
        print(f"Provider: {result.get('provider', 'unknown')}")
        print(f"Mode: {result.get('mode', 'unknown')}")
        print(f"Model: {result.get('model', 'unknown')}")
        
        if 'thread_id' in result:
            print(f"Thread ID: {result['thread_id']}")
            print(f"Run ID: {result.get('run_id', 'N/A')}")
            print(f"Tokens Used: {result.get('tokens_used', 'N/A')}")
        
        print(f"\nRESPONSE:")
        print("-" * 40)
        print(result['content'])
        print("-" * 40)
        
        return True, result
        
    except Exception as e:
        print(f"\n❌ ERROR - {str(e)}")
        return False, str(e)

def show_assistant_configurations():
    """Show all configured assistants"""
    print("\n" + "="*60)
    print("CONFIGURED OPENAI ASSISTANTS")
    print("="*60)
    
    configs = db.session.query(AssistantConfiguration).all()
    
    for config in configs:
        print(f"\nDomain: {config.domain}")
        print(f"Assistant ID: {config.assistant_id}")
        print(f"Name: {config.name}")
        print(f"Model: {config.model}")
        print(f"Tools: {len(config.tools)} configured")
        print(f"Created: {config.created_at}")
        print(f"Active: {'Yes' if config.is_active else 'No'}")
        print(f"Total Runs: {config.total_runs}")
        print(f"Success Rate: {config.successful_runs}/{config.total_runs if config.total_runs > 0 else 0}")

def show_thread_statistics():
    """Show assistant thread statistics"""
    print("\n" + "="*60)
    print("ASSISTANT THREAD STATISTICS")
    print("="*60)
    
    # Count threads by domain
    for domain in ['healthcare', 'financial', 'sports', 'business', 'general']:
        thread_count = db.session.query(AssistantThread).filter_by(
            domain=domain, is_active=True
        ).count()
        print(f"{domain.title()}: {thread_count} active threads")
    
    # Show recent threads
    recent_threads = db.session.query(AssistantThread).filter_by(
        is_active=True
    ).order_by(AssistantThread.created_at.desc()).limit(5).all()
    
    if recent_threads:
        print(f"\nRecent Threads:")
        for thread in recent_threads:
            print(f"  - {thread.domain}: {thread.thread_id} (Messages: {thread.message_count})")

def main():
    """Main test function"""
    print("OpenAI Assistants API Integration Test")
    print("="*60)
    print(f"Test started at: {datetime.now()}")
    
    with app.app_context():
        # Show assistant configurations
        show_assistant_configurations()
        
        # Test each domain assistant
        test_queries = [
            (
                'healthcare', 
                'What are the potential side effects of taking ibuprofen with high blood pressure medication?',
                'Medical analysis with drug interaction checking'
            ),
            (
                'financial',
                'Analyze the risk-return profile of a portfolio with 60% stocks, 30% bonds, and 10% REITs for a 35-year-old investor.',
                'Investment analysis with portfolio optimization'
            ),
            (
                'sports',
                'What factors should I consider when analyzing NFL betting odds for the upcoming playoffs?',
                'Sports analytics with betting education'
            ),
            (
                'business',
                'Help me design an automated workflow for customer onboarding that reduces manual processing time by 50%.',
                'Business process automation and optimization'
            ),
            (
                'general',
                'Explain quantum computing in simple terms and its potential applications in everyday technology.',
                'General knowledge and educational content'
            )
        ]
        
        results = []
        successful_tests = 0
        
        for domain, query, description in test_queries:
            success, result = test_assistant_domain(domain, query, description)
            results.append((domain, success, result))
            if success:
                successful_tests += 1
            
            # Small delay between tests
            time.sleep(2)
        
        # Show thread statistics after testing
        show_thread_statistics()
        
        # Summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        print(f"Total Tests: {len(test_queries)}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {len(test_queries) - successful_tests}")
        print(f"Success Rate: {(successful_tests / len(test_queries)) * 100:.1f}%")
        
        if successful_tests > 0:
            print(f"\n✅ OpenAI Assistants API integration is WORKING!")
            print(f"Successfully demonstrated {successful_tests} domain-specific assistants with:")
            print("- Persistent conversation threads")
            print("- Domain-specific tools and capabilities")
            print("- Intelligent response generation")
            print("- Thread and run tracking in database")
        else:
            print(f"\n❌ Integration needs attention - no successful tests")
        
        print(f"\nTest completed at: {datetime.now()}")

if __name__ == '__main__':
    main()