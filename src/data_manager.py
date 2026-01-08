import streamlit as st
import pandas as pd
from datetime import datetime
from src.database import run_query, init_db

# Initialize DB on first load of this module
init_db()

def load_habits(active_only=True):
    """Load all habits from SQLite."""
    query = "SELECT * FROM habits"
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY created_at DESC"
    
    df = run_query(query, return_df=True)
    if df.empty:
        # Return empty df with expected columns
        return pd.DataFrame(columns=['id', 'name', 'category', 'frequency_type', 'frequency_value', 'target_value', 'target_unit', 'created_at', 'is_active'])
    return df

def load_logs(days_back=30):
    """Load logs for recent history."""
    # Limit to recent logs for performance, unless needed otherwise
    query = f"""
        SELECT * FROM logs 
        WHERE date >= date('now', '-{days_back} days')
        ORDER BY date DESC
    """
    df = run_query(query, return_df=True)
    if df.empty:
        return pd.DataFrame(columns=['id', 'habit_id', 'date', 'value', 'status', 'notes', 'timestamp'])
    return df

def add_habit(habit_data):
    """Add a new habit to the database."""
    query = """
        INSERT INTO habits (name, category, frequency_type, frequency_value, target_value)
        VALUES (?, ?, ?, ?, ?)
    """
    params = (
        habit_data['name'], 
        habit_data['category'], 
        habit_data['frequency_type'], 
        habit_data['frequency_value'],
        habit_data.get('target_value', 1)
    )
    
    try:
        run_query(query, params)
        # Clear cache logic if we were using st.cache_data, but with SQL we just requery
        return True
    except Exception as e:
        st.error(f"Error adding habit: {e}")
        return False

def edit_habit(habit_id, updated_data):
    """Update an existing habit."""
    query = """
        UPDATE habits 
        SET name = ?, category = ?, frequency_type = ?, frequency_value = ?, target_value = ?
        WHERE id = ?
    """
    params = (
        updated_data['name'],
        updated_data['category'],
        updated_data['frequency_type'],
        updated_data['frequency_value'],
        updated_data['target_value'],
        habit_id
    )
    try:
        run_query(query, params)
        return True
    except Exception as e:
        st.error(f"Error updating habit: {e}")
        return False

def delete_habit(habit_id):
    """Soft delete a habit."""
    query = "UPDATE habits SET is_active = 0 WHERE id = ?"
    try:
        run_query(query, (habit_id,))
        return True
    except Exception as e:
        st.error(f"Error deleting habit: {e}")
        return False

def log_habit_completion(habit_id, date, status="Completed", notes="", value=1):
    """Log a habit completion, strictly preventing duplicates for the same day."""
    
    # Check for existing log for this habit and date
    check_query = "SELECT id FROM logs WHERE habit_id = ? AND date = ?"
    existing = run_query(check_query, (habit_id, str(date)))
    
    if existing:
        # Already logged
        return False
        
    query = """
        INSERT INTO logs (habit_id, date, status, notes, value)
        VALUES (?, ?, ?, ?, ?)
    """
    try:
        run_query(query, (habit_id, str(date), status, notes, value))
        return True
    except Exception as e:
        st.error(f"Error logging habit: {e}")
        return False

def get_habit_stats(habit_id):
    """Get simple stats for a habit."""
    query = """
        SELECT COUNT(*) as count, MAX(date) as last_log 
        FROM logs 
        WHERE habit_id = ?
    """
    res = run_query(query, (habit_id,))
    if res:
        return res[0]
    return None

# --- Reminder System ---

def add_reminder(text, priority='medium'):
    query = "INSERT INTO reminders (text, priority) VALUES (?, ?)"
    try:
        run_query(query, (text, priority))
        return True
    except Exception as e:
        st.error(f"Error adding reminder: {e}")
        return False

def get_reminders(pending_only=True):
    query = "SELECT * FROM reminders"
    if pending_only:
        query += " WHERE is_completed = 0"
    query += " ORDER BY created_at DESC"
    return run_query(query, return_df=True)

def update_reminder_status(reminder_id, is_completed=True):
    # Using 1/0 for boolean in SQLite
    val = 1 if is_completed else 0
    query = "UPDATE reminders SET is_completed = ? WHERE id = ?"
    try:
        run_query(query, (val, reminder_id))
        return True
    except:
        return False

def delete_reminder(reminder_id):
    query = "DELETE FROM reminders WHERE id = ?"
    try:
        run_query(query, (reminder_id,))
        return True
    except:
        return False

