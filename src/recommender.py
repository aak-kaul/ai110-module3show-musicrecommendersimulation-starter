import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its data features.
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences profile.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation model using Strategy Pattern.
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _song_to_dict(self, song: Song) -> Dict:
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness
        }

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "Balanced", apply_artist_penalty: bool = True) -> List[Song]:
        """
        Ranks songs based on UserProfile and returns top k Song objects.
        """
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic
        }
        song_dicts = [self._song_to_dict(s) for s in self.songs]
        ranked_tuples = recommend_songs(user_prefs, song_dicts, k=k, mode=mode, apply_artist_penalty=apply_artist_penalty)
        
        song_dict_by_id = {s.id: s for s in self.songs}
        return [song_dict_by_id[item[0]["id"]] for item in ranked_tuples]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "Balanced") -> str:
        """
        Provides a human-readable explanation of why a song was selected.
        """
        user_prefs = {
            "favorite_genre": user.favorite_genre,
            "favorite_mood": user.favorite_mood,
            "target_energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic
        }
        song_dict = self._song_to_dict(song)
        _, reasons = score_song(user_prefs, song_dict, mode=mode)
        return ", ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV dataset and converts numeric values to floats and integers.
    """
    songs = []
    with open(csv_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            song = {
                "id": int(row["id"]),
                "title": row["title"].strip(),
                "artist": row["artist"].strip(),
                "genre": row["genre"].strip().lower(),
                "mood": row["mood"].strip().lower(),
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"])
            }
            songs.append(song)
    return songs

def score_song(user_prefs: Dict, song: Dict, mode: str = "Balanced") -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences according to the selected ranking mode.
    Supports modes: 'Balanced', 'Genre-First', 'Mood-First', 'Energy-Similarity'.
    """
    score = 0.0
    reasons = []

    # Strategy Mode Weight Allocations
    if mode == "Genre-First":
        w_genre, w_mood, w_energy = 3.0, 0.5, 1.0
    elif mode == "Mood-First":
        w_genre, w_mood, w_energy = 1.0, 3.0, 1.0
    elif mode == "Energy-Similarity":
        w_genre, w_mood, w_energy = 0.5, 0.5, 3.0
    else:  # Balanced
        w_genre, w_mood, w_energy = 2.0, 1.0, 1.5

    # 1. Genre Feature Match
    pref_genre = str(user_prefs.get("genre", "") or user_prefs.get("favorite_genre", "")).lower()
    if pref_genre and song["genre"].lower() == pref_genre:
        score += w_genre
        reasons.append(f"genre match (+{w_genre:.1f})")

    # 2. Mood Feature Match
    pref_mood = str(user_prefs.get("mood", "") or user_prefs.get("favorite_mood", "")).lower()
    if pref_mood and song["mood"].lower() == pref_mood:
        score += w_mood
        reasons.append(f"mood match (+{w_mood:.1f})")

    # 3. Energy Feature Proximity Score
    target_energy = float(user_prefs.get("energy", user_prefs.get("target_energy", 0.5)))
    energy_diff = abs(target_energy - song["energy"])
    energy_pts = max(0.0, w_energy * (1.0 - energy_diff))
    score += energy_pts
    reasons.append(f"energy proximity ({energy_pts:+.2f})")

    # 4. Acousticness Feature Match
    if "likes_acoustic" in user_prefs:
        likes_acoustic = bool(user_prefs["likes_acoustic"])
        is_acoustic = song["acousticness"] > 0.6
        if likes_acoustic == is_acoustic:
            score += 0.5
            reasons.append("acoustic match (+0.5)")

    return round(score, 2), reasons

def recommend_songs(
    user_prefs: Dict, 
    songs: List[Dict], 
    k: int = 5, 
    mode: str = "Balanced", 
    apply_artist_penalty: bool = True
) -> List[Tuple[Dict, float, str]]:
    """
    Ranks all catalog songs by score and applies a fairness penalty to penalize artist repetition.
    """
    scored_candidates = []
    for song in songs:
        base_score, reasons = score_song(user_prefs, song, mode=mode)
        scored_candidates.append({
            "song": song,
            "base_score": base_score,
            "reasons": list(reasons)
        })

    scored_candidates.sort(key=lambda x: x["base_score"], reverse=True)

    selected = []
    artist_counts = {}

    for cand in scored_candidates:
        song = cand["song"]
        artist = song["artist"]
        score = cand["base_score"]
        reasons = list(cand["reasons"])

        if apply_artist_penalty:
            count = artist_counts.get(artist, 0)
            if count > 0:
                penalty = count * 0.75
                score -= penalty
                reasons.append(f"artist repetition penalty (-{penalty:.2f})")
            artist_counts[artist] = count + 1

        selected.append((song, round(score, 2), ", ".join(reasons)))

    selected.sort(key=lambda item: item[1], reverse=True)
    return selected[:k]