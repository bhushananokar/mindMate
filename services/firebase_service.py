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
    
    def create_user_profile(self, user_data):
        """Create or update user profile in Firestore"""
        if not self.enabled:
            return False
            
        try:
            user_ref = self.db.collection('users').document(user_data['uid'])
            
            # Check if user already exists
            user_doc = user_ref.get()
            
            if user_doc.exists:
                # Update last login
                user_ref.update({
                    'last_login': datetime.now(),
                    'display_name': user_data.get('displayName', ''),
                    'photo_url': user_data.get('photoURL', '')
                })
            else:
                # Create new user profile
                profile_data = {
                    'uid': user_data['uid'],
                    'email': user_data.get('email', ''),
                    'display_name': user_data.get('displayName', ''),
                    'photo_url': user_data.get('photoURL', ''),
                    'created_at': datetime.now(),
                    'last_login': datetime.now(),
                    'is_demo': user_data.get('isDemo', False),
                    'preferences': {
                        'name': user_data.get('displayName', 'Friend'),
                        'age_range': '',
                        'goals': [],
                        'exercise_preferences': [],
                        'notifications': True,
                        'privacy_level': 'Medium'
                    },
                    'stats': {
                        'total_conversations': 0,
                        'total_mood_entries': 0,
                        'current_streak': 0,
                        'exercises_completed': 0
                    }
                }
                
                user_ref.set(profile_data)
            
            return True
            
        except Exception as e:
            print(f"Error creating user profile: {e}")
            return False
    
    def get_user_profile(self, user_id):
        """Get user profile from Firestore"""
        if not self.enabled:
            return None
            
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
            
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None
    
    def update_user_preferences(self, user_id, preferences):
        """Update user preferences"""
        if not self.enabled:
            return False
            
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'preferences': preferences,
                'updated_at': datetime.now()
            })
            return True
            
        except Exception as e:
            print(f"Error updating preferences: {e}")
            return False
    
    def save_conversation(self, user_id, user_message, ai_response):
        """Save conversation to user's subcollection"""
        if not self.enabled:
            return False
            
        try:
            conversation_data = {
                'user_message': user_message,
                'ai_response': ai_response.get('response', ''),
                'mood_detected': ai_response.get('mood_detected', 'neutral'),
                'events': ai_response.get('events', []),
                'timestamp': datetime.now(),
                'session_id': datetime.now().strftime('%Y%m%d')
            }
            
            # Save to user's conversations subcollection
            self.db.collection('users').document(user_id).collection('conversations').add(conversation_data)
            
            # Update user stats
            self._update_user_stats(user_id, 'conversations')
            
            return True
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def get_user_conversations(self, user_id, limit=50):
        """Get user's conversation history"""
        if not self.enabled:
            return []
            
        try:
            conversations_ref = self.db.collection('users').document(user_id).collection('conversations')
            query = conversations_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
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
        """Save mood entry to user's subcollection"""
        if not self.enabled:
            return False
            
        try:
            mood_data = {
                'mood': mood,
                'description': description,
                'timestamp': datetime.now(),
                'date': datetime.now().date().isoformat()
            }
            
            # Save to user's mood_entries subcollection
            self.db.collection('users').document(user_id).collection('mood_entries').add(mood_data)
            
            # Update user stats
            self._update_user_stats(user_id, 'mood_entries')
            
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
            
            mood_ref = self.db.collection('users').document(user_id).collection('mood_entries')
            query = mood_ref.where('timestamp', '>=', start_date).order_by('timestamp')
            
            moods = []
            for doc in query.get():
                mood_data = doc.to_dict()
                mood_data['id'] = doc.id
                moods.append(mood_data)
            
            # Calculate analytics
            mood_counts = {}
            for mood in moods:
                mood_type = mood.get('mood', 'neutral')
                mood_counts[mood_type] = mood_counts.get(mood_type, 0) + 1
            
            return {
                'total_entries': len(moods),
                'mood_distribution': mood_counts,
                'recent_moods': moods[-7:] if len(moods) >= 7 else moods,
                'mood_history': moods
            }
            
        except Exception as e:
            print(f"Error fetching analytics: {e}")
            return {}
    
    def save_exercise_completion(self, user_id, exercise_data):
        """Save completed exercise"""
        if not self.enabled:
            return False
            
        try:
            exercise_data['timestamp'] = datetime.now()
            exercise_data['date'] = datetime.now().date().isoformat()
            
            # Save to user's exercises subcollection
            self.db.collection('users').document(user_id).collection('exercises').add(exercise_data)
            
            # Update user stats
            self._update_user_stats(user_id, 'exercises')
            
            return True
            
        except Exception as e:
            print(f"Error saving exercise: {e}")
            return False
    
    def get_user_exercises(self, user_id, limit=50):
        """Get user's exercise history"""
        if not self.enabled:
            return []
            
        try:
            exercises_ref = self.db.collection('users').document(user_id).collection('exercises')
            query = exercises_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            exercises = []
            for doc in query.get():
                exercise = doc.to_dict()
                exercise['id'] = doc.id
                exercises.append(exercise)
            
            return exercises
            
        except Exception as e:
            print(f"Error fetching exercises: {e}")
            return []
    
    def _update_user_stats(self, user_id, stat_type):
        """Update user statistics"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            
            if stat_type == 'conversations':
                user_ref.update({
                    'stats.total_conversations': firestore.Increment(1),
                    'last_activity': datetime.now()
                })
            elif stat_type == 'mood_entries':
                user_ref.update({
                    'stats.total_mood_entries': firestore.Increment(1),
                    'last_activity': datetime.now()
                })
            elif stat_type == 'exercises':
                user_ref.update({
                    'stats.exercises_completed': firestore.Increment(1),
                    'last_activity': datetime.now()
                })
                
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def delete_user_data(self, user_id):
        """Delete all user data (GDPR compliance)"""
        if not self.enabled:
            return False
            
        try:
            # Delete subcollections first
            subcollections = ['conversations', 'mood_entries', 'exercises']
            
            for subcoll in subcollections:
                docs = self.db.collection('users').document(user_id).collection(subcoll).get()
                for doc in docs:
                    doc.reference.delete()
            
            # Delete user document
            self.db.collection('users').document(user_id).delete()
            
            return True
            
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    def export_user_data(self, user_id):
        """Export all user data"""
        if not self.enabled:
            return {}
            
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'user_profile': {},
                'conversations': [],
                'mood_entries': [],
                'exercises': []
            }
            
            # Get user profile
            user_profile = self.get_user_profile(user_id)
            if user_profile:
                export_data['user_profile'] = user_profile
            
            # Get conversations
            conversations = self.get_user_conversations(user_id, limit=1000)
            export_data['conversations'] = conversations
            
            # Get mood entries
            mood_analytics = self.get_mood_analytics(user_id, days=365)
            export_data['mood_entries'] = mood_analytics.get('mood_history', [])
            
            # Get exercises
            exercises = self.get_user_exercises(user_id, limit=1000)
            export_data['exercises'] = exercises
            
            return export_data
            
        except Exception as e:
            print(f"Error exporting user data: {e}")
            return {}