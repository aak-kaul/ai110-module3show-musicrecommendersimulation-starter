"""Core logic for the Music Recommender Simulation (content-based, explainable)."""

import csv
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple

ACOUSTIC_THRESHOLD = 0.6   # acousticness above this counts as an "acoustic" song
ARTIST_PENALTY = 0.75      # points removed per earlier pick by the same artist

REQUIRED_COLUMNS = [
    "id", "title", "artist", "genre", "mood", "energy",
    "tempo_bpm", "valence", "danceability", "acousticness",
]


# --------------------------------------------------------------------------
# Data models
# --------------------------------------------------------------------------
@dataclass
class Song:
    """A song and its data features (the last five fields are the extended attributes)."""
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
    popularity: int = 50
    decade: str = ""
    detailed_mood: str = ""
    instrumentalness: float = 0.0
    language: str = "english"


@dataclass
class UserProfile:
    """A user's taste profile; the optional fields are only scored when they are set."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    favorite_decade: Optional[str] = None
    favorite_detailed_mood: Optional[str] = None
    target_popularity: Optional[int] = None
    target_instrumentalness: Optional[float] = None
    preferred_language: Optional[str] = None
    target_tempo: Optional[float] = None


# --------------------------------------------------------------------------
# Ranking modes (Strategy pattern: each mode is just a bundle of weights)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class RankingMode:
    """One ranking strategy: how many points each feature can contribute."""
    name: str
    genre: float
    mood: float
    energy: float
    acoustic: float = 0.5
    detailed_mood: float = 0.75
    decade: float = 0.5
    popularity: float = 0.5
    instrumental: float = 0.5
    language: float = 0.4
    tempo: float = 0.5


RANKING_MODES: Dict[str, RankingMode] = {
    m.name: m
    for m in [
        RankingMode("Balanced", genre=2.0, mood=1.0, energy=1.5),
        RankingMode("Genre-First", genre=3.0, mood=0.5, energy=1.0),
        RankingMode("Mood-First", genre=1.0, mood=3.0, energy=1.0),
        RankingMode("Energy-Similarity", genre=0.5, mood=0.5, energy=3.0),
        # Used for the sensitivity experiment: energy doubled, genre halved vs. Balanced.
        RankingMode("Weight-Shift", genre=1.0, mood=1.0, energy=3.0),
    ]
}


def get_mode(mode: str) -> RankingMode:
    """Look up a ranking mode by name, raising a clear error for unknown names."""
    if mode not in RANKING_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(RANKING_MODES)}")
    return RANKING_MODES[mode]


# --------------------------------------------------------------------------
# Loading data
# --------------------------------------------------------------------------
def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV into a list of dicts, converting numeric columns."""
    songs = []
    with open(csv_path, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"songs CSV is missing required columns: {missing}")
        for line_no, row in enumerate(reader, start=2):
            try:
                songs.append({
                    "id": int(row["id"]),
                    "title": row["title"].strip(),
                    "artist": row["artist"].strip(),
                    "genre": row["genre"].strip().lower(),
                    "mood": row["mood"].strip().lower(),
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                    # Extended attributes (optional so older CSVs still load)
                    "popularity": int(row.get("popularity") or 50),
                    "decade": (row.get("decade") or "").strip().lower(),
                    "detailed_mood": (row.get("detailed_mood") or "").strip().lower(),
                    "instrumentalness": float(row.get("instrumentalness") or 0.0),
                    "language": (row.get("language") or "english").strip().lower(),
                })
            except (ValueError, TypeError, KeyError, AttributeError) as err:
                raise ValueError(f"Bad song row on CSV line {line_no}: {err}") from err
    return songs


# --------------------------------------------------------------------------
# Scoring (judges ONE song)
# --------------------------------------------------------------------------
def _pref(prefs: Dict, *keys):
    """Return the first non-empty preference found under any of the given key names."""
    for key in keys:
        if prefs.get(key) not in (None, ""):
            return prefs[key]
    return None


