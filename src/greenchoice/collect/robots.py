"""robots.txt rules with wildcard support.

urllib.robotparser treats "*" and "$" in a path literally, so a rule such as
"Disallow: /*?q=" (used by Trendyol) would be ignored. This follows RFC 9309: rules match from the
start of path+query, "*" matches any characters, a trailing "$" anchors the end, the longest rule
wins, and Allow wins a tie.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    allow: bool
    pattern: str

    @property
    def regex(self) -> re.Pattern:
        anchored = self.pattern.endswith("$")
        body = self.pattern[:-1] if anchored else self.pattern
        return re.compile(".*".join(re.escape(part) for part in body.split("*"))
                          + ("$" if anchored else ""))


class Robots:
    def __init__(self, rules: list[Rule]):
        self._rules = [(rule, rule.regex) for rule in rules]

    @classmethod
    def allow_all(cls) -> Robots:
        return cls([])

    @classmethod
    def disallow_all(cls) -> Robots:
        return cls([Rule(False, "/")])

    @classmethod
    def parse(cls, text: str, user_agent: str) -> Robots:
        groups: list[tuple[list[str], list[Rule]]] = []
        agents: list[str] = []
        rules: list[Rule] = []
        collecting_agents = False
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            key = key.lower()
            if key == "user-agent":
                if not collecting_agents:
                    if agents:
                        groups.append((agents, rules))
                    agents, rules = [], []
                agents.append(value.lower())
                collecting_agents = True
            elif key in ("allow", "disallow") and agents:
                collecting_agents = False
                if value:  # an empty Disallow allows everything and adds no rule
                    rules.append(Rule(key == "allow", value))
        if agents:
            groups.append((agents, rules))
        return cls(_rules_for(groups, user_agent.lower()))

    def allowed(self, path: str) -> bool:
        """path is the URL path plus query string, e.g. "/sr?q=x"."""
        path = path if path.startswith("/") else "/" + path
        hits = [rule for rule, regex in self._rules if regex.match(path)]
        if not hits:
            return True
        best = max(hits, key=lambda r: (len(r.pattern), r.allow))
        return best.allow


def _rules_for(groups: list[tuple[list[str], list[Rule]]], user_agent: str) -> list[Rule]:
    specific = [(max(len(a) for a in agents if a != "*" and a in user_agent), rules)
                for agents, rules in groups if any(a != "*" and a in user_agent for a in agents)]
    if specific:
        best = max(score for score, _ in specific)
        return [r for score, rules in specific if score == best for r in rules]
    return [r for agents, rules in groups if "*" in agents for r in rules]


def robots_from_response(status: int, text: str, user_agent: str) -> Robots:
    """200: parse. 404/410: no robots file, everything allowed. Any other answer (403 with a
    CAPTCHA page, 429, 5xx) is not a readable policy, so nothing is fetched."""
    if status == 200:
        return Robots.parse(text, user_agent)
    if status in (404, 410):
        return Robots.allow_all()
    return Robots.disallow_all()
