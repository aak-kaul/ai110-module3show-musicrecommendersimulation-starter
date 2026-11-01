# 🎵 Music Recommender Simulation

## Project Summary

I built a small, explainable, content-based music recommender in Python. It loads a 30-song catalog from a CSV, scores every song against a user's taste profile, ranks the songs, and prints the top results in a table with the exact reasons for each score. I extended the starter project with extra song attributes, five ranking modes I can switch between, an artist-repeat penalty, and a formatted results table.

**Base files:** `src/recommender.py` (logic), `src/main.py` (CLI), `data/songs.csv` (catalog), `tests/test_recommender.py` (tests), `model_card.md` (model card), `ai_interactions.md` (AI workflow log).

---

## How Real-World Recommenders Work

Big platforms like Spotify, YouTube, and TikTok mostly combine two ideas:

- **Collaborative filtering** uses the behavior of lots of users. If people who like the same songs as me also love a track I have not heard, that track becomes a candidate for me. It does not need to know anything about the song itself, only who interacted with it.
- **Content-based filtering** uses the attributes of the items. If I keep playing high-energy, fast songs, the system looks for other songs with similar attributes (genre, mood, tempo, energy, acousticness, and so on).

**Input data** is what the system collects: song features (tempo, energy, genre, mood, audio analysis) and behavior signals (likes, skips, replays, playlist adds, listening time, searches). **User preferences** are what the system infers from that data, such as "this person likes upbeat pop and skips slow songs." **Ranking/selection** is the last step: the system scores a large pool of candidate songs against the user's preferences and then sorts them and shows the top few. Real platforms usually generate candidates first and then rank them with a trained model, and they also add rules for variety.

**My version** is content-based only. I have no other users, so I cannot do collaborative filtering. Instead, my "user history" is a hand-written taste profile. It keeps the three steps separate: songs in `songs.csv` are the **input data**, a profile dictionary is the **user preference**, and `score_song()` plus `recommend_songs()` handle **ranking**. My system prioritizes genre and mood matches, then how close a song's energy is to what the user wants, with small bonuses for the other attributes.

---

## How The System Works

### Features I use

**Song features** (from `data/songs.csv`):
- Starter attributes: `genre`, `mood`, `energy` (0-1), `tempo_bpm`, `valence`, `danceability`, `acousticness` (0-1)
- Five extended attributes I added: `popularity` (0-100), `decade`, `detailed_mood` (like "nostalgic" or "euphoric"), `instrumentalness` (0-1), and `language`

**User profile features** (a dictionary, or the `UserProfile` dataclass): `genre`, `mood`, `energy`, `likes_acoustic`, plus optional `decade`, `detailed_mood`, `popularity`, `instrumentalness`, `language`, and `tempo`. Optional preferences are only scored when they are set.

### Algorithm recipe (Balanced mode)

`score_song()` judges one song at a time:

| Rule | Points |
|---|---|
| Genre matches | +2.0 |
| Mood matches | +1.0 |
| Energy closeness | up to +1.5, calculated as `1.5 × (1 − |target − song energy|)` |
| Acoustic taste agrees with the song (acousticness > 0.6 counts as acoustic) | +0.5 |
| Detailed mood matches | +0.75 |
| Decade matches | +0.5 |
| Popularity closeness | up to +0.5 |
| Instrumentalness closeness | up to +0.5 |
| Language matches | +0.4 |
| Tempo closeness (within 60 BPM) | up to +0.5 |

Energy is scored by closeness rather than "higher is better," so a user who wants 0.30 energy is not pushed toward loud songs. Every rule that fires adds a human-readable reason like `genre match (+2.00)`.

`recommend_songs()` judges the whole list. It scores every song, picks the best one, then picks again, and so on until it has `k` songs. We need both functions because scoring answers "how good is this one song for this user?" and ranking answers "which songs do I actually show?"

### Ranking modes (Strategy pattern)

Each mode is a `RankingMode` object that holds a set of weights, and `score_song()` just reads whichever one I pass in. Adding a new mode takes one line.

| Mode | Genre | Mood | Energy |
|---|---|---|---|
| Balanced (default) | 2.0 | 1.0 | 1.5 |
| Genre-First | 3.0 | 0.5 | 1.0 |
| Mood-First | 1.0 | 3.0 | 1.0 |
| Energy-Similarity | 0.5 | 0.5 | 3.0 |
| Weight-Shift (experiment) | 1.0 | 1.0 | 3.0 |

