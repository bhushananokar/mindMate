import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Analytics - MindMate", page_icon="📊", layout="wide")

st.title("📊 Mental Health Analytics")
st.write("Track your progress and understand your mental health patterns")

# Initialize session state for demo data
if 'analytics_data' not in st.session_state:
    # Generate demo data for the past 30 days
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    moods = ['positive', 'neutral', 'anxious', 'stressed', 'negative']
    
    # Create realistic mood data with some patterns
    demo_data = []
    for i, date in enumerate(dates):
        # Simulate weekly patterns (weekends more positive)
        if date.weekday() >= 5:  # Weekend
            mood = random.choices(moods, weights=[40, 30, 10, 10, 10])[0]
        else:  # Weekday
            mood = random.choices(moods, weights=[25, 25, 20, 20, 10])[0]
        
        demo_data.append({
            'date': date.date(),
            'mood': mood,
            'mood_score': {
                'positive': 5, 'neutral': 3, 'anxious': 2, 
                'stressed': 2, 'negative': 1
            }[mood]
        })
    
    st.session_state.analytics_data = demo_data

# Get analytics data
data = pd.DataFrame(st.session_state.analytics_data)

# Main metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_entries = len(data)
    st.metric("Total Check-ins", total_entries, delta=f"+{random.randint(3, 8)} this week")

with col2:
    current_streak = random.randint(3, 12)
    st.metric("Current Streak", f"{current_streak} days", delta="+2")

with col3:
    avg_mood = data['mood_score'].mean()
    st.metric("Average Mood", f"{avg_mood:.1f}/5", delta="+0.3")

with col4:
    positive_days = len(data[data['mood'] == 'positive'])
    positive_percent = (positive_days / total_entries) * 100
    st.metric("Positive Days", f"{positive_percent:.0f}%", delta="+5%")

# Mood trend chart
st.subheader("📈 30-Day Mood Trend")

# Create mood trend chart
fig_trend = px.line(
    data, 
    x='date', 
    y='mood_score',
    title='Mood Score Over Time',
    color_discrete_sequence=['#667eea']
)

fig_trend.update_layout(
    xaxis_title="Date",
    yaxis_title="Mood Score (1-5)",
    height=400,
    showlegend=False
)

fig_trend.update_traces(line=dict(width=3))
st.plotly_chart(fig_trend, use_container_width=True)

# Mood distribution
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎭 Mood Distribution")
    
    mood_counts = data['mood'].value_counts()
    
    # Create pie chart
    fig_pie = px.pie(
        values=mood_counts.values,
        names=mood_counts.index,
        title="Distribution of Moods",
        color_discrete_map={
            'positive': '#28a745',
            'neutral': '#ffc107', 
            'anxious': '#fd7e14',
            'stressed': '#6f42c1',
            'negative': '#dc3545'
        }
    )
    
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("📅 Weekly Patterns")
    
    # Add day of week to data
    data['day_of_week'] = pd.to_datetime(data['date']).dt.day_name()
    
    # Calculate average mood score by day of week
    weekly_avg = data.groupby('day_of_week')['mood_score'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    
    fig_weekly = px.bar(
        x=weekly_avg.index,
        y=weekly_avg.values,
        title="Average Mood by Day of Week",
        color=weekly_avg.values,
        color_continuous_scale='RdYlGn'
    )
    
    fig_weekly.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Average Mood Score",
        showlegend=False
    )
    
    st.plotly_chart(fig_weekly, use_container_width=True)

# Recent activity timeline
st.subheader("⏰ Recent Activity")

# Show last 7 days
recent_data = data.tail(7).sort_values('date', ascending=False)

for _, row in recent_data.iterrows():
    mood_emoji = {
        'positive': '😊',
        'neutral': '😐', 
        'anxious': '😰',
        'stressed': '😤',
        'negative': '😔'
    }
    
    mood_color = {
        'positive': '#28a745',
        'neutral': '#ffc107',
        'anxious': '#fd7e14', 
        'stressed': '#6f42c1',
        'negative': '#dc3545'
    }
    
    st.markdown(f"""
    <div style="
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        padding: 10px;
        margin: 5px 0;
        border-left: 4px solid {mood_color[row['mood']]};
        background: #f8f9fa;
        border-radius: 5px;
    ">
        <span><strong>{row['date'].strftime('%B %d, %Y')}</strong></span>
        <span style="color: {mood_color[row['mood']]};">
            {mood_emoji[row['mood']]} {row['mood'].title()}
        </span>
    </div>
    """, unsafe_allow_html=True)

# AI Insights section
st.subheader("🤖 AI Insights & Recommendations")

insights = [
    {
        "icon": "🌅",
        "title": "Morning Pattern",
        "description": "You tend to have better moods in the morning. Try scheduling important tasks early in the day.",
        "action": "Set morning intentions"
    },
    {
        "icon": "📈", 
        "title": "Positive Trend",
        "description": "Your mood has improved 15% over the last two weeks. Great progress!",
        "action": "Keep up current habits"
    },
    {
        "icon": "🧘",
        "title": "Stress Management", 
        "description": "Breathing exercises seem to help you most on stressful days.",
        "action": "Try 5-minute breathing breaks"
    },
    {
        "icon": "🎯",
        "title": "Goal Suggestion",
        "description": "Aim for 5 consecutive positive days. You're currently at 2!",
        "action": "Focus on self-care today"
    }
]

cols = st.columns(2)
for i, insight in enumerate(insights):
    with cols[i % 2]:
        st.markdown(f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4>{insight['icon']} {insight['title']}</h4>
            <p style="color: #666; margin: 10px 0;">{insight['description']}</p>
            <small style="color: #667eea;"><strong>💡 {insight['action']}</strong></small>
        </div>
        """, unsafe_allow_html=True)

# Export data option
st.subheader("📤 Export Your Data")
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Download CSV Report", use_container_width=True):
        csv = data.to_csv(index=False)
        st.download_button(
            label="💾 Download CSV",
            data=csv,
            file_name=f"mindmate_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📈 Generate Summary Report", use_container_width=True):
        st.info("📋 Summary report would be generated here with detailed insights and recommendations.")

# Privacy notice
st.markdown("---")
st.caption("🔒 Your data is private and secure. Analytics are generated locally and help you understand your mental health patterns.")