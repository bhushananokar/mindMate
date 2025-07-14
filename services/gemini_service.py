import google.generativeai as genai
import os
import json
import re
from datetime import datetime, timedelta

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key and api_key != 'your_gemini_api_key_here':
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
        else:
            self.enabled = False
            print("Gemini API key not configured")
    
    def generate_response(self, user_message, conversation_history, current_mood):
        """Generate AI response with context"""
        if not self.enabled:
            return self._fallback_response(user_message, current_mood)
        
        try:
            # Build context from recent conversations
            context = ""
            if conversation_history:
                recent_messages = conversation_history[-5:]
                context = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                    for msg in recent_messages
                ])
            
            prompt = f"""
You are MindMate, a compassionate AI mental health companion. You provide emotional support, remember conversations, and offer practical guidance.

Current user mood: {current_mood}

Recent conversation context:
{context}

Current user message: "{user_message}"

Respond as MindMate with:
1. Empathetic, supportive response (conversational, under 150 words)
2. Reference previous conversations when relevant
3. Detect current mood: positive/neutral/negative/anxious/stressed/crisis
4. Extract any important events/dates mentioned
5. Suggest exercises if user seems stressed/anxious

Respond in JSON format:
{{
    "response": "Your caring response here",
    "mood_detected": "detected mood",
    "needs_exercise": true/false,
    "events": [
        {{
            "description": "event description",
            "date": "mentioned date/time",
            "type": "appointment/deadline/goal"
        }}
    ],
    "key_insights": ["important things to remember"]
}}
"""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean and parse JSON
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            try:
                result = json.loads(text)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, extract just the response
                return {
                    "response": text,
                    "mood_detected": current_mood,
                    "needs_exercise": current_mood in ['anxious', 'stressed', 'negative'],
                    "events": [],
                    "key_insights": []
                }
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_response(user_message, current_mood)
    
    def _fallback_response(self, user_message, current_mood):
        """Fallback response when API is unavailable"""
        responses = {
            'positive': "I'm glad to hear you're feeling good! It's wonderful when things are going well. What's been the highlight of your day?",
            'negative': "I can hear that you're going through a tough time. Your feelings are completely valid, and I'm here to support you. Would you like to talk about what's been weighing on you?",
            'anxious': "I understand you're feeling anxious right now. That can be really overwhelming. Have you tried any breathing exercises? Sometimes a few deep breaths can help calm the mind.",
            'stressed': "Stress can feel so overwhelming sometimes. You're not alone in feeling this way. What's been the biggest source of stress for you lately?",
            'neutral': "Thank you for sharing with me. I'm here to listen and support you in whatever way I can. How has your day been overall?"
        }
        
        return {
            "response": responses.get(current_mood, responses['neutral']),
            "mood_detected": current_mood,
            "needs_exercise": current_mood in ['anxious', 'stressed', 'negative'],
            "events": self._extract_basic_events(user_message),
            "key_insights": []
        }
    
    def _extract_basic_events(self, text):
        """Basic event extraction without API"""
        events = []
        
        # Look for time-related keywords
        time_patterns = [
            r'tomorrow',
            r'next week',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(appointment|meeting|interview|exam|deadline)',
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                events.append({
                    "description": f"Mentioned: {match}",
                    "date": match,
                    "type": "general"
                })
        
        return events[:3]  # Return max 3 events
    
    def generate_exercise_suggestions(self, mood, user_preferences=None):
        """Generate mood-based exercise suggestions"""
        if not self.enabled:
            return self._fallback_exercises(mood)
        
        try:
            prompt = f"""
Generate 4 specific mental health exercises for someone feeling {mood}.

User preferences: {user_preferences or 'None specified'}

Create exercises that are:
- Practical and actionable (5-15 minutes)
- Specifically helpful for {mood} mood
- Include breathing, mindfulness, physical, or cognitive techniques
- Progressively more advanced

Respond in JSON format:
{{
    "exercises": [
        {{
            "title": "Exercise name",
            "description": "Clear, step-by-step instructions",
            "duration": "X minutes", 
            "type": "breathing/mindfulness/physical/cognitive",
            "difficulty": "easy/medium/hard",
            "benefits": "How this helps with {mood}"
        }}
    ]
}}
"""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            result = json.loads(text)
            return result.get('exercises', self._fallback_exercises(mood))
            
        except Exception as e:
            print(f"Exercise generation error: {e}")
            return self._fallback_exercises(mood)
    
    def _fallback_exercises(self, mood):
        """Fallback exercises when API unavailable"""
        exercises = {
            'anxious': [
                {
                    "title": "4-7-8 Breathing",
                    "description": "Breathe in for 4 counts, hold for 7, exhale for 8. Repeat 4 times.",
                    "duration": "5 minutes",
                    "type": "breathing", 
                    "difficulty": "easy",
                    "benefits": "Activates relaxation response, reduces anxiety"
                },
                {
                    "title": "Progressive Muscle Relaxation",
                    "description": "Starting with your toes, tense each muscle group for 5 seconds, then release. Work up to your head.",
                    "duration": "10 minutes",
                    "type": "physical",
                    "difficulty": "easy", 
                    "benefits": "Releases physical tension, promotes calm"
                }
            ],
            'stressed': [
                {
                    "title": "Box Breathing",
                    "description": "Breathe in for 4, hold for 4, out for 4, hold for 4. Repeat 8 times.",
                    "duration": "6 minutes",
                    "type": "breathing",
                    "difficulty": "easy",
                    "benefits": "Reduces stress hormones, improves focus"
                },
                {
                    "title": "Mindful Walking",
                    "description": "Walk slowly, focusing on each step. Notice how your feet feel touching the ground.",
                    "duration": "10 minutes", 
                    "type": "mindfulness",
                    "difficulty": "easy",
                    "benefits": "Grounds you in present moment, reduces stress"
                }
            ],
            'negative': [
                {
                    "title": "Gratitude Practice",
                    "description": "Write down 3 things you're grateful for, no matter how small. Reflect on why each matters.",
                    "duration": "8 minutes",
                    "type": "cognitive", 
                    "difficulty": "easy",
                    "benefits": "Shifts focus to positive, improves mood"
                },
                {
                    "title": "Self-Compassion Meditation",
                    "description": "Place hand on heart. Say: 'This is a moment of suffering. Suffering is part of life. May I be kind to myself.'",
                    "duration": "10 minutes",
                    "type": "mindfulness",
                    "difficulty": "medium",
                    "benefits": "Reduces self-criticism, increases emotional resilience"
                }
            ]
        }
        
        return exercises.get(mood, exercises['anxious'])