### Fairness and diversity: artist penalty

When a song's artist already has a song in the picks, each remaining song by that artist loses **0.75 points per earlier pick**. This stops one artist from filling the whole top 5 and helps other artists get heard.

### Biases I expect

- Genre and mood are exact matches, so "chill" and "relaxed" count as totally different moods even though they feel similar.
- The catalog is tiny (30 songs, most genres have one to three songs), so niche genres get few or no good matches.
- The acoustic bonus is easy to earn for users who do *not* like acoustic music, because most songs in the catalog are not acoustic.

---

## Getting Started

### Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Run

From the project root:

```bash
python -m src.main                      # each profile uses its own ranking mode
python -m src.main --mode Mood-First    # force one ranking mode for every profile
python -m src.main --experiment         # also run the weight-shift experiment
```

### Test

```bash
pytest
```

---

## Sample Recommendation Output

This is the real output of `python -m src.main` (top 5 for each profile, with the reasons for each score):

```text
Loaded songs: 30
```

#### High-Energy Pop Fan (Genre-First)

```text
====================================================================================================
 PROFILE: High-Energy Pop Fan | Ranking mode: Genre-First
 Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.85, 'likes_acoustic': False, 'decade': '2020s', 'popularity': 85}
====================================================================================================
╒════════╤════════════════╤═════════════╤═════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title          │ Artist      │ Genre   │ Score   │ Reasons                                                      │
╞════════╪════════════════╪═════════════╪═════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Sunrise City   │ Neon Echo   │ pop     │ 5.97    │ genre match (+3.00), mood match (+0.50), energy proximity    │
│        │                │             │         │         │ (+0.97), acoustic match (+0.50), 2020s era match (+0.50),    │
│        │                │             │         │         │ popularity proximity (+0.50)                                 │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Stadium Lights │ Max Pulse   │ pop     │ 5.43    │ genre match (+3.00), energy proximity (+0.97), acoustic      │
│        │                │             │         │         │ match (+0.50), 2020s era match (+0.50), popularity proximity │
│        │                │             │         │         │ (+0.46)                                                      │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Gym Hero       │ Max Pulse   │ pop     │ 4.64    │ genre match (+3.00), energy proximity (+0.92), acoustic      │
│        │                │             │         │         │ match (+0.50), 2020s era match (+0.50), popularity proximity │
│        │                │             │         │         │ (+0.47), artist repeat penalty (-0.75)                       │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Pulse Garden   │ Cyber Pulse │ edm     │ 2.92    │ mood match (+0.50), energy proximity (+0.95), acoustic match │
│        │                │             │         │         │ (+0.50), 2020s era match (+0.50), popularity proximity       │
│        │                │             │         │         │ (+0.47)                                                      │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Samba Sol      │ Rio Rhythm  │ latin   │ 2.44    │ mood match (+0.50), energy proximity (+0.96), acoustic match │
│        │                │             │         │         │ (+0.50), popularity proximity (+0.48)                        │
╘════════╧════════════════╧═════════════╧═════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

#### Lofi & Acoustic Chill Listener (Balanced)

```text
====================================================================================================
 PROFILE: Lofi & Acoustic Chill Listener | Ranking mode: Balanced
 Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.3, 'likes_acoustic': True, 'detailed_mood': 'dreamy', 'instrumentalness': 0.85}
