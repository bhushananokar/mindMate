import streamlit as st
import time
from datetime import datetime
import sys
import os

# Add the parent directory to the path to import helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Exercises - MindMate", page_icon="🧘", layout="wide")

# Check authentication
if not get_current_user():
    st.error("Please log in to access exercises.")
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

st.title("🧘 Wellness Exercises")
user_name = get_user_display_name()
st.write(f"Personalized mental health exercises for you, {user_name}")

# Show demo mode indicator
if is_demo_user():
    st.info("🔄 **Demo Mode**: Exercise completions will be saved to your session only.")

# Mood selector
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.subheader("How are you feeling?")
    selected_mood = st.selectbox(
        "Choose your current mood:",
        ["😊 Happy", "😐 Neutral", "😰 Anxious", "😤 Stressed", "😔 Down"],
        index=1
    )

# Map mood to internal values
mood_map = {
    "😊 Happy": "positive",
    "😐 Neutral": "neutral", 
    "😰 Anxious": "anxious",
    "😤 Stressed": "stressed",
    "😔 Down": "negative"
}

current_mood = mood_map[selected_mood]

# Update session mood
st.session_state.current_mood = current_mood

# Save mood entry
save_mood_entry(current_mood, f"Selected mood during exercises: {selected_mood}", firebase_service)

