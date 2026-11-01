# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 2.0** (a content-based, explainable music recommender simulation)

---

## 2. Goal / Task and Intended Use

VibeFinder tries to suggest the top 5 songs from a small catalog that best match a user's stated taste. It does not predict what someone will actually click on. It only scores how closely each song matches the preferences I give it.

**Intended use:** classroom exploration. I built it to learn how data turns into a ranked list and to show *why* each song was picked.

**Assumptions about the user:** they can state their favorite genre, mood, and energy level up front, and they want something similar to that description.

**Not intended for:** real streaming products, real decisions about artists' exposure, or any use where the results affect people's income or access. It also should not be used to guess what a real person likes without asking them, since it has no listening history.

---

## 3. Data Used

- **Catalog:** `data/songs.csv`, **30 songs** (I started from the 10-song starter file and added 20 more, with a wider range of genres and moods).
- **Genres (17):** pop, indie pop, lofi, rock, metal, ambient, jazz, synthwave, edm, folk, latin, funk, classical, hip-hop, country, r&b, reggae. Most genres have only 1-3 songs.
- **Moods:** happy, chill, intense, relaxed, moody, focused, energetic, mellow, mystical, upbeat, sad, romantic.
- **Starter attributes:** genre, mood, energy, tempo_bpm, valence, danceability, acousticness.
- **Five attributes I added:** popularity (0-100), decade, detailed_mood (for example "nostalgic" or "euphoric"), instrumentalness (0-1), and language.
- **Important limit:** the values I added are invented for this simulation. They are not real streaming data, so the results say nothing about real music popularity.
- **Missing from the data:** user listening history, lyrics, artist fame, sub-genres, and how a song changes over time.

---

## 4. Algorithm Summary (plain language)

Think of it as a judge giving points to each song, then a list sorted by points.

**Step 1: score one song.** Starting at zero, the judge adds points when the song fits the user:
- **Genre** matches: +2.0 (this is the biggest single reward).
- **Mood** matches: +1.0.
- **Energy** is close to what the user wants: up to +1.5. The closer, the more points, so someone who wants calm music is not given loud songs just because loud songs have "more" energy.
- **Acoustic taste** agrees with the song (a song above 0.6 acousticness counts as acoustic): +0.5.
- Optional extras, only when the user cares about them: matching "vibe" tag (+0.75), matching decade (+0.5), similar popularity (up to +0.5), similar amount of vocals (up to +0.5), matching language (+0.4), and similar tempo (up to +0.5).

Every time the judge adds points, it writes down a reason, so the user can see exactly why a song scored what it did.

**Step 2: rank the list.** The recommender scores every song, then picks the best one, then the next best, and so on until it has 5. When it picks, it looks at the artist (see "Fairness" below).

**Ranking modes.** I can switch how much each feature is worth: *Balanced* (default), *Genre-First*, *Mood-First*, and *Energy-Similarity*. There is also a *Weight-Shift* mode I used for an experiment. Each mode is just a different set of weights, so switching modes does not change the rest of the code.

---

## 5. Fairness and Diversity: the Artist Penalty

Without any extra rule, one artist with several songs that fit the user could take over the whole top 5. To prevent that, each time a song from an artist is already in the picks, the other songs from that artist lose **0.75 points per earlier pick**. This gives other artists a chance to appear.

This helped in my tests. In the EDM profile, *Pulse Garden* by Cyber Pulse has very high energy and would have ranked high, but the artist already had the #1 pick (*Electric Thunder*), so it dropped to a lower score and out of the top 5, and other artists took its place. In the Pop profile, *Gym Hero* was marked down 0.75 because *Stadium Lights* by the same artist (Max Pulse) was picked first.

**How it improves fairness:** it spreads exposure across more artists, and it makes the list less of a filter bubble. **What it does not fix:** it only looks at artists. It does not look at genre, so a user could still get five songs from the same genre.

---

## 6. Observed Behavior and Biases

- **Genre dominates.** A genre match is worth +2.0 (or +3.0 in Genre-First mode), which is more than any other single feature. In the Pop profile, *Gym Hero* has an "intense" mood, not "happy," but it still lands in the top 3 because it is pop and has high energy.
- **Exact matching misses near-matches.** "Chill," "relaxed," and "mellow" feel alike to a listener, but the system treats them as completely different moods. The same is true for "pop" and "indie pop."
- **The acoustic bonus is not very selective.** Most songs in the catalog are not acoustic, so a user who does not like acoustic music gets +0.5 for most of the catalog and the bonus barely separates songs.
- **Small catalog, uneven coverage.** Many genres have only one song, so a user who likes a niche genre gets at most one genre-matched song, and the rest of the list is filled by mood and energy. When I asked for a genre that is not in the catalog at all (k-pop), nothing got a genre bonus and the system fell back to mood and energy.
- **Conflicting preferences.** A profile asking for "sad" and very high energy at the same time found only one song (*Broken Radio*) that fit both, and after that the list was just the highest-energy songs. The system does not warn the user about the conflict.
- **No real popularity bias or user history.** Because I made up the popularity values and there are no real users, I cannot say how the system would behave with real popularity data.

