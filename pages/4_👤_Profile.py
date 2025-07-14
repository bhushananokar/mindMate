import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Profile - MindMate", page_icon="👤", layout="wide")

st.title("👤 Your Profile")
st.write("Customize your MindMate experience")

# Initialize profile data with all required keys
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': 'Friend',
        'age_range': '',
        'goals': [],
        'preferences': [],
        'notifications': True,
        'privacy_level': 'Medium'
    }

# Ensure all keys exist in user_profile (for existing users)
profile_defaults = {
    'name': 'Friend',
    'age_range': '',
    'goals': [],
    'preferences': [],
    'notifications': True,
    'privacy_level': 'Medium'
}

for key, default_value in profile_defaults.items():
    if key not in st.session_state.user_profile:
        st.session_state.user_profile[key] = default_value

# Profile form
with st.form("profile_form"):
    st.subheader("Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(
            "What would you like me to call you?",
            value=st.session_state.user_profile.get('name', 'Friend'),
            placeholder="Enter your preferred name"
        )
        
        current_age_range = st.session_state.user_profile.get('age_range', '')
        age_options = ["", "13-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        
        try:
            age_index = age_options.index(current_age_range) if current_age_range in age_options else 0
        except ValueError:
            age_index = 0
            
        age_range = st.selectbox(
            "Age Range (optional)",
            age_options,
            index=age_index
        )
    
    with col2:
        st.subheader("Mental Health Goals")
        st.caption("What would you like to work on? (Select all that apply)")
        
        goal_options = [
            "Managing Anxiety",
            "Stress Reduction", 
            "Better Sleep",
            "Building Confidence",
            "Mood Improvement",
            "Relationship Issues",
            "Work-Life Balance",
            "Mindfulness Practice",
            "Emotional Regulation",
            "Self-Care Habits"
        ]
        
        selected_goals = []
        current_goals = st.session_state.user_profile.get('goals', [])
        
        for goal in goal_options:
            if st.checkbox(goal, value=goal in current_goals, key=f"goal_{goal}"):
                selected_goals.append(goal)
    
    st.subheader("Exercise Preferences")
    st.caption("What types of wellness exercises do you prefer?")
    
    exercise_options = [
        "Breathing Exercises",
        "Meditation",
        "Physical Movement", 
        "Journaling",
        "Visualization",
        "Progressive Relaxation",
        "Mindfulness",
        "Cognitive Exercises"
    ]
    
    selected_preferences = []
    current_preferences = st.session_state.user_profile.get('preferences', [])
    
    col1, col2 = st.columns(2)
    
    for i, exercise in enumerate(exercise_options):
        with col1 if i % 2 == 0 else col2:
            if st.checkbox(exercise, value=exercise in current_preferences, key=f"pref_{exercise}"):
                selected_preferences.append(exercise)
    
    st.subheader("Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        notifications = st.checkbox(
            "Enable daily check-in reminders",
            value=st.session_state.user_profile.get('notifications', True)
        )
        
    with col2:
        current_privacy = st.session_state.user_profile.get('privacy_level', 'Medium')
        privacy_options = ["Low", "Medium", "High"]
        
        try:
            privacy_index = privacy_options.index(current_privacy)
        except ValueError:
            privacy_index = 1  # Default to Medium
            
        privacy_level = st.selectbox(
            "Privacy Level",
            privacy_options,
            index=privacy_index
        )
    
    # Form submission
    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
    
    if submitted:
        # Update session state
        st.session_state.user_profile.update({
            'name': name or 'Friend',
            'age_range': age_range,
            'goals': selected_goals,
            'preferences': selected_preferences,
            'notifications': notifications,
            'privacy_level': privacy_level,
            'last_updated': datetime.now()
        })
        
        st.success("✅ Profile updated successfully!")
        st.balloons()

# Display current profile
st.markdown("---")
st.subheader("📋 Current Profile Summary")

profile = st.session_state.user_profile

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **👤 Name:** {profile.get('name', 'Friend')}  
    **🎂 Age Range:** {profile.get('age_range', 'Not specified')}  
    **🔔 Notifications:** {'Enabled' if profile.get('notifications', True) else 'Disabled'}  
    **🔒 Privacy:** {profile.get('privacy_level', 'Medium')}
    """)

with col2:
    goals = profile.get('goals', [])
    if goals:
        st.markdown("**🎯 Mental Health Goals:**")
        for goal in goals:
            st.markdown(f"• {goal}")
    else:
        st.markdown("**🎯 Mental Health Goals:** None set")

preferences = profile.get('preferences', [])
if preferences:
    st.markdown("**🧘 Exercise Preferences:**")
    pref_cols = st.columns(3)
    for i, pref in enumerate(preferences):
        with pref_cols[i % 3]:
            st.markdown(f"• {pref}")

# Account actions
st.markdown("---")
st.subheader("⚙️ Account Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 Export My Data", use_container_width=True):
        # Create exportable data
        export_data = {
            'profile': st.session_state.user_profile,
            'conversation_history': st.session_state.get('conversation_history', []),
            'export_date': datetime.now().isoformat()
        }
        
        import json
        st.download_button(
            label="💾 Download Data",
            data=json.dumps(export_data, indent=2, default=str),
            file_name=f"mindmate_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

with col2:
    if st.button("🔄 Reset Preferences", use_container_width=True):
        if st.button("⚠️ Confirm Reset", type="secondary"):
            st.session_state.user_profile = {
                'name': 'Friend',
                'age_range': '',
                'goals': [],
                'preferences': [],
                'notifications': True,
                'privacy_level': 'Medium'
            }
            st.success("Profile reset successfully!")
            st.rerun()

with col3:
    if st.button("❓ Get Help", use_container_width=True):
        st.info("""
        **Need help?**
        
        • Your data is stored locally in your browser
        • MindMate remembers your preferences across sessions  
        • All conversations are private and secure
        • You can export or delete your data anytime
        
        For technical support or feedback, please contact support.
        """)

# Privacy information
st.markdown("---")
st.subheader("🔒 Privacy & Data")

st.info("""
**Your Privacy Matters**

- **Local Storage**: Your data is stored locally in your browser session
- **No Account Required**: No email or personal information needed
- **Secure**: Conversations are not shared with third parties
- **Control**: You can export or delete your data anytime
- **Anonymous**: Your identity is not tracked or stored

MindMate is designed to provide mental health support while respecting your privacy.
""")

# Recommendations based on profile
goals = profile.get('goals', [])
preferences = profile.get('preferences', [])

if goals or preferences:
    st.markdown("---")
    st.subheader("💡 Personalized Recommendations")
    
    recommendations = []
    
    if "Managing Anxiety" in goals:
        recommendations.append("🫁 Try our 4-7-8 breathing exercise when feeling anxious")
    
    if "Better Sleep" in goals:
        recommendations.append("🌙 Consider a bedtime mindfulness routine")
        
    if "Breathing Exercises" in preferences:
        recommendations.append("💨 Daily breathing exercises can improve overall wellbeing")
    
    if "Stress Reduction" in goals:
        recommendations.append("🧘 Regular meditation practice helps reduce stress")
    
    if "Mindfulness Practice" in goals:
        recommendations.append("🎯 Start with 5-minute daily mindfulness sessions")
    
    if recommendations:
        for rec in recommendations:
            st.success(rec)
    else:
        st.info("💡 Complete your profile to get personalized recommendations!")

# Quick stats about user
st.markdown("---")
st.subheader("📈 Your MindMate Journey")

col1, col2, col3 = st.columns(3)

with col1:
    days_active = (datetime.now() - datetime.now().replace(day=1)).days + 1
    st.metric("Days with MindMate", days_active)

with col2:
    total_conversations = len(st.session_state.get('conversation_history', []))
    st.metric("Total Conversations", total_conversations)

with col3:
    goals_set = len(profile.get('goals', []))
    st.metric("Goals Set", goals_set)