import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="Exercises - MindMate", page_icon="🧘", layout="wide")

st.title("🧘 Wellness Exercises")
st.write("Personalized mental health exercises based on your current mood")

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

# Exercise suggestions based on mood
def get_exercises(mood):
    exercises = {
        'anxious': [
            {
                "title": "4-7-8 Breathing",
                "description": "A powerful technique to calm anxiety. Breathe in for 4, hold for 7, exhale for 8.",
                "duration": "5 minutes",
                "type": "Breathing",
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
                "instructions": [
                    "1. Start with your toes - tense for 5 seconds, then relax",
                    "2. Move to your calves, thighs, buttocks",
                    "3. Tense your abdomen, then chest and shoulders", 
                    "4. Make fists, tense arms, then relax",
                    "5. Scrunch face muscles, then relax",
                    "6. Notice the difference between tension and relaxation"
                ]
            }
        ],
        'stressed': [
            {
                "title": "Box Breathing",
                "description": "A simple pattern used by Navy SEALs to reduce stress quickly.",
                "duration": "6 minutes", 
                "type": "Breathing",
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
                "instructions": [
                    "1. Lie down or sit comfortably",
                    "2. Close your eyes and breathe naturally",
                    "3. Start at the top of your head",
                    "4. Slowly move attention down your body",
                    "5. Notice any tension without judgment", 
                    "6. Breathe into tense areas"
                ]
            }
        ],
        'negative': [
            {
                "title": "Gratitude Practice",
                "description": "Shift your perspective by focusing on positive aspects of your life.",
                "duration": "8 minutes",
                "type": "Cognitive",
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
                "instructions": [
                    "1. Place your hand on your heart",
                    "2. Acknowledge: 'This is a moment of suffering'",
                    "3. Remember: 'Suffering is part of the human experience'",
                    "4. Say to yourself: 'May I be kind to myself'",
                    "5. 'May I give myself the compassion I need'",
                    "6. Sit with this feeling of self-kindness"
                ]
            }
        ],
        'positive': [
            {
                "title": "Loving-Kindness Meditation",
                "description": "Spread your positive energy to yourself and others.",
                "duration": "12 minutes",
                "type": "Mindfulness",
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
                "type": "Cognitive",
                "instructions": [
                    "1. Think of a goal you want to achieve",
                    "2. Visualize yourself successfully completing it",
                    "3. Imagine how proud and happy you'll feel",
                    "4. What steps can you take today toward this goal?",
                    "5. Feel the energy and motivation building",
                    "6. Commit to one small action today"
                ]
            }
        ],
        'neutral': [
            {
                "title": "Mindful Breathing",
                "description": "Simple awareness practice to center yourself.",
                "duration": "7 minutes",
                "type": "Mindfulness",
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
                "instructions": [
                    "1. Stand and reach arms overhead",
                    "2. Gently twist side to side",
                    "3. Roll your shoulders backward 5 times",
                    "4. Tilt head side to side gently",
                    "5. Touch toes or reach toward floor",
                    "6. End with arms overhead, deep breath"
                ]
            }
        ]
    }
    
    return exercises.get(mood, exercises['neutral'])

# Display exercises
exercises = get_exercises(current_mood)
st.subheader(f"Recommended exercises for {selected_mood}:")

# Create columns for exercises
cols = st.columns(len(exercises))

for i, exercise in enumerate(exercises):
    with cols[i]:
        with st.container():
            st.markdown(f"""
            <div style="
                border: 1px solid #ddd; 
                border-radius: 10px; 
                padding: 1rem; 
                height: 400px;
                background: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
                <h4 style="color: #667eea;">{exercise['title']}</h4>
                <p style="color: #666; font-size: 0.9rem;"><strong>Type:</strong> {exercise['type']} | <strong>Duration:</strong> {exercise['duration']}</p>
                <p style="margin: 10px 0;">{exercise['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Exercise details button
            if st.button(f"Start {exercise['title']}", key=f"btn_{i}"):
                st.session_state[f'exercise_{i}'] = True
            
            # Show exercise details if button clicked
            if st.session_state.get(f'exercise_{i}', False):
                st.subheader(f"🧘 {exercise['title']}")
                st.write(exercise['description'])
                
                # Timer
                if f'timer_{i}' not in st.session_state:
                    st.session_state[f'timer_{i}'] = 0
                
                col_timer1, col_timer2, col_timer3 = st.columns(3)
                
                with col_timer1:
                    if st.button("⏯️ Start Timer", key=f"start_{i}"):
                        duration_minutes = int(exercise['duration'].split()[0])
                        st.session_state[f'timer_{i}'] = duration_minutes * 60
                        st.session_state[f'timer_active_{i}'] = True
                
                with col_timer2:
                    if st.button("⏸️ Pause", key=f"pause_{i}"):
                        st.session_state[f'timer_active_{i}'] = False
                
                with col_timer3:
                    if st.button("🔄 Reset", key=f"reset_{i}"):
                        st.session_state[f'timer_{i}'] = 0
                        st.session_state[f'timer_active_{i}'] = False
                
                # Display timer
                if st.session_state.get(f'timer_{i}', 0) > 0:
                    minutes = st.session_state[f'timer_{i}'] // 60
                    seconds = st.session_state[f'timer_{i}'] % 60
                    st.markdown(f"### ⏰ {minutes:02d}:{seconds:02d}")
                    
                    # Auto-countdown (simplified)
                    if st.session_state.get(f'timer_active_{i}', False):
                        time.sleep(1)
                        st.session_state[f'timer_{i}'] -= 1
                        if st.session_state[f'timer_{i}'] <= 0:
                            st.success("🎉 Exercise completed! Great job!")
                            st.session_state[f'timer_active_{i}'] = False
                        st.rerun()
                
                # Instructions
                st.subheader("Instructions:")
                for instruction in exercise['instructions']:
                    st.write(instruction)
                
                if st.button("✅ Complete Exercise", key=f"complete_{i}"):
                    st.success("🎉 Well done! You've completed this exercise.")
                    st.balloons()
                    st.session_state[f'exercise_{i}'] = False

# Exercise completion tracking
if 'completed_exercises' not in st.session_state:
    st.session_state.completed_exercises = []

# Daily exercise suggestions
st.markdown("---")
st.subheader("💡 Daily Wellness Tips")

tips = {
    'anxious': "When feeling anxious, remember: this feeling is temporary. Focus on what you can control right now.",
    'stressed': "Stress is your body's way of preparing for challenges. Take breaks and remember to breathe.",
    'negative': "It's okay to feel down sometimes. Be gentle with yourself and remember that you matter.",
    'positive': "Great mood! This is a perfect time to tackle challenging tasks or help others.",
    'neutral': "A calm state is perfect for reflection and planning. What would make today meaningful?"
}

st.info(f"💭 {tips.get(current_mood, tips['neutral'])}")

# Quick breathing exercise
st.markdown("---")
st.subheader("🫁 Quick 1-Minute Breathing Exercise")

if st.button("Start Quick Breathing Exercise", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 1-minute breathing exercise
    for i in range(60):
        cycle = i // 10
        phase = i % 10
        
        if phase < 4:
            status_text.text(f"Breathe in... {phase + 1}/4")
        elif phase < 6:
            status_text.text(f"Hold... {phase - 3}/2")
        else:
            status_text.text(f"Breathe out... {phase - 5}/4")
            
        progress_bar.progress((i + 1) / 60)
        time.sleep(1)
    
    status_text.text("🎉 Complete! How do you feel?")
    st.success("Great job! You've completed a 1-minute breathing exercise.")