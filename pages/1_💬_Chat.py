import streamlit as st
from datetime import datetime
import time
import random

st.set_page_config(page_title="Chat - MindMate", page_icon="💬", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("💬 Chat with MindMate")
st.write("I'm here to listen, support, and remember our conversations")

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'current_mood' not in st.session_state:
    st.session_state.current_mood = 'neutral'

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {'name': 'Friend'}

if 'ai_thinking' not in st.session_state:
    st.session_state.ai_thinking = False

# Helper functions (moved to top)
def get_mood_emoji(mood):
    """Get emoji for mood"""
    emojis = {
        'positive': '😊',
        'neutral': '😐',
        'anxious': '😰', 
        'stressed': '😤',
        'negative': '😔'
    }
    return emojis.get(mood, '😐')

def get_exercise_suggestion(mood):
    """Get exercise suggestion based on mood"""
    suggestions = {
        'anxious': "🫁 **4-7-8 Breathing Technique**: Breathe in for 4 counts, hold for 7, exhale for 8. This helps activate your body's relaxation response and can quickly reduce anxiety. Try doing this 3-4 times in a row.",
        
        'stressed': "📦 **Box Breathing**: Breathe in for 4, hold for 4, out for 4, hold for 4. This technique is used by Navy SEALs to stay calm under pressure! Repeat 8-10 cycles to feel the stress melt away.",
        
        'negative': "🙏 **Gratitude Practice**: Try writing down 3 small things you're grateful for right now, no matter how tiny they seem. Research shows this can help shift your brain toward more positive thinking patterns.",
        
        'positive': "💝 **Loving-Kindness Meditation**: Since you're feeling good, this is a great time for loving-kindness meditation. Send good wishes to yourself first, then extend them to loved ones, and even difficult people in your life!",
        
        'neutral': "🧘 **Mindful Breathing**: Perfect time for simple mindful breathing. Just sit quietly and observe your natural breath for 5 minutes. No need to change anything, just notice each inhale and exhale."
    }
    
    base_msg = suggestions.get(mood, suggestions['neutral'])
    return f"{base_msg}\n\n💡 Would you like me to guide you through this exercise step-by-step? Or check out our Exercises page for more options!"

def get_mood_tip(mood):
    """Get tip based on current mood"""
    tips = {
        'anxious': "🌟 **Anxiety Tip**: Remember that anxiety is your mind trying to protect you, but sometimes it's overprotective. Try the 5-4-3-2-1 grounding technique: Name 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
        
        'stressed': "🌟 **Stress Tip**: When overwhelmed, try the 'One Thing Rule' - focus on completing just one small task. This can help break the cycle of feeling paralyzed by too much to do. You don't have to solve everything at once.",
        
        'negative': "🌟 **Mood Tip**: It's okay to feel down sometimes. Be gentle with yourself today. Sometimes we need to feel our emotions fully before we can move through them. You're not alone in this, and these feelings are temporary.",
        
        'positive': "🌟 **Positive Tip**: Great mood! This is an ideal time to tackle challenging tasks, reach out to help someone else, or work on a goal that's important to you. Positive emotions can be contagious and help build resilience for tougher days.",
        
        'neutral': "🌟 **Mindful Tip**: Neutral moods are perfect for reflection and planning. What would make today feel meaningful to you? Sometimes the calmest moments offer the clearest insights about what we truly want."
    }
    
    return tips.get(mood, tips['neutral'])

def detect_mood_from_text(text):
    """Simple mood detection from text"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['happy', 'great', 'wonderful', 'excited', 'amazing', 'fantastic']):
        return 'positive'
    elif any(word in text_lower for word in ['anxious', 'worried', 'nervous', 'panic', 'fear']):
        return 'anxious'
    elif any(word in text_lower for word in ['stressed', 'overwhelmed', 'pressure', 'busy', 'rush']):
        return 'stressed'
    elif any(word in text_lower for word in ['sad', 'down', 'depressed', 'hopeless', 'miserable']):
        return 'negative'
    else:
        return 'neutral'

def extract_basic_events(text):
    """Extract basic events and dates from text"""
    events = []
    text_lower = text.lower()
    
    # Simple patterns for events
    if 'tomorrow' in text_lower:
        if any(word in text_lower for word in ['appointment', 'meeting', 'interview', 'exam', 'test']):
            events.append({
                'description': 'Important event tomorrow',
                'date': 'tomorrow',
                'type': 'appointment'
            })
    
    if 'next week' in text_lower:
        events.append({
            'description': 'Event next week',
            'date': 'next week', 
            'type': 'general'
        })
    
    # Look for specific appointments
    if 'therapy' in text_lower or 'counseling' in text_lower:
        events.append({
            'description': 'Therapy session',
            'date': 'upcoming',
            'type': 'therapy'
        })
    
    return events

def generate_ai_response(user_message, history, current_mood, profile):
    """Generate AI response (simplified version without external API)"""
    
    # Simple keyword-based responses for demo
    user_lower = user_message.lower()
    
    # Detect mood from message
    mood_detected = detect_mood_from_text(user_message)
    
    # Check if exercise might help
    needs_exercise = any(word in user_lower for word in ['stressed', 'anxious', 'overwhelmed', 'panic', 'worry'])
    
    # Extract basic events
    events = extract_basic_events(user_message)
    
    # Generate contextual response
    if any(word in user_lower for word in ['sad', 'down', 'depressed', 'hopeless']):
        response = f"I can hear that you're going through a difficult time, {profile['name']}. Your feelings are completely valid, and I want you to know that you're not alone. It takes courage to share these feelings. What's been weighing most heavily on your mind lately?"
        
    elif any(word in user_lower for word in ['anxious', 'worried', 'nervous', 'panic']):
        response = f"I understand you're feeling anxious right now, {profile['name']}. Anxiety can feel overwhelming, but remember that this feeling is temporary. You've gotten through difficult moments before. Have you tried any breathing exercises, or would you like me to guide you through one?"
        
    elif any(word in user_lower for word in ['stressed', 'overwhelmed', 'busy', 'pressure']):
        response = f"It sounds like you're dealing with a lot of stress, {profile['name']}. When we're overwhelmed, it can feel like everything is urgent. Let's take a step back together. What's the most pressing thing on your mind right now? Sometimes breaking things down can make them feel more manageable."
        
    elif any(word in user_lower for word in ['happy', 'good', 'great', 'excited', 'wonderful']):
        response = f"I'm so glad to hear you're feeling positive, {profile['name']}! It's wonderful when things are going well. What's been the highlight of your day? I love celebrating good moments with you."
        
    elif any(word in user_lower for word in ['tired', 'exhausted', 'drained', 'sleep']):
        response = f"It sounds like you're feeling really drained, {profile['name']}. Mental and physical exhaustion can be so challenging. Have you been getting enough rest? Sometimes our bodies and minds are telling us we need to slow down and recharge."
        
    elif 'thank you' in user_lower or 'thanks' in user_lower:
        response = f"You're so welcome, {profile['name']}! I'm here for you whenever you need support. It means a lot to me that our conversations are helpful. How are you feeling right now?"
        
    else:
        # General supportive response
        responses = [
            f"Thank you for sharing that with me, {profile['name']}. I'm here to listen and support you. Can you tell me more about what you're experiencing?",
            f"I appreciate you opening up to me, {profile['name']}. Your thoughts and feelings matter. What's been on your mind lately?",
            f"I'm glad you felt comfortable sharing that with me, {profile['name']}. How has this been affecting you day-to-day?",
            f"That sounds important, {profile['name']}. I want to understand better - can you help me see this from your perspective?"
        ]
        response = random.choice(responses)
    
    # Reference previous conversations occasionally
    if len(history) > 5 and random.random() < 0.3:
        response += " I remember we've talked before about similar feelings, and I'm here to continue supporting you through this journey."
    
    return {
        'response': response,
        'mood_detected': mood_detected,
        'needs_exercise': needs_exercise,
        'events': events
    }

# Sidebar with mood and quick actions
with st.sidebar:
    st.header("💭 Current Session")
    
    # Quick mood selector
    st.subheader("How are you feeling?")
    mood_options = {
        "😊 Happy": "positive",
        "😐 Neutral": "neutral", 
        "😰 Anxious": "anxious",
        "😤 Stressed": "stressed",
        "😔 Down": "negative"
    }
    
    selected_mood = st.selectbox(
        "Select your mood:",
        list(mood_options.keys()),
        index=list(mood_options.values()).index(st.session_state.current_mood)
    )
    
    st.session_state.current_mood = mood_options[selected_mood]
    
    # Session stats
    st.subheader("📊 Session Stats")
    st.metric("Messages", len(st.session_state.conversation_history))
    st.metric("Current Mood", st.session_state.current_mood.title())
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("🧘 Suggest Exercise", use_container_width=True):
        exercise_suggestion = get_exercise_suggestion(st.session_state.current_mood)
        st.session_state.conversation_history.append({
            'role': 'assistant',
            'content': exercise_suggestion,
            'timestamp': datetime.now(),
            'type': 'exercise_suggestion'
        })
        st.rerun()
    
    if st.button("💡 Mood Tips", use_container_width=True):
        mood_tip = get_mood_tip(st.session_state.current_mood)
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

# Main chat area
chat_container = st.container()

# Display conversation history
with chat_container:
    if st.session_state.conversation_history:
        for i, message in enumerate(st.session_state.conversation_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                    <br><small style="opacity: 0.8;">{message['timestamp'].strftime('%H:%M')}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                mood_class = f"mood-{message.get('mood_detected', 'neutral')}"
                mood_emoji = get_mood_emoji(message.get('mood_detected', 'neutral'))
                
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🧠 MindMate:</strong> {message['content']}
                    <span class="mood-indicator {mood_class}">{mood_emoji} {message.get('mood_detected', 'neutral').title()}</span>
                    <br><small style="opacity: 0.6;">{message['timestamp'].strftime('%H:%M')}</small>
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
        st.markdown(f"""
        <div class="chat-message ai-message">
            <strong>🧠 MindMate:</strong> Hi {st.session_state.user_profile['name']}! I'm MindMate, your AI mental health companion. 
            I'm here to listen, support you, and remember our conversations. I notice you're feeling {st.session_state.current_mood} today. 
            How are you doing? Feel free to share anything that's on your mind.
        </div>
        """, unsafe_allow_html=True)

# Thinking indicator
if st.session_state.ai_thinking:
    with st.empty():
        for i in range(3):
            st.markdown("🧠 MindMate is thinking" + "." * (i + 1))
            time.sleep(0.5)

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
    
    # Show thinking indicator
    st.session_state.ai_thinking = True
    
    # Generate AI response
    ai_response = generate_ai_response(
        user_input, 
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
    
    # Update current mood if AI detected a change
    if ai_response.get('mood_detected'):
        st.session_state.current_mood = ai_response['mood_detected']
    
    st.session_state.ai_thinking = False
    st.rerun()

# Footer with helpful links
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🧘 Try Exercises", use_container_width=True):
        st.switch_page("pages/2_🧘_Exercises.py")

with col2:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/3_📊_Analytics.py")

with col3:
    if st.button("👤 Update Profile", use_container_width=True):
        st.switch_page("pages/4_👤_Profile.py")

# Crisis support information
if st.session_state.current_mood == 'negative' or any('crisis' in msg.get('content', '').lower() for msg in st.session_state.conversation_history[-3:]):
    st.error("""
    🚨 **Crisis Support Resources**
    
    If you're having thoughts of self-harm, please reach out for immediate help:
    • **Crisis Text Line**: Text HOME to 741741
    • **National Suicide Prevention Lifeline**: 988
    • **Emergency Services**: 911
    
    You matter, and help is available 24/7.
    """)