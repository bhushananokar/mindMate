import streamlit as st
from datetime import datetime
import sys
import os
import json

# Add the parent directory to the path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Profile - MindMate", page_icon="👤", layout="wide")

# Check authentication
if not get_current_user():
    st.error("Please log in to access your profile.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# Initialize services
@st.cache_resource
def init_services():
    from services.firebase_service import FirebaseService
    firebase = FirebaseService()
    return firebase

firebase_service = init_services()

st.title("👤 Your Profile")
st.write("Customize your MindMate experience")

user = get_current_user()
user_display_name = get_user_display_name()

# Show demo mode warning
if is_demo_user():
    st.warning("🔄 **Demo Mode**: Changes will not be permanently saved. Sign in with Google to save your preferences.")

# Initialize profile data with all required keys
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': user_display_name,
        'age_range': '',
        'goals': [],
        'preferences': [],
        'notifications': True,
        'privacy_level': 'Medium'
    }

# Ensure all keys exist in user_profile (for existing users)
profile_defaults = {
    'name': user_display_name,
    'age_range': '',
    'goals': [],
    'preferences': [],
    'notifications': True,
    'privacy_level': 'Medium'
}

for key, default_value in profile_defaults.items():
    if key not in st.session_state.user_profile:
        st.session_state.user_profile[key] = default_value

# User info section
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 20px;
">
    <img src="{user.get('photoURL', 'https://via.placeholder.com/80')}" 
         style="width: 80px; height: 80px; border-radius: 50%; border: 3px solid white;" 
         onerror="this.src='https://via.placeholder.com/80'">
    <div>
        <h2 style="margin: 0;">{user.get('displayName', 'User')}</h2>
        <p style="margin: 0; opacity: 0.9;">{user.get('email', '')}</p>
        {'<p style="margin: 0; color: #ffa500;">🔄 Demo Mode</p>' if is_demo_user() else '<p style="margin: 0;">✅ Authenticated User</p>'}
    </div>
