import sqlite3
import os
from ..config import BASE_DIR
from ..utils.logger import logger

DB_PATH = os.path.join(BASE_DIR, "moon_assistant.db")

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        
        # Scheduled messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT NOT NULL,
                message TEXT NOT NULL,
                schedule_time TEXT NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

def add_contact(name, phone):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO contacts (name, phone) VALUES (?, ?)", (name.lower(), phone))
        conn.commit()
        conn.close()
        return f"Contact {name} saved with number {phone}."
    except Exception as e:
        logger.error(f"Error adding contact: {e}")
        return f"Failed to save contact: {e}"

def get_contact(name):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM contacts WHERE name = ?", (name.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting contact: {e}")
        return None

def list_contacts():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone FROM contacts")
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error listing contacts: {e}")
        return []

def save_scheduled_message(phone, message, schedule_time):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO scheduled_messages (phone, message, schedule_time) VALUES (?, ?, ?)", 
                       (phone, message, schedule_time))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving scheduled message: {e}")
        return False

def get_pending_messages():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, phone, message, schedule_time FROM scheduled_messages WHERE status = 'pending'")
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error getting pending messages: {e}")
        return []

def mark_message_done(msg_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE scheduled_messages SET status = 'completed' WHERE id = ?", (msg_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error marking message done: {e}")

# Initialize on import
init_db()
