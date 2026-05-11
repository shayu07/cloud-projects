"""
AI Chatbot Engine — Generative AI Upgrade
Uses Google's Gemini API instead of local NLP patterns.
"""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.chat_sessions = {}
        
        if self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("[ChatBot] Gemini API connected successfully using google-genai!")
            except Exception as e:
                print(f"[ChatBot] Error connecting to Gemini: {e}")
                self.client = None
        else:
            print("[ChatBot] WARNING: GEMINI_API_KEY not found in .env file.")
            self.client = None

    def get_response_stream(self, text, session_id="default"):
        """Get streaming response from Gemini API."""
        if not self.client:
            yield "⚠️ **Gemini API Key Missing!**\n\nPlease open the `.env` file, paste your API key as `GEMINI_API_KEY=your_key_here`, and restart the server."
            return

        try:
            if session_id not in self.chat_sessions:
                self.chat_sessions[session_id] = self.client.chats.create(
                    model='gemini-2.5-flash',
                    config={"tools": [{"google_search": {}}]}
                )
                
            chat = self.chat_sessions[session_id]
            response = chat.send_message_stream(text)
            
            for chunk in response:
                yield chunk.text
        except Exception as e:
            yield f"Sorry, I encountered an error with the AI service: {str(e)}"

    def get_suggestions(self):
        """Get suggested questions for the user."""
        return [
            "Write a poem about coding",
            "Explain quantum computing to a 5 year old",
            "Help me write a Python script",
            "Give me a 7-day workout plan",
            "Write a cold email template",
            "Translate 'Hello world' to French"
        ]
