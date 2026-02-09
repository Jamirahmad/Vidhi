"""
Session Memory for Vidhi Legal Research Platform

This module manages session state, conversation history, and context across multi-turn interactions.
It provides intelligent memory management for legal research workflows and document drafting sessions.

Features:
- Conversation history tracking
- Case context persistence
- Multi-turn dialogue support
- Context window management
- Session state persistence
- User preference storage
- Workflow progress tracking
- Citation and research caching
- Document draft versioning
- LangChain memory integration
- Token usage optimization
- Context retrieval and summarization

Author: Vidhi Development Team
License: MIT (Educational & Research Use Only)
"""

import json
import pickle
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Roles in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"


class SessionState(Enum):
    """Session lifecycle states"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


@dataclass
class Message:
    """Represents a single message in conversation"""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_count: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'role': self.role.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'token_count': self.token_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create from dictionary"""
        return cls(
            role=MessageRole(data['role']),
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            token_count=data.get('token_count')
        )


@dataclass
class CaseMemory:
    """Memory specific to a legal case"""
    case_id: str
    case_type: str
    jurisdiction: str
    identified_issues: List[str] = field(default_factory=list)
    relevant_cases: List[Dict] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    legal_arguments: List[Dict] = field(default_factory=list)
    document_drafts: Dict[str, str] = field(default_factory=dict)
    limitation_status: Optional[Dict] = None
    compliance_checks: List[Dict] = field(default_factory=list)
    research_notes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'case_id': self.case_id,
            'case_type': self.case_type,
            'jurisdiction': self.jurisdiction,
            'identified_issues': self.identified_issues,
            'relevant_cases': self.relevant_cases,
            'citations': self.citations,
            'legal_arguments': self.legal_arguments,
            'document_drafts': self.document_drafts,
            'limitation_status': self.limitation_status,
            'compliance_checks': self.compliance_checks,
            'research_notes': self.research_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CaseMemory':
        """Create from dictionary"""
        return cls(
            case_id=data['case_id'],
            case_type=data['case_type'],
            jurisdiction=data['jurisdiction'],
            identified_issues=data.get('identified_issues', []),
            relevant_cases=data.get('relevant_cases', []),
            citations=data.get('citations', []),
            legal_arguments=data.get('legal_arguments', []),
            document_drafts=data.get('document_drafts', {}),
            limitation_status=data.get('limitation_status'),
            compliance_checks=data.get('compliance_checks', []),
            research_notes=data.get('research_notes', []),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )


@dataclass
class UserPreferences:
    """User preferences and settings"""
    user_id: str
    language: str = "english"
    jurisdiction_default: str = ""
    citation_style: str = "standard"
    output_format: str = "markdown"
    auto_save: bool = True
    show_citations: bool = True
    verbose_mode: bool = False
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreferences':
        """Create from dictionary"""
        return cls(**data)


