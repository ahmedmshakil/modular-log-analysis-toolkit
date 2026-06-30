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
        if self.max_age_days < 0:
            raise ValueError("max_age_days must be non-negative")
        if self.compress_after_days < 0:
            raise ValueError("compress_after_days must be non-negative")
        if self.delete_after_days < 0:
            raise ValueError("delete_after_days must be non-negative")


class RetentionManager:
    """Manage log file retention and cleanup."""

    def __init__(self, log_directory: str):
        self.log_directory = Path(log_directory)
        self.policies: List[RetentionPolicy] = []
        self._actions_log: List[Dict] = []

    def add_policy(self, policy: RetentionPolicy):
        """Add a retention policy."""
        self.policies.append(policy)

    def scan_files(self) -> List[Dict]:
        """Scan log files and their metadata."""
        files = []
        for policy in self.policies:
            for pattern in policy.patterns:
                for file_path in self.log_directory.glob(pattern):
                    stat = file_path.stat()
                    age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                    files.append({
                        "path": str(file_path),
                        "size_mb": stat.st_size / (1024 * 1024),
                        "age_days": age_days,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "policy": policy.name,
                    })
        return files

    def enforce(self, dry_run: bool = False) -> List[Dict]:
        """Enforce retention policies. Returns list of actions taken."""
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
        return self._actions_log
