import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime
import json

class FirebaseService:
    def __init__(self):
        try:
            if not firebase_admin._apps:
                # Initialize Firebase
                cred_path = os.getenv('FIREBASE_PRIVATE_KEY_PATH', 'serviceAccountKey.json')
                
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use environment variables for deployment
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            self.enabled = True
            
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            self.enabled = False
    
    def save_conversation(self, user_id, user_message, ai_response):
        """Save conversation to Firestore"""
        if not self.enabled:
            return False
            
        try:
            conversation_data = {
                'user_id': user_id,
                'user_message': user_message,
                'ai_response': ai_response.get('response', ''),
                'mood_detected': ai_response.get('mood_detected', 'neutral'),
                'events': ai_response.get('events', []),
                'timestamp': datetime.now()
            }
            
            self.db.collection('conversations').add(conversation_data)
            return True
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_user_conversations(self, user_id, limit=50):
        """Get user's conversation history"""
        if not self.enabled:
            return []
            
        try:
            query = self.db.collection('conversations').where('user_id', '==', user_id)
            query = query.limit(limit)
            
            conversations = []
            for doc in query.get():
                conv = doc.to_dict()
                conv['id'] = doc.id
                conversations.append(conv)
            
            return conversations
            
        except Exception as e:
            print(f"Error fetching conversations: {e}")
            return []
    
    def save_mood_entry(self, user_id, mood, description=""):
        """Save mood entry"""
        if not self.enabled:
            return False
            
        try:
            mood_data = {
                'user_id': user_id,
                'mood': mood,
                'description': description,
                'timestamp': datetime.now(),
                'date': datetime.now().date().isoformat()
            }
            
            self.db.collection('mood_entries').add(mood_data)
            return True
            
        except Exception as e:
            print(f"Error saving mood: {e}")
            return False
    
    def get_mood_analytics(self, user_id, days=30):
        """Get mood analytics for user"""
        if not self.enabled:
            return {}
            
        try:
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            query = self.db.collection('mood_entries').where('user_id', '==', user_id)
            query = query.where('timestamp', '>=', start_date)
            
            moods = []
            for doc in query.get():
                moods.append(doc.to_dict())
            
            # Calculate analytics
            mood_counts = {}
            for mood in moods:
                mood_type = mood.get('mood', 'neutral')
                mood_counts[mood_type] = mood_counts.get(mood_type, 0) + 1
            
            return {
                'total_entries': len(moods),
                'mood_distribution': mood_counts,
                'recent_moods': moods[-7:] if len(moods) >= 7 else moods
            }
            
        except Exception as e:
            print(f"Error fetching analytics: {e}")
            return {}