# Exercise suggestions based on mood
def get_exercises(mood):
    exercises = {
        'anxious': [
            {
                "title": "4-7-8 Breathing",
                "description": "A powerful technique to calm anxiety. Breathe in for 4, hold for 7, exhale for 8.",
                "duration": "5 minutes",
                "type": "Breathing",
                "difficulty": "Easy",
                "benefits": "Activates relaxation response, reduces anxiety quickly",
                "instructions": [
                    "1. Sit comfortably with your back straight",
                    "2. Exhale completely through your mouth", 
                    "3. Close your mouth and inhale through nose for 4 counts",
                    "4. Hold your breath for 7 counts",
                    "5. Exhale through mouth for 8 counts",
                    "6. Repeat 3-4 times"
                ]
            },
            {
                "title": "Progressive Muscle Relaxation", 
                "description": "Release physical tension by systematically tensing and relaxing muscle groups.",
                "duration": "12 minutes",
                "type": "Physical",
                "difficulty": "Medium",
                "benefits": "Releases physical tension, promotes deep relaxation",
                "instructions": [
                    "1. Start with your toes - tense for 5 seconds, then relax",
                    "2. Move to your calves, thighs, buttocks",
                    "3. Tense your abdomen, then chest and shoulders", 
                    "4. Make fists, tense arms, then relax",
                    "5. Scrunch face muscles, then relax",
                    "6. Notice the difference between tension and relaxation"
                ]
            },
            {
                "title": "5-4-3-2-1 Grounding",
                "description": "Use your senses to ground yourself in the present moment.",
                "duration": "5 minutes",
                "type": "Mindfulness",
                "difficulty": "Easy",
                "benefits": "Interrupts anxiety spiral, brings focus to present",
                "instructions": [
                    "1. Name 5 things you can see around you",
                    "2. Name 4 things you can touch",
                    "3. Name 3 things you can hear",
                    "4. Name 2 things you can smell",
                    "5. Name 1 thing you can taste",
                    "6. Take three deep breaths"
                ]
            }
        ],
        'stressed': [
            {
                "title": "Box Breathing",
                "description": "A simple pattern used by Navy SEALs to reduce stress quickly.",
                "duration": "6 minutes", 
                "type": "Breathing",
                "difficulty": "Easy",
                "benefits": "Lowers stress hormones, improves focus",
                "instructions": [
                    "1. Sit with feet flat on floor",
                    "2. Breathe in for 4 counts",
                    "3. Hold for 4 counts", 
                    "4. Exhale for 4 counts",
                    "5. Hold empty for 4 counts",
                    "6. Repeat 8-10 cycles"
                ]
            },
            {
                "title": "Mindful Body Scan",
                "description": "Systematically focus on different body parts to release stress.",
                "duration": "10 minutes",
                "type": "Mindfulness", 
                "difficulty": "Medium",
                "benefits": "Reduces physical tension, promotes awareness",
                "instructions": [
                    "1. Lie down or sit comfortably",
                    "2. Close your eyes and breathe naturally",
                    "3. Start at the top of your head",
                    "4. Slowly move attention down your body",
                    "5. Notice any tension without judgment", 
                    "6. Breathe into tense areas"
                ]
            },
            {
                "title": "Stress Release Visualization",
                "description": "Imagine stress leaving your body like water flowing away.",
                "duration": "8 minutes",
                "type": "Visualization",
                "difficulty": "Medium",
                "benefits": "Activates relaxation response, reduces cortisol",
                "instructions": [
                    "1. Close your eyes and breathe deeply",
                    "2. Imagine stress as a dark color in your body",
                    "3. Visualize bright, healing light entering your head",
                    "4. See the light pushing the darkness down and out",
                    "5. Feel the stress flowing out through your feet",
                    "6. End surrounded by peaceful, healing light"
                ]
            }
        ],
        'negative': [
            {
                "title": "Gratitude Practice",
                "description": "Shift your perspective by focusing on positive aspects of your life.",
                "duration": "8 minutes",
                "type": "Cognitive",
                "difficulty": "Easy",
                "benefits": "Improves mood, shifts focus to positive",
                "instructions": [
                    "1. Get a pen and paper or open notes app",
                    "2. Write down 3 things you're grateful for today",
                    "3. For each item, write WHY you're grateful",
                    "4. Think of someone who helped make this possible",
                    "5. Consider how your life would be different without it",
                    "6. Take a moment to really feel the gratitude"
                ]
            },
            {
                "title": "Self-Compassion Break",
                "description": "Treat yourself with the same kindness you'd show a good friend.",
                "duration": "10 minutes",
                "type": "Mindfulness",
                "difficulty": "Medium",
                "benefits": "Reduces self-criticism, increases emotional resilience",
                "instructions": [
                    "1. Place your hand on your heart",
                    "2. Acknowledge: 'This is a moment of suffering'",
                    "3. Remember: 'Suffering is part of the human experience'",
                    "4. Say to yourself: 'May I be kind to myself'",
                    "5. 'May I give myself the compassion I need'",
                    "6. Sit with this feeling of self-kindness"
                ]
            },
            {
                "title": "Positive Affirmations",
                "description": "Replace negative self-talk with supportive, encouraging statements.",
                "duration": "6 minutes",
                "type": "Cognitive",
                "difficulty": "Easy",
                "benefits": "Counters negative thinking, builds self-esteem",
                "instructions": [
                    "1. Look in a mirror or close your eyes",
                    "2. Say: 'I am worthy of love and respect'",
                    "3. 'I am doing the best I can with what I have'",
                    "4. 'This difficult time will pass'",
                    "5. 'I have overcome challenges before'",
                    "6. Repeat each affirmation 3 times with conviction"
                ]
            }
        ],
        'positive': [
            {
                "title": "Loving-Kindness Meditation",
                "description": "Spread your positive energy to yourself and others.",
                "duration": "12 minutes",
                "type": "Mindfulness",
                "difficulty": "Medium",
                "benefits": "Increases compassion, spreads positivity",
                "instructions": [
                    "1. Sit comfortably and close your eyes",
                    "2. Start by sending love to yourself: 'May I be happy'",
                    "3. Extend to loved ones: 'May you be happy'",
                    "4. Include neutral people in your life",
                    "5. Even include difficult people",
                    "6. End with all beings: 'May all beings be happy'"
                ]
            },
            {
                "title": "Energy Boost Visualization",
                "description": "Channel your positive mood into motivation and goal setting.",
                "duration": "8 minutes", 
                "type": "Visualization",
                "difficulty": "Easy",
                "benefits": "Builds motivation, clarifies goals",
                "instructions": [
                    "1. Think of a goal you want to achieve",
                    "2. Visualize yourself successfully completing it",
                    "3. Imagine how proud and happy you'll feel",
                    "4. What steps can you take today toward this goal?",
                    "5. Feel the energy and motivation building",
                    "6. Commit to one small action today"
                ]
            },
            {
                "title": "Gratitude & Joy Amplification",
                "description": "Deepen your positive feelings and share them with the world.",
                "duration": "10 minutes",
                "type": "Cognitive",
                "difficulty": "Easy",
                "benefits": "Amplifies positive emotions, increases life satisfaction",
                "instructions": [
                    "1. Think of what's making you happy right now",
                    "2. Focus on the physical sensations of joy",
                    "3. Imagine this happiness growing brighter",
                    "4. Picture sharing this joy with someone you love",
                    "5. Send this positive energy out to the world",
                    "6. Make a plan to spread more joy today"
                ]
            }
        ],
        'neutral': [
            {
                "title": "Mindful Breathing",
                "description": "Simple awareness practice to center yourself.",
                "duration": "7 minutes",
                "type": "Mindfulness",
                "difficulty": "Easy",
                "benefits": "Increases mindfulness, promotes calm",
                "instructions": [
                    "1. Sit quietly and close your eyes",
                    "2. Notice your natural breathing rhythm",
                    "3. Don't try to change it, just observe",
                    "4. When mind wanders, gently return to breath",
                    "5. Notice the pause between inhale and exhale",
                    "6. End by taking three deeper breaths"
                ]
            },
            {
                "title": "Gentle Stretching",
                "description": "Light movement to connect with your body.",
                "duration": "10 minutes",
                "type": "Physical",
                "difficulty": "Easy",
                "benefits": "Improves circulation, relieves tension",
                "instructions": [
                    "1. Stand and reach arms overhead",
                    "2. Gently twist side to side",
                    "3. Roll your shoulders backward 5 times",
                    "4. Tilt head side to side gently",
                    "5. Touch toes or reach toward floor",
                    "6. End with arms overhead, deep breath"
                ]
            },
            {
                "title": "Intention Setting",
                "description": "Clarify what you want to focus on today.",
                "duration": "8 minutes",
                "type": "Cognitive",
                "difficulty": "Easy",
                "benefits": "Increases purpose, improves focus",
                "instructions": [
                    "1. Sit quietly and center yourself",
                    "2. Ask: 'What do I need most today?'",
                    "3. Listen to your inner wisdom",
                    "4. Set one clear intention for today",
                    "5. Visualize yourself living this intention",
                    "6. Write it down where you'll see it"
                ]
            }
        ]
    }
    
    return exercises.get(mood, exercises['neutral'])