class SessionMemory:
    """
    Intelligent session and context management for Vidhi platform.
    
    This memory system:
    1. Tracks conversation history
    2. Maintains case-specific context
    3. Manages workflow state
    4. Stores user preferences
    5. Caches research findings
    6. Handles context window limits
    7. Provides context retrieval
    8. Supports session persistence
    """
    
    def __init__(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        max_history_length: int = 100,
        max_context_tokens: int = 8000,
        persistence_directory: Optional[Path] = None,
        auto_save: bool = True
    ):
        """
        Initialize Session Memory.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier
            max_history_length: Maximum conversation messages to retain
            max_context_tokens: Maximum tokens for context window
            persistence_directory: Directory for saving sessions
            auto_save: Automatically save on updates
        """
        self.session_id = session_id
        self.user_id = user_id or "anonymous"
        self.max_history_length = max_history_length
        self.max_context_tokens = max_context_tokens
        self.persistence_directory = persistence_directory or Path("./sessions")
        self.auto_save = auto_save
        
        # Session state
        self.state = SessionState.ACTIVE
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        
        # Conversation history
        self.conversation_history: deque = deque(maxlen=max_history_length)
        
        # Case memory
        self.case_memories: Dict[str, CaseMemory] = {}
        self.active_case_id: Optional[str] = None
        
        # User preferences
        self.user_preferences = UserPreferences(user_id=self.user_id)
        
        # Workflow state tracking
        self.workflow_states: Dict[str, Dict] = {}
        
        # Context cache
        self.context_cache: Dict[str, Any] = {}
        
        # Token usage tracking
        self.total_tokens_used = 0
        self.session_metadata: Dict[str, Any] = {}
        
        # Create persistence directory
        self.persistence_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"SessionMemory initialized: {session_id}")
    
    # ===================================================================
    # CONVERSATION MANAGEMENT
    # ===================================================================
    
    def add_message(
        self,
        role: MessageRole,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        Add a message to conversation history.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Created Message object
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {},
            token_count=self._estimate_tokens(content)
        )
        
        self.conversation_history.append(message)
        self.total_tokens_used += message.token_count or 0
        self._update_last_accessed()
        
        if self.auto_save:
            self.save_session()
        
        logger.debug(f"Added message: {role.value} ({message.token_count} tokens)")
        return message
    
    def add_user_message(self, content: str, metadata: Optional[Dict] = None) -> Message:
        """Add a user message"""
        return self.add_message(MessageRole.USER, content, metadata)
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict] = None) -> Message:
        """Add an assistant message"""
        return self.add_message(MessageRole.ASSISTANT, content, metadata)
    
    def add_system_message(self, content: str, metadata: Optional[Dict] = None) -> Message:
        """Add a system message"""
        return self.add_message(MessageRole.SYSTEM, content, metadata)
    
    def get_conversation_history(
        self,
        limit: Optional[int] = None,
        role_filter: Optional[MessageRole] = None
    ) -> List[Message]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of messages to return
            role_filter: Filter by message role
            
        Returns:
            List of messages
        """
        messages = list(self.conversation_history)
        
        if role_filter:
            messages = [m for m in messages if m.role == role_filter]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_recent_context(
        self,
        max_tokens: Optional[int] = None,
        include_system: bool = True
    ) -> List[Dict]:
        """
        Get recent conversation context within token limit.
        
        Args:
            max_tokens: Maximum tokens (defaults to max_context_tokens)
            include_system: Include system messages
            
        Returns:
            List of message dictionaries
        """
        max_tokens = max_tokens or self.max_context_tokens
        
        messages = list(self.conversation_history)
        if not include_system:
            messages = [m for m in messages if m.role != MessageRole.SYSTEM]
        
        # Build context from most recent messages
        context = []
        current_tokens = 0
        
        for message in reversed(messages):
            tokens = message.token_count or self._estimate_tokens(message.content)
            
            if current_tokens + tokens > max_tokens:
                break
            
            context.insert(0, {
                'role': message.role.value,
                'content': message.content
            })
            current_tokens += tokens
        
        logger.debug(f"Retrieved context: {len(context)} messages, ~{current_tokens} tokens")
        return context
    
    def clear_conversation_history(self) -> None:
        """Clear all conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def summarize_conversation(self) -> str:
        """
        Generate a summary of the conversation.
        
        Returns:
            Summary string
        """
        messages = list(self.conversation_history)
        
        if not messages:
            return "No conversation history"
        
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
        
        summary = f"""
Conversation Summary:
- Total Messages: {len(messages)}
- User Messages: {len(user_messages)}
- Assistant Messages: {len(assistant_messages)}
- Session Duration: {(datetime.now() - self.created_at).total_seconds() / 60:.1f} minutes
- Tokens Used: {self.total_tokens_used}
"""
        
        if self.active_case_id:
            summary += f"\nActive Case: {self.active_case_id}"
        
        return summary.strip()
    
    # ===================================================================
    # CASE MEMORY MANAGEMENT
    # ===================================================================
    
    def create_case_memory(
        self,
        case_id: str,
        case_type: str,
        jurisdiction: str
    ) -> CaseMemory:
        """
        Create a new case memory.
        
        Args:
            case_id: Case identifier
            case_type: Type of case
            jurisdiction: Jurisdiction
            
        Returns:
            Created CaseMemory object
        """
        case_memory = CaseMemory(
            case_id=case_id,
            case_type=case_type,
            jurisdiction=jurisdiction
        )
        
        self.case_memories[case_id] = case_memory
        self.active_case_id = case_id
        
        logger.info(f"Created case memory: {case_id}")
        
        if self.auto_save:
            self.save_session()
        
        return case_memory
    
    def get_case_memory(self, case_id: Optional[str] = None) -> Optional[CaseMemory]:
        """
        Get case memory.
        
        Args:
            case_id: Case ID (defaults to active case)
            
        Returns:
            CaseMemory or None
        """
        case_id = case_id or self.active_case_id
        return self.case_memories.get(case_id)
    
    def update_case_memory(
        self,
        case_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """
        Update case memory with new information.
        
        Args:
            case_id: Case identifier
            updates: Dictionary of updates
        """
        case_memory = self.case_memories.get(case_id)
        if not case_memory:
            logger.warning(f"Case memory not found: {case_id}")
            return
        
        # Update fields
        for key, value in updates.items():
            if hasattr(case_memory, key):
                current_value = getattr(case_memory, key)
                
                # Handle list fields (append)
                if isinstance(current_value, list) and isinstance(value, list):
                    current_value.extend(value)
                # Handle dict fields (update)
                elif isinstance(current_value, dict) and isinstance(value, dict):
                    current_value.update(value)
                # Direct assignment
                else:
                    setattr(case_memory, key, value)
        
        case_memory.update_timestamp()
        
        logger.debug(f"Updated case memory: {case_id}")
        
        if self.auto_save:
            self.save_session()
    
    def add_citation_to_case(self, citation: str, case_id: Optional[str] = None) -> None:
        """Add a citation to case memory"""
        case_id = case_id or self.active_case_id
        if not case_id:
            return
        
        case_memory = self.case_memories.get(case_id)
        if case_memory and citation not in case_memory.citations:
            case_memory.citations.append(citation)
            case_memory.update_timestamp()
            
            if self.auto_save:
                self.save_session()
    
    def add_research_note(self, note: str, case_id: Optional[str] = None) -> None:
        """Add a research note to case memory"""
        case_id = case_id or self.active_case_id
        if not case_id:
            return
        
        case_memory = self.case_memories.get(case_id)
        if case_memory:
            case_memory.research_notes.append(note)
            case_memory.update_timestamp()
            
            if self.auto_save:
                self.save_session()
    
    def save_document_draft(
        self,
        draft_name: str,
        content: str,
        case_id: Optional[str] = None
    ) -> None:
        """Save a document draft in case memory"""
        case_id = case_id or self.active_case_id
        if not case_id:
            return
        
        case_memory = self.case_memories.get(case_id)
        if case_memory:
            case_memory.document_drafts[draft_name] = content
            case_memory.update_timestamp()
            
            logger.info(f"Saved draft: {draft_name} ({len(content)} chars)")
            
            if self.auto_save:
                self.save_session()
    
    def get_document_draft(
        self,
        draft_name: str,
        case_id: Optional[str] = None
    ) -> Optional[str]:
        """Get a document draft from case memory"""
        case_id = case_id or self.active_case_id
        if not case_id:
            return None
        
        case_memory = self.case_memories.get(case_id)
        return case_memory.document_drafts.get(draft_name) if case_memory else None
    
    def list_case_memories(self) -> List[str]:
        """Get list of all case IDs in memory"""
        return list(self.case_memories.keys())
    
    # ===================================================================
    # WORKFLOW STATE MANAGEMENT
    # ===================================================================
    
    def save_workflow_state(self, workflow_id: str, state: Dict) -> None:
        """
        Save workflow state.
        
        Args:
            workflow_id: Workflow identifier
            state: Workflow state dictionary
        """
        self.workflow_states[workflow_id] = {
            'state': state,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.debug(f"Saved workflow state: {workflow_id}")
        
        if self.auto_save:
            self.save_session()
    
    def get_workflow_state(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow state"""
        workflow_data = self.workflow_states.get(workflow_id)
        return workflow_data['state'] if workflow_data else None
    
    def clear_workflow_state(self, workflow_id: str) -> None:
        """Clear workflow state"""
        if workflow_id in self.workflow_states:
            del self.workflow_states[workflow_id]
            logger.debug(f"Cleared workflow state: {workflow_id}")
    
    # ===================================================================
    # USER PREFERENCES
    # ===================================================================
    
    def update_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update user preferences"""
        for key, value in preferences.items():
            if hasattr(self.user_preferences, key):
                setattr(self.user_preferences, key, value)
            else:
                self.user_preferences.custom_settings[key] = value
        
        logger.debug("User preferences updated")
        
        if self.auto_save:
            self.save_session()
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        if hasattr(self.user_preferences, key):
            return getattr(self.user_preferences, key)
        return self.user_preferences.custom_settings.get(key, default)
    
    # ===================================================================
    # CONTEXT CACHE
    # ===================================================================
    
    def cache_context(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Cache context data.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        cache_entry = {
            'value': value,
            'timestamp': datetime.now(),
            'ttl': ttl
        }
        
        self.context_cache[key] = cache_entry
        logger.debug(f"Cached context: {key}")
    
    def get_cached_context(self, key: str) -> Optional[Any]:
        """Get cached context data"""
        cache_entry = self.context_cache.get(key)
        
        if not cache_entry:
            return None
        
        # Check TTL
        if cache_entry['ttl']:
            age = (datetime.now() - cache_entry['timestamp']).total_seconds()
            if age > cache_entry['ttl']:
                del self.context_cache[key]
                return None
        
        return cache_entry['value']
    
    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear cache (specific key or all)"""
        if key:
            if key in self.context_cache:
                del self.context_cache[key]
        else:
            self.context_cache.clear()
            logger.debug("All cache cleared")
    
    # ===================================================================
    # SESSION PERSISTENCE
    # ===================================================================
    
    def save_session(self, filepath: Optional[Path] = None) -> None:
        """
        Save session to disk.
        
        Args:
            filepath: Optional custom filepath
        """
        if not filepath:
            filepath = self.persistence_directory / f"{self.session_id}.json"
        
        try:
            session_data = {
                'session_id': self.session_id,
                'user_id': self.user_id,
                'state': self.state.value,
                'created_at': self.created_at.isoformat(),
                'last_accessed': self.last_accessed.isoformat(),
                'conversation_history': [m.to_dict() for m in self.conversation_history],
                'case_memories': {
                    cid: cm.to_dict() for cid, cm in self.case_memories.items()
                },
                'active_case_id': self.active_case_id,
                'user_preferences': self.user_preferences.to_dict(),
                'workflow_states': self.workflow_states,
                'total_tokens_used': self.total_tokens_used,
                'session_metadata': self.session_metadata
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Session saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            raise
    
    @classmethod
    def load_session(
        cls,
        session_id: str,
        persistence_directory: Optional[Path] = None
    ) -> 'SessionMemory':
        """
        Load session from disk.
        
        Args:
            session_id: Session identifier
            persistence_directory: Directory containing sessions
            
        Returns:
            Loaded SessionMemory object
        """
        persistence_directory = persistence_directory or Path("./sessions")
        filepath = persistence_directory / f"{session_id}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Create session
            session = cls(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                persistence_directory=persistence_directory
            )
            
            # Restore state
            session.state = SessionState(session_data['state'])
            session.created_at = datetime.fromisoformat(session_data['created_at'])
            session.last_accessed = datetime.fromisoformat(session_data['last_accessed'])
            
            # Restore conversation history
            session.conversation_history = deque(
                [Message.from_dict(m) for m in session_data['conversation_history']],
                maxlen=session.max_history_length
            )
            
            # Restore case memories
            session.case_memories = {
                cid: CaseMemory.from_dict(cm)
                for cid, cm in session_data['case_memories'].items()
            }
            session.active_case_id = session_data.get('active_case_id')
            
            # Restore user preferences
            session.user_preferences = UserPreferences.from_dict(
                session_data['user_preferences']
            )
            
            # Restore workflow states
            session.workflow_states = session_data.get('workflow_states', {})
            
            # Restore metadata
            session.total_tokens_used = session_data.get('total_tokens_used', 0)
            session.session_metadata = session_data.get('session_metadata', {})
            
            logger.info(f"Session loaded: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            raise
    
    def delete_session(self) -> None:
        """Delete session from disk"""
        filepath = self.persistence_directory / f"{self.session_id}.json"
        
        if filepath.exists():
            filepath.unlink()
            logger.info(f"Session deleted: {self.session_id}")
    
    # ===================================================================
    # LANGCHAIN INTEGRATION
    # ===================================================================
    
    def to_langchain_messages(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Convert conversation history to LangChain message format.
        
        Args:
            limit: Maximum number of messages
            
        Returns:
            List of message dictionaries for LangChain
        """
        messages = self.get_conversation_history(limit=limit)
        
        langchain_messages = []
        for msg in messages:
            # Map roles to LangChain format
            role = msg.role.value
            if role == "assistant":
                role = "ai"
            elif role == "agent":
                role = "ai"
            
            langchain_messages.append({
                "role": role,
                "content": msg.content
            })
        
        return langchain_messages
    
    def add_langchain_message(self, role: str, content: str) -> None:
        """Add a message from LangChain format"""
        # Map LangChain roles to internal roles
        role_map = {
            'user': MessageRole.USER,
            'ai': MessageRole.ASSISTANT,
            'assistant': MessageRole.ASSISTANT,
            'system': MessageRole.SYSTEM
        }
        
        message_role = role_map.get(role, MessageRole.ASSISTANT)
        self.add_message(message_role, content)
    
    # ===================================================================
    # UTILITY METHODS
    # ===================================================================
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)"""
        # Rough estimate: ~4 characters per token
        return max(1, len(text) // 4)
    
    def _update_last_accessed(self) -> None:
        """Update last accessed timestamp"""
        self.last_accessed = datetime.now()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'duration_minutes': (datetime.now() - self.created_at).total_seconds() / 60,
            'message_count': len(self.conversation_history),
            'total_tokens': self.total_tokens_used,
            'case_count': len(self.case_memories),
            'active_case': self.active_case_id,
            'workflow_count': len(self.workflow_states)
        }
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if session is expired"""
        age = datetime.now() - self.last_accessed
        return age > timedelta(hours=max_age_hours)
    
    def archive_session(self) -> None:
        """Archive the session"""
        self.state = SessionState.ARCHIVED
        self.save_session()
        logger.info(f"Session archived: {self.session_id}")
    
    def close_session(self) -> None:
        """Close the session"""
        self.state = SessionState.COMPLETED
        self.save_session()
        logger.info(f"Session closed: {self.session_id}")


class SessionManager:
    """
    Manager for multiple sessions.
    
    Handles session lifecycle, cleanup, and retrieval.
    """
    
    def __init__(
        self,
        persistence_directory: Optional[Path] = None,
        max_session_age_hours: int = 24
    ):
        """
        Initialize Session Manager.
        
        Args:
            persistence_directory: Directory for session storage
            max_session_age_hours: Maximum age before session expires
        """
        self.persistence_directory = persistence_directory or Path("./sessions")
        self.max_session_age_hours = max_session_age_hours
        self.persistence_directory.mkdir(parents=True, exist_ok=True)
        
        # Active sessions cache
        self.active_sessions: Dict[str, SessionMemory] = {}
        
        logger.info("SessionManager initialized")
    
    def create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SessionMemory:
        """Create a new session"""
        if not session_id:
            session_id = self._generate_session_id()
        
        session = SessionMemory(
            session_id=session_id,
            user_id=user_id,
            persistence_directory=self.persistence_directory
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Created session: {session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Get an existing session"""
        # Check active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Try to load from disk
        try:
            session = SessionMemory.load_session(
                session_id,
                self.persistence_directory
            )
            self.active_sessions[session_id] = session
            return session
        except FileNotFoundError:
            logger.warning(f"Session not found: {session_id}")
            return None
    
    def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> SessionMemory:
        """Get existing session or create new one"""
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id, user_id)
        return session
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[str]:
        """List all session IDs (optionally filtered by user)"""
        session_files = list(self.persistence_directory.glob("*.json"))
        session_ids = [f.stem for f in session_files]
        
        if user_id:
            # Filter by user_id (requires loading each session)
            filtered_ids = []
            for sid in session_ids:
                try:
                    session = self.get_session(sid)
                    if session and session.user_id == user_id:
                        filtered_ids.append(sid)
                except Exception:
                    continue
            return filtered_ids
        
        return session_ids
    
    def cleanup_expired_sessions(self) -> int:
        """Delete expired sessions"""
        session_ids = self.list_sessions()
        deleted_count = 0
        
        for sid in session_ids:
            try:
                session = self.get_session(sid)
                if session and session.is_expired(self.max_session_age_hours):
                    session.delete_session()
                    if sid in self.active_sessions:
                        del self.active_sessions[sid]
                    deleted_count += 1
                    logger.info(f"Deleted expired session: {sid}")
            except Exception as e:
                logger.error(f"Error checking session {sid}: {e}")
        
        return deleted_count
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        timestamp = datetime.now().isoformat()
        random_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"session_{random_hash}"


# Convenience functions

def create_session(session_id: Optional[str] = None, user_id: Optional[str] = None) -> SessionMemory:
    """Create a new session"""
    manager = SessionManager()
    return manager.create_session(session_id, user_id)


def load_session(session_id: str) -> SessionMemory:
    """Load an existing session"""
    return SessionMemory.load_session(session_id)


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("VIDHI SESSION MEMORY - DEMONSTRATION")
    print("=" * 80)
    
    # Create session
    session = create_session(user_id="demo_user")
    print(f"\nCreated session: {session.session_id}")
    
    # Add conversation
    print("\nAdding conversation messages...")
    session.add_user_message("I need help with a bail application")
    session.add_assistant_message(
        "I can help you draft a bail application. Please provide the case details."
    )
    session.add_user_message("The accused was arrested on 15th January 2026 under Section 420 IPC")
    
    # Create case memory
    print("\nCreating case memory...")
    case_memory = session.create_case_memory(
        case_id="BAIL_001",
        case_type="criminal",
        jurisdiction="Delhi"
    )
    
    # Update case memory
    session.update_case_memory("BAIL_001", {
        'identified_issues': ['Bail under Section 437 CrPC'],
        'citations': ['AIR 1978 SC 1675']
    })
    
    # Save document draft
    session.save_document_draft(
        "bail_application_v1",
        "IN THE COURT OF...\n\nAPPLICATION FOR BAIL..."
    )
    
    # Get conversation context
    print("\nRecent conversation context:")
    context = session.get_recent_context(max_tokens=500)
    for msg in context:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Get statistics
    print("\nSession Statistics:")
    stats = session.get_session_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Save session
    print("\nSaving session...")
    session.save_session()
    
    # Load session
    print("\nLoading session...")
    loaded_session = load_session(session.session_id)
    print(f"Loaded session: {loaded_session.session_id}")
    print(f"Messages: {len(loaded_session.conversation_history)}")
    print(f"Case memories: {len(loaded_session.case_memories)}")
    
    # Cleanup
    print("\nClosing session...")
    session.close_session()
    
    print("\n" + "=" * 80)
    print("Session memory demonstration complete!")
