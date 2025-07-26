import sys
import os
import json
import time
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scheduler import ReminderScheduler
from db_handler import DatabaseHandler


def test_scheduler_functionality():
    """Test the scheduler functionality."""
    print("🧪 Testing ReminderScheduler Functionality")
    print("=" * 60)
    
    # Use a unique database file for this test
    import uuid
    test_db_path = f"test_scheduler_{uuid.uuid4().hex[:8]}.db"
    
    # Initialize database and scheduler
    db = DatabaseHandler(test_db_path)
    scheduler = ReminderScheduler(test_db_path)
    
    # Create test events with different reminder times
    now = datetime.now()
    
    # Event 1: Reminder 1 due in 1 minute
    event_time_1 = now + timedelta(hours=2)
    reminder_1_time = now + timedelta(minutes=1)  # Due very soon
    
    event_id_1 = db.add_event(
        user_id="user1",
        source_chat_id="chat1",
        event_summary="Test meeting in 2 hours",
        event_dt=event_time_1,
        reminder_1_dt=reminder_1_time,
        reminder_2_dt=now + timedelta(hours=1)
    )
    
    # Event 2: Reminder 2 due in 2 minutes (status should be 'reminded_1')
    event_time_2 = now + timedelta(hours=3)
    reminder_2_time = now + timedelta(minutes=2)
    
    event_id_2 = db.add_event(
        user_id="user2",
        source_chat_id="chat2",
        event_summary="Test meeting in 3 hours",
        event_dt=event_time_2,
        reminder_1_dt=now - timedelta(hours=1),  # Already passed
        reminder_2_dt=reminder_2_time
    )
    
    # Manually set status for event 2 to 'reminded_1'
    db.update_event(event_id_2, status='reminded_1')
    
    # Event 3: No reminders due
    event_time_3 = now + timedelta(hours=4)
    
    event_id_3 = db.add_event(
        user_id="user3",
        source_chat_id="chat3",
        event_summary="Test meeting in 4 hours",
        event_dt=event_time_3,
        reminder_1_dt=now + timedelta(hours=2),  # Not due yet
        reminder_2_dt=now + timedelta(hours=3)
    )
    
    print(f"Created test events:")
    print(f"  Event 1 (ID: {event_id_1}): Reminder 1 due in 1 minute")
    print(f"  Event 2 (ID: {event_id_2}): Reminder 2 due in 2 minutes (status: reminded_1)")
    print(f"  Event 3 (ID: {event_id_3}): No reminders due")
    
    # Test the reminder checking function
    print(f"\n🔍 Testing reminder checking...")
    
    # Wait for reminders to become due
    print("Waiting for reminders to become due...")
    time.sleep(70)  # Wait 70 seconds for reminders to be due
    
    # Manually call the reminder checking function
    scheduler.check_and_send_reminders()
    
    # Check the results
    print(f"\n📊 Checking results...")
    
    # Get updated event information
    event_1 = db.get_event(event_id_1)
    event_2 = db.get_event(event_id_2)
    event_3 = db.get_event(event_id_3)
    
    print(f"Event 1 status: {event_1.get('status', 'unknown') if event_1 else 'not found'}")
    print(f"Event 2 status: {event_2.get('status', 'unknown') if event_2 else 'not found'}")
    print(f"Event 3 status: {event_3.get('status', 'unknown') if event_3 else 'not found'}")
    
    # Verify expected status changes
    if event_1 and event_1.get('status') == 'reminded_1':
        print("✅ Event 1: Status correctly updated to 'reminded_1'")
    else:
        print("❌ Event 1: Status not updated correctly")
    
    if event_2 and event_2.get('status') == 'reminded_2':
        print("✅ Event 2: Status correctly updated to 'reminded_2'")
    else:
        print("❌ Event 2: Status not updated correctly")
    
    if event_3 and event_3.get('status') == 'pending':
        print("✅ Event 3: Status correctly remains 'pending'")
    else:
        print("❌ Event 3: Status unexpectedly changed")
    
    print("\n" + "=" * 60)
    print("🎉 Scheduler testing completed!")
    
    # Clean up
    try:
        os.remove(test_db_path)
        print("🧹 Test database cleaned up")
    except FileNotFoundError:
        pass


