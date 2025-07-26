#!/usr/bin/env python3
"""
Test script for the Gemini API wrapper.
This script tests the analyze_chat function with various scenarios.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.llm_tool import analyze_chat, GeminiAnalyzer


def test_gemini_analyzer():
    """Test the Gemini analyzer with various chat scenarios."""
    print("🧪 Testing Gemini API Wrapper")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Team Meeting Agreement",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Hey team, should we have a meeting tomorrow at 3 PM?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'That works for me!',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user3',
                    'username': 'Charlie',
                    'message': 'I can make it too.',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "Lunch Plan",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'How about lunch on Friday?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Sure, where should we go?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'How about that new Italian place downtown?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Perfect!',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "No Agreement - General Discussion",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'How was your weekend?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'It was great! Went hiking.',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'That sounds fun!',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "Dinner Tonight",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Dinner tonight at 7 PM?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Yes, sounds good!',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "Project Call Next Week",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'We should have a project review call next week',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Good idea. How about Tuesday at 10 AM?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Perfect!',
                    'timestamp': datetime.now()
                }
            ]
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print("-" * 30)
        
        try:
            result = analyze_chat(scenario['messages'])
            
            if result:
                if result.get('agreement_detected'):
                    print("✅ Agreement detected!")
                    print(f"   Event: {result.get('event_summary', 'N/A')}")
                    print(f"   DateTime: {result.get('event_datetime', 'N/A')}")
                    print(f"   Participants: {result.get('participants', [])}")
                    print(f"   Location: {result.get('location', 'N/A')}")
                    print(f"   Type: {result.get('event_type', 'N/A')}")
                    print(f"   Confidence: {result.get('confidence', 'N/A')}")
                else:
                    print("❌ No agreement detected (as expected for general discussion)")
            else:
                print("❌ Analysis failed or returned None")
                
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Gemini API wrapper testing completed!")


def test_gemini_analyzer_class():
    """Test the GeminiAnalyzer class directly."""
    print("\n🧪 Testing GeminiAnalyzer Class")
    print("=" * 50)
    
    try:
        # Initialize the analyzer
        analyzer = GeminiAnalyzer()
        print("✅ GeminiAnalyzer initialized successfully")
        
        # Test with a simple scenario
        test_messages = [
            {
                'user_id': 'user1',
                'username': 'Alice',
                'message': 'Let\'s meet tomorrow at 2 PM for the project review',
                'timestamp': datetime.now()
            },
            {
                'user_id': 'user2',
                'username': 'Bob',
                'message': 'Works for me!',
                'timestamp': datetime.now()
            }
        ]
        
        result = analyzer.analyze_chat_simple(test_messages)
        
        if result and result.get('agreement_detected'):
            print("✅ Class-based analysis successful!")
            print(f"   Result: {json.dumps(result, indent=2, default=str)}")
        else:
            print("❌ Class-based analysis failed or no agreement detected")
            
    except Exception as e:
        print(f"❌ Error testing GeminiAnalyzer class: {e}")


if __name__ == "__main__":
    # Check if GEMINI_API_KEY is set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   Please set your Gemini API key to test the functionality")
        print("   You can set it with: export GEMINI_API_KEY='your-api-key'")
        print("   Or create a .env file with: GEMINI_API_KEY=your-api-key")
        sys.exit(1)
    
    # Run tests
    test_gemini_analyzer()
    test_gemini_analyzer_class()
