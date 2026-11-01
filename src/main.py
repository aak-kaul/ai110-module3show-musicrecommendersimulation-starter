"""CLI runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main                       # each profile uses its own ranking mode
    python -m src.main --mode Mood-First     # force one ranking mode for every profile
    python -m src.main --experiment          # also run the weight-shift experiment
"""

import argparse
from pathlib import Path

from tabulate import tabulate

from src.recommender import RANKING_MODES, load_songs, recommend_songs

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"

PROFILES = [
    {
        "name": "High-Energy Pop Fan",
        "mode": "Genre-First",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False,
                  "decade": "2020s", "popularity": 85},
    },
    {
        "name": "Lofi & Acoustic Chill Listener",
        "mode": "Balanced",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.30, "likes_acoustic": True,
                  "detailed_mood": "dreamy", "instrumentalness": 0.85},
    },
    {
        "name": "High-Tempo EDM Vibe Chaser",
        "mode": "Energy-Similarity",
        "prefs": {"genre": "edm", "mood": "energetic", "energy": 0.95, "likes_acoustic": False,
                  "tempo": 128},
    },
    {
        "name": "Hip-Hop Head",
        "mode": "Mood-First",
        "prefs": {"genre": "hip-hop", "mood": "intense", "energy": 0.80, "likes_acoustic": False,
                  "decade": "2010s", "language": "english"},
    },
]

EDGE_CASES = [
    {
        "name": "Adversarial: Sad but Very High Energy",
        "mode": "Balanced",
        "prefs": {"genre": "rock", "mood": "sad", "energy": 0.90, "likes_acoustic": False},
    },
    {
        "name": "Adversarial: Genre Not in Catalog (k-pop)",
        "mode": "Balanced",
        "prefs": {"genre": "k-pop", "mood": "happy", "energy": 0.80, "likes_acoustic": False},
    },
]


def show(name, prefs, songs, mode, k=5):
    """Print one profile's top-k recommendations as a table with reasons."""
    print("\n" + "=" * 100)
    print(f" PROFILE: {name} | Ranking mode: {mode}")
    print(f" Preferences: {prefs}")
    print("=" * 100)
    recs = recommend_songs(prefs, songs, k=k, mode=mode, apply_artist_penalty=True)
    rows = [
        [rank, song["title"], song["artist"], song["genre"], f"{score:.2f}", reasons]
        for rank, (song, score, reasons) in enumerate(recs, 1)
    ]
    print(tabulate(rows, headers=["Rank", "Title", "Artist", "Genre", "Score", "Reasons"],
                   tablefmt="fancy_grid", disable_numparse=True, maxcolwidths=[None, 22, 16, 10, None, 60]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--mode", choices=list(RANKING_MODES), help="override every profile's ranking mode")
    parser.add_argument("--experiment", action="store_true", help="run the weight-shift experiment")
    args = parser.parse_args()

    songs = load_songs(str(DATA_PATH))
    print(f"Loaded songs: {len(songs)}")

    for p in PROFILES + EDGE_CASES:
        show(p["name"], p["prefs"], songs, args.mode or p["mode"])

    if args.experiment:
        pop = PROFILES[0]
        print("\n\n##### EXPERIMENT: Balanced vs. Weight-Shift (energy x2, genre x0.5) #####")
        show(pop["name"], pop["prefs"], songs, "Balanced")
        show(pop["name"], pop["prefs"], songs, "Weight-Shift")


if __name__ == "__main__":
    main()