# Display exercises
exercises = get_exercises(current_mood)
st.subheader(f"Recommended exercises for {selected_mood}:")

# Create tabs for different exercises
tab_titles = [f"{ex['title']}" for ex in exercises]
tabs = st.tabs(tab_titles)

for i, (tab, exercise) in enumerate(zip(tabs, exercises)):
    with tab:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {exercise['title']}")
            st.write(exercise['description'])
            
            # Exercise metadata
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            
            with col_meta1:
                difficulty_colors = {
                    "Easy": "#28a745",
                    "Medium": "#ffc107", 
                    "Hard": "#dc3545"
                }
                difficulty_color = difficulty_colors.get(exercise.get('difficulty', 'Easy'), "#28a745")
                st.markdown(f"**Difficulty:** <span style='color: {difficulty_color}'>●</span> {exercise.get('difficulty', 'Easy')}", unsafe_allow_html=True)
            
            with col_meta2:
                st.markdown(f"**Type:** {exercise['type']}")
            
            with col_meta3:
                st.markdown(f"**Duration:** {exercise['duration']}")
            
            st.markdown(f"**Benefits:** {exercise.get('benefits', 'Promotes wellbeing')}")
        
        with col2:
            # Timer and controls
            st.markdown("#### Exercise Timer")
            
            # Initialize timer state
            if f'timer_{i}' not in st.session_state:
                st.session_state[f'timer_{i}'] = 0
            
            if f'timer_active_{i}' not in st.session_state:
                st.session_state[f'timer_active_{i}'] = False
            
            if f'timer_paused_{i}' not in st.session_state:
                st.session_state[f'timer_paused_{i}'] = False
            
            # Timer display
            if st.session_state[f'timer_{i}'] > 0:
                minutes = st.session_state[f'timer_{i}'] // 60
                seconds = st.session_state[f'timer_{i}'] % 60
                st.markdown(f"### ⏰ {minutes:02d}:{seconds:02d}")
                
                # Progress bar
                duration_minutes = int(exercise['duration'].split()[0])
                total_seconds = duration_minutes * 60
                progress = 1 - (st.session_state[f'timer_{i}'] / total_seconds)
                st.progress(progress)
            else:
                st.markdown("### ⏰ Ready to start")
            
            # Control buttons
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if not st.session_state[f'timer_active_{i}']:
                    if st.button("▶️ Start", key=f"start_{i}", use_container_width=True):
                        if st.session_state[f'timer_{i}'] == 0:
                            duration_minutes = int(exercise['duration'].split()[0])
                            st.session_state[f'timer_{i}'] = duration_minutes * 60
                        st.session_state[f'timer_active_{i}'] = True
                        st.session_state[f'timer_paused_{i}'] = False
                        st.rerun()
                else:
                    if st.button("⏸️ Pause", key=f"pause_{i}", use_container_width=True):
                        st.session_state[f'timer_active_{i}'] = False
                        st.session_state[f'timer_paused_{i}'] = True
            
            with col_btn2:
                if st.button("🔄 Reset", key=f"reset_{i}", use_container_width=True):
                    st.session_state[f'timer_{i}'] = 0
                    st.session_state[f'timer_active_{i}'] = False
                    st.session_state[f'timer_paused_{i}'] = False
        
        # Instructions
        st.markdown("#### Step-by-Step Instructions")
        
        with st.expander("📋 View Instructions", expanded=True):
            for instruction in exercise['instructions']:
                st.markdown(instruction)
        
        # Exercise completion
        if st.session_state[f'timer_{i}'] == 0 and st.session_state.get(f'timer_was_running_{i}', False):
            st.success("🎉 Congratulations! You've completed this exercise!")
            st.balloons()
            
            # Save exercise completion
            exercise_data = {
                'title': exercise['title'],
                'type': exercise['type'],
                'duration': exercise['duration'],
                'mood_before': current_mood,
                'completed_at': datetime.now()
            }
            
            save_exercise_completion(firebase_service, exercise_data)
            
            # Reset the completion flag
            st.session_state[f'timer_was_running_{i}'] = False
            
            # Mood check after exercise
            st.markdown("#### How do you feel now?")
            post_exercise_mood = st.selectbox(
                "Rate your mood after the exercise:",
                ["😊 Much Better", "🙂 Better", "😐 Same", "🙁 Worse"],
                key=f"post_mood_{i}"
            )
            
            if st.button("Submit Feedback", key=f"feedback_{i}"):
                st.success("Thank you for your feedback! This helps us recommend better exercises.")
        
        elif st.button("✅ Mark as Complete", key=f"complete_{i}", use_container_width=True):
            st.success("🎉 Great job completing this exercise!")
            
            # Save exercise completion
            exercise_data = {
                'title': exercise['title'],
                'type': exercise['type'],
                'duration': exercise['duration'],
                'mood_before': current_mood,
                'completed_manually': True,
                'completed_at': datetime.now()
            }
            
            save_exercise_completion(firebase_service, exercise_data)
            st.balloons()