---

## 7. Evaluation Process

**Automated tests:** `tests/test_recommender.py` has 9 tests. They check that the dataset loads with at least 20 songs and all the extended columns, that scores are numeric for every song in every mode, that the explanation text matches the scoring rules, that switching modes changes the top result, that the artist penalty does not reduce artist variety, that results come back sorted from highest to lowest score, and that a bad mode name raises a clear error.

**Profiles I ran** (top 5 each, full output is in `README.md`):
1. High-Energy Pop Fan (Genre-First)
2. Lofi & Acoustic Chill Listener (Balanced)
3. High-Tempo EDM Vibe Chaser (Energy-Similarity)
4. Hip-Hop Head (Mood-First)
5. Edge case: sad but very high energy (Balanced)
6. Edge case: genre not in the catalog (Balanced)

**Hand check:** I added up one score by hand to confirm the math. For *Library Rain* in the Lofi profile: 2.00 + 1.00 + 1.425 + 0.50 + 0.75 + 0.475 = 6.15, which matches the program output of 6.15.

**What surprised me:**
- A rock song (*Storm Runner*) beat a hip-hop song for the hip-hop fan in Mood-First mode, because a mood match was worth +3.0 and genre only +1.0.
- Shifting the weights (energy doubled, genre halved) removed *Gym Hero* from the Pop profile's top 5. The results were different, but I do not think they were more accurate.
- The explanation text made it easy to see why a song surprised me, which is the main point of an explainable system.

### Comparing the profiles, pair by pair

- **Pop Fan vs. Lofi Listener:** no shared songs. The pop profile wants energy around 0.85 with non-acoustic songs, so it returns loud, danceable tracks. The lofi profile wants 0.30 energy with acoustic, instrumental songs, so it returns quiet tracks like *Library Rain*. This is what I would expect from two opposite tastes.
- **Pop Fan vs. EDM Chaser:** they share *Stadium Lights* and *Samba Sol* because both want high energy. The pop list starts with pop songs because Genre-First rewards genre. The EDM list starts with *Electric Thunder* and then ranks purely on closeness to 0.95 energy, so a pop song, a synthwave song, a latin song, and a rock song all appear.
- **Pop Fan vs. Hip-Hop Head:** they share only *Gym Hero*, but for different reasons: it is there for the pop fan because it is pop, and for the hip-hop fan because its "intense" mood matches.
- **Lofi Listener vs. EDM Chaser:** no shared songs. They sit at opposite ends of the energy scale (0.30 vs. 0.95), and the acoustic preference is reversed.
- **Lofi Listener vs. Hip-Hop Head:** no shared songs. The lofi profile pulls toward instrumental, acoustic songs, while the hip-hop profile pulls toward vocal, English-language songs with intense moods.
- **EDM Chaser vs. Hip-Hop Head:** they share only *Storm Runner*. The EDM profile likes it because its energy of 0.91 is close to 0.95, and the hip-hop profile likes it because its mood is "intense." Same song, different reason, which the reason text shows clearly.

**Why *Gym Hero* keeps showing up for people who just want "Happy Pop" (plain-language answer):** Gym Hero is a pop song with very high energy that is not acoustic. A "happy pop" listener with a high energy target ticks three of those boxes. The song is "intense" rather than "happy," so it misses the mood bonus, but a genre match is worth more than a mood match, so it still ranks near the top.

---

## 8. Ideas for Improvement

1. **Give partial credit for similar moods and genres** (for example "chill" and "relaxed," or "pop" and "indie pop") instead of all-or-nothing matches.
2. **Add a genre-level diversity penalty** next to the artist penalty, so the top 5 cannot be five songs from one genre.
3. **Grow the catalog** to at least a few songs per genre, and use real data for popularity and decade so those features mean something.
4. **Warn on conflicting or empty preferences,** for example when no song matches the requested genre.

---

## 9. Personal Reflection

My biggest learning moment was seeing how much of the "recommendation" is really my own weight choices. When I doubled the energy weight and halved the genre weight, the top 5 changed noticeably even though the user and the songs stayed the same. Nothing in the system could tell me which version was "right," so I had to use my own judgment about what a pop fan would want.

AI tools helped me move faster with the code, the dataset expansion, and brainstorming a design for the ranking modes. I still had to check the work myself: I ran the tests, added up a score by hand, and read the reason text against the numbers to make sure the explanations were not just generic. I also noticed that the AI-made attribute values are invented, so I wrote that limit down in the data section.

What surprised me is how simple rules can still *feel* like a recommendation. A genre match, a mood match, and an energy gap are enough to produce lists that look sensible, as long as the user asks for something common. The weak spots only showed up when I tried unusual profiles. If I extended this project, I would add partial-credit similarity for moods and genres, and I would try collaborative filtering with a few fake users to see how it differs from this content-based approach.
