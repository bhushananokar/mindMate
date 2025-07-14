import streamlit as st
from datetime import datetime
import time
import random
import sys
import os

# Add the parent directory to the path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Chat - MindMate", page_icon="💬", layout="wide")

# Check authentication
if not get_current_user():
    st.error("Please log in to start chatting.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# Initialize services
@st.cache_resource
def init_services():
    from services.firebase_service import FirebaseService
    from services.gemini_service import GeminiService
    firebase = FirebaseService()
    gemini = GeminiService()
    return firebase, gemini

firebase_service, gemini_service = init_services()

# Custom CSS for chat interface
st.markdown("""
<style>
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 5px;
    }
    
    .ai-message {
        background: #f0f2f6;
        color: #333;
        border-bottom-left-radius: 5px;
        border-left: 4px solid #667eea;
    }
    
    .mood-indicator {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }
    
    .mood-positive { background: #d4edda; color: #155724; }
    .mood-neutral { background: #fff3cd; color: #856404; }
    .mood-anxious { background: #fdeacf; color: #8a4e00; }
    .mood-stressed { background: #e2e3e5; color: #383d41; }
    .mood-negative { background: #f8d7da; color: #721c24; }
    
    .user-info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 Chat with MindMate")
user_name = get_user_display_name()
user = get_current_user()

# Show demo mode indicator
if is_demo_user():
    st.info("🔄 **Demo Mode**: Conversations will be saved to your session only. Sign in with Google to save permanently!")

st.write(f"I'm here to listen, support, and remember our conversations, {user_name}")

# Initialize session state
init_session_state()

# Load user data from Firebase if not demo
if not is_demo_user():
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading your conversation history..."):
            load_user_data_from_firebase(firebase_service)
            st.session_state.data_loaded = True

# Helper functions
def generate_ai_response(user_message, history, current_mood, profile):
    """Generate AI response using Gemini service or fallback"""
    try:
        return gemini_service.generate_response(user_message, history, current_mood)
    except Exception as e:
        print(f"Gemini service error: {e}")
        return generate_fallback_response(user_message, current_mood, profile)

def generate_fallback_response(user_message, current_mood, profile):
    """Generate fallback response when AI service is unavailable"""
    user_lower = user_message.lower()
    name = profile.get('name', user_name)
    
    # Detect mood from message
    mood_detected = detect_mood_from_text(user_message)
    
    # Check if exercise might help
    needs_exercise = any(word in user_lower for word in ['stressed', 'anxious', 'overwhelmed', 'panic', 'worry'])
    
    # Extract basic events
    events = extract_events_from_text(user_message)
    
    # Get conversation history from session state
    conversation_history = st.session_state.get('conversation_history', [])
    
    # Generate contextual response
    if any(word in user_lower for word in ['sad', 'down', 'depressed', 'hopeless']):
        response = f"I can hear that you're going through a difficult time, {name}. Your feelings are completely valid, and I want you to know that you're not alone. It takes courage to share these feelings. What's been weighing most heavily on your mind lately?"
        
    elif any(word in user_lower for word in ['anxious', 'worried', 'nervous', 'panic']):
        response = f"I understand you're feeling anxious right now, {name}. Anxiety can feel overwhelming, but remember that this feeling is temporary. You've gotten through difficult moments before. Have you tried any breathing exercises, or would you like me to guide you through one?"
        
    elif any(word in user_lower for word in ['stressed', 'overwhelmed', 'busy', 'pressure']):
        response = f"It sounds like you're dealing with a lot of stress, {name}. When we're overwhelmed, it can feel like everything is urgent. Let's take a step back together. What's the most pressing thing on your mind right now? Sometimes breaking things down can make them feel more manageable."
        
    elif any(word in user_lower for word in ['happy', 'good', 'great', 'excited', 'wonderful']):
        response = f"I'm so glad to hear you're feeling positive, {name}! It's wonderful when things are going well. What's been the highlight of your day? I love celebrating good moments with you."
        
    elif any(word in user_lower for word in ['tired', 'exhausted', 'drained', 'sleep']):
        response = f"It sounds like you're feeling really drained, {name}. Mental and physical exhaustion can be so challenging. Have you been getting enough rest? Sometimes our bodies and minds are telling us we need to slow down and recharge."
        
    elif 'thank you' in user_lower or 'thanks' in user_lower:
        response = f"You're so welcome, {name}! I'm here for you whenever you need support. It means a lot to me that our conversations are helpful. How are you feeling right now?"
        
    else:
        # General supportive response
        responses = [
            f"Thank you for sharing that with me, {name}. I'm here to listen and support you. Can you tell me more about what you're experiencing?",
            f"I appreciate you opening up to me, {name}. Your thoughts and feelings matter. What's been on your mind lately?",
            f"I'm glad you felt comfortable sharing that with me, {name}. How has this been affecting you day-to-day?",
            f"That sounds important, {name}. I want to understand better - can you help me see this from your perspective?"
        ]
        response = random.choice(responses)
    
    # Reference previous conversations occasionally
    if len(conversation_history) > 5 and random.random() < 0.3:
        response += " I remember we've talked before about similar feelings, and I'm here to continue supporting you through this journey."
    
    return {
        'response': response,
        'mood_detected': mood_detected,
        'needs_exercise': needs_exercise,
        'events': events
    }

# Sidebar with user info and quick actions
with st.sidebar:
    # User profile section
    st.markdown(f"""
    <div class="user-info-card">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="{user.get('photoURL', 'https://via.placeholder.com/50')}" 
                 style="width: 50px; height: 50px; border-radius: 50%;" 
                 onerror="this.src='https://via.placeholder.com/50'">
            <div>
                <strong>{user.get('displayName', 'User')}</strong>
                <br><small>{user.get('email', '')}</small>
                {'<br><span style="color: #ffa500;">🔄 Demo Mode</span>' if is_demo_user() else ''}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick mood check
    st.subheader("Quick Mood Check")
    mood_options = {
        "😊 Happy": "positive",
        "😐 Neutral": "neutral", 
        "😰 Anxious": "anxious",
        "😤 Stressed": "stressed",
        "😔 Down": "negative"
    }
    
    selected_mood = st.selectbox(
        "How are you feeling?",
        list(mood_options.keys()),
        index=list(mood_options.values()).index(st.session_state.current_mood)
    )
    
    st.session_state.current_mood = mood_options[selected_mood]
    
    # Save mood entry
    if st.button("📝 Log This Mood", use_container_width=True):
        save_mood_entry(st.session_state.current_mood, f"Mood logged during chat: {selected_mood}", firebase_service)
        st.success("Mood logged!")
        time.sleep(1)
        st.rerun()
    
    # Session stats
    st.subheader("📊 Session Stats")
    user_stats = format_user_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages", len([msg for msg in st.session_state.conversation_history if msg.get('role') == 'user']))
    with col2:
        st.metric("Mood", st.session_state.current_mood.title())
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("🧘 Suggest Exercise", use_container_width=True):
        exercise_suggestion = get_exercise_for_mood(st.session_state.current_mood)
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': f"Based on your current mood ({st.session_state.current_mood}), I recommend: **{exercise_suggestion['title']}**\n\n{exercise_suggestion['description']}\n\n**Duration:** {exercise_suggestion['duration']}\n**Benefits:** {exercise_suggestion['benefits']}\n\nWould you like me to guide you through this exercise step by step?",
            'timestamp': datetime.now(),
            'type': 'exercise_suggestion'
        })
        st.rerun()
    
    if st.button("💡 Mood Tips", use_container_width=True):
        tips = {
            'anxious': "🌟 **Anxiety Tip**: Remember that anxiety is your mind trying to protect you, but sometimes it's overprotective. Try the 5-4-3-2-1 grounding technique: Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
            'stressed': "🌟 **Stress Tip**: When overwhelmed, try the 'One Thing Rule' - focus on completing just one small task. This can help break the cycle of feeling paralyzed by too much to do. You don't have to solve everything at once.",
            'negative': "🌟 **Mood Tip**: It's okay to feel down sometimes. Be gentle with yourself today. Sometimes we need to feel our emotions fully before we can move through them. You're not alone in this, and these feelings are temporary.",
            'positive': "🌟 **Positive Tip**: Great mood! This is an ideal time to tackle challenging tasks, reach out to help someone else, or work on a goal that's important to you. Positive emotions can be contagious and help build resilience for tougher days.",
            'neutral': "🌟 **Mindful Tip**: Neutral moods are perfect for reflection and planning. What would make today feel meaningful to you? Sometimes the calmest moments offer the clearest insights about what we truly want."
        }
        
        mood_tip = tips.get(st.session_state.current_mood, tips['neutral'])
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': mood_tip,
            'timestamp': datetime.now(),
            'type': 'mood_tip'
        })
        st.rerun()
    
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
    
    # Navigation
    st.markdown("---")
    st.subheader("🧭 Navigate")
    
    if st.button("🧘 Exercises", use_container_width=True):
        st.switch_page("pages/2_🧘_Exercises.py")
    
    if st.button("📊 Analytics", use_container_width=True):
        st.switch_page("pages/3_📊_Analytics.py")
    
    if st.button("👤 Profile", use_container_width=True):
        st.switch_page("pages/4_👤_Profile.py")

