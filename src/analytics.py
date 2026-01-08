import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import timedelta
from src.utils import is_habit_due

def calculate_streaks(habit, habit_logs):
    """
    Calculate current streak based on 'Consecutive Due Dates Completed'.
    """
    if habit_logs.empty:
        return 0
    
    today = pd.Timestamp.now().date()
    # Parse created_at safely
    try:
        created_at = pd.to_datetime(habit['created_at']).date()
    except:
        return 0
        
    if created_at > today: return 0

    # Get all dates where habit was due, up to today
    due_dates = []
    curr = created_at
    while curr <= today:
        if is_habit_due(habit, curr):
            due_dates.append(curr)
        curr += timedelta(days=1)
        
    if not due_dates: return 0
    
    # Sort descending (latest first)
    due_dates.sort(reverse=True)
    
    # Check logs for these dates
    logged_dates = set(pd.to_datetime(habit_logs['date']).dt.date)
    
    streak = 0
    
    for d in due_dates:
        if d in logged_dates:
            streak += 1
        else:
            # If d is TODAY and not logged, we don't break streak yet IF user hasn't finished day
            # But technically streak is "consecutive completed". 
            # If I haven't done today, my streak is technically "pending".
            # Standard logic: If today is missed, streak doesn't reset until tomorrow.
            if d == today:
                continue
            else:
                break
    return streak

def calculate_completion_rate(habit, habit_logs):
    """
    Calculate completion percentage: (Days Completed / Days Due) * 100
    """
    today = pd.Timestamp.now().date()
    try:
        created_at = pd.to_datetime(habit['created_at']).date()
    except:
        return 0.0, 0
    
    if created_at > today: return 0.0, 0
    
    total_due = 0
    
    curr = created_at
    while curr <= today:
        if is_habit_due(habit, curr):
            total_due += 1
        curr += timedelta(days=1)
        
    completed_count = len(habit_logs['date'].unique()) 
    
    if total_due == 0: return 0.0, 0
    
    # Cap at 100% just in case
    pct = min(100.0, (completed_count / total_due) * 100)
    return pct, total_due

def render_analytics(habits, logs):
    if habits.empty:
        st.info("No data yet.")
        return

    st.subheader("📊 Habit Performance")
    
    metrics = []
    
    for _, habit in habits.iterrows():
        habit_logs = logs[logs['habit_id'] == habit['id']]
        streak = calculate_streaks(habit, habit_logs)
        rate, total_due = calculate_completion_rate(habit, habit_logs)
        
        metrics.append({
            "Name": habit['name'],
            "Streak": streak,
            "Completion Rate": rate,
            "Total Completions": len(habit_logs)
        })
    
    df_metrics = pd.DataFrame(metrics)
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    if not df_metrics.empty:
        max_streak = df_metrics['Streak'].max()
        most_consistent = df_metrics.sort_values("Completion Rate", ascending=False).iloc[0]['Name']
        total_checkins = df_metrics['Total Completions'].sum()
    else:
        max_streak, most_consistent, total_checkins = 0, "-", 0
    
    c1.metric("Longest Active Streak", max_streak)
    c2.metric("Most Consistent Habit", most_consistent)
    c3.metric("Total Check-ins", total_checkins)
    
    # 🌟 Compliment logic
    if not df_metrics.empty:
        top_habit = df_metrics.sort_values("Completion Rate", ascending=False).iloc[0]
        if top_habit['Completion Rate'] > 80:
            st.success(f"🌟 Amazing discipline with **{top_habit['Name']}**! You are building a rock-solid routine.")
        elif top_habit['Completion Rate'] > 50:
            st.info(f"👍 Good job keeping up with **{top_habit['Name']}**. Consistency is key!")
    
    # Charts
    st.write("### Consistency Trends")
    fig = px.bar(df_metrics, x='Name', y='Completion Rate', color='Streak', title="Completion Rate % by Habit")
    st.plotly_chart(fig, use_container_width=True)
    
    # Table
    st.dataframe(
        df_metrics.style.format({"Completion Rate": "{:.1f}%"}), 
        use_container_width=True
    )
