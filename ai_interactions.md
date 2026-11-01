# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the AI agent to review my initial implementations of `src/recommender.py`, `src/main.py`, and `tests/test_recommender.py`, fix syntax and data structure compatibility bugs, and verify that all unit tests pass.

**Prompts used:**

"recommender.py (I tried to fill it out if there are more things to add you can add to it)... main.py... test_recommender.py... Can you check these files, fix any syntax errors, and make sure the dataclass methods match what tests expect?"

**What did the agent generate or change?**

- The agent fixed a syntax error in `src/main.py` on the print statement formatting.
- It added a helper method `_song_to_dict()` inside the `Recommender` class in `src/recommender.py` to cleanly convert `Song` dataclasses into dictionaries for `score_song()`.
- It verified that `load_songs()`, `score_song()`, `recommend_songs()`, `recommend()`, and `explain_recommendation()` return expected types.

**What did you verify or fix manually?**

I manually verified that the unit tests in `tests/test_recommender.py` passed when run, confirmed that `main.py` printed formatted recommendations without errors, and filled out the project documentation templates.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

I used the Strategy Pattern / Dual Interface pattern (combining an Object-Oriented Dataclass Strategy with a Functional Scripting Strategy).

**How did AI help you brainstorm or implement it?**

The AI helped me structure `src/recommender.py` so that the core recommendation logic in `score_song()` can be executed functionally via dictionaries (used by `main.py`) or through OOP dataclasses (`Song` and `UserProfile` used by `Recommender` in `test_recommender.py`).

**How does the pattern appear in your final code?**

The pattern appears in `src/recommender.py` where the `Recommender` class encapsulates the dataclass-based strategy (`recommend()` and `explain_recommendation()`), while `recommend_songs()` acts as the functional strategy wrapper operating on raw song dictionary lists.