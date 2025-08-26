import pickle
import streamlit as st
import requests
import pandas as pd
import math
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="🎬 CineMatch - Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS & Styling ---
st.markdown("""
<style>
  /* Ensure dark background and white text */
  html, body, .stApp {
    background-color: #000 !important;
    color: #fff !important;
  }
  /* Poppins font */
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
  .stApp { font-family: 'Poppins', sans-serif !important; }

  /* Navigation button styling */
  .nav-btn {
    background: rgba(0,0,0,0.3);
    backdrop-filter: blur(5px);
    color: #fff !important;
    text-decoration: none;
    border-radius: 10px;
    padding: 0.5rem 1.5rem;
    font-weight: 600;
    border: 1px solid rgba(255,25,255,0.2);
  }
  .nav-btn:hover {
    background: rgba(0,242,234,0.8) !important;
    color: #0f0c29 !important;
  }

  /* Movie card styling */
  .movie-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 1rem;
    margin: 10px 0;
    transition: 0.3s;
    border: 1px solid transparent;
    min-height: 400px;
    backdrop-filter: blur(5px);
  }
  .movie-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    border-color: #00f2ea;
  }
  .movie-poster {
    border-radius: 10px;
    width: 100%;
    height: 250px;
    object-fit: cover;
    margin-bottom: 1rem;
  }
  .movie-title {
    font-weight: 600;
    font-size: 1.1rem;
    color: #fff;
    text-align: center;
    margin-top: 0.5rem;
  }

  /* Header styling */
  .main-header {
    font-size: 3.5rem;
    text-align: center;
    background: linear-gradient(45deg, #8f94fb, #00f2ea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-top: 3rem;
    padding-bottom: 1rem;
    font-weight: 700;
  }

  /* Sidebar header styling */
  .sidebar-header {
    font-size: 1.5rem;
    font-weight: 700;
    text-align: center;
    padding: 10px;
    background: rgba(0,242,234,0.1);
    border-radius: 10px;
    margin-bottom: 1rem;
  }

  /* Details container styling */
  .details-container {
    position: relative;
    background: rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.2);
    margin-top: 1rem;
  }
  .details-poster {
    border-radius: 10px;
  }

  /* Footer */
  .footer {
    text-align: center;
    padding: 2rem;
    margin-top: 3rem;
    color: #ccc;
    border-top: 1px solid #4e54c8;
  }
</style>
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

# --- Session State Defaults ---
defaults = {
    'view': 'home',
    'selected_movie': None,
    'current_page': 1,
    'previous_view': 'home',
    'previous_page': 1,
    'recommendations': [],
    'selected_for_rec': '',
    'filtered_df': None,
    'top_movies_df': None
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Query Params Helpers ---
def get_qp():
    try:
        return dict(st.query_params)
    except:
        return st.experimental_get_query_params()

def set_qp(**kwargs):
    try:
        for k, v in kwargs.items():
            st.query_params[k] = str(v)
    except:
        st.experimental_set_query_params(**kwargs)

# --- API Helpers ---
@st.cache_data
def fetch_poster(title):
    try:
        movie_id = movies[movies['title'] == title]['movie_id'].iat[0]
        api_key = st.secrets["TMDB_API_KEY"]
        resp = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}"
            f"?api_key={api_key}&language=en-US"
        ).json()
        path = resp.get('poster_path')
        if path:
            return "https://image.tmdb.org/t/p/w500/" + path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_details(title):
    try:
        row = movies[movies['title'] == title].iloc[0]
        return {
            'title': row['title'],
            'overview': (
                " ".join(row.get('overview', []))
                if isinstance(row.get('overview'), list)
                else row.get('overview', 'No overview available.')
            ),
            'release_date': row.get('release_date', 'N/A'),
            'runtime': row.get('runtime', 'N/A'),
            'vote_average': row.get('vote_average', 0),
            'genres': row.get('genres_flat', []),
            'cast': row.get('cast_flat', [])[:5],
            'directors': row.get('director_flat', []),
            'poster': fetch_poster(title)
        }
    except:
        return None

def recommend_movies(title):
    try:
        idx = movies[movies['title'] == title].index[0]
        sims = similarity[idx]
        top_idxs = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[1:6]
        return [movies.iloc[i[0]].title for i in top_idxs]
    except:
        return []

def filter_movies():
    df = movies.copy()
    g = st.session_state.get('filter_genre', '-- Select Genre --')
    a = st.session_state.get('filter_actor', '-- Select Actor --')
    d = st.session_state.get('filter_director', '-- Select Director --')
    yrs = st.session_state.get('filter_years')
    r = st.session_state.get('filter_rating', 0.0)
    s = st.session_state.get('filter_sort_by', 'popularity')

    if g != "-- Select Genre --":
        df = df[df['genres_flat'].apply(lambda x: g in x if isinstance(x, list) else False)]
    if a != "-- Select Actor --":
        df = df[df['cast_flat'].apply(lambda x: a in x if isinstance(x, list) else False)]
    if d != "-- Select Director --":
        df = df[df['director_flat'].apply(lambda x: d in x if isinstance(x, list) else False)]
    if yrs:
        df = df[(df['year'] >= yrs[0]) & (df['year'] <= yrs[1])]
    if r > 0:
        df = df[df['vote_average'] >= r]
    if s:
        df = df.sort_values(by=s, ascending=False)
    return df

@st.cache_data
def get_top(n=50, sort_by='weighted_rating'):
    return movies.sort_values(by=sort_by, ascending=False).head(n)

def display_cards(titles):
    cols = st.columns(5)
    for i, t in enumerate(titles):
        with cols[i % 5]:
            st.markdown(f"""
                <div class="movie-card">
                  <img class="movie-poster" src="{fetch_poster(t)}">
                  <div class="movie-title">{t}</div>
                </div>
            """, unsafe_allow_html=True)

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("<div class='sidebar-header'>🔎 Filter Movies</div>", unsafe_allow_html=True)
    st.selectbox("Genre", ["-- Select Genre --"] + genres, key='filter_genre')
    st.selectbox("Actor", ["-- Select Actor --"] + actors, key='filter_actor')
    st.selectbox("Director", ["-- Select Director --"] + directors, key='filter_director')
    if 'year' in movies.columns:
        mn, mx = int(movies['year'].min()), int(movies['year'].max())
        st.slider("Year Range", mn, mx, (mn, mx), key='filter_years')
    else:
        st.session_state.filter_years = None
    st.slider("Minimum Rating", 0.0, 10.0, 0.0, 0.5, key='filter_rating')
    st.selectbox("Sort By", ["popularity", "release_date", "vote_average", "weighted_rating"], key='filter_sort_by')
    if st.button("Apply Filters"):
        set_qp(view='filtered_results', page=1)
        st.rerun()
    st.markdown("<div class='sidebar-header'>🏆 Top Movies</div>", unsafe_allow_html=True)
    if st.button("Show Top Movies"):
        st.session_state.top_movies_df = get_top()
        set_qp(view='top_movies', page=1)
        st.rerun()

# --- Main Header and Home Link ---
st.markdown("<a href='/?view=home&page=1' class='nav-btn home-btn'>🏠 Home</a>", unsafe_allow_html=True)
st.markdown("<div class='main-header'>🎬 CineMatch</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Ultimate Movie Recommendation System</p>", unsafe_allow_html=True)

# --- Routing Logic ---
qp = get_qp()
view = qp.get('view', ['home'])[0]
page = int(qp.get('page', ['1'])[0])
st.session_state.view = view
st.session_state.current_page = page

if 'movie' in qp:
    st.session_state.view = 'details'
    st.session_state.selected_movie = qp['movie'][0]
    st.session_state.previous_view = qp.get('prev_view', ['home'])[0]
    st.session_state.previous_page = int(qp.get('prev_page', ['1'])[0])

# --- Page Rendering ---
if st.session_state.view == 'home':
    st.subheader("Get Instant Recommendations")
    choice = st.selectbox("Select a movie you like:", movies['title'].values, key="main_selector")
    if st.button("Get Recommendations"):
        st.session_state.recommendations = recommend_movies(choice)
        st.session_state.selected_for_rec = choice
        st.rerun()
    if st.session_state.recommendations:
        st.subheader(f"Because you liked '{st.session_state.selected_for_rec}':")
        display_cards(st.session_state.recommendations)
    st.markdown("---")
    st.subheader("🔥 Top Picks For Today")
    display_cards(get_top(n=5)['title'].tolist())

elif st.session_state.view == 'top_movies':
    st.header("Top Rated Movies")
    df = st.session_state.top_movies_df if st.session_state.top_movies_df is not None else get_top()
    per = 10
    total = math.ceil(len(df) / per)
    p = st.session_state.current_page
    subset = df['title'].iloc[(p-1)*per : p*per].tolist()
    display_cards(subset)
    c1, c2, c3 = st.columns([3,1,3])
    if c1.button("⬅️ Previous", disabled=p<=1):
        set_qp(view='top_movies', page=p-1)
        st.rerun()
    c2.markdown(f"<div style='text-align:center;'>Page {p} of {total}</div>", unsafe_allow_html=True)
    if c3.button("Next ➡️", disabled=p>=total):
        set_qp(view='top_movies', page=p+1)
        st.rerun()

elif st.session_state.view == 'filtered_results':
    st.header("Filtered Movie Results")
    df = filter_movies()
    per = 10
    total = math.ceil(len(df) / per)
    p = st.session_state.current_page
    subset = df['title'].iloc[(p-1)*per : p*per].tolist()
    if subset:
        display_cards(subset)
        c1, c2, c3 = st.columns([3,1,3])
        if c1.button("⬅️ Previous", disabled=p<=1):
            set_qp(view='filtered_results', page=p-1)
            st.rerun()
        c2.markdown(f"<div style='text-align:center;'>Page {p} of {total}</div>", unsafe_allow_html=True)
        if c3.button("Next ➡️", disabled=p>=total):
            set_qp(view='filtered_results', page=p+1)
            st.rerun()
    else:
        st.warning("No movies found with current filters.")

elif st.session_state.view == 'details':
    details = fetch_details(st.session_state.selected_movie)
    if details:
        if st.button("⬅️ Back to List"):
            set_qp(view=st.session_state.previous_view, page=st.session_state.previous_page)
            st.rerun()
        st.markdown(f"<div class='details-container' style='--bg-image:url({details['poster']});'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(details['poster'], use_column_width=True, caption=None, clamp=False)
        with col2:
            st.title(details['title'])
            st.markdown(f"**Rating:** ⭐ {details['vote_average']:.1f}/10")
            if details['runtime'] != 'N/A':
                st.markdown(f"**Runtime:** {details['runtime']} minutes")
            st.markdown(f"**Genres:** {', '.join(details['genres'])}")
            st.markdown(f"**Cast:** {', '.join(details['cast'])}")
            st.markdown(f"**Director(s):** {', '.join(details['directors'])}")
            st.subheader("Overview")
            st.write(details['overview'])
    else:
        st.error("Could not load movie details.")
        if st.button("⬅️ Back to Home"):
            set_qp(view='home', page=1)
            st.rerun()

# --- Footer ---
st.markdown("""
<div class='footer'>
  <p>Nikhil More | nikhil.030304@gmail.com</p>
  <p>CineMatch © 2025</p>
</div>
""", unsafe_allow_html=True)
