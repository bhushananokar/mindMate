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
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    from services.firebase_service import FirebaseService
    from services.gemini_service import GeminiService
    
    firebase = FirebaseService()
    gemini = GeminiService()
    
    return firebase, gemini

# Initialize session state
def init_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_mood' not in st.session_state:
        st.session_state.current_mood = 'neutral'
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'name': 'Friend',
            'preferences': [],
            'goals': []
        }

def main():
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 MindMate</h1>
        <p>Your AI Mental Health Companion</p>
        <p><em>I remember our conversations and care about your wellbeing</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🧠 MindMate")
        st.write(f"Hello, {st.session_state.user_profile['name']}!")
        
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
            st.metric("Conversations", len(st.session_state.conversation_history))
        
        with col2:
            st.metric("Current Streak", "3 days")
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("🧘 Get Exercise Suggestion", use_container_width=True):
            st.switch_page("pages/2_🧘_Exercises.py")
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/3_📊_Analytics.py")
    
    # Main chat interface
    st.header("💬 Chat with MindMate")
    
    # Initialize services
    try:
        firebase, gemini = init_services()
        
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
                st.markdown("""
                <div class="chat-message ai-message">
                    <strong>🧠 MindMate:</strong> Hi there! I'm MindMate, your AI mental health companion. 
                    I'm here to listen, support you, and remember our conversations. How are you feeling today?
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
                    
                    # Save to Firebase
                    firebase.save_conversation(
                        st.session_state.user_id,
                        user_input,
                        ai_response
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
    
    except Exception as e:
        st.error("Unable to connect to services. Running in offline mode.")
        st.write("You can still use the basic chat functionality!")
        
        # Basic offline chat
        if st.session_state.conversation_history:
            for message in st.session_state.conversation_history[-5:]:
                if message['role'] == 'user':
                    st.chat_message("user").write(message['content'])
                else:
                    st.chat_message("assistant").write(message['content'])
        
        user_input = st.chat_input("Share what's on your mind...")
        if user_input:
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': user_input,
                'timestamp': datetime.now()
            })
            
            # Simple offline response
            offline_response = f"Thank you for sharing that with me. I understand you're feeling {st.session_state.current_mood}. I'm here to listen and support you, even when my AI features aren't working perfectly."
            
            st.session_state.conversation_history.append({
                'role': 'assistant',
                'content': offline_response,
                'timestamp': datetime.now()
            })
            
            st.rerun()

if __name__ == "__main__":
    main()