# Auto-countdown for active timers
for i in range(len(exercises)):
    if st.session_state.get(f'timer_active_{i}', False) and st.session_state.get(f'timer_{i}', 0) > 0:
        time.sleep(1)
        st.session_state[f'timer_{i}'] -= 1
        
        if st.session_state[f'timer_{i}'] <= 0:
            st.session_state[f'timer_active_{i}'] = False
            st.session_state[f'timer_was_running_{i}'] = True
        
        st.rerun()

# Exercise completion tracking
if 'exercise_completions' not in st.session_state:
    st.session_state.exercise_completions = []

# Daily exercise suggestions
st.markdown("---")
st.subheader("💡 Daily Wellness Tips")

tips = {
    'anxious': "When feeling anxious, remember: this feeling is temporary. Focus on what you can control right now. Your breathing is always with you as an anchor.",
    'stressed': "Stress is your body's way of preparing for challenges. Take breaks, prioritize tasks, and remember that you don't have to handle everything at once.",
    'negative': "It's okay to feel down sometimes. Be gentle with yourself and remember that asking for help is a sign of strength, not weakness.",
    'positive': "Great mood! This is a perfect time to tackle challenging tasks, connect with others, or work on personal goals. Use this energy wisely!",
    'neutral': "A calm state is perfect for reflection and planning. What would make today meaningful? Sometimes the best insights come in quiet moments."
}