# Main chat area
chat_container = st.container()

# Display conversation history
with chat_container:
    if st.session_state.conversation_history:
        # Show last 20 messages to keep performance good
        recent_messages = st.session_state.conversation_history[-20:]
        
        for i, message in enumerate(recent_messages):
            timestamp = message.get('timestamp', datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                    <br><small style="opacity: 0.8;">{timestamp.strftime('%H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                mood_detected = message.get('mood_detected', 'neutral')
                mood_class = f"mood-{mood_detected}"
                mood_emoji = get_mood_emoji(mood_detected)
                
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🧠 MindMate:</strong> {message['content']}
                    <span class="mood-indicator {mood_class}">{mood_emoji} {mood_detected.title()}</span>
                    <br><small style="opacity: 0.6;">{timestamp.strftime('%H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Show exercise suggestion if available
                if message.get('needs_exercise'):
                    st.info("💡 I think some wellness exercises might help you feel better. Check out the Exercises page!")
                
                # Show events detected
                if message.get('events'):
                    with st.expander("📅 Events I remembered"):
                        for event in message['events']:
                            st.write(f"• {event.get('description', 'Event')} - {event.get('date', 'Date not specified')}")
    else:
        # Welcome message
        welcome_msg = show_welcome_message()
        if welcome_msg:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🧠 MindMate:</strong> {welcome_msg}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message ai-message">
                <strong>🧠 MindMate:</strong> Welcome back, {user_name}! I'm here to support you on your mental health journey. 
                I remember our conversations and can help you track your progress over time. 
                How are you feeling today?
            </div>
            """, unsafe_allow_html=True)

# Show typing indicator if AI is thinking
if st.session_state.get('ai_thinking', False):
    st.markdown("""
    <div class="chat-message ai-message" style="opacity: 0.7;">
        <strong>🧠 MindMate:</strong> <em>typing...</em>
    </div>
    """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Share what's on your mind...")

if user_input:
    # Validate input
    is_valid, error_msg = validate_input(user_input)
    if not is_valid:
        st.error(error_msg)
        st.stop()
    
    # Check for crisis situations
    if is_crisis_situation(user_input):
        crisis_resources = get_crisis_resources()
        st.error(f"""
        🚨 **Crisis Support Needed**
        
        {crisis_resources['message']}
        
        **Immediate Help:**
        • **Crisis Text Line**: {crisis_resources['crisis_text_line']}
        • **Suicide Prevention**: {crisis_resources['suicide_prevention']}
        • **Emergency**: {crisis_resources['emergency']}
        """)
    
    # Add user message to history
    st.session_state.conversation_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now(),
        'mood': st.session_state.current_mood
    })
    
    # Show thinking indicator
    st.session_state.ai_thinking = True
    st.rerun()

# Process AI response if user just sent a message
if st.session_state.get('ai_thinking', False):
    # Get the last user message
    user_messages = [msg for msg in st.session_state.conversation_history if msg['role'] == 'user']
    if user_messages:
        last_user_message = user_messages[-1]['content']
        
        # Generate AI response
        with st.spinner("MindMate is thinking..."):
            try:
                ai_response = generate_ai_response(
                    last_user_message,
                    st.session_state.conversation_history,
                    st.session_state.current_mood,
                    st.session_state.user_profile
                )
                
                # Add AI response to history
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': ai_response['response'],
                    'timestamp': datetime.now(),
                    'mood_detected': ai_response.get('mood_detected', 'neutral'),
                    'needs_exercise': ai_response.get('needs_exercise', False),
                    'events': ai_response.get('events', []),
                    'type': 'chat_response'
                })
                
                # Save to Firebase (if not demo user)
                if not is_demo_user():
                    firebase_service.save_conversation(
                        get_user_id(),
                        last_user_message,
                        ai_response
                    )
                    
                    # Save mood entry if detected
                    if ai_response.get('mood_detected') and ai_response['mood_detected'] != 'neutral':
                        save_mood_entry(
                            ai_response['mood_detected'],
                            f"Detected from conversation: {last_user_message[:50]}...",
                            firebase_service
                        )
                
                # Update current mood if detected
                if ai_response.get('mood_detected'):
                    st.session_state.current_mood = ai_response['mood_detected']
                
                st.session_state.ai_thinking = False
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
                
                st.session_state.ai_thinking = False
                st.rerun()

# Show suggestions if conversation is just starting
if len(st.session_state.conversation_history) <= 2:
    st.markdown("---")
    st.subheader("💬 Conversation Starters")
    
    col1, col2, col3 = st.columns(3)
    
    suggestions = [
        "I'm feeling overwhelmed with work lately",
        "I had a really good day today",
        "I'm anxious about an upcoming event",
        "I've been having trouble sleeping",
        "I want to work on my mental health",
        "I feel like I need some motivation"
    ]
    
    for i, suggestion in enumerate(suggestions):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                # Add suggestion as user message
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': suggestion,
                    'timestamp': datetime.now(),
                    'mood': st.session_state.current_mood
                })
                st.session_state.ai_thinking = True
                st.rerun()

# Footer with helpful information
st.markdown("---")

# Show crisis support if mood is negative
if st.session_state.current_mood == 'negative' or any('crisis' in msg.get('content', '').lower() for msg in st.session_state.conversation_history[-3:]):
    st.error("""
    🚨 **Crisis Support Resources**
    
    If you're having thoughts of self-harm, please reach out for immediate help:
    • **Crisis Text Line**: Text HOME to 741741
    • **National Suicide Prevention Lifeline**: 988
    • **Emergency Services**: 911
    
    You matter, and help is available 24/7.
    """)

# Tips and reminders
tips_col1, tips_col2 = st.columns(2)

with tips_col1:
    st.info("""
    💡 **Chat Tips:**
    - Be honest about your feelings
    - MindMate remembers your conversations
    - Use the mood selector to track daily feelings
    - Try exercises when suggested
    """)

with tips_col2:
    if not is_demo_user():
        st.success("""
        ✅ **Your Progress is Saved:**
        - Conversations sync across devices
        - Mood history builds analytics
        - Profile saves your preferences
        - Exercise progress tracked
        """)
    else:
        st.warning("""
        ⚠️ **Demo Mode Active:**
        - Data saved to session only
        - Sign in to save permanently
        - Full features available after login
        - Export option available
        """)

# Conversation statistics
if len(st.session_state.conversation_history) > 0:
    st.markdown("---")
    st.subheader("📈 This Conversation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    user_msg_count = len([msg for msg in st.session_state.conversation_history if msg['role'] == 'user'])
    ai_msg_count = len([msg for msg in st.session_state.conversation_history if msg['role'] == 'assistant'])
    
    with col1:
        st.metric("Your Messages", user_msg_count)
    
    with col2:
        st.metric("MindMate Replies", ai_msg_count)
    
    with col3:
        if st.session_state.conversation_history:
            duration = datetime.now() - st.session_state.conversation_history[0]['timestamp']
            st.metric("Duration", f"{duration.seconds // 60} min")
        else:
            st.metric("Duration", "0 min")
    
    with col4:
        mood_changes = len(set(msg.get('mood_detected', 'neutral') for msg in st.session_state.conversation_history if msg['role'] == 'assistant'))
        st.metric("Mood Insights", mood_changes)