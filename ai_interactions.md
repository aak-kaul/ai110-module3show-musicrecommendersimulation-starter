# AI Interactions Log

This file documents how I used an AI assistant for the stretch features. The prompts below are the ones I used, shortened where noted.

---

## Agentic Workflow: Additional Song Attributes (SF8)

**What task did you give the agent?**

I asked the agent to add five or more new attributes to the song dataset and update the scoring logic so it uses them, without breaking the existing tests or the `Song` and `UserProfile` dataclasses.

**Prompts used:**

> "Add 5+ new song attributes to songs.csv (for example popularity 0-100, release decade, detailed mood tags, instrumentalness, and language) for all songs, and expand the catalog to around 30 songs with more genres and moods. Update load_songs and score_song so each new attribute is actually used in scoring. The new user preferences should be optional so my existing profiles and tests still work."

> "Make sure every score still comes with a list of reasons, and that the reasons mention the new attributes when they fire."

**What did the agent generate or change?**

- Expanded `data/songs.csv` from 20 to **30 songs** and added a header with all 15 columns. In the original file, ten rows had extra `popularity` and `decade` values with no header names, so `csv.DictReader` was silently dropping them. The agent fixed the header and filled in the missing values for the first ten songs.
- Added **five new attributes:** `popularity` (0-100), `decade`, `detailed_mood`, `instrumentalness` (0-1), and `language`.
- Updated `load_songs()` to read the new columns, to default them when they are missing (so an older CSV still loads), and to raise a clear error that names the CSV line when a row is bad.
- Updated `score_song()` so each new attribute is scored when the user sets a preference for it: detailed mood match (+0.75), decade match (+0.5), popularity closeness (up to +0.5), instrumentalness closeness (up to +0.5), and language match (+0.4). Each one adds its own entry to the reasons list.
- Added the new fields to the `Song` and `UserProfile` dataclasses **with default values**, so the original two tests still construct objects the same way.
- Added tests that check the new columns load and that scores stay numeric for every song and mode.

**What did you verify or fix manually?**

- I ran the full test suite after the change and checked that the original two tests still passed unchanged.
- I added up one score by hand: *Library Rain* for the Lofi profile in Balanced mode is 2.00 + 1.00 + 1.425 + 0.50 + 0.75 + 0.475 = 6.15, which matches the program output.
- I read the reasons text for each profile in `main.py`'s output to make sure the new attributes show up only when the profile asks for them (for example, the EDM profile never shows a "dreamy" reason).
- I checked that I understood the limit of this data: the new attribute values are invented for this simulation, not real streaming data, and I wrote that in the model card.

---

## Design Pattern: Multiple Ranking Modes (SF10)

**Which design pattern did you use?**

The **Strategy pattern**. Each ranking mode is a small `RankingMode` object that holds a set of weights. They are all kept in one `RANKING_MODES` dictionary, and the scoring code works with whichever one is picked.

**How did AI help you brainstorm or implement it?**

I asked the AI for a simple way to switch between ranking strategies in `main.py` without copying the scoring function.

> "Attach recommender.py. Brainstorm a simple Strategy-style design so I can have Genre-First, Mood-First, and Energy-Similarity ranking modes, and switch between them from main.py, without duplicating score_song."

The AI suggested two options: (1) a separate function or class for every mode, or (2) one scoring function that takes a "weights" object. I **chose option 2** and rejected the one-class-per-mode version, because the modes only differ in their weights and separate classes would repeat almost all of the same code. The AI also suggested a frozen dataclass for the weights, which I kept because it prevents a mode from being changed by accident while the program runs.

**How does the pattern appear in your final code?**

- `RankingMode` (a frozen dataclass) in `src/recommender.py` holds the weights for each feature.
- `RANKING_MODES` maps a mode name to its `RankingMode`, and `get_mode()` returns a clear error for an unknown name.
- `score_song(user_prefs, song, mode)` and `recommend_songs(..., mode=...)` take the mode name and read the weights from the registry.
- In `src/main.py`, every profile has its own `mode`, and I can override it for all profiles from the command line: `python -m src.main --mode Mood-First`.
- Adding a new mode is a single line in `RANKING_MODES`. I added `Weight-Shift` this way for my sensitivity experiment.

I also kept a thin `Recommender` class (with `recommend()` and `explain_recommendation()`) that wraps the same functions, so the dataclass-based tests and the dictionary-based CLI share the exact same scoring logic.

---

## Other AI Notes

**Diversity penalty (artist repeat).** The first version I got from the AI sorted all songs once and then applied the penalty while walking down the sorted list. That could leave a song that had been penalized in the wrong position, so I asked for it to be changed to pick songs one at a time and re-check the penalty each time. I verified it using the EDM profile, where *Pulse Garden* drops out of the top 5 because its artist already has the #1 pick.

**Visual table.** I asked for a `tabulate` table that shows the reasons for every song. The first version turned scores like `5.00` into `5` and `3.80` into `3.8`, so I turned off number parsing so the scores print with two decimals.

**Dependencies.** The original `requirements.txt` did not include `tabulate`, which `main.py` imports, so I added it.
