#!/usr/bin/env python3
"""
Integration test demonstrating the complete flow:
Chat Analysis -> Confidence Check -> Database Storage
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from processor import process_chat
from db_handler import DatabaseHandler
from tools.llm_tool import analyze_chat


def test_complete_integration():
    """Test the complete integration flow."""
    print("🔗 Testing Complete Integration Flow")
    print("=" * 60)
    
    # Initialize database
    db = DatabaseHandler("test_integration.db")
    
    # Test scenarios
    scenarios = [
        {
            "name": "High Confidence Team Meeting",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Team meeting tomorrow at 3 PM in the conference room',
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
                    'message': 'Perfect, see you all tomorrow.',
                    'timestamp': datetime.now()
                }
            ],
            "expected_outcome": "Should save to database (confidence > 0.8)"
        },
        {
            "name": "Medium Confidence Discussion",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Maybe we should have a call sometime next week?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Yeah, that could work.',
                    'timestamp': datetime.now()
                }
            ],
            "expected_outcome": "Should NOT save to database (confidence < 0.8)"
        },
        {
            "name": "Lunch Plan with Location",
            "messages": [
                {
                    'user_id': 'user1',
                    'username': 'Alice',
                    'message': 'Lunch today at 12 PM at the Italian restaurant?',
                    'timestamp': datetime.now()
                },
                {
                    'user_id': 'user2',
                    'username': 'Bob',
                    'message': 'Sounds great! I\'ll meet you there.',
                    'timestamp': datetime.now()
                }
            ],
            "expected_outcome": "Should save to database (confidence > 0.8)"
        }
    ]
    
    # Track results
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        print(f"   Expected: {scenario['expected_outcome']}")
        print("-" * 50)
        
        # Get initial database count
        initial_stats = db.get_database_stats()
        initial_count = initial_stats['total_events']
        
        # Process the chat
        result = process_chat(scenario['messages'], f"chat_{i}")
        
        if result:
            if result.get('error'):
                print(f"❌ Error: {result['message']}")
                results.append({
                    'scenario': scenario['name'],
                    'status': 'error',
                    'message': result['message']
                })
            elif result.get('event_detected'):
                if result.get('threshold_met'):
                    print("✅ Event detected and saved to database!")
                    print(f"   Event ID: {result.get('event_id')}")
                    print(f"   Confidence: {result.get('confidence')}")
                    print(f"   Summary: {result.get('event_summary')}")
                    print(f"   DateTime: {result.get('event_datetime')}")
                    print(f"   Participants: {result.get('participants')}")
                    print(f"   Location: {result.get('location', 'N/A')}")
                    print(f"   Reminder 1: {result.get('reminder_1_dt', 'N/A')}")
                    print(f"   Reminder 2: {result.get('reminder_2_dt', 'N/A')}")
                    
                    # Verify database was updated
                    final_stats = db.get_database_stats()
                    final_count = final_stats['total_events']
                    
                    if final_count > initial_count:
                        print(f"   ✅ Database updated: {initial_count} -> {final_count} events")
                    else:
                        print(f"   ❌ Database not updated: {initial_count} -> {final_count} events")
                    
                    results.append({
                        'scenario': scenario['name'],
                        'status': 'saved',
                        'event_id': result.get('event_id'),
                        'confidence': result.get('confidence')
                    })
                else:
                    print("⚠️  Event detected but confidence below threshold")
                    print(f"   Confidence: {result.get('confidence')}")
                    print(f"   Threshold: 0.8")
                    
                    # Verify database was NOT updated
                    final_stats = db.get_database_stats()
                    final_count = final_stats['total_events']
                    
                    if final_count == initial_count:
                        print(f"   ✅ Database unchanged: {initial_count} events")
                    else:
                        print(f"   ❌ Database unexpectedly updated: {initial_count} -> {final_count} events")
                    
                    results.append({
                        'scenario': scenario['name'],
                        'status': 'below_threshold',
                        'confidence': result.get('confidence')
                    })
            else:
                print("❌ No event detected")
                results.append({
                    'scenario': scenario['name'],
                    'status': 'no_event'
                })
        else:
            print("❌ Processing returned None")
            results.append({
                'scenario': scenario['name'],
                'status': 'failed'
            })
    
    # Summary
    print(f"\n📊 Integration Test Summary")
    print("=" * 40)
    
    saved_count = len([r for r in results if r['status'] == 'saved'])
    below_threshold_count = len([r for r in results if r['status'] == 'below_threshold'])
    no_event_count = len([r for r in results if r['status'] == 'no_event'])
    error_count = len([r for r in results if r['status'] == 'error'])
    
    print(f"Events saved to database: {saved_count}")
    print(f"Events below threshold: {below_threshold_count}")
    print(f"No events detected: {no_event_count}")
    print(f"Errors: {error_count}")
    
    # Final database stats
    final_stats = db.get_database_stats()
    print(f"\nFinal Database Stats:")
    print(f"   Total events: {final_stats['total_events']}")
    print(f"   Events with reminders: {final_stats['events_with_reminders']}")
    print(f"   Upcoming events: {final_stats['upcoming_events']}")
    
    print("\n" + "=" * 60)
    print("🎉 Integration testing completed!")
    
    # Clean up
    try:
        os.remove("test_integration.db")
        print("🧹 Test database cleaned up")
    except FileNotFoundError:
        pass
    
    return results


def test_confidence_threshold_behavior():
    """Test the confidence threshold behavior specifically."""
    print("\n🎯 Testing Confidence Threshold Behavior")
    print("=" * 50)
    
    # Test different confidence levels
    confidence_levels = [0.9, 0.8, 0.79, 0.7, 0.6]
    
    for confidence in confidence_levels:
        print(f"\nTesting confidence level: {confidence}")
        
        # Create a mock result with specific confidence
        mock_messages = [
            {
                'user_id': 'user1',
                'username': 'Alice',
                'message': f'Test meeting with confidence {confidence}',
                'timestamp': datetime.now()
            }
        ]
        
        # Process with mock confidence
        result = process_chat(mock_messages, f"confidence_test_{confidence}")
        
        if result and result.get('event_detected'):
            threshold_met = result.get('threshold_met', False)
            actual_confidence = result.get('confidence', 0)
            
            if threshold_met:
                print(f"   ✅ Confidence {actual_confidence} >= 0.8: Event saved")
            else:
                print(f"   ⚠️  Confidence {actual_confidence} < 0.8: Event not saved")
        else:
            print(f"   ❌ No event detected")
    
    print("\n" + "=" * 50)
    print("🎉 Confidence threshold testing completed!")


if __name__ == "__main__":
    # Check if GEMINI_API_KEY is set
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  Warning: GEMINI_API_KEY environment variable not set")
        print("   This test will work with simulated confidence levels")
        print("   Set your API key for real Gemini analysis")
    
    # Run integration tests
    test_complete_integration()
    test_confidence_threshold_behavior() 