====================================================================================================
╒════════╤════════════════════╤════════════════╤═════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title              │ Artist         │ Genre   │ Score   │ Reasons                                                      │
╞════════╪════════════════════╪════════════════╪═════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Library Rain       │ Paper Lanterns │ lofi    │ 6.15    │ genre match (+2.00), mood match (+1.00), energy proximity    │
│        │                    │                │         │         │ (+1.42), acoustic match (+0.50), 'dreamy' vibe match         │
│        │                    │                │         │         │ (+0.75), instrumental proximity (+0.47)                      │
├────────┼────────────────────┼────────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Midnight Coding    │ LoRoom         │ lofi    │ 5.32    │ genre match (+2.00), mood match (+1.00), energy proximity    │
│        │                    │                │         │         │ (+1.32), acoustic match (+0.50), instrumental proximity      │
│        │                    │                │         │         │ (+0.50)                                                      │
├────────┼────────────────────┼────────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Spacewalk Thoughts │ Orbit Bloom    │ ambient │ 4.17    │ mood match (+1.00), energy proximity (+1.47), acoustic match │
│        │                    │                │         │         │ (+0.50), 'dreamy' vibe match (+0.75), instrumental proximity │
│        │                    │                │         │         │ (+0.45)                                                      │
├────────┼────────────────────┼────────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Focus Flow         │ LoRoom         │ lofi    │ 3.58    │ genre match (+2.00), energy proximity (+1.35), acoustic      │
│        │                    │                │         │         │ match (+0.50), instrumental proximity (+0.48), artist repeat │
│        │                    │                │         │         │ penalty (-0.75)                                              │
├────────┼────────────────────┼────────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Midnight Jazz Jam  │ Miles Drift    │ jazz    │ 3.37    │ mood match (+1.00), energy proximity (+1.47), acoustic match │
│        │                    │                │         │         │ (+0.50), instrumental proximity (+0.40)                      │
╘════════╧════════════════════╧════════════════╧═════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

#### High-Tempo EDM Vibe Chaser (Energy-Similarity)

```text
====================================================================================================
 PROFILE: High-Tempo EDM Vibe Chaser | Ranking mode: Energy-Similarity
 Preferences: {'genre': 'edm', 'mood': 'energetic', 'energy': 0.95, 'likes_acoustic': False, 'tempo': 128}
====================================================================================================
╒════════╤══════════════════╤═════════════╤═══════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title            │ Artist      │ Genre     │ Score   │ Reasons                                                      │
╞════════╪══════════════════╪═════════════╪═══════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Electric Thunder │ Cyber Pulse │ edm       │ 5.00    │ genre match (+0.50), mood match (+0.50), energy proximity    │
│        │                  │             │           │         │ (+3.00), acoustic match (+0.50), tempo proximity (+0.50)     │
├────────┼──────────────────┼─────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Stadium Lights   │ Max Pulse   │ pop       │ 4.29    │ mood match (+0.50), energy proximity (+2.79), acoustic match │
│        │                  │             │           │         │ (+0.50), tempo proximity (+0.50)                             │
├────────┼──────────────────┼─────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Neon Skyline     │ Retro Wave  │ synthwave │ 4.24    │ mood match (+0.50), energy proximity (+2.79), acoustic match │
│        │                  │             │           │         │ (+0.50), tempo proximity (+0.45)                             │
├────────┼──────────────────┼─────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Samba Sol        │ Rio Rhythm  │ latin     │ 3.80    │ energy proximity (+2.82), acoustic match (+0.50), tempo      │
│        │                  │             │           │         │ proximity (+0.48)                                            │
├────────┼──────────────────┼─────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Storm Runner     │ Voltline    │ rock      │ 3.68    │ energy proximity (+2.88), acoustic match (+0.50), tempo      │
│        │                  │             │           │         │ proximity (+0.30)                                            │
╘════════╧══════════════════╧═════════════╧═══════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

#### Hip-Hop Head (Mood-First)

```text
====================================================================================================
 PROFILE: Hip-Hop Head | Ranking mode: Mood-First
 Preferences: {'genre': 'hip-hop', 'mood': 'intense', 'energy': 0.8, 'likes_acoustic': False, 'decade': '2010s', 'language': 'english'}
====================================================================================================
╒════════╤═════════════════════╤═══════════════╤═════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title               │ Artist        │ Genre   │ Score   │ Reasons                                                      │
╞════════╪═════════════════════╪═══════════════╪═════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Concrete Crown      │ Lyric Kane    │ hip-hop │ 6.40    │ genre match (+1.00), mood match (+3.00), energy proximity    │
│        │                     │               │         │         │ (+1.00), acoustic match (+0.50), 2010s era match (+0.50),    │
│        │                     │               │         │         │ english language match (+0.40)                               │
├────────┼─────────────────────┼───────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Storm Runner        │ Voltline      │ rock    │ 5.29    │ mood match (+3.00), energy proximity (+0.89), acoustic match │
│        │                     │               │         │         │ (+0.50), 2010s era match (+0.50), english language match     │
│        │                     │               │         │         │ (+0.40)                                                      │
├────────┼─────────────────────┼───────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Gym Hero            │ Max Pulse     │ pop     │ 4.77    │ mood match (+3.00), energy proximity (+0.87), acoustic match │
│        │                     │               │         │         │ (+0.50), english language match (+0.40)                      │
├────────┼─────────────────────┼───────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Shadows in the Mist │ Obsidian Void │ metal   │ 4.76    │ mood match (+3.00), energy proximity (+0.86), acoustic match │
│        │                     │               │         │         │ (+0.50), english language match (+0.40)                      │
├────────┼─────────────────────┼───────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Late Night Verses   │ Lyric Kane    │ hip-hop │ 2.40    │ genre match (+1.00), energy proximity (+0.75), acoustic      │
│        │                     │               │         │         │ match (+0.50), 2010s era match (+0.50), english language     │
│        │                     │               │         │         │ match (+0.40), artist repeat penalty (-0.75)                 │
╘════════╧═════════════════════╧═══════════════╧═════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

