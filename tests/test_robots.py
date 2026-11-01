import pytest

from greenchoice.collect.robots import Robots, robots_from_response

UA = "GreenChoice-AcademicResearch/0.1 (bitirme projesi; dusuk hizli toplama)"

# Shape of the Trendyol file read on 2026-11-02: grouped agents, wildcards, "$" anchors.
GROUPED = """# comment
User-agent: *
User-agent: Googlebot
Disallow: /*?q=
Disallow: /sr?
Disallow: /sr$
Disallow: /gw/
"""


def test_wildcard_prefix_and_end_anchor_rules():
    r = Robots.parse(GROUPED, UA)
    assert not r.allowed("/sr?q=buzdolabi")
    assert not r.allowed("/bosch/urun-p-1?q=abc")  # "/*?q=" needs wildcard support
    assert not r.allowed("/sr")                      # "/sr$"
    assert not r.allowed("/gw/api/x")
    assert r.allowed("/srx")                         # neither "/sr?" nor "/sr$"
    assert r.allowed("/bosch/urun-p-1")


def test_longest_rule_wins_and_allow_wins_ties():
    r = Robots.parse("User-agent: *\nDisallow: /a\nAllow: /a/b\nDisallow: /p\nAllow: /p\n", UA)
    assert r.allowed("/a/b/c")
    assert not r.allowed("/a/x")
    assert r.allowed("/p/anything")


def test_specific_group_beats_star_group():
    text = "User-agent: *\nAllow: /\n\nUser-agent: greenchoice-academicresearch\nDisallow: /\n"
    assert not Robots.parse(text, UA).allowed("/anything")
    assert Robots.parse(text, "SomeOtherBot/1.0").allowed("/anything")


def test_directives_are_case_insensitive_and_empty_disallow_allows_everything():
    assert Robots.parse("USER-AGENT: *\nDISALLOW:\n", UA).allowed("/x")
    assert not Robots.parse("user-agent: *\ndisallow: /private\n", UA).allowed("/private/a")


def test_no_matching_group_means_allowed():
    assert Robots.parse("User-agent: OtherBot\nDisallow: /\n", UA).allowed("/x")


@pytest.mark.parametrize("status,expected", [(200, True), (404, True), (410, True),
                                             (401, False), (403, False), (429, False), (500, False)])
def test_response_status_policy(status, expected):
    """404/410: no robots file, allowed. Anything else that is not a readable file: nothing is."""
    robots = robots_from_response(status, "User-agent: *\nDisallow: /private\n", UA)
    assert robots.allowed("/public") is expected
    if status == 200:
        assert not robots.allowed("/private")
