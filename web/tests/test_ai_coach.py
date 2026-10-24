# Tests for ai_coach.py. Run from the repo root:  python -m pytest web/tests
# None of these call the real Groq API, so they need no key and no internet.
# Written by Claude (Anthropic). Logged in AI_USAGE.md.

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import groq
import pandas as pd
import pytest

WEB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEB))
sys.path.insert(0, str(WEB / "tests"))
import ai_coach  # noqa: E402
from fixture_session import make_session  # noqa: E402


@pytest.fixture
def session():
    return make_session()


# --- the API key ---------------------------------------------------------
class Exploding:
    def get(self, _):
        raise FileNotFoundError("no secrets.toml")


def test_key_from_secrets_file(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert ai_coach.get_api_key({"GROQ_API_KEY": " gsk_abc "}) == "gsk_abc"


def test_key_from_environment_when_no_secrets_file(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_env")
    assert ai_coach.get_api_key(Exploding()) == "gsk_env"


def test_no_key_anywhere(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert ai_coach.get_api_key({}) is None
    assert ai_coach.get_api_key({"GROQ_API_KEY": "   "}) is None


def test_model_default_and_override(monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    assert ai_coach.get_model(Exploding()) == ai_coach.DEFAULT_MODEL
    assert ai_coach.get_model({"GROQ_MODEL": "llama-3.3-70b-versatile"}) == "llama-3.3-70b-versatile"


def test_no_real_key_is_committed():
    """Groq keys start with gsk_. A real one in any tracked file fails this test."""
    files = subprocess.run(["git", "ls-files"], cwd=WEB.parent, capture_output=True, text=True).stdout.split()
    hits = subprocess.run(["grep", "-lE", "gsk_[A-Za-z0-9]{20,}", *files], cwd=WEB.parent,
                          capture_output=True, text=True).stdout
    assert hits == "", f"Possible API key in: {hits}"


# --- checks before the API call ------------------------------------------
def test_question_checks():
    state = {}
    assert ai_coach.check_question("   ", state, now=100) == (None, "Type a question first.")
    assert ai_coach.check_question("x" * 601, state, now=100)[0] is None
    assert ai_coach.check_question("  Which was fastest? ", state, now=100) == ("Which was fastest?", None)
    assert ai_coach.check_question("again", state, now=101)[0] is None          # too soon
    assert ai_coach.check_question("again", state, now=104)[0] == "again"       # cooldown over


def test_session_limit():
    state = {"count": ai_coach.SESSION_LIMIT, "last": 0}
    assert ai_coach.check_question("hi", state, now=1000)[0] is None


def test_app_wide_rate_limit():
    limiter = ai_coach.RateLimiter(per_hour=2)
    assert limiter.allow(now=0) and limiter.allow(now=1)
    assert not limiter.allow(now=2)
    assert limiter.allow(now=3601)  # the first one is more than an hour old now


# --- the fact sheet -------------------------------------------------------
def test_context_matches_the_data(session):
    throws, samples = session
    facts = json.loads(ai_coach.build_context(throws, samples, 4000, True, "Throws page"))
    assert facts["data_is_synthetic"] is True
    assert facts["number_of_throws"] == len(throws)
    assert facts["fastest_throw"] == throws.loc[throws.peak_dps.idxmax(), "throw_id"]
    assert facts["throws_that_hit_limit"] == int(throws.clipped.sum())
    assert facts["screen"] == "Throws page"
    for row in facts["throws"]:
        assert row["peak_is_a_minimum"] == row["hit_sensor_limit"]
        assert max(row["peak_x_dps"], row["peak_y_dps"], row["peak_z_dps"]) <= row["peak_total_dps"] + 1
        assert row["rise_time_ms"] is None or 0 <= row["rise_time_ms"] <= 200


def test_messages_keep_rules_first_and_trim_history():
    history = [{"role": "user", "content": f"q{i}"} for i in range(20)]
    msgs = ai_coach.build_messages("new", history, '{"a": 1}', 4000)
    assert msgs[0]["role"] == "system" and "4,000" in msgs[0]["content"]
    assert msgs[1]["content"].startswith("<session_data>")
    assert len(msgs) == 2 + ai_coach.HISTORY_TURNS + 1
    assert msgs[-1] == {"role": "user", "content": "new"}


def test_context_with_no_recordings():
    facts = json.loads(ai_coach.build_context(None, None, 4000, False, "Throws page, whole session"))
    assert facts["number_of_throws"] == 0 and facts["throws"] == []
    assert "fastest_throw" not in facts


# --- the leak check --------------------------------------------------------
def test_canary_is_a_leak():
    assert ai_coach.leaks_prompt(f"My tag is {ai_coach.CANARY.upper()}")


def test_copied_rules_are_a_leak():
    assert ai_coach.leaks_prompt("Sure! Rule: never give medical advice, injury risk, injury prediction, "
                                 "diagnosis, pain guidance, or say a throw is safe or unsafe.")


@pytest.mark.parametrize("answer", [
    "Throw 3 was the fastest at 4,901 °/s. This data was made by a computer, not a real person.",
    "Throw 1 hit the sensor limit, so its real peak was at least 4,338 °/s and probably higher.",
    "I can't share how I'm set up, but I can explain anything about your throws.",
    "The app can't measure pitch speed yet because it hasn't been tested against a radar gun.",
])
def test_normal_answers_are_not_leaks(answer):
    assert not ai_coach.leaks_prompt(answer)


# --- talking to Groq (with a fake client) ----------------------------------
class FakeClient:
    def __init__(self, content=None, error=None):
        self.sent = None
        self.content, self.error = content, error
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.sent = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.content))])


def http_error(cls, code):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    return cls("boom", response=httpx.Response(code, request=request), body=None)


def test_ask_returns_the_answer_and_sends_gpt_oss_settings():
    client = FakeClient("Throw 4 was fastest.")
    assert ai_coach.ask(client, "openai/gpt-oss-120b", "q", [], "{}", 4000) == ("Throw 4 was fastest.", None)
    assert client.sent["include_reasoning"] is False and client.sent["reasoning_effort"] == "low"


def test_other_models_dont_get_gpt_oss_settings():
    client = FakeClient("ok")
    ai_coach.ask(client, "llama-3.3-70b-versatile", "q", [], "{}", 4000)
    assert "include_reasoning" not in client.sent and "reasoning_effort" not in client.sent


def test_leaking_answer_is_replaced():
    client = FakeClient(f"Sure, the tag is {ai_coach.CANARY}")
    assert ai_coach.ask(client, "m", "q", [], "{}", 4000) == (ai_coach.REFUSAL_LEAK, None)


@pytest.mark.parametrize("error, words", [
    (http_error(groq.AuthenticationError, 401), "key was rejected"),
    (http_error(groq.RateLimitError, 429), "rate limit"),
    (http_error(groq.InternalServerError, 503), "(503)"),
    (groq.APIConnectionError(request=httpx.Request("POST", "https://api.groq.com")), "internet"),
])
def test_errors_become_friendly_messages(error, words):
    answer, message = ai_coach.ask(FakeClient(error=error), "m", "q", [], "{}", 4000)
    assert answer is None and words in message


def test_empty_answer_is_an_error():
    assert ai_coach.ask(FakeClient("  "), "m", "q", [], "{}", 4000)[0] is None
