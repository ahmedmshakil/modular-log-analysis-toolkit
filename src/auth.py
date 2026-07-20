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

    def __repr__(self) -> str:
        return f"AuthManager(users={len(self._users)}, sessions={len(self._sessions)})"

    def _hash_password(self, password: str, salt: str = None) -> str:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        hash_val = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return f"{salt}:{hash_val}"

    def _verify_password(self, password: str, stored: str) -> bool:
        """Verify a password against stored hash."""
        try:
            salt, hash_val = stored.split(":", 1)
        except (AttributeError, ValueError):
            return False
        return self._hash_password(password, salt) == f"{salt}:{hash_val}"

    def create_user(self, username: str, password: str, role: str = "viewer") -> bool:
        """Create a new user.

        Args:
            username: Username for the new account.
            password: Password for the new account.
            role: User role (viewer, analyst, admin).

        Returns:
            True if user was created successfully.
        """
        if not username or not isinstance(username, str):
            return False
        if not password or not isinstance(password, str):
            return False
        if len(password) < 8:
            return False
        if len(username) < 3:
            return False
        if username in self._users:
            return False
        if role not in self.ROLES:
            return False
        if not username.isalnum():
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
        """Validate session token and return username.

        Args:
            token: Session token to validate.

        Returns:
            Username if session is valid, None otherwise.
        """
        if not token or not isinstance(token, str):
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

    def get_session_info(self, token: str) -> Optional[Dict]:
        """Get session information without expiry validation.

        Args:
            token: Session token to look up.

        Returns:
            Session info dict if found, None otherwise.
        """
        if not token or not isinstance(token, str):
            return None
        session = self._sessions.get(token)
        if not session:
            return None
        return {
            "username": session["username"],
            "expires": session["expires"].isoformat(),
            "is_expired": datetime.now() > session["expires"],
        }

    def list_users(self) -> List[Dict]:
        """List all users (admin only)."""
        return [u.to_dict() for u in self._users.values()]

    def delete_user(self, username: str) -> bool:
        """Delete a user.

        Args:
            username: Username to delete.

        Returns:
            True if user was deleted, False if not found.

        Raises:
            TypeError: If username is not a string.
        """
        if not isinstance(username, str):
            raise TypeError("username must be a string")
        if username in self._users:
            del self._users[username]
            self._save_users()
            return True
        return False

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username.

        Args:
            username: Username to look up.

        Returns:
            User if found, None otherwise.
        """
        return self._users.get(username)

    def user_count(self) -> int:
        """Get total number of registered users."""
        return len(self._users)

    def active_sessions(self) -> int:
        """Get number of active sessions."""
        return len(self._sessions)

    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a specific role.

        Args:
            role: Role name.

        Returns:
            List of permission strings.
        """
        return self.ROLES.get(role, [])

    def change_user_role(self, username: str, new_role: str) -> bool:
        """Change a user's role.

        Args:
            username: Username to update.
            new_role: New role to assign.

        Returns:
            True if role was changed, False if user not found or invalid role.
        """
        if new_role not in self.ROLES:
            return False
        user = self._users.get(username)
        if not user:
            return False
        user.role = new_role
        self._save_users()
        return True

    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account.

        Args:
            username: Username to deactivate.

        Returns:
            True if user was deactivated, False if not found.
        """
        user = self._users.get(username)
        if not user:
            return False
        user.active = False
        self._save_users()
        return True

    def activate_user(self, username: str) -> bool:
        """Activate a user account.

        Args:
            username: Username to activate.

        Returns:
            True if user was activated, False if not found.
        """
        user = self._users.get(username)
        if not user:
            return False
        user.active = True
        self._save_users()
        return True

    def get_active_users(self) -> List[Dict]:
        """Get list of active users.

        Returns:
            List of active user dictionaries.
        """
        return [u.to_dict() for u in self._users.values() if u.active]

    def get_inactive_users(self) -> List[Dict]:
        """Get list of inactive users.

        Returns:
            List of inactive user dictionaries.
        """
        return [u.to_dict() for u in self._users.values() if not u.active]

    def has_users(self) -> bool:
        """Check if any users exist.

        Returns:
            True if users exist.
        """
        return len(self._users) > 0

    def get_users_by_role(self, role: str) -> List[Dict]:
        """Get users filtered by role.

        Args:
            role: Role to filter by.

        Returns:
            List of user dictionaries with the specified role.
        """
        return [u.to_dict() for u in self._users.values() if u.role == role]

    def get_all_users(self) -> List[Dict]:
        """Get all users.

        Returns:
            List of all user dictionaries.
        """
        return [u.to_dict() for u in self._users.values()]

    def get_roles(self) -> List[str]:
        """Get list of available roles.

        Returns:
            List of role strings.
        """
        return list(self.ROLES.keys())

    def has_sessions(self) -> bool:
        """Check if any sessions exist.

        Returns:
            True if sessions exist.
        """
        return len(self._sessions) > 0

    def get_session_count(self) -> int:
        """Get number of active sessions.

        Returns:
            Count of sessions.
        """
        return len(self._sessions)

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get auth manager statistics as dictionary.

        Returns:
            Dictionary with auth stats.
        """
        return {
            "users": len(self._users),
            "active_users": len(self.get_active_users()),
            "sessions": len(self._sessions),
            "roles": len(self.ROLES),
        }

    def get_summary_string(self) -> str:
        """Get a formatted summary string.

        Returns:
            Formatted summary string.
        """
        return (
            f"Users: {len(self._users)}, "
            f"Active: {len(self.get_active_users())}, "
            f"Sessions: {len(self._sessions)}"
        )

    def get_role_counts(self) -> Dict[str, int]:
        """Get count of users per role.

        Returns:
            Dictionary mapping role names to counts.
        """
        from collections import Counter
        return dict(Counter(u.role for u in self._users.values()))

    def get_active_user_count(self) -> int:
        """Get count of active users.

        Returns:
            Count of active users.
        """
        return sum(1 for u in self._users.values() if u.active)

    def get_inactive_user_count(self) -> int:
        """Get count of inactive users.

        Returns:
            Count of inactive users.
        """
        return sum(1 for u in self._users.values() if not u.active)

    def has_role(self, role: str) -> bool:
        """Check if any user has a specific role.

        Args:
            role: Role name to check.

        Returns:
            True if role exists.
        """
        return any(u.role == role for u in self._users.values())

    def get_role_distribution(self) -> Dict[str, float]:
        """Get role distribution as percentages.

        Returns:
            Dictionary mapping role names to percentages.
        """
        if not self._users:
            return {}
        total = len(self._users)
        counts = self.get_role_counts()
        return {role: round(count / total * 100, 2) for role, count in counts.items()}

    def get_active_rate(self) -> float:
        """Get active user rate as percentage.

        Returns:
            Active user rate percentage.
        """
        if not self._users:
            return 0.0
        return round(self.get_active_user_count() / len(self._users) * 100, 2)

    def get_inactive_rate(self) -> float:
        """Get inactive user rate as percentage.

        Returns:
            Inactive user rate percentage.
        """
        if not self._users:
            return 0.0
        return round(self.get_inactive_user_count() / len(self._users) * 100, 2)

    def get_most_common_role(self) -> Optional[str]:
        """Get the most common user role.

        Returns:
            Most common role string, or None.
        """
        counts = self.get_role_counts()
        if not counts:
            return None
        return max(counts, key=counts.get)

    def get_session_rate(self) -> float:
        """Get sessions per user rate.

        Returns:
            Sessions per user rate.
        """
        if not self._users:
            return 0.0
        return round(len(self._sessions) / len(self._users), 2)

    def _save_users(self):
        """Save users to file."""
        data = {}
        for name, user in self._users.items():
            data[name] = {
                "password_hash": user.password_hash,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
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
                    last_login=datetime.fromisoformat(info["last_login"]) if info.get("last_login") else None,
                    active=info.get("active", True),
                )
