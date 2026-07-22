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

    def get_rules(self) -> List[Dict]:
        """Get all rules as dictionaries.

        Returns:
            List of rule dictionaries.
        """
        return [
            {"name": r.name, "tag": r.tag, "conditions": r.conditions,
             "color": r.color, "priority": r.priority}
            for r in self._rules
        ]

    def clear_manual_tags(self):
        """Clear all manual tags while keeping rules."""
        self._manual_tags.clear()

    def get_tags_for_entry(self, entry_dict: Dict) -> List[str]:
        """Get all matching tags for an entry without applying them.

        Args:
            entry_dict: Entry dictionary to check.

        Returns:
            List of matching tag names.
        """
        tags = []
        for rule in self._rules:
            if rule.matches(entry_dict):
                tags.append(rule.tag)
        return tags

    def remove_rule_by_tag(self, tag: str) -> int:
        """Remove all rules that produce a specific tag.

        Args:
            tag: Tag name to remove rules for.

        Returns:
            Number of rules removed.
        """
        before = len(self._rules)
        self._rules = [r for r in self._rules if r.tag != tag]
        return before - len(self._rules)

    def get_all_tag_names(self) -> List[str]:
        """Get list of all unique tag names from rules.

        Returns:
            List of tag names.
        """
        return list(set(r.tag for r in self._rules))

    def get_rules_by_priority(self, min_priority: int = 0) -> List[Dict]:
        """Get rules filtered by minimum priority.

        Args:
            min_priority: Minimum priority level.

        Returns:
            List of rule dictionaries.
        """
        return [
            {"name": r.name, "tag": r.tag, "conditions": r.conditions,
             "color": r.color, "priority": r.priority}
            for r in self._rules if r.priority >= min_priority
        ]

    def has_manual_tags(self) -> bool:
        """Check if any manual tags exist.

        Returns:
            True if manual tags are present.
        """
        return len(self._manual_tags) > 0

    def has_rules(self) -> bool:
        """Check if any rules are configured.

        Returns:
            True if rules exist.
        """
        return len(self._rules) > 0

    def has_tag(self, tag: str) -> bool:
        """Check if a tag exists in any rule.

        Args:
            tag: Tag name to check.

        Returns:
            True if tag exists.
        """
        return any(r.tag == tag for r in self._rules)

    def get_rule_by_name(self, name: str) -> Optional[Dict]:
        """Get a rule by name.

        Args:
            name: Rule name.

        Returns:
            Rule dictionary if found, None otherwise.
        """
        for rule in self._rules:
            if rule.name == name:
                return {
                    "name": rule.name,
                    "tag": rule.tag,
                    "conditions": rule.conditions,
                    "color": rule.color,
                    "priority": rule.priority,
                }
        return None

    def get_manual_tag_count(self) -> int:
        """Get number of manual tags.

        Returns:
            Count of manual tags.
        """
        return sum(len(tags) for tags in self._manual_tags.values())

    def get_rule_count(self) -> int:
        """Get number of rules.

        Returns:
            Count of rules.
        """
        return len(self._rules)

    def get_rules_dict(self) -> List[Dict[str, Any]]:
        """Get all rules as dictionaries.

        Returns:
            List of rule dictionaries.
        """
        return [
            {
                "name": r.name,
                "tag": r.tag,
                "conditions": r.conditions,
                "color": r.color,
                "priority": r.priority,
            }
            for r in self._rules
        ]

    def get_stats_dict(self) -> Dict[str, Any]:
        """Get tag manager statistics as dictionary.

        Returns:
            Dictionary with tag stats.
        """
        return {
            "rules": len(self._rules),
            "manual_tags": self.get_manual_tag_count(),
            "unique_tags": len(self.get_all_tag_names()),
        }

    def has_tags(self) -> bool:
        """Check if any tags exist (rules or manual).

        Returns:
            True if tags exist.
        """
        return len(self._rules) > 0 or len(self._manual_tags) > 0

    def get_rule_count_formatted(self) -> str:
        """Get formatted rule count string.

        Returns:
            Formatted rule count string.
        """
        return f"{self.get_rule_count()} rules"

    def get_manual_tag_count_formatted(self) -> str:
        """Get formatted manual tag count string.

        Returns:
            Formatted manual tag count string.
        """
        return f"{self.get_manual_tag_count()} manual tags"

    def get_unique_tag_count_formatted(self) -> str:
        """Get formatted unique tag count string.

        Returns:
            Formatted unique tag count string.
        """
        return f"{len(self.get_all_tag_names())} unique tags"

    def get_tag_names_formatted(self) -> str:
        """Get formatted tag names string.

        Returns:
            Formatted tag names string.
        """
        names = self.get_all_tag_names()
        if not names:
            return "none"
        return ", ".join(names)

    def get_rule_names_formatted(self) -> str:
        """Get formatted rule names string.

        Returns:
            Formatted rule names string.
        """
        names = [r.name for r in self._rules]
        if not names:
            return "none"
        return ", ".join(names)

    def get_average_priority(self) -> float:
        """Get average rule priority.

        Returns:
            Average priority.
        """
        if not self._rules:
            return 0.0
        return round(sum(r.priority for r in self._rules) / len(self._rules), 2)

    def get_average_priority_formatted(self) -> str:
        """Get formatted average priority string.

        Returns:
            Formatted average priority string.
        """
        return f"avg priority: {self.get_average_priority():.2f}"

    def get_stats_formatted(self) -> str:
        """Get formatted stats string.

        Returns:
            Formatted stats string.
        """
        return f"Rules: {len(self._rules)}, Manual Tags: {self.get_manual_tag_count()}, Unique Tags: {len(self.get_all_tag_names())}"

    def get_rules_by_priority_formatted(self, min_priority: int = 0) -> str:
        """Get formatted rules by priority string.

        Args:
            min_priority: Minimum priority level.

        Returns:
            Formatted rules by priority string.
        """
        rules = self.get_rules_by_priority(min_priority)
        if not rules:
            return "none"
        return ", ".join(f"{r['name']}({r['priority']})" for r in rules)

    def get_manual_tags_formatted(self) -> str:
        """Get formatted manual tags string.

        Returns:
            Formatted manual tags string.
        """
        if not self._manual_tags:
            return "none"
        all_tags = set()
        for tags in self._manual_tags.values():
            all_tags.update(tags)
        return ", ".join(sorted(all_tags)) if all_tags else "none"

    def get_rule_count_by_priority(self, min_priority: int = 0) -> int:
        """Get count of rules by minimum priority.

        Args:
            min_priority: Minimum priority level.

        Returns:
            Count of rules.
        """
        return len(self.get_rules_by_priority(min_priority))