#### Edge Case: Sad but Very High Energy (Balanced)

```text
====================================================================================================
 PROFILE: Adversarial: Sad but Very High Energy | Ranking mode: Balanced
 Preferences: {'genre': 'rock', 'mood': 'sad', 'energy': 0.9, 'likes_acoustic': False}
====================================================================================================
╒════════╤══════════════╤══════════════╤═══════════╤═════════╤═══════════════════════════════════════════════════════════╕
│ Rank   │ Title        │ Artist       │ Genre     │ Score   │ Reasons                                                   │
╞════════╪══════════════╪══════════════╪═══════════╪═════════╪═══════════════════════════════════════════════════════════╡
│ 1      │ Broken Radio │ Hollow Teeth │ rock      │ 4.55    │ genre match (+2.00), mood match (+1.00), energy proximity │
│        │              │              │           │         │ (+1.05), acoustic match (+0.50)                           │
├────────┼──────────────┼──────────────┼───────────┼─────────┼───────────────────────────────────────────────────────────┤
│ 2      │ Storm Runner │ Voltline     │ rock      │ 3.98    │ genre match (+2.00), energy proximity (+1.48), acoustic   │
│        │              │              │           │         │ match (+0.50)                                             │
├────────┼──────────────┼──────────────┼───────────┼─────────┼───────────────────────────────────────────────────────────┤
│ 3      │ Pulse Garden │ Cyber Pulse  │ edm       │ 2.00    │ energy proximity (+1.50), acoustic match (+0.50)          │
├────────┼──────────────┼──────────────┼───────────┼─────────┼───────────────────────────────────────────────────────────┤
│ 4      │ Samba Sol    │ Rio Rhythm   │ latin     │ 1.98    │ energy proximity (+1.48), acoustic match (+0.50)          │
├────────┼──────────────┼──────────────┼───────────┼─────────┼───────────────────────────────────────────────────────────┤
│ 5      │ Neon Skyline │ Retro Wave   │ synthwave │ 1.97    │ energy proximity (+1.47), acoustic match (+0.50)          │
╘════════╧══════════════╧══════════════╧═══════════╧═════════╧═══════════════════════════════════════════════════════════╛
```

#### Edge Case: Genre Not in Catalog (Balanced)

