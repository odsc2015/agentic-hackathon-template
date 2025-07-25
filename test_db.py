import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from db_handler import DatabaseHandler


def test_database_functionality():
    """Test all database functionality."""
    print("🧪 Testing Database Functionality")
    print("=" * 50)
    
    # Initialize database
    db = DatabaseHandler("test_events.db")
    
    # Test 1: Add events
    print("\n1. Testing event creation...")
    now = datetime.now()
    
    # Event 1: Meeting in 2 hours
    event_time_1 = now + timedelta(hours=2)
    reminder_1_1 = now + timedelta(minutes=30)
    reminder_2_1 = now + timedelta(hours=1)
    
    event_id_1 = db.add_event(
        user_id="user123",
        source_chat_id="chat456",
        event_summary="Team meeting at 3 PM",
        event_dt=event_time_1,
        reminder_1_dt=reminder_1_1,
        reminder_2_dt=reminder_2_1
    )
    print(f"   ✅ Created event 1 with ID: {event_id_1}")
    
    # Event 2: Lunch tomorrow
    event_time_2 = now + timedelta(days=1, hours=12)
    reminder_1_2 = now + timedelta(days=1, hours=11)
    
    event_id_2 = db.add_event(
        user_id="user123",
        source_chat_id="chat789",
        event_summary="Lunch with client",
        event_dt=event_time_2,
        reminder_1_dt=reminder_1_2
    )
    print(f"   ✅ Created event 2 with ID: {event_id_2}")
    
    # Event 3: Different user
    event_time_3 = now + timedelta(hours=4)
    
    event_id_3 = db.add_event(
        user_id="user456",
        source_chat_id="chat456",
        event_summary="Project review",
        event_dt=event_time_3
    )
    print(f"   ✅ Created event 3 with ID: {event_id_3}")
    
    # Test 2: Retrieve events
    print("\n2. Testing event retrieval...")
    
    # Get specific event
    event = db.get_event(event_id_1)
    if event:
        print(f"   ✅ Retrieved event: {event['event_summary']}")
    else:
        print("   ❌ Failed to retrieve event")
    
    # Get user events
    user_events = db.get_user_events("user123")
    print(f"   ✅ User 123 has {len(user_events)} events")
    
    # Test 3: Update event
    print("\n3. Testing event update...")
    success = db.update_event(event_id_1, event_summary="Updated: Team meeting at 3 PM")
    if success:
        print("   ✅ Event updated successfully")
        
        # Verify update
        updated_event = db.get_event(event_id_1)
        if updated_event and "Updated:" in updated_event['event_summary']:
            print("   ✅ Update verified")
        else:
            print("   ❌ Update verification failed")
    else:
        print("   ❌ Event update failed")
    
    # Test 4: Get due reminders
    print("\n4. Testing due reminders...")
    
    # Create a past reminder for testing
    past_time = now - timedelta(minutes=5)
    db.update_event(event_id_1, reminder_1_dt=past_time)
    
    due_reminders = db.get_due_reminders(now)
    print(f"   ✅ Found {len(due_reminders)} due reminders")
    
    # Test 5: Database statistics
    print("\n5. Testing database statistics...")
    stats = db.get_database_stats()
    print(f"   ✅ Database stats: {stats}")
    
    # Test 6: Delete event
    print("\n6. Testing event deletion...")
    success = db.delete_event(event_id_3)
    if success:
        print("   ✅ Event deleted successfully")
        
        # Verify deletion
        deleted_event = db.get_event(event_id_3)
        if deleted_event is None:
            print("   ✅ Deletion verified")
        else:
            print("   ❌ Deletion verification failed")
    else:
        print("   ❌ Event deletion failed")
    
    # Final statistics
    print("\n7. Final database statistics...")
    final_stats = db.get_database_stats()
    print(f"   ✅ Final stats: {final_stats}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    
    # # Clean up test database
    # try:
    #     os.remove("test_events.db")
    #     print("🧹 Test database cleaned up")
    # except FileNotFoundError:
    #     pass


if __name__ == "__main__":
    test_database_functionality() 