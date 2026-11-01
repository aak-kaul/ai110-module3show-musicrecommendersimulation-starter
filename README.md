# 🎵 Music Recommender Simulation

## Project Summary

In this project, I built and evaluated an explainable music recommender system that models user taste profiles and ranks songs using multi-attribute content scoring. 

My goal was to:
- Represent songs and user taste profiles using structured data schemas (`Song` and `UserProfile`).
- Design scoring algorithms that combine feature matching (genre, mood, energy, acousticness) with customizable ranking modes (`Balanced`, `Genre-First`, `Mood-First`, `Energy-Similarity`).
- Implement an **Artist Penalty** component to introduce fairness, prevent artist repetition, and avoid filter bubbles.
- Present transparent, explainable recommendations formatted in visual summary tables.

---

## How The System Works

My recommendation engine scores candidate songs based on four core attributes:
- **Genre** (e.g., pop, lofi, hip-hop, rock, edm, classical, acoustic)
- **Mood** (e.g., happy, chill, energetic, sad)
- **Energy Level** (scalar from `0.0` to `1.0`)
- **Acousticness** (scalar from `0.0` to `1.0`)

### Scoring & Strategy Design Pattern
My system uses a flexible scoring function `score_song(user_prefs, song, mode)` supporting distinct ranking modes:
- **Balanced (Default):** Genre match (+2.0), Mood match (+1.0), Energy proximity (up to +1.5), Acoustic match (+0.5).
- **Genre-First:** Prioritizes exact genre matches (+3.0 genre weight).
- **Mood-First:** Prioritizes mood alignment (+3.0 mood weight).
- **Energy-Similarity:** Prioritizes target energy closeness (+3.0 energy weight).

### Fairness & Diversity Component
To prevent artist monopoly in top-$k$ results, my `recommend_songs()` function applies a **-0.75 penalty** for each duplicate artist already selected in the recommendation list.

---

## Getting Started

### Setup

1. Activate your environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate