# 🧠 MindMate - A Streamlit AI Wellness Assistant

**MindMate** is a mental wellness assistant built with **Streamlit** and powered by **Google's Gemini AI**. It provides a safe and interactive space for users to engage in supportive conversations, access mental exercises, and track their emotional well-being. User authentication is handled securely through **Google Firebase**.

---

## 📋 Features

- 💬 **Conversational Chat**: Engage with the Gemini-powered AI for support and conversation.  
- 🧘 **Guided Exercises**: Access a collection of mental wellness exercises.  
- 📊 **Analytics**: Track your mood and progress over time *(feature in development)*.  
- 👤 **User Profile**: Secure user authentication and profile management via Firebase.

---

## 📂 Project Structure

```
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
```

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.8+
- Pip
- A Google account with access to the Gemini API
- A Google Firebase project with Authentication service enabled

---

## 🛠 Installation & Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/bhushananokar/mindMate.git
cd mindMate
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set Up Environment Variables

Create a `.env` file in the root directory and add the following (replace placeholders with your actual credentials):

```env
# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Firebase Configuration
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_PRIVATE_KEY_PATH=/absolute/path/to/your/firebase-private-key.json

# Flask Configuration (if needed)
FLASK_SECRET_KEY=your_super_secret_key_here_change_this_in_production
FLASK_ENV=development

# App Configuration
APP_NAME=MindMate
APP_VERSION=1.0.0
DEBUG=True
```

> 🔐 **Note**:
> - `GEMINI_API_KEY`: Get from [Google AI Studio](https://makersuite.google.com/).
> - `FIREBASE_PRIVATE_KEY_PATH`: In Firebase console → Project Settings → Service accounts → Generate private key.

---

## ⚙️ Usage

Run the Streamlit app from the root folder:

```bash
streamlit run app.py
```

The application will open in your default browser.

---

## 📌 License

This project is for educational and wellness use. Please check licensing terms before commercial use.

---

## 🤝 Contributions

Pull requests are welcome! Feel free to open issues or suggest features.

---

## 🙌 Acknowledgements

- [Streamlit](https://streamlit.io)
- [Google Firebase](https://firebase.google.com)
- [Gemini AI](https://ai.google.dev)
