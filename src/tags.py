"""Custom tag and label system for log categorization."""

import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TagRule:
    """Rule for automatically tagging log entries."""
    name: str
    tag: str
    conditions: Dict[str, str]  # field -> pattern
    color: str = "#808080"
    priority: int = 0

    def __repr__(self) -> str:
        return f"TagRule(name={self.name!r}, tag={self.tag!r}, priority={self.priority})"

    def matches(self, entry_dict: Dict) -> bool:
        """Check if an entry matches this rule.

        Args:
            entry_dict: Dictionary representation of a log entry.

        Returns:
            True if the entry matches all conditions.
        """
        if not self.conditions or not entry_dict:
            return False
        if not isinstance(entry_dict, dict):
            return False
        for field_name, pattern in self.conditions.items():
            value = entry_dict.get(field_name)
            if value is None:
                return False
            if pattern.lower() not in str(value).lower():
                return False
        return True


class TagManager:
    """Manage tags and labels for log entries."""

    def __init__(self):
        self._rules: List[TagRule] = []
        self._manual_tags: Dict[int, Set[str]] = {}  # line_number -> tags
        self._tag_colors: Dict[str, str] = {}

    def add_rule(self, rule: TagRule):
        """Add an automatic tagging rule."""
        if not rule.name or not rule.tag:
            raise ValueError("Rule must have a name and tag")
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        self._tag_colors[rule.tag] = rule.color

    def bulk_add(self, rules: List[TagRule]) -> int:
        """Add multiple rules at once. Returns count of rules added."""
        added = 0
        for rule in rules:
            try:
                self.add_rule(rule)
                added += 1
            except ValueError:
                continue
        return added

    def remove_rule(self, name: str):
        """Remove a tagging rule by name."""
        self._rules = [r for r in self._rules if r.name != name]

    def has_rule(self, name: str) -> bool:
        """Check if a rule with the given name exists."""
        return any(r.name == name for r in self._rules)

    def apply_rules(self, entries: List[Dict]) -> List[Dict]:
        """Apply tagging rules to entries.

        Args:
            entries: List of entry dictionaries to tag.

        Returns:
            The same list with tags applied to each entry.

        Raises:
            TypeError: If entries is not a list.
        """
        if not entries:
            return []
        if not isinstance(entries, list):
            raise TypeError("entries must be a list")
        for entry in entries:
            line_num = entry.get("line_number", 0)
            tags = set(entry.get("tags", []))

            for rule in self._rules:
                if rule.matches(entry):
                    tags.add(rule.tag)

            entry["tags"] = list(tags)
        return entries

    def add_manual_tag(self, line_number: int, tag: str):
        """Manually add a tag to an entry."""
        if line_number not in self._manual_tags:
            self._manual_tags[line_number] = set()
        self._manual_tags[line_number].add(tag)

    def remove_manual_tag(self, line_number: int, tag: str):
        """Remove a manual tag."""
        if line_number in self._manual_tags:
            self._manual_tags[line_number].discard(tag)

    def get_tags(self, line_number: int) -> Set[str]:
        """Get all tags for an entry."""
        return set(self._manual_tags.get(line_number, set()))

    def get_all_tags(self) -> Dict[str, int]:
        """Get all tags with their counts."""
        counts: Dict[str, int] = {}
        for tags in self._manual_tags.values():
            for tag in tags:
                counts[tag] = counts.get(tag, 0) + 1
        return counts

    def get_color(self, tag: str) -> str:
        """Get color for a tag."""
        return self._tag_colors.get(tag, "#808080")

    def reset(self):
        """Clear all rules, manual tags, and color mappings."""
        self._rules.clear()
        self._manual_tags.clear()
        self._tag_colors.clear()

    @property
    def rule_count(self) -> int:
        """Get number of registered rules."""
        return len(self._rules)

    @property
    def tag_count(self) -> int:
        """Get total number of manual tags applied."""
        return sum(len(tags) for tags in self._manual_tags.values())

    def export_rules(self, path: str):
        """Export rules to JSON file."""
        data = [
            {"name": r.name, "tag": r.tag, "conditions": r.conditions,
             "color": r.color, "priority": r.priority}
            for r in self._rules
        ]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def import_rules(self, path: str) -> int:
        """Import rules from JSON file.

        Args:
            path: Path to the JSON rules file.

        Returns:
            Number of rules successfully imported.

        Raises:
            ValueError: If file cannot be read or parsed.
        """
        try:
            with open(path) as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to import rules: {e}")
        if not isinstance(data, list):
            raise ValueError("Rules file must contain a JSON array")
        imported = 0
        for item in data:
            try:
                self.add_rule(TagRule(**item))
                imported += 1
            except (TypeError, ValueError):
                continue
        return imported
