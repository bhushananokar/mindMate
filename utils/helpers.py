import streamlit as st
import re
from datetime import datetime, timedelta
import random
import json

def init_session_state():
    """Initialize all session state variables"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'current_mood' not in st.session_state:
        st.session_state.current_mood = 'neutral'
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'name': 'Friend',
            'age_range': '',
            'goals': [],
            'preferences': [],
            'notifications': True,
            'privacy_level': 'Medium',
            'created_at': datetime.now()
        }
    
    if 'user_stats' not in st.session_state:
        st.session_state.user_stats = {
            'total_conversations': 0,
            'total_mood_entries': 0,
            'current_streak': 0,
            'exercises_completed': 0
        }
    
    if 'mood_history' not in st.session_state:
        st.session_state.mood_history = []
    
    if 'exercise_completions' not in st.session_state:
        st.session_state.exercise_completions = []

def get_current_user():
    """Get current authenticated user"""
    return st.session_state.get('user', None)

def is_demo_user():
    """Check if current user is a demo user"""
    user = get_current_user()
    return user and user.get('isDemo', False)

def get_user_id():
    """Get current user ID"""
    user = get_current_user()
    return user['uid'] if user else None

def get_user_display_name():
    """Get user's display name"""
    user = get_current_user()
    if user:
        return user.get('displayName', 'Friend')
    return st.session_state.user_profile.get('name', 'Friend')

def load_user_data_from_firebase(firebase_service):
    """Load user data from Firebase"""
    user_id = get_user_id()
    if not user_id or is_demo_user():
        return False
    
    try:
        # Load conversations
        conversations = firebase_service.get_user_conversations(user_id, limit=50)
        if conversations:
            # Convert Firebase conversations to session format
            st.session_state.conversation_history = []
            for conv in reversed(conversations):  # Reverse to get chronological order
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': conv['user_message'],
                    'timestamp': conv['timestamp']
                })
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': conv['ai_response'],
                    'timestamp': conv['timestamp'],
                    'mood_detected': conv.get('mood_detected', 'neutral'),
                    'events': conv.get('events', [])
                })
        
        # Load mood analytics
        mood_data = firebase_service.get_mood_analytics(user_id, days=30)
        if mood_data and mood_data.get('mood_history'):
            st.session_state.mood_history = mood_data['mood_history']
        
        # Load user profile
        profile = firebase_service.get_user_profile(user_id)
        if profile:
            st.session_state.user_profile = profile.get('preferences', st.session_state.user_profile)
            st.session_state.user_stats = profile.get('stats', st.session_state.user_stats)
        
        return True
        
    except Exception as e:
        print(f"Error loading user data from Firebase: {e}")
        return False

def save_user_profile_to_firebase(firebase_service, profile_data):
    """Save user profile to Firebase"""
    user_id = get_user_id()
    if not user_id or is_demo_user():
        return False
    
    try:
        return firebase_service.update_user_preferences(user_id, profile_data)
    except Exception as e:
        print(f"Error saving profile to Firebase: {e}")
        return False

def get_mood_emoji(mood):
    """Return emoji for given mood"""
    mood_emojis = {
        'positive': '😊',
        'neutral': '😐',
        'anxious': '😰',
        'stressed': '😤',
        'negative': '😔',
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'excited': '🤩',
        'calm': '😌'
    }
    return mood_emojis.get(mood.lower(), '😐')

def get_mood_color(mood):
    """Return color code for given mood"""
    mood_colors = {
        'positive': '#28a745',
        'neutral': '#ffc107',
        'anxious': '#fd7e14',
        'stressed': '#6f42c1',
        'negative': '#dc3545',
        'happy': '#28a745',
        'sad': '#dc3545',
        'angry': '#dc3545',
        'excited': '#17a2b8',
        'calm': '#20c997'
    }
    return mood_colors.get(mood.lower(), '#6c757d')

