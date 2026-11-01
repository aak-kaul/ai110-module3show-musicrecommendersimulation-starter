from pathlib import Path

import pytest

from src.recommender import (
    RANKING_MODES, Song, UserProfile, Recommender,
    load_songs, recommend_songs, score_song,
)

DATA = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---- Extra tests -----------------------------------------------------------

def test_dataset_loads_with_enough_songs_and_extended_columns():
    songs = load_songs(str(DATA))
    assert len(songs) >= 20
    for key in ("popularity", "decade", "detailed_mood", "instrumentalness", "language"):
        assert all(key in s for s in songs)
    assert all(isinstance(s["energy"], float) for s in songs)


def test_score_is_numeric_for_every_song_and_mode():
    songs = load_songs(str(DATA))
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}
    for mode in RANKING_MODES:
        for song in songs:
            score, reasons = score_song(prefs, song, mode=mode)
            assert isinstance(score, float) and score >= 0
            assert any("energy" in r for r in reasons)


def test_explanation_matches_scoring_rules():
    songs = load_songs(str(DATA))
    gym = next(s for s in songs if s["title"] == "Gym Hero")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False}
    score, reasons = score_song(prefs, gym, mode="Balanced")
    text = " ".join(reasons)
    assert "genre match (+2.00)" in text
    assert "mood match" not in text  # Gym Hero is "intense", not "happy"
    assert score > 0


def test_switching_mode_changes_the_top_result():
    songs = load_songs(str(DATA))
    prefs = {"genre": "pop", "mood": "sad", "energy": 0.9, "likes_acoustic": False}
    genre_first = recommend_songs(prefs, songs, k=1, mode="Genre-First")[0][0]
    mood_first = recommend_songs(prefs, songs, k=1, mode="Mood-First")[0][0]
    assert genre_first["genre"] == "pop"
    assert mood_first["mood"] == "sad"


def test_artist_penalty_reduces_repeat_artists():
    songs = load_songs(str(DATA))
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True}
    no_penalty = recommend_songs(prefs, songs, k=5, apply_artist_penalty=False)
    with_penalty = recommend_songs(prefs, songs, k=5, apply_artist_penalty=True)
    artists_no = [s["artist"] for s, _, _ in no_penalty]
    artists_yes = [s["artist"] for s, _, _ in with_penalty]
    assert len(set(artists_yes)) >= len(set(artists_no))


def test_recommend_returns_requested_number_sorted_descending():
    songs = load_songs(str(DATA))
    prefs = {"genre": "edm", "mood": "energetic", "energy": 0.95, "likes_acoustic": False}
    recs = recommend_songs(prefs, songs, k=5)
    scores = [score for _, score, _ in recs]
    assert len(recs) == 5
    assert scores == sorted(scores, reverse=True)


def test_unknown_mode_raises_clear_error():
    with pytest.raises(ValueError):
        recommend_songs({"genre": "pop"}, [], mode="Nonsense")
