"""Log retention policy configuration and enforcement."""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class RetentionPolicy:
    """Defines a log retention policy."""
    name: str
    max_age_days: int
    compress_after_days: int = 0
    delete_after_days: int = 0
    max_size_mb: float = 0
    patterns: List[str] = None

    def __post_init__(self):
        if self.patterns is None:
            self.patterns = ["*.log"]
        if not isinstance(self.max_age_days, int):
            raise TypeError(f"max_age_days must be an integer, got {type(self.max_age_days).__name__}")
        if self.max_age_days < 0:
            raise ValueError("max_age_days must be non-negative")
        if not isinstance(self.compress_after_days, int):
            raise TypeError(f"compress_after_days must be an integer, got {type(self.compress_after_days).__name__}")
        if self.compress_after_days < 0:
            raise ValueError("compress_after_days must be non-negative")
        if not isinstance(self.delete_after_days, int):
            raise TypeError(f"delete_after_days must be an integer, got {type(self.delete_after_days).__name__}")
        if self.delete_after_days < 0:
            raise ValueError("delete_after_days must be non-negative")
        if not isinstance(self.max_size_mb, (int, float)):
            raise TypeError(f"max_size_mb must be a number, got {type(self.max_size_mb).__name__}")
        if self.max_size_mb < 0:
            raise ValueError("max_size_mb must be non-negative")

    def __repr__(self) -> str:
        return (
            f"RetentionPolicy(name={self.name!r}, max_age_days={self.max_age_days}, "
            f"compress_after_days={self.compress_after_days}, delete_after_days={self.delete_after_days})"
        )

    def __str__(self) -> str:
        parts = [f"RetentionPolicy('{self.name}'"]
        if self.max_age_days:
            parts.append(f"max_age={self.max_age_days}d")
        if self.compress_after_days:
            parts.append(f"compress_after={self.compress_after_days}d")
        if self.delete_after_days:
            parts.append(f"delete_after={self.delete_after_days}d")
        if self.max_size_mb:
            parts.append(f"max_size={self.max_size_mb}MB")
        if self.patterns and self.patterns != ["*.log"]:
            parts.append(f"patterns={self.patterns}")
        return ", ".join(parts) + ")"


