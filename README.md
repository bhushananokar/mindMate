

## 🧠 MindMate - A Streamlit AI Wellness Assistant

MindMate is a mental wellness assistant built with Streamlit and powered by Google's Gemini AI. It provides a safe and interactive space for users to engage in supportive conversations, access mental exercises, and track their emotional well-being. User authentication is handled securely through Google Firebase.

## 📋 Features

💬 Conversational Chat: Engage with the Gemini-powered AI for support and conversation.

🧘 Guided Exercises: Access a collection of mental wellness exercises.

📊 Analytics: Track your mood and progress over time (feature in development).

👤 User Profile: Secure user authentication and profile management via Firebase (Feature in development)

## 📂 Project Structure
Generated code
mindmate-streamlit/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
├── services/
│   ├── __init__.py
│   ├── firebase_service.py
│   ├── gemini_service.py
│   └── auth_service.py
├── pages/
│   ├── 1_💬_Chat.py
│   ├── 2_🧘_Exercises.py
│   ├── 3_📊_Analytics.py
│   └── 4_👤_Profile.py
└── utils/
    ├── __init__.py
    └── helpers.py

##🚀 Getting Started

Follow these instructions to get a local copy up and running.

## Prerequisites

Python 3.8+ and Pip

A Google account with access to the Gemini API.

A Google Firebase project with the Authentication service enabled.

Installation & Configuration

Clone the repository

Generated sh
git clone https://github.com/your-username/mindmate-streamlit.git
cd mindmate-streamlit
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Sh
IGNORE_WHEN_COPYING_END

Create a virtual environment (Recommended)

Generated sh
# For Windows
python -m venv venv
.\venv\Scripts\Activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Sh
IGNORE_WHEN_COPYING_END

Install dependencies

Generated sh
pip install -r requirements.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Sh
IGNORE_WHEN_COPYING_END

Set up Environment Variables
Create a file named .env in the root directory of the project and add the following configuration.

Important: You must replace the placeholder values with your actual credentials.

Generated dotenv
# Gemini AI API Key
GEMINI_API_KEY=AIzaSyB4YsVZrGEFdBZQzyLvMu0Oae4BlXedlks

# Firebase Configuration
# Find this in your Firebase project settings
FIREBASE_PROJECT_ID=project1-88048
# The full, absolute path to the service account key you downloaded from Firebase
FIREBASE_PRIVATE_KEY_PATH=C:\Users\Bhushan\Downloads\project1-88048-firebase-adminsdk-fbsvc-c906bb898f.json

# Flask Configuration (if needed)
FLASK_SECRET_KEY=your_super_secret_key_here_change_this_in_production
FLASK_ENV=development

# App Configuration
APP_NAME=MindMate
APP_VERSION=1.0.0
DEBUG=True
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Dotenv
IGNORE_WHEN_COPYING_END

GEMINI_API_KEY: Get this from Google AI Studio.

FIREBASE_PRIVATE_KEY_PATH: Go to your Firebase project -> Project Settings -> Service accounts -> Generate new private key. Make sure the path is correct for your system.

⚙️ Usage

Once the dependencies are installed and your .env file is configured, run the Streamlit application from the root directory:

Generated sh
streamlit run app.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Sh
IGNORE_WHEN_COPYING_END

The application will open in a new tab in your default web browser.
