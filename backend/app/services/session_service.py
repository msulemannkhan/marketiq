"""
Session Service for managing chat conversation history and context
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import uuid

# Simple in-memory storage (in production, use Redis or database)
class SessionManager:
    def __init__(self):
        self.sessions = {}  # session_id -> session_data
        self.max_messages_per_session = 50
        self.session_timeout_hours = 24

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get existing session or create new one"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "messages": [],
                "user_preferences": {},
                "context_summary": ""
            }

        # Update last activity
        self.sessions[session_id]["last_activity"] = datetime.utcnow()
        return session_id

    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to session history"""
        if session_id not in self.sessions:
            session_id = self.get_or_create_session(session_id)

        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        self.sessions[session_id]["messages"].append(message)

        # Keep only last N messages to prevent memory bloat
        if len(self.sessions[session_id]["messages"]) > self.max_messages_per_session:
            self.sessions[session_id]["messages"] = self.sessions[session_id]["messages"][-self.max_messages_per_session:]

    def get_recent_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get recent messages from session"""
        if session_id not in self.sessions:
            return []

        messages = self.sessions[session_id]["messages"]
        return messages[-limit:] if messages else []

    def get_conversation_history(self, session_id: str, limit: int = 30) -> List[Dict]:
        """Get conversation history for context (20-30 messages)"""
        if session_id not in self.sessions:
            return []

        messages = self.sessions[session_id]["messages"]
        # Return last 'limit' messages (default 30)
        recent_messages = messages[-limit:] if len(messages) > limit else messages

        # Format for LLM context
        formatted_history = []
        for msg in recent_messages:
            formatted_history.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg.get("timestamp"),
                "metadata": msg.get("metadata", {})
            })

        return formatted_history

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get full session context"""
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "recent_messages": self.get_recent_messages(session_id, 20),
            "conversation_history": self.get_conversation_history(session_id, 30),
            "user_preferences": session.get("user_preferences", {}),
            "context_summary": session.get("context_summary", ""),
            "session_duration": (datetime.utcnow() - session["created_at"]).total_seconds(),
            "total_messages": len(session["messages"]),
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat()
        }

    def update_user_preferences(self, session_id: str, preferences: Dict):
        """Update user preferences in session"""
        if session_id not in self.sessions:
            session_id = self.get_or_create_session(session_id)

        current_prefs = self.sessions[session_id].get("user_preferences", {})
        current_prefs.update(preferences)
        self.sessions[session_id]["user_preferences"] = current_prefs

    def update_context_summary(self, session_id: str, summary: str):
        """Update context summary for session"""
        if session_id not in self.sessions:
            return

        self.sessions[session_id]["context_summary"] = summary

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if session["last_activity"] < cutoff_time
        ]

        for sid in expired_sessions:
            del self.sessions[sid]

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]
        messages = session["messages"]

        user_messages = [m for m in messages if m["role"] == "user"]
        assistant_messages = [m for m in messages if m["role"] == "assistant"]

        return {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "session_duration_minutes": (datetime.utcnow() - session["created_at"]).total_seconds() / 60,
            "last_activity": session["last_activity"].isoformat()
        }

# Global session manager instance
session_manager = SessionManager()