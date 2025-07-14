import streamlit as st
import os
import json
from datetime import datetime
import streamlit.components.v1 as components

class AuthService:
    def __init__(self):
        self.firebase_config = {
            "apiKey": os.getenv('FIREBASE_API_KEY'),
            "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
            "databaseURL": os.getenv('FIREBASE_DATABASE_URL'),
            "projectId": os.getenv('FIREBASE_PROJECT_ID'),
            "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
            "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            "appId": os.getenv('FIREBASE_APP_ID')
        }
    
    def render_auth_component(self):
        """Render Firebase Auth component"""
        firebase_auth_component = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js"></script>
            <script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-auth-compat.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .auth-container {{
                    background: white;
                    padding: 2rem;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    text-align: center;
                    max-width: 400px;
                    width: 100%;
                }}
                .logo {{
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }}
                .title {{
                    font-size: 1.8rem;
                    color: #333;
                    margin-bottom: 0.5rem;
                }}
                .subtitle {{
                    color: #666;
                    margin-bottom: 2rem;
                }}
                .google-btn {{
                    background: #4285f4;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: background 0.3s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    width: 100%;
                    margin-bottom: 1rem;
                }}
                .google-btn:hover {{
                    background: #3367d6;
                }}
                .demo-btn {{
                    background: #6c757d;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 20px;
                    font-size: 0.9rem;
                    cursor: pointer;
                    width: 100%;
                }}
                .demo-btn:hover {{
                    background: #5a6268;
                }}
                .user-info {{
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 1rem 0;
                }}
                .sign-out-btn {{
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 15px;
                    cursor: pointer;
                    margin-top: 1rem;
                }}
                .sign-out-btn:hover {{
                    background: #c82333;
                }}
                .loading {{
                    color: #666;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="auth-container">
                <div class="logo">🧠</div>
                <h1 class="title">MindMate</h1>
                <p class="subtitle">Your AI Mental Health Companion</p>
                
                <div id="auth-section">
                    <div id="signed-out" style="display: none;">
                        <button id="google-signin" class="google-btn">
                            <svg width="20" height="20" viewBox="0 0 24 24">
                                <path fill="white" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                                <path fill="white" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                                <path fill="white" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                                <path fill="white" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                            </svg>
                            Continue with Google
                        </button>
                        <button id="demo-signin" class="demo-btn">
                            Continue as Guest
                        </button>
                    </div>
                    
                    <div id="signed-in" style="display: none;">
                        <div class="user-info">
                            <img id="user-photo" src="" alt="Profile" style="width: 60px; height: 60px; border-radius: 50%; margin-bottom: 10px;">
                            <div id="user-name"></div>
                            <div id="user-email" style="color: #666; font-size: 0.9rem;"></div>
                        </div>
                        <button id="continue-btn" class="google-btn">Continue to MindMate</button>
                        <button id="sign-out" class="sign-out-btn">Sign Out</button>
                    </div>
                    
                    <div id="loading" style="display: block;">
                        <p class="loading">Initializing...</p>
                    </div>
                </div>
            </div>

            <script>
                // Firebase configuration
                const firebaseConfig = {json.dumps(self.firebase_config)};

                // Initialize Firebase
                firebase.initializeApp(firebaseConfig);
                const auth = firebase.auth();

                // Google Auth Provider
                const googleProvider = new firebase.auth.GoogleAuthProvider();
                googleProvider.addScope('profile');
                googleProvider.addScope('email');

                // UI Elements
                const signedOutDiv = document.getElementById('signed-out');
                const signedInDiv = document.getElementById('signed-in');
                const loadingDiv = document.getElementById('loading');
                const googleSigninBtn = document.getElementById('google-signin');
                const demoSigninBtn = document.getElementById('demo-signin');
                const signOutBtn = document.getElementById('sign-out');
                const continueBtn = document.getElementById('continue-btn');

                // Auth state listener
                auth.onAuthStateChanged((user) => {{
                    loadingDiv.style.display = 'none';
                    
                    if (user) {{
                        // User is signed in
                        signedOutDiv.style.display = 'none';
                        signedInDiv.style.display = 'block';
                        
                        document.getElementById('user-photo').src = user.photoURL || '';
                        document.getElementById('user-name').textContent = user.displayName || 'User';
                        document.getElementById('user-email').textContent = user.email || '';
                        
                        // Send user data to Streamlit
                        const userData = {{
                            uid: user.uid,
                            email: user.email,
                            displayName: user.displayName,
                            photoURL: user.photoURL,
                            isDemo: false
                        }};
                        
                        window.parent.postMessage({{
                            type: 'auth_success',
                            user: userData
                        }}, '*');
                        
                    }} else {{
                        // User is signed out
                        signedOutDiv.style.display = 'block';
                        signedInDiv.style.display = 'none';
                    }}
                }});

                // Google Sign In
                googleSigninBtn.addEventListener('click', () => {{
                    auth.signInWithPopup(googleProvider)
                        .then((result) => {{
                            console.log('Google sign-in successful');
                        }})
                        .catch((error) => {{
                            console.error('Error during sign-in:', error);
                            alert('Sign-in failed. Please try again.');
                        }});
                }});

                // Demo Sign In
                demoSigninBtn.addEventListener('click', () => {{
                    const demoUser = {{
                        uid: 'demo_user_' + Date.now(),
                        email: 'demo@mindmate.app',
                        displayName: 'Demo User',
                        photoURL: '',
                        isDemo: true
                    }};
                    
                    window.parent.postMessage({{
                        type: 'auth_success',
                        user: demoUser
                    }}, '*');
                }});

                // Continue to app
                continueBtn.addEventListener('click', () => {{
                    window.parent.postMessage({{
                        type: 'continue_to_app'
                    }}, '*');
                }});

                // Sign Out
                signOutBtn.addEventListener('click', () => {{
                    auth.signOut().then(() => {{
                        window.parent.postMessage({{
                            type: 'auth_signout'
                        }}, '*');
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        # Render the component
        components.html(firebase_auth_component, height=600)
    
    def handle_auth_state(self):
        """Handle authentication state changes"""
        
        # Listen for messages from the auth component
        auth_script = """
        <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'auth_success') {
                    // Store user data in session storage for Streamlit
                    sessionStorage.setItem('mindmate_user', JSON.stringify(event.data.user));
                    // Trigger a rerun by setting a flag
                    sessionStorage.setItem('auth_changed', 'true');
                } else if (event.data.type === 'continue_to_app') {
                    sessionStorage.setItem('continue_to_app', 'true');
                } else if (event.data.type === 'auth_signout') {
                    sessionStorage.removeItem('mindmate_user');
                    sessionStorage.setItem('auth_changed', 'signout');
                }
            });
            
            // Check if auth state changed
            const authChanged = sessionStorage.getItem('auth_changed');
            if (authChanged) {
                sessionStorage.removeItem('auth_changed');
                window.parent.location.reload();
            }
        </script>
        """
        
        components.html(auth_script, height=0)
    
    def get_current_user(self):
        """Get current authenticated user"""
        # In a real implementation, you'd get this from session state
        # after the JavaScript component sets it
        return st.session_state.get('user', None)
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def sign_out(self):
        """Sign out current user"""
        if 'user' in st.session_state:
            del st.session_state.user
        st.rerun()