```text
====================================================================================================
 PROFILE: Adversarial: Genre Not in Catalog (k-pop) | Ranking mode: Balanced
 Preferences: {'genre': 'k-pop', 'mood': 'happy', 'energy': 0.8, 'likes_acoustic': False}
====================================================================================================
╒════════╤════════════════╤═══════════════╤═══════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title          │ Artist        │ Genre     │ Score   │ Reasons                                                      │
╞════════╪════════════════╪═══════════════╪═══════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Sunrise City   │ Neon Echo     │ pop       │ 2.97    │ mood match (+1.00), energy proximity (+1.47), acoustic match │
│        │                │               │           │         │ (+0.50)                                                      │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Rooftop Lights │ Indigo Parade │ indie pop │ 2.94    │ mood match (+1.00), energy proximity (+1.44), acoustic match │
│        │                │               │           │         │ (+0.50)                                                      │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Samba Sol      │ Rio Rhythm    │ latin     │ 2.87    │ mood match (+1.00), energy proximity (+1.36), acoustic match │
│        │                │               │           │         │ (+0.50)                                                      │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Pulse Garden   │ Cyber Pulse   │ edm       │ 2.85    │ mood match (+1.00), energy proximity (+1.35), acoustic match │
│        │                │               │           │         │ (+0.50)                                                      │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Concrete Crown │ Lyric Kane    │ hip-hop   │ 2.00    │ energy proximity (+1.50), acoustic match (+0.50)             │
╘════════╧════════════════╧═══════════════╧═══════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

### Explanations for specific recommendations

1. **Sunrise City ranked #1 for the High-Energy Pop Fan (5.97).** It is a pop song (+3.00 genre match in Genre-First mode) with a "happy" mood (+0.50). Its energy of 0.82 is very close to the 0.85 target (+0.97), it is not acoustic like the user wants (+0.50), it is from the 2020s (+0.50), and its popularity of 85 matches the user's target (+0.50).
2. **Library Rain ranked #1 for the Lofi Listener (6.15).** It matches the lofi genre (+2.00) and the chill mood (+1.00). Its energy of 0.35 is close to the 0.30 target (+1.42), it is acoustic (+0.50), it has the "dreamy" tag the user asked for (+0.75), and it is mostly instrumental (+0.47).
3. **Storm Runner ranked #2 for the Hip-Hop Head (5.29) even though it is rock.** In Mood-First mode, its "intense" mood match is worth +3.00. It also matches on energy (+0.89), is not acoustic (+0.50), is from the 2010s (+0.50), and is in English (+0.40). Genre was not enough to win, so a rock song beat a hip-hop song.
4. **Pulse Garden dropped out of the EDM profile's top 5.** It is an EDM song with very high energy, but it is by Cyber Pulse, the same artist as the #1 pick (Electric Thunder). The artist repeat penalty (-0.75) pushed it below Storm Runner (3.68), so the user gets a wider mix of artists.
5. **Gym Hero ranked #3 for the Pop Fan (4.64).** Its mood is "intense," not "happy," so it does not get the mood bonus. It still ranks high because it is pop (+3.00) and its energy of 0.93 is close to the target. It also lost 0.75 for being the second Max Pulse song in the list.

---

## Experiments

### Experiment 1: Different user profiles

I ran four normal profiles and two edge-case profiles. The differences between them are explained in more detail in `model_card.md`, and the short version is:

- **Pop Fan vs. Lofi Listener:** these two share no songs. The pop profile pulls toward 0.8-0.9 energy and non-acoustic tracks, while the lofi profile shifts to low-energy, acoustic, instrumental tracks.
- **Pop Fan vs. EDM Chaser:** both want high energy, so they share Stadium Lights and Samba Sol. The pop profile puts pop songs first because Genre-First counts genre, while the EDM profile is in Energy-Similarity mode and ranks by closeness to 0.95 energy regardless of genre.
- **EDM Chaser vs. Hip-Hop Head:** they only share Storm Runner. The EDM profile likes it for its energy, and the hip-hop profile likes it for its "intense" mood.
- **Edge case, sad but high energy:** the only song that is both rock and sad is Broken Radio, so it wins. After the top 2 rock songs, the list is just the highest-energy songs, since no sad song in the catalog has high energy.
- **Edge case, genre not in the catalog:** with no k-pop songs, no song gets a genre bonus, and the recommender falls back to mood and energy. It still returns a sensible list, but genre is clearly the feature that separates users most.

### Experiment 2: Weight shift (energy doubled, genre halved)

I compared Balanced (genre 2.0, energy 1.5) against Weight-Shift (genre 1.0, energy 3.0) for the same Pop Fan profile. I did not change the profile, only the weights.

```text
====================================================================================================
 PROFILE: High-Energy Pop Fan | Ranking mode: Balanced
 Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.85, 'likes_acoustic': False, 'decade': '2020s', 'popularity': 85}
