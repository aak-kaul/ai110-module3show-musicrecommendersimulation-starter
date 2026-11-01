# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Music Recommender Simulation v1.0 

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

I designed this model to generate personalized top-k music recommendations based on user preference metadata. It assumes that the user can explicitly state their favorite genre, target mood, preferred energy level, and acoustic preference. This recommender is created specifically for classroom exploration and educational simulation to demonstrate explainable recommendation scoring, rather than real-world commercial streaming.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

I use four main song features in the catalog: genre, mood, energy level, and acousticness. The model considers user preferences for their favorite genre, desired mood, target energy score, and whether they like acoustic tracks. 

To create a final recommendation score, the system starts at zero and adds points based on how closely a song matches the user:
- If the song genre matches the user's favorite genre, it gets +2.0 points.
- If the song mood matches the target mood, it gets +1.0 point.
- It calculates how close the song's energy is to the user's target energy level and awards up to +1.5 points for close matches.
- If the user likes acoustic music and the song is acoustic (or vice versa), it gets +0.5 points.

I enhanced the starter logic by ensuring smooth fallback checks between object properties and dictionary representations, while also providing a detailed text explanation listing every reason a song earned its points.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The model uses the `data/songs.csv` catalog file containing candidate songs. The catalog represents popular genres such as pop, lofi, rock, and ambient across moods like happy, chill, energetic, and sad. I used the standard dataset without removing entries. 

However, there are key parts of musical taste missing in this dataset: it does not capture complex nuances like artist familiarity, lyric sentiment, release era, sub-genres, or dynamic changes in tempo across a track.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

The system works very well for users with strong, explicit genre and mood preferences (for example, a user looking specifically for happy pop music to work out to). 

The scoring successfully prioritizes exact genre matches while smoothly scaling energy proximity, so a high-energy pop track scores much higher than a low-energy lofi loop when a user asks for high energy. The recommendations matched my intuition by giving clear, explainable reasons for why the top track placed first.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

The model does not consider attributes like song length, release year, user listen history, or attributes like valence and danceability (even though they exist in the raw CSV). 

Underrepresented genres or niche moods in the dataset can get easily drowned out. Because a genre match awards a massive +2.0 points, the system heavily favors songs that match the exact genre tag, sometimes overfitting and ignoring a song from a different genre that perfectly matches the user's mood and energy target.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

I evaluated the recommender by running automated unit tests in `tests/test_recommender.py` and running execution tests in `src/main.py`. I tested user profiles looking for happy pop tracks (`genre="pop"`, `mood="happy"`, `energy=0.8`, `likes_acoustic=False`) versus chill acoustic tracks. 

I looked for whether the top-ranked song correctly matched the preferred genre and energy target. I ran comparisons between different `k` values and verified that the explanation strings accurately reflected the numerical math calculated in `score_song()`.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

In future versions, I would incorporate `danceability`, `valence`, and `tempo_bpm` into the scoring mathematical formula. 

I would also implement a diversity penalty so that top-k recommendations don't just return 5 songs from the exact same artist or album, ensuring users get a wider variety of tracks while still matching their target vibe.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned how rule-based content filtering works under the hood and how simple mathematical weighting can dramatically change recommendation outcomes. I found it interesting how small adjustments to energy scoring or genre point values immediately change which songs rise to the top of the queue. Building this changed how I view apps like Spotify: I now realize how much deliberate feature engineering goes into balancing what I ask for with song recommendations.