class RetentionManager:
    """Manage log file retention and cleanup."""

    def __init__(self, log_directory: str):
        self.log_directory = Path(log_directory)
        self.policies: List[RetentionPolicy] = []
        self._actions_log: List[Dict] = []

    def __repr__(self) -> str:
        return f"RetentionManager(dir={self.log_directory}, policies={len(self.policies)})"

    def add_policy(self, policy: RetentionPolicy):
        """Add a retention policy.

        Args:
            policy: RetentionPolicy to add.

        Raises:
            TypeError: If policy is not a RetentionPolicy instance.
        """
        if not isinstance(policy, RetentionPolicy):
            raise TypeError("policy must be a RetentionPolicy instance")
        self.policies.append(policy)

    def scan_files(self) -> List[Dict]:
        """Scan log files and their metadata.

        Returns:
            List of file metadata dictionaries.
        """
        files = []
        for policy in self.policies:
            for pattern in policy.patterns:
                for file_path in self.log_directory.glob(pattern):
                    try:
                        if not file_path.is_file():
                            continue
                        stat = file_path.stat()
                        age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                        files.append({
                            "path": str(file_path),
                            "size_mb": stat.st_size / (1024 * 1024),
                            "age_days": age_days,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "policy": policy.name,
                        })
                    except (OSError, PermissionError):
                        continue
        return files

    def enforce(self, dry_run: bool = False) -> List[Dict]:
        """Enforce retention policies.

        Args:
            dry_run: If True, only report actions without executing them.

        Returns:
            List of actions taken or planned.
        """
        actions = []
        files = self.scan_files()

        for file_info in files:
            policy = next((p for p in self.policies if p.name == file_info["policy"]), None)
            if not policy:
                continue

            path = Path(file_info["path"])
            age = file_info["age_days"]
            size = file_info["size_mb"]

            # Check delete threshold
            if policy.delete_after_days and age > policy.delete_after_days:
                action = {"action": "delete", "file": str(path), "reason": f"age {age}d > {policy.delete_after_days}d"}
                if not dry_run:
                    path.unlink(missing_ok=True)
                actions.append(action)

            # Check compress threshold
            elif policy.compress_after_days and age > policy.compress_after_days and not str(path).endswith(".gz"):
                action = {"action": "compress", "file": str(path), "reason": f"age {age}d > {policy.compress_after_days}d"}
                if not dry_run:
                    self._compress_file(path)
                actions.append(action)

            # Check size threshold
            elif policy.max_size_mb and size > policy.max_size_mb:
                action = {"action": "rotate", "file": str(path), "reason": f"size {size:.1f}MB > {policy.max_size_mb}MB"}
                if not dry_run:
                    self._rotate_file(path)
                actions.append(action)

        self._actions_log.extend(actions)
        return actions

    def _compress_file(self, path: Path):
        """Compress a log file with gzip."""
        gz_path = path.with_suffix(path.suffix + ".gz")
        with open(path, "rb") as f_in:
            with gzip.open(gz_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        path.unlink()

    def _rotate_file(self, path: Path):
        """Rotate a log file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")
        path.rename(rotated)

    def get_actions_log(self) -> List[Dict]:
        """Get history of retention actions."""
        return list(self._actions_log)

    def remove_policy(self, name: str) -> bool:
        """Remove a retention policy by name.

        Args:
            name: Name of the policy to remove.

        Returns:
            True if policy was found and removed, False otherwise.
        """
        before = len(self.policies)
        self.policies = [p for p in self.policies if p.name != name]
        return len(self.policies) < before

    def has_policy(self, name: str) -> bool:
        """Check if a policy with the given name exists.

        Args:
            name: Policy name to check.

        Returns:
            True if policy exists, False otherwise.
        """
        return any(p.name == name for p in self.policies)

    @property
    def stats(self) -> Dict[str, int]:
        """Get retention manager statistics."""
        return {
            "policies": len(self.policies),
            "actions_taken": len(self._actions_log),
        }

    @property
    def last_action(self) -> Optional[Dict]:
        """Get the most recent retention action.

        Returns:
            Last action dict, or None if no actions taken.
        """
        return self._actions_log[-1] if self._actions_log else None

    def clear_actions_log(self):
        """Clear the actions history."""
        self._actions_log.clear()

    def get_policy_names(self) -> List[str]:
        """Get list of policy names.

        Returns:
            List of policy names.
        """
        return [p.name for p in self.policies]

    def total_size_mb(self) -> float:
        """Get total size of all scanned files in MB.

        Returns:
            Total size in megabytes.
        """
        files = self.scan_files()
        return round(sum(f["size_mb"] for f in files), 2)

    def get_files_by_age(self, min_age_days: int = 0) -> List[Dict]:
        """Get files older than specified age.

        Args:
            min_age_days: Minimum age in days.

        Returns:
            List of file metadata dictionaries.
        """
        files = self.scan_files()
        return [f for f in files if f["age_days"] >= min_age_days]

    def get_compressed_files(self) -> List[Dict]:
        """Get list of already compressed files.

        Returns:
            List of compressed file metadata.
        """
        files = self.scan_files()
        return [f for f in files if f["path"].endswith(".gz")]

    def get_uncompressed_files(self) -> List[Dict]:
        """Get list of uncompressed log files.

        Returns:
            List of uncompressed file metadata.
        """
        files = self.scan_files()
        return [f for f in files if not f["path"].endswith(".gz")]

    def get_file_count(self) -> int:
        """Get total number of log files.

        Returns:
            Count of files found.
        """
        return len(self.scan_files())

    def get_actions_count(self) -> int:
        """Get number of retention actions taken.

        Returns:
            Count of actions.
        """
        return len(self._actions_log)

    def get_policy_by_name(self, name: str) -> Optional[RetentionPolicy]:
        """Get a policy by name.

        Args:
            name: Policy name.

        Returns:
            RetentionPolicy if found, None otherwise.
        """
        for policy in self.policies:
            if policy.name == name:
                return policy
        return None

    def has_policies(self) -> bool:
        """Check if any policies are configured.

        Returns:
            True if policies exist.
        """
        return len(self.policies) > 0

    def has_actions(self) -> bool:
        """Check if any actions have been taken.

        Returns:
            True if actions exist.
        """
        return len(self._actions_log) > 0

    def has_files(self) -> bool:
        """Check if any log files exist.

        Returns:
            True if files found.
        """
        return len(self.scan_files()) > 0

    def get_total_size_formatted(self) -> str:
        """Get total size as formatted string.

        Returns:
            Formatted size string.
        """
        from .reader import format_size
        files = self.scan_files()
        total_bytes = sum(f.get("size_bytes", 0) for f in files)
        return format_size(total_bytes)

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get retention manager statistics as dictionary.

        Returns:
            Dictionary with retention stats.
        """
        return {
            "policies": len(self.policies),
            "files": self.get_file_count(),
            "actions": self.get_actions_count(),
            "has_files": self.has_files(),
        }

    def get_actions_log(self) -> List[Dict]:
        """Get actions log.

        Returns:
            List of action dictionaries.
        """
        return list(self._actions_log)

    def get_policies_dict(self) -> List[Dict[str, Any]]:
        """Get all policies as dictionaries.

        Returns:
            List of policy dictionaries.
        """
        return [
            {
                "name": p.name,
                "max_age_days": p.max_age_days,
                "compress_after_days": p.compress_after_days,
                "delete_after_days": p.delete_after_days,
                "max_size_mb": p.max_size_mb,
            }
            for p in self.policies
        ]

    def get_compressed_count(self) -> int:
        """Get count of compressed files.

        Returns:
            Count of compressed files.
        """
        return len(self.get_compressed_files())

    def get_uncompressed_count(self) -> int:
        """Get count of uncompressed files.

        Returns:
            Count of uncompressed files.
        """
        return len(self.get_uncompressed_files())

    def get_compression_rate(self) -> float:
        """Get compression rate as percentage.

        Returns:
            Compression rate percentage.
        """
        files = self.scan_files()
        if not files:
            return 0.0
        compressed = sum(1 for f in files if f["path"].endswith(".gz"))
        return round(compressed / len(files) * 100, 2)

    def get_compression_rate_formatted(self) -> str:
        """Get formatted compression rate string.

        Returns:
            Formatted compression rate string.
        """
        return f"{self.get_compression_rate():.1f}%"

    def get_average_file_size(self) -> float:
        """Get average file size in MB.

        Returns:
            Average file size in MB.
        """
        files = self.scan_files()
        if not files:
            return 0.0
        total_mb = sum(f.get("size_mb", 0) for f in files)
        return round(total_mb / len(files), 2)

    def get_average_file_size_formatted(self) -> str:
        """Get formatted average file size string.

        Returns:
            Formatted average file size string.
        """
        return f"{self.get_average_file_size():.2f} MB"

    def get_compressed_count_formatted(self) -> str:
        """Get formatted compressed count string.

        Returns:
            Formatted compressed count string.
        """
        return f"{self.get_compressed_count()} compressed"

    def get_uncompressed_count_formatted(self) -> str:
        """Get formatted uncompressed count string.

        Returns:
            Formatted uncompressed count string.
        """
        return f"{self.get_uncompressed_count()} uncompressed"

    def get_file_count_formatted(self) -> str:
        """Get formatted file count string.

        Returns:
            Formatted file count string.
        """
        return f"{self.get_file_count()} files"

    def get_actions_count_formatted(self) -> str:
        """Get formatted actions count string.

        Returns:
            Formatted actions count string.
        """
        return f"{self.get_actions_count()} actions"

    def get_policy_count_formatted(self) -> str:
        """Get formatted policy count string.

        Returns:
            Formatted policy count string.
        """
        return f"{len(self.policies)} policies"
