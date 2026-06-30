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

    def matches(self, entry_dict: Dict) -> bool:
        """Check if an entry matches this rule."""
        if not self.conditions:
            return False
        for field_name, pattern in self.conditions.items():
            value = str(entry_dict.get(field_name, ""))
            if pattern.lower() not in value.lower():
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
        self._rules.append(rule)
        self._rules.sort(key=lambda r: r.priority, reverse=True)
        self._tag_colors[rule.tag] = rule.color

    def remove_rule(self, name: str):
        """Remove a tagging rule by name."""
        self._rules = [r for r in self._rules if r.name != name]

    def apply_rules(self, entries: List[Dict]) -> List[Dict]:
        """Apply tagging rules to entries."""
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
        return self._manual_tags.get(line_number, set())

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

    def import_rules(self, path: str):
        """Import rules from JSON file."""
        with open(path) as f:
            data = json.load(f)
        for item in data:
            self.add_rule(TagRule(**item))
