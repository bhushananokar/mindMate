import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure Streamlit page
st.set_page_config(
    page_title="MindMate - AI Mental Health Companion",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #667eea;
        color: white;
        margin-left: auto;
    }
    
    .ai-message {
        background-color: #f0f2f6;
        color: #333;
    }
    
    .mood-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .exercise-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .user-profile {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    from services.firebase_service import FirebaseService
    from services.gemini_service import GeminiService
    from services.auth_service import AuthService
    
    firebase = FirebaseService()
    gemini = GeminiService()
    auth = AuthService()
    
    return firebase, gemini, auth

# Check authentication status
def check_auth():
    """Check if user is authenticated"""
    # Check for auth data in session state
    if 'user' not in st.session_state:
        # Check browser storage for persisted auth
        auth_check_script = """
        <script>
            const userData = sessionStorage.getItem('mindmate_user');
            const continueApp = sessionStorage.getItem('continue_to_app');
            
            if (userData && continueApp) {
                const user = JSON.parse(userData);
                window.parent.postMessage({
                    type: 'restore_auth',
                    user: user
                }, '*');
            }
        </script>
        """
        st.components.v1.html(auth_check_script, height=0)
    
    return st.session_state.get('user') is not None

# Initialize session state for authenticated user
def init_user_session(user_data, firebase_service):
    """Initialize session state with user data"""
    st.session_state.user = user_data
    
    # Load user profile from Firebase
    if not user_data.get('isDemo', False):
        profile = firebase_service.get_user_profile(user_data['uid'])
        if profile:
            st.session_state.user_profile = profile.get('preferences', {})
            st.session_state.user_stats = profile.get('stats', {})
        else:
            # Create new user profile
            firebase_service.create_user_profile(user_data)
            st.session_state.user_profile = {
                'name': user_data.get('displayName', 'Friend'),
                'age_range': '',
                'goals': [],
                'preferences': [],
                'notifications': True,
                'privacy_level': 'Medium'
            }
            st.session_state.user_stats = {
                'total_conversations': 0,
                'total_mood_entries': 0,
                'current_streak': 0,
                'exercises_completed': 0
            }
    else:
        # Demo user - use session storage only
        st.session_state.user_profile = {
            'name': 'Demo User',
            'age_range': '',
            'goals': [],
            'preferences': [],
            'notifications': True,
            'privacy_level': 'Medium'
        }
        st.session_state.user_stats = {
            'total_conversations': 0,
            'total_mood_entries': 0,
            'current_streak': 0,
            'exercises_completed': 0
        }
    
    # Initialize other session state
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_mood' not in st.session_state:
        st.session_state.current_mood = 'neutral'
    
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []

def show_auth_page():
    """Show authentication page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🧠 Welcome to MindMate</h1>
        <p style="font-size: 1.2rem; color: #666;">Your AI Mental Health Companion</p>
        <p>Please sign in to continue your mental health journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize auth service and render auth component
    _, _, auth_service = init_services()
    auth_service.render_auth_component()
    auth_service.handle_auth_state()

def main():
    # Initialize services
    firebase, gemini, auth_service = init_services()
    
    # Handle auth messages from JavaScript
    auth_message_handler = """
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'restore_auth' || event.data.type === 'auth_success') {
                // Store user data for Streamlit
                window.streamlit_user_data = event.data.user;
            }
        });
        
        // Make user data available to Streamlit
        if (window.streamlit_user_data) {
            window.parent.postMessage({
                type: 'set_streamlit_user',
                user: window.streamlit_user_data
            }, '*');
        }
    </script>
    """
    st.components.v1.html(auth_message_handler, height=0)
    
    # Check authentication
    if not check_auth():
        show_auth_page()
        return
    
    # User is authenticated, initialize session
    user_data = st.session_state.user
    init_user_session(user_data, firebase)
    
    # Main App Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🧠 MindMate</h1>
        <p>Your AI Mental Health Companion</p>
        <p><em>Welcome back, {st.session_state.user_profile.get('name', user_data.get('displayName', 'Friend'))}!</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar with user info and navigation
    with st.sidebar:
        # User profile section
        st.markdown(f"""
        <div class="user-profile">
            <div style="display: flex; align-items: center; gap: 10px;">
                <img src="{user_data.get('photoURL', 'https://via.placeholder.com/50')}" 
                     style="width: 50px; height: 50px; border-radius: 50%;" 
                     onerror="this.src='https://via.placeholder.com/50'">
                <div>
                    <strong>{user_data.get('displayName', 'User')}</strong>
                    <br><small>{user_data.get('email', '')}</small>
                    {'<br><span style="color: #ffa500;">🔄 Demo Mode</span>' if user_data.get('isDemo') else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick mood check
        st.subheader("Quick Mood Check")
        mood = st.selectbox(
            "How are you feeling?",
            ["😊 Happy", "😐 Neutral", "😰 Anxious", "😤 Stressed", "😔 Down"],
            key="mood_selector"
        )
        
        # Update current mood
        mood_mapping = {
            "😊 Happy": "positive",
            "😐 Neutral": "neutral", 
            "😰 Anxious": "anxious",
            "😤 Stressed": "stressed",
            "😔 Down": "negative"
        }
        st.session_state.current_mood = mood_mapping.get(mood, "neutral")
        
        # Quick stats
        st.subheader("Your Stats")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Conversations", 
                st.session_state.user_stats.get('total_conversations', len(st.session_state.conversation_history))
            )
        
        with col2:
            st.metric("Streak", f"{st.session_state.user_stats.get('current_streak', 3)} days")
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("🧘 Get Exercise", use_container_width=True):
            st.switch_page("pages/2_🧘_Exercises.py")
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/3_📊_Analytics.py")
        
        if st.button("👤 Profile Settings", use_container_width=True):
            st.switch_page("pages/4_👤_Profile.py")
        
        # Sign out button
        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Clear browser storage
            st.components.v1.html("""
            <script>
                sessionStorage.removeItem('mindmate_user');
                sessionStorage.removeItem('continue_to_app');
                window.location.reload();
            </script>
            """, height=0)
    
    # Main chat interface
    st.header("💬 Chat with MindMate")
    
    # Display conversation history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.conversation_history:
            for message in st.session_state.conversation_history[-10:]:  # Show last 10 messages
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>🧠 MindMate:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Welcome message
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🧠 MindMate:</strong> Hi {st.session_state.user_profile.get('name', user_data.get('displayName', 'Friend'))}! 
                I'm here to support you on your mental health journey. I remember our conversations and can help you track your progress. 
                How are you feeling today?
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Share what's on your mind...")
    
    if user_input:
        # Add user message to history
        st.session_state.conversation_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now(),
            'mood': st.session_state.current_mood
        })
        
        # Generate AI response
        with st.spinner("MindMate is thinking..."):
            try:
                ai_response = gemini.generate_response(
                    user_input,
                    st.session_state.conversation_history,
                    st.session_state.current_mood
                )
                
                # Add AI response to history
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': ai_response['response'],
                    'timestamp': datetime.now(),
                    'mood_detected': ai_response.get('mood_detected', 'neutral'),
                    'events': ai_response.get('events', [])
                })
                
                # Save to Firebase (if not demo user)
                if not user_data.get('isDemo', False):
                    firebase.save_conversation(
                        user_data['uid'],
                        user_input,
                        ai_response
                    )
                    
                    # Save mood entry if detected
                    if ai_response.get('mood_detected') and ai_response['mood_detected'] != 'neutral':
                        firebase.save_mood_entry(
                            user_data['uid'],
                            ai_response['mood_detected']
                        )
                
                # Update mood if detected
                if ai_response.get('mood_detected'):
                    st.session_state.current_mood = ai_response['mood_detected']
                
                # Show exercise suggestion if needed
                if ai_response.get('needs_exercise'):
                    st.info("💡 I think some wellness exercises might help you feel better. Check out the Exercises page!")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"Sorry, I had trouble processing that. Error: {str(e)}")
                
                # Fallback response
                fallback_response = "I'm here to listen and support you. Sometimes I have technical difficulties, but I care about your wellbeing. Can you tell me more about how you're feeling?"
                
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': fallback_response,
                    'timestamp': datetime.now()
                })
                
                st.rerun()

if __name__ == "__main__":
    main()