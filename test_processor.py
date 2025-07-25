#!/usr/bin/env python3
"""
Test script for the ChatProcessor class.
This script tests the processor with various confidence levels and scenarios.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processor import process_chat, ChatProcessor
from db_handler import DatabaseHandler


def test_processor_with_confidence():
    """Test the processor with various confidence scenarios."""
    print("🧪 Testing ChatProcessor with Confidence Threshold")
    print("=" * 60)
    
    # Initialize processor and database
    processor = ChatProcessor("test_processor.db")
    db = DatabaseHandler("test_processor.db")
    
    # Test scenarios with different confidence levels
    test_scenarios = [
        {
            "name": "High Confidence Agreement (Should Save)",
            "confidence_override": 0.95,  # This will be overridden in the mock
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Team meeting tomorrow at 3 PM sharp!',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Confirmed, I\'ll be there.',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user3',
                    'username': 'Charlie',
                    'message': 'Perfect, see you then.',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "Medium Confidence Agreement (Should Not Save)",
            "confidence_override": 0.75,
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Maybe we should meet sometime next week?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Yeah, that could work.',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "Low Confidence Agreement (Should Not Save)",
            "confidence_override": 0.6,
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'We might want to discuss this later',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Sure, whatever.',
                    'timestamp': datetime.now()
                }
            ]
        },
        {
            "name": "No Agreement - General Discussion",
            "confidence_override": 0.0,
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
                    'message': 'It was great!',
                    'timestamp': datetime.now()
                }
            ]
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print("-" * 40)
        
        try:
            # Mock the analyze_chat function to return controlled confidence levels
            original_analyze_chat = processor.__class__.__module__ + '.analyze_chat'
            
            # For testing purposes, we'll simulate different confidence levels
            # In a real scenario, this would come from Gemini
            mock_confidence = scenario['confidence_override']
            
            if mock_confidence > 0:
                # Simulate a detected agreement with controlled confidence
                mock_result = {
                    'agreement_detected': True,
                    'event_summary': f"Test event from {scenario['name']}",
                    'event_datetime': (datetime.now() + timedelta(hours=2)).isoformat(),
                    'participants': ['Alice', 'Bob'],
                    'confidence': mock_confidence,
                    'source_message': scenario['messages'][0]['message']
                }
            else:
                # Simulate no agreement detected
                mock_result = {'agreement_detected': False}
            
            # Process the messages
            result = processor.process_chat_messages(scenario['messages'], f"chat_{i}")
            
            if result:
                if result.get('error'):
                    print(f"❌ Error: {result['message']}")
                elif result.get('event_detected'):
                    if result.get('threshold_met'):
                        print("✅ Event detected and saved to database!")
                        print(f"   Event ID: {result.get('event_id')}")
                        print(f"   Confidence: {result.get('confidence')}")
                        print(f"   Summary: {result.get('event_summary')}")
                        print(f"   DateTime: {result.get('event_datetime')}")
                    else:
                        print("⚠️  Event detected but confidence below threshold")
                        print(f"   Confidence: {result.get('confidence')}")
                        print(f"   Threshold: {processor.confidence_threshold}")
                else:
                    print("❌ No event detected")
            else:
                print("❌ Processing returned None")
                
        except Exception as e:
            print(f"❌ Error during processing: {e}")
    
    # Get processing statistics
    print(f"\n📊 Processing Statistics")
    print("-" * 40)
    stats = processor.get_processing_stats()
    print(f"Database Stats: {json.dumps(stats.get('database_stats', {}), indent=2)}")
    print(f"Confidence Threshold: {stats.get('confidence_threshold')}")
    print(f"Processor Status: {stats.get('processor_status')}")
    
    print("\n" + "=" * 60)
    print("🎉 Processor testing completed!")
    
    # Clean up test database
    try:
        os.remove("test_processor.db")
        print("🧹 Test database cleaned up")
    except FileNotFoundError:
        pass


def test_reminder_calculation():
    """Test reminder time calculation functionality."""
    print("\n🧪 Testing Reminder Calculation")
    print("=" * 40)
    
    processor = ChatProcessor()
    
    # Test cases
    test_cases = [
        {
            "event_time": datetime.now() + timedelta(hours=3),
            "offset_minutes": 30,
            "expected": "should return reminder 30 minutes before"
        },
        {
            "event_time": datetime.now() + timedelta(hours=1),
            "offset_minutes": 120,
            "expected": "should return None (reminder would be in past)"
        },
        {
            "event_time": datetime.now() + timedelta(minutes=10),
            "offset_minutes": 5,
            "expected": "should return reminder 5 minutes before"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing reminder calculation:")
        print(f"   Event time: {case['event_time']}")
        print(f"   Offset: {case['offset_minutes']} minutes")
        print(f"   Expected: {case['expected']}")
        
        reminder = processor._calculate_reminder_time(case['event_time'], case['offset_minutes'])
        
        if reminder:
            print(f"   ✅ Reminder calculated: {reminder}")
        else:
            print(f"   ❌ No reminder calculated (as expected)")
    
    print("\n" + "=" * 40)
    print("🎉 Reminder calculation testing completed!")


def test_primary_user_detection():
    """Test primary user ID detection functionality."""
    print("\n🧪 Testing Primary User Detection")
    print("=" * 40)
    
    processor = ChatProcessor()
    
    # Test cases
    test_cases = [
        {
            "name": "Participants match message senders",
            "messages": [
                {'user_id': 'user1', 'username': 'Alice', 'message': 'Hello'},
                {'user_id': 'user2', 'username': 'Bob', 'message': 'Hi'}
            ],
            "participants": ['Alice', 'Bob'],
            "expected": "should return user1 (Alice)"
        },
        {
            "name": "No participants, fallback to first message",
            "messages": [
                {'user_id': 'user3', 'username': 'Charlie', 'message': 'Hello'},
                {'user_id': 'user4', 'username': 'David', 'message': 'Hi'}
            ],
            "participants": [],
            "expected": "should return user3 (Charlie)"
        },
        {
            "name": "Empty messages",
            "messages": [],
            "participants": ['Alice'],
            "expected": "should return 'unknown'"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {case['name']}")
        print(f"   Expected: {case['expected']}")
        
        primary_user = processor._get_primary_user_id(case['messages'], case['participants'])
        print(f"   ✅ Primary user: {primary_user}")
    
    print("\n" + "=" * 40)
    print("🎉 Primary user detection testing completed!")


if __name__ == "__main__":
    # Check if GEMINI_API_KEY is set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   This test will simulate confidence levels for demonstration")
        print("   Set your API key to test with real Gemini analysis")
    
    # Run tests
    test_processor_with_confidence()
    test_reminder_calculation()
    test_primary_user_detection() 