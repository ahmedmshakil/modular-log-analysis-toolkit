"""User authentication and access control for log viewer."""

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class User:
    """User account for log access."""
    username: str
    password_hash: str
    role: str = "viewer"  # viewer, analyst, admin
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    active: bool = True

    def __repr__(self) -> str:
        return f"User(username={self.username!r}, role={self.role!r}, active={self.active})"

    @property
    def is_active(self) -> bool:
        """Check if user account is active."""
        return self.active

    def to_dict(self) -> Dict:
        return {
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "active": self.active,
        }


class AuthManager:
    """Manage user authentication and sessions."""

    ROLES = {
        "viewer": ["read"],
        "analyst": ["read", "search", "export"],
        "admin": ["read", "search", "export", "manage", "configure"],
    }
    SESSION_DURATION_HOURS = 24

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Dict] = {}  # token -> {username, expires}
        self._load_users()

    def _hash_password(self, password: str, salt: str = None) -> str:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        hash_val = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return f"{salt}:{hash_val}"

    def _verify_password(self, password: str, stored: str) -> bool:
        """Verify a password against stored hash."""
        salt, hash_val = stored.split(":")
        return self._hash_password(password, salt) == stored

    def create_user(self, username: str, password: str, role: str = "viewer") -> bool:
        """Create a new user."""
        if not username or not isinstance(username, str):
            return False
        if not password or not isinstance(password, str):
            return False
        if len(password) < 8:
            return False
        if username in self._users:
            return False
        if role not in self.ROLES:
            return False

        self._users[username] = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role,
        )
        self._save_users()
        return True

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return session token."""
        user = self._users.get(username)
        if not user or not user.active:
            return None
        if not self._verify_password(password, user.password_hash):
            return None

        token = secrets.token_hex(32)
        self._sessions[token] = {
            "username": username,
            "expires": datetime.now() + timedelta(hours=self.SESSION_DURATION_HOURS),
        }
        user.last_login = datetime.now()
        self._save_users()
        return token

    def validate_session(self, token: str) -> Optional[str]:
        """Validate session token and return username."""
        if not token:
            return None
        session = self._sessions.get(token)
        if not session:
            return None
        if datetime.now() > session["expires"]:
            del self._sessions[token]
            return None
        return session["username"]

    def check_permission(self, token: str, permission: str) -> bool:
        """Check if user has a specific permission."""
        username = self.validate_session(token)
        if not username:
            return False
        user = self._users.get(username)
        if not user:
            return False
        return permission in self.ROLES.get(user.role, [])

    def logout(self, token: str):
        """Invalidate a session."""
        self._sessions.pop(token, None)

    def has_permission(self, username: str, permission: str) -> bool:
        """Check if a user has a specific permission by username."""
        user = self._users.get(username)
        if not user or not user.active:
            return False
        return permission in self.ROLES.get(user.role, [])

    def expire_sessions(self) -> int:
        """Remove all expired sessions. Returns count of removed sessions."""
        now = datetime.now()
        expired = [t for t, s in self._sessions.items() if now > s["expires"]]
        for token in expired:
            del self._sessions[token]
        return len(expired)

    def list_users(self) -> List[Dict]:
        """List all users (admin only)."""
        return [u.to_dict() for u in self._users.values()]

    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        if username in self._users:
            del self._users[username]
            self._save_users()
            return True
        return False

    def _save_users(self):
        """Save users to file."""
        data = {}
        for name, user in self._users.items():
            data[name] = {
                "password_hash": user.password_hash,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
                "active": user.active,
            }
        path = self.data_dir / "users.json"
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_users(self):
        """Load users from file."""
        path = self.data_dir / "users.json"
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            for name, info in data.items():
                self._users[name] = User(
                    username=name,
                    password_hash=info["password_hash"],
                    role=info.get("role", "viewer"),
                    active=info.get("active", True),
                )