def test_scheduler_status():
    """Test the scheduler status functionality."""
    print("\n🧪 Testing Scheduler Status")
    print("=" * 40)
    
    scheduler = ReminderScheduler("test_status.db")
    
    # Check status before starting
    status_before = scheduler.get_scheduler_status()
    print(f"Status before starting: {json.dumps(status_before, indent=2)}")
    
    # Start the scheduler
    scheduler.start()
    
    # Check status after starting
    status_after = scheduler.get_scheduler_status()
    print(f"Status after starting: {json.dumps(status_after, indent=2)}")
    
    # Stop the scheduler
    scheduler.stop()
    
    # Check status after stopping
    status_stopped = scheduler.get_scheduler_status()
    print(f"Status after stopping: {json.dumps(status_stopped, indent=2)}")
    
    print("\n" + "=" * 40)
    print("🎉 Scheduler status testing completed!")
    
    # Clean up
    try:
        os.remove("test_status.db")
        print("🧹 Test database cleaned up")
    except FileNotFoundError:
        pass


def test_message_formatting():
    """Test the message formatting functionality."""
    print("\n🧪 Testing Message Formatting")
    print("=" * 40)
    
    scheduler = ReminderScheduler()
    
    # Test cases
    test_cases = [
        {
            "event_summary": "Team meeting",
            "event_dt": datetime.now() + timedelta(days=1),
            "is_first_reminder": True,
            "description": "Reminder 1 for tomorrow"
        },
        {
            "event_summary": "Lunch with client",
            "event_dt": datetime.now() + timedelta(hours=2),
            "is_first_reminder": False,
            "description": "Reminder 2 for today"
        },
        {
            "event_summary": "Project review",
            "event_dt": datetime.now() + timedelta(minutes=30),
            "is_first_reminder": True,
            "description": "Reminder 1 for soon"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['description']}:")
        message = scheduler._format_reminder_message(
            case['event_summary'],
            case['event_dt'],
            case['is_first_reminder']
        )
        print(f"   Message: {message}")
    
    print("\n" + "=" * 40)
    print("🎉 Message formatting testing completed!")


def test_due_reminders_query():
    """Test the due reminders query functionality."""
    print("\n🧪 Testing Due Reminders Query")
    print("=" * 40)
    
    db = DatabaseHandler("test_query.db")
    
    # Create test events with specific statuses
    now = datetime.now()
    
    # Event with pending status and due reminder 1
    event_id_1 = db.add_event(
        user_id="user1",
        source_chat_id="chat1",
        event_summary="Test event 1",
        event_dt=now + timedelta(hours=2),
        reminder_1_dt=now - timedelta(minutes=5),  # Due 5 minutes ago
        reminder_2_dt=now + timedelta(hours=1)
    )
    
    # Event with reminded_1 status and due reminder 2
    event_id_2 = db.add_event(
        user_id="user2",
        source_chat_id="chat2",
        event_summary="Test event 2",
        event_dt=now + timedelta(hours=3),
        reminder_1_dt=now - timedelta(hours=1),
        reminder_2_dt=now - timedelta(minutes(3))  # Due 3 minutes ago
    )
    db.update_event(event_id_2, status='reminded_1')
    
    # Event with pending status but no due reminders
    event_id_3 = db.add_event(
        user_id="user3",
        source_chat_id="chat3",
        event_summary="Test event 3",
        event_dt=now + timedelta(hours=4),
        reminder_1_dt=now + timedelta(hours=1),  # Not due yet
        reminder_2_dt=now + timedelta(hours=2)
    )
    
    # Test the query
    due_reminders = db.get_due_reminders_with_status(now)
    
    print(f"Found {len(due_reminders)} due reminders:")
    for reminder in due_reminders:
        print(f"  Event ID: {reminder['event_id']}")
        print(f"  Summary: {reminder['event_summary']}")
        print(f"  Status: {reminder['status']}")
        print(f"  Reminder 1: {reminder.get('reminder_1_dt')}")
        print(f"  Reminder 2: {reminder.get('reminder_2_dt')}")
        print()
    
    # Verify expected results
    expected_event_ids = {event_id_1, event_id_2}
    found_event_ids = {reminder['event_id'] for reminder in due_reminders}
    
    if expected_event_ids == found_event_ids:
        print("✅ Due reminders query working correctly")
    else:
        print("❌ Due reminders query not working as expected")
        print(f"Expected: {expected_event_ids}")
        print(f"Found: {found_event_ids}")
    
    print("\n" + "=" * 40)
    print("🎉 Due reminders query testing completed!")
    
    # Clean up
    try:
        os.remove("test_query.db")
        print("🧹 Test database cleaned up")
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    # Run all tests
    test_scheduler_functionality()
    test_scheduler_status()
    test_message_formatting()
    test_due_reminders_query()
