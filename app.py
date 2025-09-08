import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from imdb import IMDb

# ------------------------
# Streamlit Page Config
# ------------------------
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🍿",
    layout="wide"
)

# ------------------------
# Load Metadata
# ------------------------
movies = pd.read_csv("movies.csv")
movies["comb"] = movies["comb"].fillna("")

# Build TF-IDF matrix
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies["comb"])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# ------------------------
# IMDb Instance
# ------------------------
ia = IMDb()

def get_poster(movie_title):
    """Fetch movie poster + IMDb link from IMDb"""
    try:
        results = ia.search_movie(movie_title)
        if results:
            movie = results[0]
            ia.update(movie)
            poster_url = movie.get("full-size cover url", None)
            imdb_id = movie.movieID
            imdb_url = f"https://www.imdb.com/title/tt{imdb_id}/"
            return poster_url, imdb_url
    except Exception as e:
        print("IMDb fetch error:", e)
    return "https://via.placeholder.com/200x300?text=No+Image", None

# ------------------------
# Recommendation Function
# ------------------------
def recommend_movie(user_input, cosine_sim=cosine_sim):
    # Find closest dataset title that contains the user input
    matches = movies[movies["movie_title"].str.lower().str.contains(user_input.lower())]
    if matches.empty:
        return None, None

    # Use the first matching dataset title
    idx = matches.index[0]
    selected_title = movies.iloc[idx]["movie_title"].title()  # ✅ Capitalized

    # Similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # top 5

    movie_indices = [i[0] for i in sim_scores]
    rec_titles = movies.iloc[movie_indices]["movie_title"].apply(lambda x: x.title()).tolist()

    return selected_title, rec_titles

# ------------------------
# Streamlit UI
# ------------------------
st.title("🍿 Content-Based Movie Recommender")

user_input = st.text_input("Enter a movie title:")

if st.button("Recommend"):
    if user_input.strip() == "":
        st.warning("Please type a movie title first.")
    else:
        selected, recs = recommend_movie(user_input)
        if selected is None:
            st.error("Movie not found in database. Try another title.")
        else:
            # Show selected movie
            st.subheader(f"Selected Movie: {selected}")
            poster, imdb_url = get_poster(selected)
            if poster:
                st.image(poster, caption=selected, width=250)
                if imdb_url:
                    st.markdown(f"[🔗 View on IMDb]({imdb_url})")
            else:
                st.image("https://via.placeholder.com/200x300?text=No+Image", caption=selected, width=250)

            # Show recommendations
            st.subheader(f"Top 5 Recommendations for **{selected}**:")
            cols = st.columns(5)
            for i, r in enumerate(recs):
                with cols[i]:
                    poster, imdb_url = get_poster(r)
                    if poster:
                        st.image(poster, caption=r, use_column_width=True)
                        if imdb_url:
                            st.markdown(f"[IMDb Page]({imdb_url})", unsafe_allow_html=True)
                    else:
                        st.image("https://via.placeholder.com/200x300?text=No+Image", caption=r, use_column_width=True)
