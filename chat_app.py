from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from groq import Groq
import os
import uuid

app = FastAPI(title="Safeguard Chat API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your Groq API key
groq_api_key = "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"
client = Groq(api_key=groq_api_key)

# Initialize session storage (in a real app, you'd use a database)
chat_sessions: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    reply: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API status"""
    try:
        # Simple connection test to Groq API
        # Using a minimal request to check connectivity
        client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        return {"status": "ok", "message": "Service is operational"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    message = request.message
    session_id = request.session_id
    
    # Initialize session if it doesn't exist
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "system", "content": (
            '''You are SAHELI AI, a multilingual, friendly, and empathetic chatbot created to support women experiencing workplace harassment in India. Your mission is to:

Listen with compassion, creating a safe and non-judgmental environment for users to share their concerns.

Communicate in the user’s preferred language, including English, Hindi, Telugu, Tamil, Kannada, Bengali, or Marathi.

Provide realistic, practical, and legally accurate advice based on Indian laws, especially the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013.

Guide users through their options, such as filing a complaint with their Internal Complaints Committee (ICC), contacting legal authorities, or seeking help from verified NGOs and women’s helplines.

Maintain a polite, understanding, and respectful tone at all times. Your responses must feel human, supportive, and empowering—not robotic or generic.

In every conversation:

Begin by introducing yourself as SAHELI AI and asking for the user’s preferred language.

Offer legal guidance in simple, understandable terms.

Reassure users that their privacy and dignity are your priority.

Never pressure users—only inform and support.

Your ultimate goal is to make the user feel heard, safe, and empowered to take the right steps based on their comfort level and the law.

Give Helplines for India and Emergency as 

Be Concise and only reply with what is asked

''')}
        ]
    
    # Add user message to session history
    chat_sessions[session_id].append({"role": "user", "content": message})
    
    try:
        # Call Groq API with the conversation history
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_sessions[session_id],
            temperature=1.0,  # Lower temperature for more focused responses
            max_tokens=1000     # Keep responses concise
        )
        
        # Extract assistant response
        assistant_reply = response.choices[0].message.content.strip()
        
        # Add assistant response to session history
        chat_sessions[session_id].append({"role": "assistant", "content": assistant_reply})
        
        return ChatResponse(reply=assistant_reply)
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        
        # Provide a friendly error message to the user
        fallback_response = "I'm having trouble connecting right now. Please try again in a moment."
        return ChatResponse(reply=fallback_response, error=error_message)

# Cleanup old sessions (would be handled by a scheduled task in production)
@app.get("/api/admin/cleanup")
def cleanup_old_sessions():
    """Admin endpoint to clean up old sessions (would require auth in production)"""
    session_count = len(chat_sessions)
    chat_sessions.clear()
    return {"message": f"Cleared {session_count} sessions"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("chat_app:app", host="127.0.0.1", port=5100, reload=True)