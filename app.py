import pickle
import streamlit as st
import requests
import pandas as pd
import math
import urllib.parse
import os

# --- TMDB API Key from Streamlit Cloud secrets ---
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

# Page configuration
st.set_page_config(
    page_title="🎬 MovieMatch - Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced CSS with Aurora Animation, Background Color, and Professional UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    .stApp { background-color: #0f0c29; color: #ffffff; font-family: 'Poppins', sans-serif; }
    body { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }

    .aurora-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; }
    .aurora { position: absolute; border-radius: 50%; mix-blend-mode: screen; animation: aurora-anim 12s infinite linear; }
    @keyframes aurora-anim { 0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; } 50% { transform: translate(50%, 50%) scale(1.5); opacity: 0.3; } 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; } }
    .aurora-1 { width: 80vmax; height: 80vmax; top: 50%; left: 50%; background: radial-gradient(circle, #00f2ea 0%, rgba(0, 242, 234, 0) 70%); animation-duration: 15s; }
    .aurora-2 { width: 60vmax; height: 60vmax; top: 20%; left: 20%; background: radial-gradient(circle, #8f94fb 0%, rgba(143, 148, 251, 0) 70%); animation-duration: 12s; animation-direction: reverse; }
    .aurora-3 { width: 70vmax; height: 70vmax; top: 80%; left: 80%; background: radial-gradient(circle, #4e54c8 0%, rgba(78, 84, 200, 0) 70%); animation-duration: 18s; }
    
    .starfall-container { pointer-events:none; position:fixed; top:0; left:0; width:100vw; height:120px; z-index:100; }
    .star { position:absolute; border-radius:50%; opacity:0.7; width:8px; height:8px; animation: fall 3s linear infinite; }
    .star.s1 { left: 5vw; animation-duration: 1.3s; background: #ffd700;}
    .star.s2 { left: 15vw; animation-duration: 2.0s; background: #4a90e2;}
    .star.s3 { left: 25vw; animation-duration: 2.7s; background: #ff69b4;}
    .star.s4 { left: 35vw; animation-duration: 2.2s; background: #43c6ac;}
    .star.s5 { left: 45vw; animation-duration: 2.8s; background: #fff;}
    .star.s6 { left: 55vw; animation-duration: 2.4s; background: #ffd700;}
    .star.s7 { left: 65vw; animation-duration: 2.0s; background: #4a90e2;}
    .star.s8 { left: 75vw; animation-duration: 1.9s; background: #ff69b4;}
    .star.s9 { left: 85vw; animation-duration: 2.2s; background: #43c6ac;}
    .star.s10 { left: 95vw; animation-duration: 1.8s; background: #fff;}
    @keyframes fall { 0% { top: 0; opacity: 0.8;} 80% { opacity: 0.8;} 100% { top: 110px; opacity: 0;} }

    .stButton > button { border-radius: 8px; border: 1px solid #00f2ea; background-color: transparent; color: #00f2ea; transition: all 0.3s ease-in-out; padding: 0.5rem 1rem; }
    .stButton > button:hover { background-color: #00f2ea; color: #1a1a2e; border-color: #00f2ea; box-shadow: 0 0 15px #00f2ea; }
    
    .nav-btn { background: rgba(0,0,0,0.3); backdrop-filter: blur(5px); color: white !important; text-decoration: none; border-radius: 10px; padding: 0.5rem 1.5rem; font-weight: 600; cursor: pointer; z-index: 2000; border: 1px solid rgba(255,25,255,0.2); transition: all 0.2s ease-in-out; }
    .nav-btn:hover { background: rgba(0, 242, 234, 0.8); box-shadow: 0 0 15px #00f2ea; color: #0f0c29 !important; }
    .home-btn {  top: 60px; left: 200px; }

    .movie-card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 1rem; margin: 10px 0; transition: all 0.3s ease; border: 1px solid transparent; min-height: 400px; backdrop-filter: blur(5px); }
    a:hover .movie-card { transform: translateY(-8px); box-shadow: 0 10px 20px rgba(0,0,0,0.4); border-color: #00f2ea; }
    .movie-poster { border-radius: 10px; width: 100%; height: 250px; object-fit: cover; margin-bottom: 1rem; }
    .movie-title { font-weight: 600; font-size: 1.1rem; color: #ffffff; text-align: center; height: 3.3em; overflow: hidden; }
    .main-header { font-size: 3.5rem; text-align: center; background: linear-gradient(45deg, #8f94fb, #00f2ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; padding-top: 5rem; font-weight: 700; }
</style>
<div class="aurora-container">
    <div class="aurora aurora-1"></div>
    <div class="aurora aurora-2"></div>
    <div class="aurora aurora-3"></div>
</div>
<div class="starfall-container">
    <div class="star s1"></div> <div class="star s2"></div>
    <div class="star s3"></div> <div class="star s4"></div>
    <div class="star s5"></div> <div class="star s6"></div>
    <div class="star s7"></div> <div class="star s8"></div>
    <div class="star s9"></div> <div class="star s10"></div>
</div>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_resource
def load_data():
    movies = pickle.load(open('movies_full.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    genres = pickle.load(open('genres.pkl', 'rb'))
    actors = pickle.load(open('actors.pkl', 'rb'))
    directors = pickle.load(open('directors.pkl', 'rb'))
    if 'year' not in movies.columns and 'release_date' in movies.columns:
        movies['year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year
    return movies, similarity, genres, actors, directors

movies, similarity, genres, actors, directors = load_data()

# --- Session State ---
if 'view' not in st.session_state: st.session_state.view = 'home'
if 'selected_movie' not in st.session_state: st.session_state.selected_movie = None
if 'current_page' not in st.session_state: st.session_state.current_page = 1

# --- Fetch Poster ---
@st.cache_data
def fetch_poster(movie_title):
    try:
        movie_id = movies[movies['title'] == movie_title]['movie_id'].values[0]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

# --- Recommendation ---
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        return [movies.iloc[i[0]].title for i in movies_list]
    except Exception:
        return []

# --- Display Movies with Filters ---
def filter_movies():
    df = movies.copy()
    genre = st.session_state.get('filter_genre', '-- Select Genre --')
    actor = st.session_state.get('filter_actor', '-- Select Actor --')
    director = st.session_state.get('filter_director', '-- Select Director --')
    years = st.session_state.get('filter_years')
    rating = st.session_state.get('filter_rating', 0.0)
    sort_by = st.session_state.get('filter_sort_by', 'popularity')
    if genre != "-- Select Genre --": df = df[df['genres_flat'].apply(lambda x: genre in x)]
    if actor != "-- Select Actor --": df = df[df['cast_flat'].apply(lambda x: actor in x)]
    if director != "-- Select Director --": df = df[df['director_flat'].apply(lambda x: director in x)]
    if years and 'year' in df.columns: df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
    if rating > 0: df = df[df['vote_average'] >= rating]
    if sort_by: df = df.sort_values(by=sort_by, ascending=False)
    return df

# --- Display Movie Cards ---
def display_movie_cards(movie_titles):
    cols = st.columns(5)
    for i, title in enumerate(movie_titles):
        with cols[i % 5]:
            encoded_title = urllib.parse.quote_plus(title)
            prev_view = st.session_state.view
            st.markdown(f"""
            <a href="?movie={encoded_title}&prev_view={prev_view}" target="_self" style="text-decoration: none;">
                <div class="movie-card">
                    <img class="movie-poster" src="{fetch_poster(title)}">
                    <div class="movie-title">{title}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- Sidebar Filters ---
with st.sidebar:
    st.selectbox("Genre", ["-- Select Genre --"] + genres, key='filter_genre')
    st.selectbox("Actor", ["-- Select Actor --"] + actors, key='filter_actor')
    st.selectbox("Director", ["-- Select Director --"] + directors, key='filter_director')
    if 'year' in movies.columns:
        year_min, year_max = int(movies['year'].min()), int(movies['year'].max())
        st.slider("Year Range", year_min, year_max, (year_min, year_max), key='filter_years')
    else:
        st.session_state.filter_years = None
    st.slider("Minimum Rating", 0.0, 10.0, 0.0, step=0.5, key='filter_rating')
    st.selectbox("Sort By", ["popularity", 'release_date', 'vote_average', 'weighted_rating'], key='filter_sort_by')
    if st.button("Apply Filters"):
        st.session_state.view = 'filtered_results'

# --- Main Header ---
st.markdown("<h1 class='main-header'>🎬 MovieMatch</h1>", unsafe_allow_html=True)

# --- Handle Query Params for Back Button ---
params = st.experimental_get_query_params()
if 'movie' in params:
    st.session_state.view = 'details'
    st.session_state.selected_movie = params['movie'][0]

# --- Display Pages ---
if st.session_state.view == 'home':
    st.write("Welcome! Apply filters from sidebar or click a movie for details.")
elif st.session_state.view == 'filtered_results':
    filtered = filter_movies()
    display_movie_cards(filtered['title'].tolist())
elif st.session_state.view == 'details' and st.session_state.selected_movie:
    movie_title = st.session_state.selected_movie
    st.markdown(f"<h2 style='text-align:center'>{movie_title}</h2>", unsafe_allow_html=True)
    st.image(fetch_poster(movie_title))
    st.markdown("<a href='?view=filtered_results' class='nav-btn back-btn'>🔙 Back</a>", unsafe_allow_html=True)
    st.write("Details and recommendations would go here.")