def score_song(user_prefs: Dict, song: Dict, mode: str = "Balanced") -> Tuple[float, List[str]]:
    """Score one song for one user; returns (score, list of human-readable reasons)."""
    w = get_mode(mode)
    score = 0.0
    reasons: List[str] = []

    # 1. Genre: exact match
    genre = _pref(user_prefs, "genre", "favorite_genre")
    if genre and song["genre"] == str(genre).lower():
        score += w.genre
        reasons.append(f"genre match (+{w.genre:.2f})")

    # 2. Mood: exact match
    mood = _pref(user_prefs, "mood", "favorite_mood")
    if mood and song["mood"] == str(mood).lower():
        score += w.mood
        reasons.append(f"mood match (+{w.mood:.2f})")

    # 3. Energy: closer to the target = more points (never negative)
    energy = _pref(user_prefs, "energy", "target_energy")
    energy = 0.5 if energy is None else float(energy)
    pts = max(0.0, w.energy * (1.0 - abs(energy - song["energy"])))
    score += pts
    reasons.append(f"energy proximity (+{pts:.2f})")

    # 4. Acousticness: does the user's taste agree with the song's sound?
    if "likes_acoustic" in user_prefs and user_prefs["likes_acoustic"] is not None:
        if bool(user_prefs["likes_acoustic"]) == (song["acousticness"] > ACOUSTIC_THRESHOLD):
            score += w.acoustic
            reasons.append(f"acoustic match (+{w.acoustic:.2f})")

    # 5. Detailed mood tag: exact match (extended attribute)
    detailed = _pref(user_prefs, "detailed_mood", "favorite_detailed_mood")
    if detailed and song.get("detailed_mood") == str(detailed).lower():
        score += w.detailed_mood
        reasons.append(f"'{song['detailed_mood']}' vibe match (+{w.detailed_mood:.2f})")

    # 6. Decade: exact match (extended attribute)
    decade = _pref(user_prefs, "decade", "favorite_decade")
    if decade and song.get("decade") == str(decade).lower():
        score += w.decade
        reasons.append(f"{song['decade']} era match (+{w.decade:.2f})")

    # 7. Popularity: closeness to the user's preferred popularity, 0-100 scale
    pop = _pref(user_prefs, "popularity", "target_popularity")
    if pop is not None:
        pts = w.popularity * (1.0 - abs(float(pop) - song.get("popularity", 50)) / 100.0)
        score += pts
        reasons.append(f"popularity proximity (+{pts:.2f})")

    # 8. Instrumentalness: closeness to the preferred amount of vocals
    inst = _pref(user_prefs, "instrumentalness", "target_instrumentalness")
    if inst is not None:
        pts = w.instrumental * (1.0 - abs(float(inst) - song.get("instrumentalness", 0.0)))
        score += pts
        reasons.append(f"instrumental proximity (+{pts:.2f})")

    # 9. Language: exact match (extended attribute)
    lang = _pref(user_prefs, "language", "preferred_language")
    if lang and song.get("language") == str(lang).lower():
        score += w.language
        reasons.append(f"{song['language']} language match (+{w.language:.2f})")

    # 10. Tempo: closeness within a 60 BPM window
    tempo = _pref(user_prefs, "tempo", "target_tempo")
    if tempo is not None:
        pts = w.tempo * max(0.0, 1.0 - abs(float(tempo) - song["tempo_bpm"]) / 60.0)
        score += pts
        reasons.append(f"tempo proximity (+{pts:.2f})")

    return round(score, 2), reasons


# --------------------------------------------------------------------------
# Ranking (judges the WHOLE list)
# --------------------------------------------------------------------------
def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "Balanced",
    apply_artist_penalty: bool = True,
) -> List[Tuple[Dict, float, str]]:
    """Rank songs by score and return the top k as (song, score, explanation).

    With the artist penalty on, picks are made one at a time: each time an artist
    is already in the list, their remaining songs lose ARTIST_PENALTY points per
    earlier pick, which lets other artists rise.
    """
    get_mode(mode)  # fail early on a bad mode name
    pool = []
    for song in songs:
        base, reasons = score_song(user_prefs, song, mode=mode)
        pool.append({"song": song, "base": base, "reasons": reasons})

    picked: List[Tuple[Dict, float, str]] = []
    artist_counts: Dict[str, int] = {}

    while pool and len(picked) < k:
        best, best_score, best_reasons = None, None, None
        for cand in pool:
            adjusted = cand["base"]
            reasons = list(cand["reasons"])
            repeats = artist_counts.get(cand["song"]["artist"], 0)
            if apply_artist_penalty and repeats:
                penalty = repeats * ARTIST_PENALTY
                adjusted -= penalty
                reasons.append(f"artist repeat penalty (-{penalty:.2f})")
            # Highest score wins; ties are broken alphabetically for consistent output
            better = (
                best is None
                or adjusted > best_score
                or (adjusted == best_score and cand["song"]["title"] < best["song"]["title"])
            )
            if better:
                best, best_score, best_reasons = cand, adjusted, reasons
        pool.remove(best)
        artist_counts[best["song"]["artist"]] = artist_counts.get(best["song"]["artist"], 0) + 1
        picked.append((best["song"], round(best_score, 2), ", ".join(best_reasons)))

    return picked


# --------------------------------------------------------------------------
# Object-oriented wrapper (used by the unit tests)
# --------------------------------------------------------------------------
class Recommender:
    """OOP wrapper around the functional scoring and ranking code."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _profile_to_prefs(user: UserProfile) -> Dict:
        """Convert a UserProfile into the preference dict that score_song expects."""
        return asdict(user)

    def recommend(self, user: UserProfile, k: int = 5, mode: str = "Balanced",
                  apply_artist_penalty: bool = True) -> List[Song]:
        """Return the top k Song objects for a UserProfile."""
        ranked = recommend_songs(
            self._profile_to_prefs(user), [asdict(s) for s in self.songs],
            k=k, mode=mode, apply_artist_penalty=apply_artist_penalty,
        )
        by_id = {s.id: s for s in self.songs}
        return [by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song, mode: str = "Balanced") -> str:
        """Return a plain-text reason string for why a song scored the way it did."""
        _, reasons = score_song(self._profile_to_prefs(user), asdict(song), mode=mode)
        return ", ".join(reasons)