def detect_mood_from_text(text):
    """Detect mood from user text input"""
    text_lower = text.lower()
    
    # Positive mood indicators
    positive_words = ['happy', 'great', 'wonderful', 'excited', 'amazing', 'fantastic', 
                     'good', 'better', 'awesome', 'love', 'perfect', 'brilliant']
    
    # Anxious mood indicators
    anxious_words = ['anxious', 'worried', 'nervous', 'panic', 'fear', 'scared', 
                    'frightened', 'terrified', 'concern', 'worry']
    
    # Stressed mood indicators
    stressed_words = ['stressed', 'overwhelmed', 'pressure', 'busy', 'rush', 
                     'deadline', 'exhausted', 'tired', 'overloaded']
    
    # Negative mood indicators
    negative_words = ['sad', 'down', 'depressed', 'hopeless', 'miserable', 
                     'awful', 'terrible', 'horrible', 'upset', 'disappointed']
    
    # Count matches for each mood category
    positive_count = sum(1 for word in positive_words if word in text_lower)
    anxious_count = sum(1 for word in anxious_words if word in text_lower)
    stressed_count = sum(1 for word in stressed_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    # Determine dominant mood
    mood_scores = {
        'positive': positive_count,
        'anxious': anxious_count,
        'stressed': stressed_count,
        'negative': negative_count
    }
    
    # Return mood with highest score, default to neutral
    dominant_mood = max(mood_scores, key=mood_scores.get)
    return dominant_mood if mood_scores[dominant_mood] > 0 else 'neutral'

def extract_events_from_text(text):
    """Extract potential events and dates from user text"""
    events = []
    text_lower = text.lower()
    
    # Time patterns
    time_patterns = [
        r'tomorrow',
        r'next week',
        r'next month',
        r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
        r'\d{1,2}/(1[0-2]|0?[1-9])',  # MM/DD pattern
        r'in\s+\d+\s+(days?|weeks?|months?)'
    ]
    
    # Event keywords
    event_keywords = ['appointment', 'meeting', 'interview', 'exam', 'test', 'deadline', 
                     'therapy', 'doctor', 'dentist', 'presentation', 'conference', 
                     'wedding', 'party', 'vacation', 'trip']
    
    # Find time expressions
    for pattern in time_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if isinstance(match, tuple):
                match = ' '.join(match)
            
            # Look for nearby event keywords
            for keyword in event_keywords:
                if keyword in text_lower:
                    events.append({
                        'description': f"{keyword.title()} mentioned",
                        'date': match,
                        'type': 'appointment',
                        'extracted_from': text[:100] + '...' if len(text) > 100 else text
                    })
                    break
            else:
                # Generic event if no specific keyword found
                events.append({
                    'description': f"Event on {match}",
                    'date': match,
                    'type': 'general',
                    'extracted_from': text[:100] + '...' if len(text) > 100 else text
                })
    
    return events[:3]  # Return max 3 events

def get_supportive_response(mood, user_name="Friend", context=""):
    """Generate contextual supportive responses based on mood"""
    
    responses = {
        'positive': [
            f"I'm so glad to hear you're feeling positive, {user_name}! It's wonderful when things are going well. What's been the highlight of your day?",
            f"Your positive energy is contagious, {user_name}! I love celebrating good moments with you. What's making you feel so good today?",
            f"It's beautiful to see you in such a good mood, {user_name}! These moments are precious. How can we help this feeling last?"
        ],
        
        'anxious': [
            f"I can sense you're feeling anxious right now, {user_name}. That must feel overwhelming. Remember that anxiety is temporary, and you've gotten through difficult moments before.",
            f"Anxiety can feel so intense, {user_name}. Your feelings are completely valid. Would it help to talk about what's triggering these feelings?",
            f"I understand you're feeling anxious, {user_name}. Let's take this one breath at a time. You're safe right now, and I'm here with you."
        ],
        
        'stressed': [
            f"It sounds like you're dealing with a lot of pressure, {user_name}. When we're overwhelmed, everything can feel urgent. Let's break this down together.",
            f"Stress can be so exhausting, {user_name}. You're handling more than many people could. What feels like the most pressing concern right now?",
            f"I hear that you're feeling overwhelmed, {user_name}. Sometimes our minds need a moment to pause and reset. You don't have to carry this alone."
        ],
        
        'negative': [
            f"I can hear that you're going through a difficult time, {user_name}. Your feelings are completely valid, and you're incredibly brave for sharing them with me.",
            f"It takes courage to acknowledge when we're struggling, {user_name}. You're not alone in this, and these feelings won't last forever.",
            f"I'm sorry you're feeling this way, {user_name}. Dark moments can feel endless, but you matter, and there are people who care about you."
        ],
        
        'neutral': [
            f"Thank you for sharing with me, {user_name}. I'm here to listen and support you in whatever way I can. What's been on your mind lately?",
            f"I appreciate you opening up to me, {user_name}. Sometimes neutral moments are perfect for reflection. How has your day been?",
            f"I'm glad you're here, {user_name}. Whether you need to talk through something specific or just want company, I'm here for you."
        ]
    }
    
    mood_responses = responses.get(mood, responses['neutral'])
    return random.choice(mood_responses)

def get_exercise_for_mood(mood):
    """Return appropriate exercise suggestions based on mood"""
    exercises = {
        'anxious': {
            'title': '4-7-8 Breathing',
            'description': 'A powerful technique to calm anxiety',
            'instructions': [
                'Sit comfortably with your back straight',
                'Exhale completely through your mouth',
                'Close your mouth and inhale through nose for 4 counts',
                'Hold your breath for 7 counts',
                'Exhale through mouth for 8 counts',
                'Repeat 3-4 times'
            ],
            'duration': '5 minutes',
            'benefits': 'Activates relaxation response, reduces anxiety'
        },
        
        'stressed': {
            'title': 'Progressive Muscle Relaxation',
            'description': 'Release physical tension systematically',
            'instructions': [
                'Start with your toes - tense for 5 seconds, then relax',
                'Move to your calves, thighs, buttocks',
                'Tense your abdomen, then chest and shoulders',
                'Make fists, tense arms, then relax',
                'Scrunch face muscles, then relax',
                'Notice the difference between tension and relaxation'
            ],
            'duration': '12 minutes',
            'benefits': 'Releases physical stress, promotes calm'
        },
        
        'negative': {
            'title': 'Gratitude Practice',
            'description': 'Shift perspective to positive aspects',
            'instructions': [
                'Get a pen and paper or open notes app',
                'Write down 3 things you\'re grateful for today',
                'For each item, write WHY you\'re grateful',
                'Think of someone who helped make this possible',
                'Consider how your life would be different without it',
                'Take a moment to really feel the gratitude'
            ],
            'duration': '8 minutes',
            'benefits': 'Improves mood, shifts focus to positive'
        },
        
        'positive': {
            'title': 'Loving-Kindness Meditation',
            'description': 'Spread positive energy to yourself and others',
            'instructions': [
                'Sit comfortably and close your eyes',
                'Start by sending love to yourself: "May I be happy"',
                'Extend to loved ones: "May you be happy"',
                'Include neutral people in your life',
                'Even include difficult people',
                'End with all beings: "May all beings be happy"'
            ],
            'duration': '12 minutes',
            'benefits': 'Increases compassion, spreads positivity'
        },
        
        'neutral': {
            'title': 'Mindful Breathing',
            'description': 'Simple awareness practice to center yourself',
            'instructions': [
                'Sit quietly and close your eyes',
                'Notice your natural breathing rhythm',
                'Don\'t try to change it, just observe',
                'When mind wanders, gently return to breath',
                'Notice the pause between inhale and exhale',
                'End by taking three deeper breaths'
            ],
            'duration': '7 minutes',
            'benefits': 'Increases mindfulness, promotes calm'
        }
    }
    
    return exercises.get(mood, exercises['neutral'])

def save_exercise_completion(firebase_service, exercise_data):
    """Save exercise completion to Firebase or session state"""
    user_id = get_user_id()
    
    if user_id and not is_demo_user():
        # Save to Firebase
        return firebase_service.save_exercise_completion(user_id, exercise_data)
    else:
        # Save to session state for demo users
        if 'exercise_completions' not in st.session_state:
            st.session_state.exercise_completions = []
        
        exercise_data['timestamp'] = datetime.now()
        st.session_state.exercise_completions.append(exercise_data)
        
        # Update stats
        if 'user_stats' not in st.session_state:
            st.session_state.user_stats = {'exercises_completed': 0}
        st.session_state.user_stats['exercises_completed'] += 1
        
        return True

def calculate_mood_streak():
    """Calculate current positive mood streak"""
    if 'mood_history' not in st.session_state or not st.session_state.mood_history:
        return 0
    
    streak = 0
    for mood_entry in reversed(st.session_state.mood_history):
        if mood_entry.get('mood') in ['positive', 'happy', 'excited']:
            streak += 1
        else:
            break
    
    return streak

def get_personalized_greeting():
    """Generate personalized greeting based on user data"""
    user = get_current_user()
    name = get_user_display_name()
    current_mood = st.session_state.get('current_mood', 'neutral')
    
    # Time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"
    
    # Mood-based addition
    mood_additions = {
        'positive': "I can sense your positive energy today!",
        'anxious': "I'm here to support you through whatever you're feeling.",
        'stressed': "Let's take things one step at a time today.",
        'negative': "I'm glad you're here. You're not alone.",
        'neutral': "I'm here to listen and support you."
    }
    
    mood_addition = mood_additions.get(current_mood, mood_additions['neutral'])
    
    if user and user.get('isDemo'):
        return f"{time_greeting}, {name}! {mood_addition} What's on your mind today? (Demo Mode)"
    else:
        return f"{time_greeting}, {name}! {mood_addition} What's on your mind today?"

def format_timestamp(timestamp):
    """Format timestamp for display"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def save_mood_entry(mood, description="", firebase_service=None):
    """Save mood entry to Firebase or session state"""
    user_id = get_user_id()
    
    if user_id and not is_demo_user() and firebase_service:
        # Save to Firebase
        return firebase_service.save_mood_entry(user_id, mood, description)
    else:
        # Save to session state for demo users
        if 'mood_history' not in st.session_state:
            st.session_state.mood_history = []
        
        mood_entry = {
            'mood': mood,
            'description': description,
            'timestamp': datetime.now(),
            'date': datetime.now().date().isoformat()
        }
        
        st.session_state.mood_history.append(mood_entry)
        
        # Keep only last 100 entries
        if len(st.session_state.mood_history) > 100:
            st.session_state.mood_history = st.session_state.mood_history[-100:]
        
        # Update stats
        if 'user_stats' not in st.session_state:
            st.session_state.user_stats = {'total_mood_entries': 0}
        st.session_state.user_stats['total_mood_entries'] += 1
        
        return True

def get_mood_analytics(firebase_service=None):
    """Calculate mood analytics from session data or Firebase"""
    user_id = get_user_id()
    
    if user_id and not is_demo_user() and firebase_service:
        # Get from Firebase
        return firebase_service.get_mood_analytics(user_id, days=30)
    else:
        # Calculate from session state
        if 'mood_history' not in st.session_state:
            return {'total_entries': 0, 'mood_distribution': {}}
        
        moods = st.session_state.mood_history
        
        if not moods:
            return {'total_entries': 0, 'mood_distribution': {}}
        
        # Calculate distribution
        mood_counts = {}
        for entry in moods:
            mood = entry.get('mood', 'neutral')
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Calculate recent trend (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_moods = [
            entry for entry in moods 
            if entry.get('timestamp', datetime.min) >= week_ago
        ]
        
        return {
            'total_entries': len(moods),
            'mood_distribution': mood_counts,
            'recent_moods': recent_moods[-7:],  # Last 7 entries
            'current_streak': calculate_mood_streak(),
            'mood_history': moods
        }

def is_crisis_situation(text):
    """Detect if text indicates a mental health crisis"""
    crisis_keywords = [
        'suicide', 'kill myself', 'end it all', 'not worth living',
        'hurt myself', 'self harm', 'want to die', 'better off dead'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in crisis_keywords)

def get_crisis_resources():
    """Return crisis support resources"""
    return {
        'crisis_text_line': 'Text HOME to 741741',
        'suicide_prevention': 'Call 988',
        'emergency': 'Call 911',
        'message': 'If you\'re having thoughts of self-harm, please reach out for immediate help. You matter, and support is available 24/7.'
    }

def export_user_data(firebase_service=None):
    """Export all user data for download"""
    user_id = get_user_id()
    
    if user_id and not is_demo_user() and firebase_service:
        # Export from Firebase
        return firebase_service.export_user_data(user_id)
    else:
        # Export from session state
        export_data = {
            'user': st.session_state.get('user', {}),
            'profile': st.session_state.get('user_profile', {}),
            'conversation_history': st.session_state.get('conversation_history', []),
            'mood_history': st.session_state.get('mood_history', []),
            'exercise_completions': st.session_state.get('exercise_completions', []),
            'user_stats': st.session_state.get('user_stats', {}),
            'export_timestamp': datetime.now().isoformat(),
            'app_version': '1.0.0',
            'data_source': 'demo_mode' if is_demo_user() else 'session_state'
        }
        
        return export_data

def delete_user_data(firebase_service=None):
    """Delete all user data (GDPR compliance)"""
    user_id = get_user_id()
    
    if user_id and not is_demo_user() and firebase_service:
        # Delete from Firebase
        return firebase_service.delete_user_data(user_id)
    else:
        # Clear session state
        keys_to_clear = [
            'conversation_history', 'mood_history', 'exercise_completions',
            'user_profile', 'user_stats', 'current_mood'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        return True

def validate_input(text, max_length=1000):
    """Validate user input"""
    if not text or not text.strip():
        return False, "Please enter a message"
    
    if len(text) > max_length:
        return False, f"Message too long. Please keep it under {max_length} characters."
    
    return True, ""

def get_conversation_context(history, limit=5):
    """Get recent conversation context for AI"""
    if not history:
        return ""
    
    recent_messages = history[-limit:]
    context_parts = []
    
    for msg in recent_messages:
        role = "User" if msg['role'] == 'user' else "Assistant"
        content = msg.get('content', '')
        context_parts.append(f"{role}: {content}")
    
    return "\n".join(context_parts)

def should_suggest_exercise(mood, recent_messages):
    """Determine if exercise should be suggested"""
    if mood in ['anxious', 'stressed', 'negative']:
        return True
    
    # Check recent conversation for stress indicators
    if recent_messages:
        recent_text = " ".join([msg.get('content', '') for msg in recent_messages[-3:]])
        stress_indicators = ['overwhelmed', 'can\'t cope', 'too much', 'exhausted']
        return any(indicator in recent_text.lower() for indicator in stress_indicators)
    
    return False

def sync_session_with_firebase(firebase_service):
    """Sync session state with Firebase data"""
    user_id = get_user_id()
    if not user_id or is_demo_user():
        return False
    
    try:
        # Load fresh data from Firebase
        load_user_data_from_firebase(firebase_service)
        return True
    except Exception as e:
        print(f"Error syncing with Firebase: {e}")
        return False

def get_user_timezone():
    """Get user's timezone (placeholder for future implementation)"""
    # For now, return default timezone
    # In future, this could be detected from browser or user settings
    return "UTC"

def format_user_stats():
    """Format user statistics for display"""
    stats = st.session_state.get('user_stats', {})
    
    return {
        'conversations': stats.get('total_conversations', 0),
        'mood_entries': stats.get('total_mood_entries', 0),
        'streak': stats.get('current_streak', 0),
        'exercises': stats.get('exercises_completed', 0)
    }

def update_user_activity():
    """Update user's last activity timestamp"""
    user_id = get_user_id()
    if user_id and not is_demo_user():
        # This would update last_activity in Firebase
        # Implementation depends on your Firebase service structure
        pass

def get_app_version():
    """Get current app version"""
    return "1.0.0"

def is_first_time_user():
    """Check if this is user's first time using the app"""
    user = get_current_user()
    if not user:
        return False
    
    # Check if user has any conversation history
    return len(st.session_state.get('conversation_history', [])) == 0

def show_welcome_message():
    """Show welcome message for new users"""
    if is_first_time_user():
        return f"""
        Welcome to MindMate, {get_user_display_name()}! 🌟
        
        I'm your AI mental health companion, and I'm here to:
        • Listen to your thoughts and feelings without judgment
        • Help you track your mood and emotional patterns
        • Suggest personalized wellness exercises
        • Remember our conversations to provide better support
        
        Your privacy and wellbeing are my top priorities. Let's start this journey together!
        """
    return None