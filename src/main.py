"""
CLI runner for the Music Recommender Simulation.
"""

from recommender import load_songs, recommend_songs
from tabulate import tabulate

def print_profile_recommendations(profile_name: str, user_prefs: dict, songs: list, mode: str = "Balanced"):
    print(f"\n================================================================================")
    print(f" PROFILE: {profile_name.upper()} | Ranking Mode: '{mode}'")
    print(f" Preferences: Genre={user_prefs.get('genre')}, Mood={user_prefs.get('mood')}, "
          f"Energy={user_prefs.get('energy')}, Likes Acoustic={user_prefs.get('likes_acoustic')}")
    print(f"================================================================================")

    recs = recommend_songs(user_prefs, songs, k=4, mode=mode, apply_artist_penalty=True)
    
    table_data = []
    for rank, (song, score, explanation) in enumerate(recs, 1):
        table_data.append([
            rank,
            song['title'],
            song['artist'],
            song['genre'].capitalize(),
            f"{score:.2f}",
            explanation
        ])
        
    headers = ["Rank", "Title", "Artist", "Genre", "Score", "Reason / Match Factors"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

def main() -> None:
    songs = load_songs("data/songs.csv")

    profiles = [
        {
            "name": "Pop / Upbeat Workout Fan",
            "prefs": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
            "mode": "Genre-First"
        },
        {
            "name": "Lofi & Acoustic Chill Listener",
            "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.30, "likes_acoustic": True},
            "mode": "Balanced"
        },
        {
            "name": "High-Tempo EDM Vibe Chaser",
            "prefs": {"genre": "edm", "mood": "energetic", "energy": 0.95, "likes_acoustic": False},
            "mode": "Energy-Similarity"
        }
    ]

    for p in profiles:
        print_profile_recommendations(p["name"], p["prefs"], songs, mode=p["mode"])

if __name__ == "__main__":
    main()