import streamlit as st
import pandas as pd
import datetime
from src.database import init_db
from src.data_manager import (
    add_project, get_projects, load_habits, load_logs, add_habit, log_habit_completion, delete_habit, edit_habit,
    add_reminder, get_reminders, update_project_status, update_reminder_status, delete_reminder
)
from src.ui_components import render_add_habit_form, render_habit_card, render_edit_habit_form
from src.analytics import render_analytics
from src.ml_logic import get_motivational_message, get_smart_suggestions
from src.utils import is_habit_due

st.set_page_config(
    page_title="Smart Habit Tracker",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✨ Smart Habit Tracker")

# DB Initialization
if "db_initialized" not in st.session_state:
    if init_db():
        st.session_state.db_initialized = True
    else:
        st.error("Failed to initialize database.")
        st.stop()

# Navigation
selected_tab = st.radio(
    "Navigation", 
    ["🔥 Dashboard", "➕ Add Habit", "📝 Add Reminder", "🗂️ Add Project", "📊 Analytics", "⚙️ Settings"], 
    horizontal=True,
    label_visibility="collapsed"
)

# Custom Navbar CSS
st.markdown("""
<style>
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap; 
        justify-content: center;
        gap: 10px;
        background-color: #0E1117;
        padding: 10px;
        margin-bottom: 20px;
        border-bottom: 1px solid #262730;
    }
    div[role="radiogroup"] label {
        background-color: #262730;
        padding: 12px 20px;
        border-radius: 15px;
        border: 1px solid #363945;
        cursor: pointer;
        transition: all 0.2s;
        font-weight: 600;
        margin: 5px !important; 
        flex-grow: 1; 
        text-align: center;
        min-width: 140px;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #363945;
    }
    div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(90deg, #F63366 0%, #FF6B6B 100%);
        color: white !important;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

if selected_tab == "🔥 Dashboard":
    # --- 0. Projects Section ---
    projects = get_projects(pending_only=True)
    if not projects.empty:
        st.markdown("### 🗂️ Pending Projects")
        for idx, row in projects.iterrows():
            # Determine icon for CSS targeting
            icon = "🚨" if row['priority'] == 'high' else "⚠️" if row['priority'] == 'medium' else "🟢"
            
            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                with c1:
                    # Emoji must be present for :has() selector to work
                    st.markdown(f" <b style='font-size: 1.5rem;'>{icon} {row['text']}</b>", unsafe_allow_html=True)
                with c2:
                    if st.button("Done", key=f"dash_project_{row['id']}", help="Mark Done"):
                        update_project_status(row['id'], True)
                        st.rerun()

    # --- 1. Reminders Section ---
    reminders = get_reminders(pending_only=True)
    if not reminders.empty:
        st.markdown("### 📝 Reminders")
        for idx, row in reminders.iterrows():
            # Determine icon for CSS targeting
            icon = "🚨" if row['priority'] == 'high' else "⚠️" if row['priority'] == 'medium' else "🟢"
            
            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                with c1:
                    # Emoji must be present for :has() selector to work
                    st.markdown(f" <b style='font-size: 1.5rem;'>{icon} {row['text']}</b>", unsafe_allow_html=True)
                with c2:
                    if st.button("Done", key=f"dash_rem_{row['id']}", help="Mark Done"):
                        update_reminder_status(row['id'], True)
                        st.rerun()

    # --- 2. Habits Section ---
    st.markdown("### Today's Focus")
    
    habits = load_habits(active_only=True)
    logs = load_logs()
    
    if habits.empty:
        st.info("No habits found. Go to 'Add Habit' to start!")
    else:
        # 🧠 Smart Section
        suggestions = get_smart_suggestions(habits, logs)
        if suggestions:
             st.info(suggestions[0])

        # Filter for TODAY
        today = pd.Timestamp.now()
        today_str = today.strftime("%Y-%m-%d")
        
        todays_habits = []
        for _, habit in habits.iterrows():
            if is_habit_due(habit, today):
                todays_habits.append(habit)
        
        todays_habits_df = pd.DataFrame(todays_habits)

        # Filter out Completed (Vanish Effect)
        if not todays_habits_df.empty:
            pending_habits = []
            if logs.empty:
                 pending_habits = todays_habits_df
            else:
                completed_ids = logs[logs['date'].astype(str) == today_str]['habit_id'].unique()
                pending_habits = todays_habits_df[~todays_habits_df['id'].isin(completed_ids)]
            
            if pending_habits.empty:
                 st.balloons()
                 st.success("🎉 All habits completed for today! You are crushing it!")
            else:
                for index, habit in pending_habits.iterrows():
                    render_habit_card(habit, logs, log_habit_completion)
        else:
            st.write("No habits scheduled for today.")

elif selected_tab == "➕ Add Habit":
    st.write("### Create New Habit")
    
    if "habit_success" in st.session_state:
        st.success(st.session_state.habit_success)
        st.balloons()
        del st.session_state["habit_success"]
        
    habit_data = render_add_habit_form()
    if habit_data:
        if add_habit(habit_data):
            st.session_state.habit_success = f"Habit '{habit_data['name']}' created successfully!"
            st.rerun()
        else:
            st.error("Failed to save habit.")

elif selected_tab == "📝 Add Reminder":
    st.write("### 🧠 Sticky Reminders")
    st.caption("A place for non-habit tasks like 'Call Mom' or 'Pay Bills'")
    
    # Input
    
    # with c1:
    new_reminder = st.text_input("New Reminder", label_visibility="collapsed", placeholder="What needs to be done?")

    c1, c2 = st.columns([3, 1],gap="large")
    with c1:
        priority = st.selectbox("Priority", ["High", "Medium", "Low"], label_visibility="collapsed", index=1) # Default Medium
    with c2:
        if st.button("Add Reminder", use_container_width=False,type="primary"):
            if new_reminder:
                if add_reminder(new_reminder, priority.lower()):
                    st.toast("Reminder added!")
                    st.rerun()

    st.divider()
    
    # List Reminders
    reminders = get_reminders(pending_only=True)
    if reminders.empty:
        st.info("No active reminders. You're free! 🎉")
    else:
        st.subheader("⚠️ Pending Reminders")
        for idx, row in reminders.iterrows():
            # Styling based on priority
            p_color = "#FFCDD2" if row['priority'] == 'high' else "#E1BEE7" if row['priority'] == 'medium' else "#C8E6C9"
            p_emoji = "🔴" if row['priority'] == 'high' else "🟡" if row['priority'] == 'medium' else "🟢"
            
            with st.container():
                rc1, rc2 = st.columns([2, 1])
                rc1.markdown(f" <b style='font-size: 1.5rem;'>{p_emoji} {row['text']}</b>", unsafe_allow_html=True)
                if rc2.button("mark as Done", key=f"rem_done_{row['id']}", help="Mark as Done"):
                    update_reminder_status(row['id'], True)
                    st.rerun()
        st.divider()

elif selected_tab == "🗂️ Add Project":
    st.write("### 🗂️ Add Projects")
    st.caption("A place to track larger tasks(projects) or goals.")
    new_project = st.text_input("On which project do you wish to work?", placeholder="e.g. smart habit tracker").strip()
    # Input
    c1, c2 = st.columns([3,2])
    with c1:
        new_project_description = st.text_input("Description", placeholder="Add a brief description (optional)")
    with c2:
        priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1) # Default Medium

    if st.button("Add Project", use_container_width=False,type="primary"):
        if new_project:
            if add_project(new_project, new_project_description,priority.lower()):
                st.toast("Project added!")
                st.rerun()
        
    st.divider()

    # List Projects
    projects = get_projects(pending_only=True)
    if projects.empty:
        st.info("No active Projects. You're free! 🎉")
    else:
        st.subheader("⚠️ Pending Projects")
        for idx, row in projects.iterrows():
            # Styling based on priority
            p_color = "#FFCDD2" if row['priority'] == 'high' else "#E1BEE7" if row['priority'] == 'medium' else "#C8E6C9"
            p_emoji = "🟥" if row['priority'] == 'high' else "🟨" if row['priority'] == 'medium' else "🟩"
            
            with st.container():
                rc1, rc2 = st.columns([6, 1])
                
                rc1.markdown(f" <b style='font-size: 1.5rem;'>{p_emoji} {row['text']}</b>", unsafe_allow_html=True)
                if rc2.button("Mark as Done", key=f"project_done_{row['id']}", help="Mark as Done"):
                    update_project_status(row['id'], True)
                    st.rerun()
            st.divider()

elif selected_tab == "📊 Analytics":
    habits = load_habits()
    logs = load_logs()
    render_analytics(habits, logs)

elif selected_tab == "⚙️ Settings":
    st.write("### Manage Habits")
    habits = load_habits()
    
    if "edit_mode_id" not in st.session_state:
        st.session_state.edit_mode_id = None

    if habits.empty:
        st.write("No habits to manage.")
    else:
        # If in edit mode, show the edit form for that habit
        if st.session_state.edit_mode_id:
            habit_to_edit = habits[habits['id'] == st.session_state.edit_mode_id].iloc[0]
            
            if st.button("← Back to List"):
                st.session_state.edit_mode_id = None
                st.rerun()
                
            from src.ui_components import render_edit_habit_form
            updated_data = render_edit_habit_form(habit_to_edit['id'], habit_to_edit)
            
            if updated_data:
                if edit_habit(habit_to_edit['id'], updated_data):
                    st.success("Habit updated successfully!")
                    st.session_state.edit_mode_id = None
                    st.rerun()
                else:
                    st.error("Failed to update habit.")
                    
        else:
            # List View
            for index, habit in habits.iterrows():
                # Use a container for better layout
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                    c1.write(f"**{habit['name']}**")
                    c2.caption(f"{habit['frequency_type']}")
                    
                    if c3.button("Edit", key=f"edit_{habit['id']}"):
                        st.session_state.edit_mode_id = habit['id']
                        st.rerun()
                        
                    if c4.button("Delete", key=f"del_{habit['id']}"):
                        if delete_habit(habit['id']):
                            st.success("Deleted!")
                            st.rerun()
                    st.divider()
