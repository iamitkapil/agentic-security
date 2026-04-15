#!/usr/bin/env python3
"""
Agent Memory System - Persistent memory and state management
Enables learning from past executions and context retention
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


class MemoryEntry:
    """Represents a single memory entry"""
    
    def __init__(
        self,
        key: str,
        value: Any,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.key = key
        self.value = value
        self.category = category
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.access_count = 0
        self.last_accessed = self.timestamp
    
    def access(self) -> Any:
        """Access the memory entry and update statistics"""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        entry = cls(
            key=data["key"],
            value=data["value"],
            category=data.get("category", "general"),
            metadata=data.get("metadata", {})
        )
        entry.timestamp = datetime.fromisoformat(data["timestamp"])
        entry.access_count = data.get("access_count", 0)
        entry.last_accessed = datetime.fromisoformat(data.get("last_accessed", data["timestamp"]))
        return entry


class AgentMemory:
    """
    Persistent memory system for the agent.
    Stores and retrieves information across sessions.
    """
    
    def __init__(self, memory_dir: str = ".agent_memory", max_entries: int = 1000):
        """
        Initialize agent memory.
        
        Args:
            memory_dir: Directory to store memory files
            max_entries: Maximum number of entries to keep in memory
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.max_entries = max_entries
        
        # In-memory storage
        self.short_term: Dict[str, MemoryEntry] = {}
        self.long_term: Dict[str, MemoryEntry] = {}
        
        # Load existing memory
        self._load_memory()
    
    def store(
        self,
        key: str,
        value: Any,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        persist: bool = False
    ) -> None:
        """
        Store information in memory.
        
        Args:
            key: Unique identifier for the memory
            value: The value to store
            category: Category for organization
            metadata: Additional metadata
            persist: Whether to persist to long-term memory
        """
        entry = MemoryEntry(key, value, category, metadata)
        
        if persist:
            self.long_term[key] = entry
            self._save_memory()
        else:
            self.short_term[key] = entry
        
        # Enforce max entries limit
        if len(self.short_term) > self.max_entries:
            self._evict_old_entries()
        
        logger.debug(f"Stored memory: {key} (persist={persist})")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve information from memory.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        # Check short-term first
        if key in self.short_term:
            return self.short_term[key].access()
        
        # Then check long-term
        if key in self.long_term:
            return self.long_term[key].access()
        
        return None
    
    def search(
        self,
        category: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """
        Search memory entries by category or metadata.
        
        Args:
            category: Filter by category
            metadata_filter: Filter by metadata key-value pairs
            
        Returns:
            List of matching memory entries
        """
        results = []
        
        # Search both short-term and long-term
        all_entries = list(self.short_term.values()) + list(self.long_term.values())
        
        for entry in all_entries:
            # Category filter
            if category and entry.category != category:
                continue
            
            # Metadata filter
            if metadata_filter:
                match = all(
                    entry.metadata.get(k) == v
                    for k, v in metadata_filter.items()
                )
                if not match:
                    continue
            
            results.append(entry)
        
        return results
    
    def get_recent(self, n: int = 10, category: Optional[str] = None) -> List[MemoryEntry]:
        """
        Get the n most recent memory entries.
        
        Args:
            n: Number of entries to retrieve
            category: Optional category filter
            
        Returns:
            List of recent memory entries
        """
        all_entries = list(self.short_term.values()) + list(self.long_term.values())
        
        if category:
            all_entries = [e for e in all_entries if e.category == category]
        
        # Sort by timestamp (most recent first)
        all_entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return all_entries[:n]
    
    def get_frequently_accessed(self, n: int = 10) -> List[MemoryEntry]:
        """
        Get the n most frequently accessed entries.
        
        Args:
            n: Number of entries to retrieve
            
        Returns:
            List of frequently accessed entries
        """
        all_entries = list(self.short_term.values()) + list(self.long_term.values())
        
        # Sort by access count (most accessed first)
        all_entries.sort(key=lambda e: e.access_count, reverse=True)
        
        return all_entries[:n]
    
    def delete(self, key: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            key: The key to delete
            
        Returns:
            True if deleted, False if not found
        """
        deleted = False
        
        if key in self.short_term:
            del self.short_term[key]
            deleted = True
        
        if key in self.long_term:
            del self.long_term[key]
            self._save_memory()
            deleted = True
        
        return deleted
    
    def clear_short_term(self) -> None:
        """Clear all short-term memory"""
        self.short_term.clear()
        logger.info("Short-term memory cleared")
    
    def clear_all(self) -> None:
        """Clear all memory (short-term and long-term)"""
        self.short_term.clear()
        self.long_term.clear()
        self._save_memory()
        logger.info("All memory cleared")
    
    def _evict_old_entries(self) -> None:
        """Evict old entries when memory is full"""
        # Keep the most recently accessed entries
        entries = sorted(
            self.short_term.values(),
            key=lambda e: e.last_accessed,
            reverse=True
        )
        
        # Keep only the most recent max_entries
        self.short_term = {
            e.key: e for e in entries[:self.max_entries]
        }
        
        logger.debug(f"Evicted old entries, kept {len(self.short_term)}")
    
    def _save_memory(self) -> None:
        """Save long-term memory to disk"""
        try:
            memory_file = self.memory_dir / "long_term_memory.json"
            
            data = {
                "entries": [entry.to_dict() for entry in self.long_term.values()],
                "saved_at": datetime.now().isoformat()
            }
            
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self.long_term)} entries to {memory_file}")
            
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def _load_memory(self) -> None:
        """Load long-term memory from disk"""
        try:
            memory_file = self.memory_dir / "long_term_memory.json"
            
            if not memory_file.exists():
                logger.debug("No existing memory file found")
                return
            
            with open(memory_file, 'r') as f:
                data = json.load(f)
            
            for entry_data in data.get("entries", []):
                entry = MemoryEntry.from_dict(entry_data)
                self.long_term[entry.key] = entry
            
            logger.info(f"Loaded {len(self.long_term)} entries from {memory_file}")
            
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        all_entries = list(self.short_term.values()) + list(self.long_term.values())
        
        categories = {}
        for entry in all_entries:
            categories[entry.category] = categories.get(entry.category, 0) + 1
        
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "total_count": len(all_entries),
            "categories": categories,
            "total_accesses": sum(e.access_count for e in all_entries),
            "memory_dir": str(self.memory_dir)
        }
    
    def export_memory(self, output_file: str) -> None:
        """
        Export all memory to a file.
        
        Args:
            output_file: Path to export file
        """
        try:
            all_entries = {
                "short_term": [e.to_dict() for e in self.short_term.values()],
                "long_term": [e.to_dict() for e in self.long_term.values()],
                "exported_at": datetime.now().isoformat(),
                "statistics": self.get_statistics()
            }
            
            with open(output_file, 'w') as f:
                json.dump(all_entries, f, indent=2)
            
            logger.info(f"Memory exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
    
    def import_memory(self, input_file: str, merge: bool = True) -> None:
        """
        Import memory from a file.
        
        Args:
            input_file: Path to import file
            merge: Whether to merge with existing memory or replace
        """
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            if not merge:
                self.clear_all()
            
            # Import short-term
            for entry_data in data.get("short_term", []):
                entry = MemoryEntry.from_dict(entry_data)
                self.short_term[entry.key] = entry
            
            # Import long-term
            for entry_data in data.get("long_term", []):
                entry = MemoryEntry.from_dict(entry_data)
                self.long_term[entry.key] = entry
            
            self._save_memory()
            
            logger.info(f"Memory imported from {input_file}")
            
        except Exception as e:
            logger.error(f"Error importing memory: {e}")


class ConversationMemory:
    """
    Specialized memory for conversation history.
    Maintains context across agent interactions.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of conversation turns to keep
        """
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
    
    def add_turn(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a conversation turn.
        
        Args:
            role: Role (user, assistant, system)
            content: The message content
            metadata: Additional metadata
        """
        turn = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.history.append(turn)
        
        # Enforce max history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, n: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            n: Number of recent turns to get (None for all)
            
        Returns:
            List of conversation turns
        """
        if n is None:
            return self.history.copy()
        return self.history[-n:]
    
    def get_context_window(self, max_tokens: int = 4000) -> List[Dict[str, Any]]:
        """
        Get conversation history that fits within a token limit.
        
        Args:
            max_tokens: Approximate maximum tokens
            
        Returns:
            List of recent conversation turns
        """
        # Simple approximation: ~4 chars per token
        max_chars = max_tokens * 4
        
        result = []
        total_chars = 0
        
        for turn in reversed(self.history):
            turn_chars = len(turn["content"])
            if total_chars + turn_chars > max_chars:
                break
            result.insert(0, turn)
            total_chars += turn_chars
        
        return result
    
    def clear(self) -> None:
        """Clear conversation history"""
        self.history.clear()
    
    def summarize(self) -> str:
        """Get a summary of the conversation"""
        if not self.history:
            return "No conversation history"
        
        summary = f"Conversation with {len(self.history)} turns:\n"
        for i, turn in enumerate(self.history[-5:], 1):  # Last 5 turns
            summary += f"{i}. {turn['role']}: {turn['content'][:100]}...\n"
        
        return summary

# Made with Bob