</div>
""", unsafe_allow_html=True)

# Profile form
with st.form("profile_form"):
    st.subheader("Personal Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input(
            "What would you like me to call you?",
            value=st.session_state.user_profile.get('name', user_display_name),
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
            index=privacy_index,
            help="Low: Basic data collection, Medium: Standard privacy, High: Minimal data collection"
        )
    
    # Form submission
    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
    
    if submitted:
        # Update session state
        updated_profile = {
            'name': name or user_display_name,
            'age_range': age_range,
            'goals': selected_goals,
            'preferences': selected_preferences,
            'notifications': notifications,
            'privacy_level': privacy_level,
            'last_updated': datetime.now()
        }
        
        st.session_state.user_profile.update(updated_profile)
        
        # Save to Firebase if not demo user
        if not is_demo_user():
            success = save_user_profile_to_firebase(firebase_service, updated_profile)
            if success:
                st.success("✅ Profile updated and saved to your account!")
            else:
                st.warning("✅ Profile updated locally. Unable to sync with cloud.")
        else:
            st.success("✅ Profile updated! (Demo mode - changes saved to session only)")
        
        st.balloons()

# Display current profile
st.markdown("---")
st.subheader("📋 Current Profile Summary")

profile = st.session_state.user_profile

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **👤 Name:** {profile.get('name', user_display_name)}  
    **🎂 Age Range:** {profile.get('age_range', 'Not specified')}  
    **🔔 Notifications:** {'Enabled' if profile.get('notifications', True) else 'Disabled'}  
    **🔒 Privacy:** {profile.get('privacy_level', 'Medium')}  
    **📧 Email:** {user.get('email', 'Not available')}
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
        # Export user data
        export_data = export_user_data(firebase_service)
        
        # Convert to JSON string
        json_str = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="💾 Download Data",
            data=json_str,
            file_name=f"mindmate_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

with col2:
    if st.button("🔄 Reset Preferences", use_container_width=True):
        with st.expander("⚠️ Confirm Reset"):
            st.warning("This will reset all your preferences to default values.")
            if st.button("Confirm Reset", type="secondary"):
                st.session_state.user_profile = {
                    'name': user_display_name,
                    'age_range': '',
                    'goals': [],
                    'preferences': [],
                    'notifications': True,
                    'privacy_level': 'Medium'
                }
                
                # Save to Firebase if not demo user
                if not is_demo_user():
                    save_user_profile_to_firebase(firebase_service, st.session_state.user_profile)
                
                st.success("Profile reset successfully!")
                st.rerun()

with col3:
    if st.button("❓ Get Help", use_container_width=True):
        st.info("""
        **Need help?**
        
        • Your data is securely stored and encrypted
        • MindMate remembers your preferences across sessions  
        • All conversations are private and confidential
        • You can export or delete your data anytime
        • Demo mode data is only stored locally
        
        For technical support or feedback, please contact our support team.
        """)

# Data management section
st.markdown("---")
st.subheader("🗂️ Data Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📊 Your Data Overview:**")
    stats = format_user_stats()
    
    st.metric("Total Conversations", stats['conversations'])
    st.metric("Mood Entries", stats['mood_entries'])
    st.metric("Exercises Completed", stats['exercises'])

with col2:
    st.markdown("**⚙️ Advanced Options:**")
    
    if not is_demo_user():
        st.info("🔄 **Auto-sync enabled** - Your data is automatically saved to the cloud")
        
        if st.button("🔄 Sync Now", use_container_width=True):
            with st.spinner("Syncing with cloud..."):
                success = sync_session_with_firebase(firebase_service)
                if success:
                    st.success("✅ Data synced successfully!")
                else:
                    st.error("❌ Sync failed. Please try again.")
    else:
        st.warning("📱 **Demo Mode** - Data stored locally only")
        st.caption("Sign in with Google to enable cloud sync and data persistence")

# Privacy information
st.markdown("---")
st.subheader("🔒 Privacy & Data Security")

privacy_level = profile.get('privacy_level', 'Medium')

if privacy_level == 'High':
    privacy_info = """
    **🔒 High Privacy Mode**
    
    - Minimal data collection and processing
    - Conversations stored with enhanced encryption
    - No analytics or usage tracking
    - Data automatically deleted after 30 days of inactivity
    - No personalization features
    """
elif privacy_level == 'Low':
    privacy_info = """
    **📊 Enhanced Experience Mode**
    
    - Full feature access with personalization
    - Advanced analytics and insights
    - Usage patterns analyzed for better recommendations
    - Data retained for improved service
    - Enhanced conversation memory
    """
else:
    privacy_info = """
    **⚖️ Balanced Privacy Mode**
    
    - Standard data collection for core features
    - Basic analytics for service improvement
    - Conversations stored securely
    - Personalization with privacy protection
    - Data retention per standard policy
    """

st.info(privacy_info)

st.markdown("**Universal Privacy Principles:**")
st.markdown("""
- 🔐 All data is encrypted in transit and at rest
- 🚫 We never share your personal information with third parties
- 🗑️ You can delete your data at any time
- 📋 You have full control over what data is collected
- 🛡️ We comply with GDPR and other privacy regulations
""")

# Account deletion
st.markdown("---")
st.subheader("⚠️ Account Deletion")

with st.expander("🗑️ Delete All My Data"):
    st.warning("""
    **⚠️ This action cannot be undone!**
    
    Deleting your account will permanently remove:
    - All conversation history
    - Mood tracking data
    - Exercise progress
    - Profile preferences
    - Analytics data
    """)
    
    if not is_demo_user():
        delete_confirmation = st.text_input(
            "Type 'DELETE' to confirm:",
            placeholder="Type DELETE here"
        )
        
        if st.button("🗑️ Permanently Delete Account", type="secondary"):
            if delete_confirmation == "DELETE":
                success = delete_user_data(firebase_service)
                if success:
                    st.success("Your account has been deleted. You will be signed out.")
                    # Clear all session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.switch_page("app.py")
                else:
                    st.error("Failed to delete account. Please try again or contact support.")
            else:
                st.error("Please type 'DELETE' to confirm account deletion.")
    else:
        if st.button("🗑️ Clear Demo Data", type="secondary"):
            delete_user_data()
            st.success("Demo data cleared!")
            st.rerun()

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
    
    if "Work-Life Balance" in goals:
        recommendations.append("⚖️ Set boundaries and practice saying 'no' to overcommitment")
    
    if "Building Confidence" in goals:
        recommendations.append("💪 Try positive affirmations and celebrate small wins")
    
    if recommendations:
        for rec in recommendations:
            st.success(rec)
    else:
        st.info("💡 Complete your profile to get personalized recommendations!")

# Quick stats about user journey
st.markdown("---")
st.subheader("📈 Your MindMate Journey")

col1, col2, col3 = st.columns(3)

with col1:
    # Calculate days since account creation or first conversation
    if st.session_state.conversation_history:
        first_conversation = min(
            msg['timestamp'] for msg in st.session_state.conversation_history 
            if isinstance(msg.get('timestamp'), datetime)
        )
        days_active = (datetime.now() - first_conversation).days + 1
    else:
        days_active = 1
    
    st.metric("Days with MindMate", days_active)

with col2:
    total_conversations = len([
        msg for msg in st.session_state.get('conversation_history', [])
        if msg.get('role') == 'user'
    ])
    st.metric("Total Conversations", total_conversations)

with col3:
    goals_set = len(profile.get('goals', []))
    st.metric("Goals Set", goals_set)

# Footer with helpful links
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💬 Back to Chat", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("🧘 Try Exercises", use_container_width=True):
        st.switch_page("pages/2_🧘_Exercises.py")

with col3:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/3_📊_Analytics.py")