st.info(f"💭 {tips.get(current_mood, tips['neutral'])}")

# Personalized recommendations based on user profile
if st.session_state.get('user_profile'):
    user_goals = st.session_state.user_profile.get('goals', [])
    user_preferences = st.session_state.user_profile.get('preferences', [])
    
    if user_goals or user_preferences:
        st.markdown("---")
        st.subheader("🎯 Personalized for You")
        
        recommendations = []
        
        if "Managing Anxiety" in user_goals and current_mood == 'anxious':
            recommendations.append("🎯 Based on your goal to manage anxiety, try the 4-7-8 breathing exercise first.")
        
        if "Stress Reduction" in user_goals and current_mood == 'stressed':
            recommendations.append("🎯 Since stress reduction is one of your goals, the Box Breathing exercise might be perfect right now.")
        
        if "Mindfulness Practice" in user_goals:
            recommendations.append("🧘 You've set mindfulness as a goal - any of these exercises will help build that skill!")
        
        if "Breathing Exercises" in user_preferences:
            recommendations.append("💨 I notice you prefer breathing exercises - great choice! They're scientifically proven to work quickly.")
        
        for rec in recommendations:
            st.success(rec)

# Quick breathing exercise
st.markdown("---")
st.subheader("🫁 Quick 1-Minute Breathing Reset")
st.write("No time for a full exercise? Try this quick reset!")

if st.button("Start 1-Minute Breathing Reset", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 1-minute breathing exercise (6 cycles of 10 seconds each)
    for cycle in range(6):
        for second in range(10):
            total_second = cycle * 10 + second
            
            if second < 4:
                status_text.markdown(f"### 🫁 Breathe in... {second + 1}/4")
            elif second < 6:
                status_text.markdown(f"### ⏸️ Hold... {second - 3}/2")
            else:
                status_text.markdown(f"### 💨 Breathe out... {second - 5}/4")
                
            progress_bar.progress((total_second + 1) / 60)
            time.sleep(1)
    
    status_text.markdown("### 🎉 Complete! Take a moment to notice how you feel.")
    st.success("Great job! Even one minute of mindful breathing can make a difference.")
    
    # Save quick exercise completion
    quick_exercise_data = {
        'title': '1-Minute Breathing Reset',
        'type': 'Breathing',
        'duration': '1 minute',
        'mood_before': current_mood,
        'completed_at': datetime.now()
    }
    save_exercise_completion(firebase_service, quick_exercise_data)

# User stats and progress
st.markdown("---")
st.subheader("📈 Your Exercise Progress")

col1, col2, col3 = st.columns(3)

user_stats = format_user_stats()

with col1:
    st.metric("Exercises Completed", user_stats['exercises'])

with col2:
    # Calculate exercises this week
    exercises_this_week = len([
        ex for ex in st.session_state.get('exercise_completions', [])
        if ex.get('completed_at', datetime.min) >= datetime.now() - timedelta(days=7)
    ])
    st.metric("This Week", exercises_this_week)

with col3:
    # Most common exercise type
    if st.session_state.get('exercise_completions'):
        types = [ex.get('type', 'Unknown') for ex in st.session_state.exercise_completions]
        most_common = max(set(types), key=types.count) if types else 'None'
        st.metric("Favorite Type", most_common)
    else:
        st.metric("Favorite Type", "None yet")

# Footer navigation
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💬 Back to Chat", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/3_📊_Analytics.py")

with col3:
    if st.button("👤 Profile Settings", use_container_width=True):
        st.switch_page("pages/4_👤_Profile.py")