====================================================================================================
╒════════╤════════════════╤═════════════╤═════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title          │ Artist      │ Genre   │ Score   │ Reasons                                                      │
╞════════╪════════════════╪═════════════╪═════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Sunrise City   │ Neon Echo   │ pop     │ 5.96    │ genre match (+2.00), mood match (+1.00), energy proximity    │
│        │                │             │         │         │ (+1.46), acoustic match (+0.50), 2020s era match (+0.50),    │
│        │                │             │         │         │ popularity proximity (+0.50)                                 │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Stadium Lights │ Max Pulse   │ pop     │ 4.92    │ genre match (+2.00), energy proximity (+1.46), acoustic      │
│        │                │             │         │         │ match (+0.50), 2020s era match (+0.50), popularity proximity │
│        │                │             │         │         │ (+0.46)                                                      │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Gym Hero       │ Max Pulse   │ pop     │ 4.10    │ genre match (+2.00), energy proximity (+1.38), acoustic      │
│        │                │             │         │         │ match (+0.50), 2020s era match (+0.50), popularity proximity │
│        │                │             │         │         │ (+0.47), artist repeat penalty (-0.75)                       │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Pulse Garden   │ Cyber Pulse │ edm     │ 3.89    │ mood match (+1.00), energy proximity (+1.42), acoustic match │
│        │                │             │         │         │ (+0.50), 2020s era match (+0.50), popularity proximity       │
│        │                │             │         │         │ (+0.47)                                                      │
├────────┼────────────────┼─────────────┼─────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Samba Sol      │ Rio Rhythm  │ latin   │ 3.42    │ mood match (+1.00), energy proximity (+1.44), acoustic match │
│        │                │             │         │         │ (+0.50), popularity proximity (+0.48)                        │
╘════════╧════════════════╧═════════════╧═════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

```text
====================================================================================================
 PROFILE: High-Energy Pop Fan | Ranking mode: Weight-Shift
 Preferences: {'genre': 'pop', 'mood': 'happy', 'energy': 0.85, 'likes_acoustic': False, 'decade': '2020s', 'popularity': 85}
====================================================================================================
╒════════╤════════════════╤═══════════════╤═══════════╤═════════╤══════════════════════════════════════════════════════════════╕
│ Rank   │ Title          │ Artist        │ Genre     │ Score   │ Reasons                                                      │
╞════════╪════════════════╪═══════════════╪═══════════╪═════════╪══════════════════════════════════════════════════════════════╡
│ 1      │ Sunrise City   │ Neon Echo     │ pop       │ 6.41    │ genre match (+1.00), mood match (+1.00), energy proximity    │
│        │                │               │           │         │ (+2.91), acoustic match (+0.50), 2020s era match (+0.50),    │
│        │                │               │           │         │ popularity proximity (+0.50)                                 │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 2      │ Stadium Lights │ Max Pulse     │ pop       │ 5.38    │ genre match (+1.00), energy proximity (+2.91), acoustic      │
│        │                │               │           │         │ match (+0.50), 2020s era match (+0.50), popularity proximity │
│        │                │               │           │         │ (+0.46)                                                      │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 3      │ Pulse Garden   │ Cyber Pulse   │ edm       │ 5.32    │ mood match (+1.00), energy proximity (+2.85), acoustic match │
│        │                │               │           │         │ (+0.50), 2020s era match (+0.50), popularity proximity       │
│        │                │               │           │         │ (+0.47)                                                      │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 4      │ Samba Sol      │ Rio Rhythm    │ latin     │ 4.87    │ mood match (+1.00), energy proximity (+2.88), acoustic match │
│        │                │               │           │         │ (+0.50), popularity proximity (+0.48)                        │
├────────┼────────────────┼───────────────┼───────────┼─────────┼──────────────────────────────────────────────────────────────┤
│ 5      │ Rooftop Lights │ Indigo Parade │ indie pop │ 4.67    │ mood match (+1.00), energy proximity (+2.73), acoustic match │
│        │                │               │           │         │ (+0.50), popularity proximity (+0.44)                        │
╘════════╧════════════════╧═══════════════╧═══════════╧═════════╧══════════════════════════════════════════════════════════════╛
```

**What changed:** the top 2 stayed the same (Sunrise City, Stadium Lights), but with the weights shifted, **Gym Hero fell out of the top 5** and non-pop songs (Pulse Garden, Samba Sol, Rooftop Lights) moved up. The new results are more *different* than more *accurate*. A real pop fan probably wants Gym Hero more than an EDM song, so I think the Balanced weights fit this user better. The experiment showed me how much of the ranking is just my weight choices.

---

## Limitations and Next Steps

- With only 30 songs, one or two songs decide most rankings.
- Exact-match genre and mood miss near-matches (chill vs. relaxed, pop vs. indie pop).
- The acoustic bonus rewards almost every song for users who do not like acoustic music, so it separates songs poorly for them.
- All of my extended attribute values were made up by me with AI help for this simulation, so they are not real streaming data.
- Next steps: a similarity map between moods and genres, more songs per genre, and a genre-level diversity penalty.

See `model_card.md` for the full model card and `ai_interactions.md` for how I used AI.
