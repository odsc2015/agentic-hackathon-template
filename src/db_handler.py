import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union, Tuple
from contextlib import contextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class DatabaseHandler:
    """SQLite database handler for managing events and reminders."""
    
    def __init__(self, db_path: str = "events.db"):
        self.db_path = db_path
        self._connection = None
        self.init_database()
    
    def init_database(self):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create Events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        source_chat_id TEXT NOT NULL,
                        event_summary TEXT NOT NULL,
                        event_dt DATETIME NOT NULL,
                        reminder_1_dt DATETIME,
                        reminder_2_dt DATETIME,
                        status TEXT DEFAULT 'pending',
                        creation_dt DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id 
                    ON Events(user_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reminder_1_dt 
                    ON Events(reminder_1_dt)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_reminder_2_dt 
                    ON Events(reminder_2_dt)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_event_dt 
                    ON Events(event_dt)
                ''')
                
                conn.commit()
                logger.info(f"Database initialized successfully at {self.db_path}")
                
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        if not self._connection:
            self._connection = sqlite3.connect(self.db_path)
        try:
            yield self._connection
        except Exception:
            self._connection.rollback()
            raise
        finally:
            self._connection.commit()
    
    def add_event(self, user_id: str, source_chat_id: str, event_summary: str, 
                  event_dt: datetime, reminder_1_dt: Optional[datetime] = None, 
                  reminder_2_dt: Optional[datetime] = None) -> int:
        """
        Add a new event to the database.
        
        Args:
            user_id: ID of the user who created the event
            source_chat_id: ID of the chat where the event was mentioned
            event_summary: Summary/description of the event
            event_dt: Exact date and time of the event
            reminder_1_dt: Time for the first reminder (optional)
            reminder_2_dt: Time for the second reminder (optional)
            
        Returns:
            event_id: The ID of the newly created event
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO Events (user_id, source_chat_id, event_summary, 
                                      event_dt, reminder_1_dt, reminder_2_dt)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, source_chat_id, event_summary, event_dt, 
                     reminder_1_dt, reminder_2_dt))
                
                event_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Event added successfully with ID: {event_id}")
                return event_id
                
        except sqlite3.Error as e:
            logger.error(f"Error adding event: {e}")
            raise
    
    def get_event(self, event_id: int) -> Union[Dict[str, Any], None]:
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''SELECT * FROM Events WHERE event_id = ?''', (event_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving event: {e}")
            raise DatabaseError(f"Failed to get event {event_id}: {e}")
    
    def get_user_events(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM Events WHERE user_id = ? 
                    ORDER BY event_dt ASC
                ''', (user_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving user events: {e}")
            raise
    
    def get_due_reminders(self, current_time: datetime) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM Events 
                    WHERE (reminder_1_dt IS NOT NULL AND reminder_1_dt <= ?)
                       OR (reminder_2_dt IS NOT NULL AND reminder_2_dt <= ?)
                    ORDER BY reminder_1_dt ASC, reminder_2_dt ASC
                ''', (current_time, current_time))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving due reminders: {e}")
            raise
    
    def get_due_reminders_with_status(self, current_time: datetime) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM Events 
                    WHERE (reminder_1_dt IS NOT NULL AND reminder_1_dt <= ? AND status = 'pending')
                       OR (reminder_2_dt IS NOT NULL AND reminder_2_dt <= ? AND status = 'reminded_1')
                    ORDER BY reminder_1_dt ASC, reminder_2_dt ASC
                ''', (current_time, current_time))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving due reminders with status: {e}")
            raise
    
    def update_event(self, event_id: int, **kwargs) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                valid_fields = [
                    'user_id', 'source_chat_id', 'event_summary', 'event_dt', 'reminder_1_dt',
                    'reminder_2_dt', 'status'
                ]
                update_fields = []
                values = []
                
                for field, value in kwargs.items():
                    if field in valid_fields:
                        update_fields.append(f"{field} = ?")
                        values.append(value)
                
                if not update_fields:
                    logger.warning("No valid fields to update")
                    return False
                
                values.append(event_id)
                query = f"UPDATE Events SET {', '.join(update_fields)} WHERE event_id = ?"
                
                cursor.execute(query, values)
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Event {event_id} updated successfully")
                    return True
                else:
                    logger.warning(f"Event {event_id} not found for update")
                    return False
                
        except sqlite3.Error as e:
            logger.error(f"Error updating event: {e}")
            raise
    
    def delete_event(self, event_id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM Events WHERE event_id = ?', (event_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"Event {event_id} deleted successfully")
                    return True
                else:
                    logger.warning(f"Event {event_id} not found for deletion")
                    return False
                
        except sqlite3.Error as e:
            logger.error(f"Error deleting event: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    COUNT(*) as total_events,
                    SUM(CASE WHEN reminder_1_dt IS NOT NULL OR reminder_2_dt IS NOT NULL THEN 1 ELSE 0 END) as events_with_reminders,
                    SUM(CASE WHEN event_dt >= datetime('now') AND event_dt <= datetime('now', '+7 days') THEN 1 ELSE 0 END) as upcoming_events
                FROM Events
                """
                cursor.execute(query)
                result = cursor.fetchone()
                
                return {
                    'total_events': result[0],
                    'events_with_reminders': result[1],
                    'upcoming_events': result[2]
                }
                
        except sqlite3.Error as e:
            logger.error(f"Error getting database stats: {e}")
            raise


if __name__ == "__main__":
    db = DatabaseHandler()
    
    # Example: Add a test event
    now = datetime.now()
    event_time = now + timedelta(hours=2)
    reminder_1 = now + timedelta(minutes=30)
    reminder_2 = now + timedelta(hours=1)
    
    event_id = db.add_event(
        user_id="user123",
        source_chat_id="chat456",
        event_summary="Team meeting at 3 PM",
        event_dt=event_time,
        reminder_1_dt=reminder_1,
        reminder_2_dt=reminder_2
    )
    print(f"Created event with ID: {event_id}")

    stats = db.get_database_stats()
    print(f"Database stats: {stats}")

