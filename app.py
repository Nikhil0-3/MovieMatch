import pickle
import streamlit as st
import requests
import pandas as pd
import math
import urllib.parse

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="🎬 CineMatch - Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization ---
if 'view' not in st.session_state:
    st.session_state.view = 'home'
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'previous_view' not in st.session_state:
    st.session_state.previous_view = 'home'
if 'previous_page' not in st.session_state:
    st.session_state.previous_page = 1
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'selected_for_rec' not in st.session_state:
    st.session_state.selected_for_rec = ""
if 'top_movies' not in st.session_state:
    st.session_state.top_movies = None
if 'filtered_movies' not in st.session_state:
    st.session_state.filtered_movies = None

# --- Enhanced CSS with Aurora Animation and Professional UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, .stApp { background: #000!important; color: #fff!important; font-family: 'Poppins', sans-serif!important; }
    /* Aurora */
    .aurora { position: fixed; top:0; left:0; width:200%; height:200%; background: radial-gradient(circle,#00f2ea55 0%,transparent 70%); animation: move 15s infinite alternate; mix-blend-mode: screen; }
    @keyframes move { 0% { transform: translate(-25%, -25%) scale(1);} 100% { transform: translate(-50%, -50%) scale(1.2);} }
    /* Starfall */
    .star { position: fixed; top: -5px; width:4px; height:4px; background: #fff; border-radius:50%; animation: fall 4s linear infinite; opacity:.7; }
    .star:nth-child(1){ left:10%; animation-delay:0s;}
    .star:nth-child(2){ left:25%; animation-delay:1s;}
    .star:nth-child(3){ left:40%; animation-delay:2s;}
    .star:nth-child(4){ left:55%; animation-delay:.5s;}
    .star:nth-child(5){ left:70%; animation-delay:1.5s;}
    @keyframes fall {0%{top:-5px;}100%{top:110px;opacity:0;}}
    /* Nav buttons */
    .nav-btn{background:rgba(0,0,0,.3);backdrop-filter:blur(5px);color:#fff!important;
      text-decoration:none;border-radius:10px;padding:.5rem 1.5rem;font-weight:600;border:1px solid rgba(255,25,255,.2);}
    .nav-btn:hover{background:rgba(0,242,234,.8)!important;color:#0f0c29!important;}
    /* Headers */
    .main-header{font-size:3rem;text-align:center;
      background:linear-gradient(45deg,#8f94fb,#00f2ea);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
      margin-top:2rem;margin-bottom:1rem;font-weight:700;}
    /* Sidebar */
    .sidebar-header{font-size:1.3rem;font-weight:700;text-align:center;
      margin-bottom:1rem;padding:.5rem;background:rgba(0,242,234,.1);border-radius:10px;}
    /* Movie cards */
    .movie-card{background:rgba(255,255,255,.05);border-radius:15px;padding:1rem;margin:10px 0;
      transition:.3s;border:1px solid transparent;backdrop-filter:blur(5px);}
    .movie-card:hover{transform:translateY(-5px);box-shadow:0 8px 15px rgba(0,0,0,.4);border-color:#00f2ea;}
    .movie-title{font-weight:600;font-size:1.1rem;color:#fff;text-align:center;margin-top:.5rem;}
    /* Details */
    .details-container{background:rgba(0,0,0,.3);padding:2rem;border-radius:15px;
      margin-top:1rem;border:1px solid rgba(255,255,255,.2);}
    /* Footer */
    .footer{text-align:center;padding:2rem;margin-top:2rem;color:#ccc;border-top:1px solid #4e54c8;}
</style>
<div class="aurora"></div>
<div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div><div class="star"></div>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_resource
def load_data():
    try:
        movies = pickle.load(open('movies_full.pkl', 'rb'))
        similarity = pickle.load(open('similarity.pkl', 'rb'))
        genres = pickle.load(open('genres.pkl', 'rb'))
        actors = pickle.load(open('actors.pkl', 'rb'))
        directors = pickle.load(open('directors.pkl', 'rb'))
        
        if 'year' not in movies.columns and 'release_date' in movies.columns:
            movies['year'] = pd.to_datetime(movies['release_date'], errors='coerce').dt.year
            
        return movies, similarity, genres, actors, directors
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None, None

movies, similarity, genres, actors, directors = load_data()

# Check if data loaded successfully
if movies is None:
    st.error("Failed to load data. Please check your data files.")
    st.stop()

# --- API & Helper Functions ---
@st.cache_data
def fetch_poster(movie_title):
    try:
        # Use secrets for API key
        api_key = st.secrets["TMDB_API_KEY"]
        movie_id = movies[movies['title'] == movie_title]['movie_id'].values[0]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception as e:
        st.error(f"Error fetching poster: {str(e)}")
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_movie_details(movie_title):
    try:
        movie_data = movies[movies['title'] == movie_title].iloc[0]
        return {
            'title': movie_data['title'],
            'overview': (
                " ".join(movie_data.get('overview', []))
                if isinstance(movie_data.get('overview'), list)
                else movie_data.get('overview', 'No overview available.')
            ),
            'release_date': movie_data.get('release_date', 'N/A'),
            'runtime': movie_data.get('runtime', 'N/A'),
            'vote_average': movie_data.get('vote_average', 0),
            'genres': movie_data.get('genres_flat', []),
            'cast': movie_data.get('cast_flat', [])[:5],
            'directors': movie_data.get('director_flat', []),
            'poster': fetch_poster(movie_title)
        }
    except IndexError:
        return None

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:6]
        return [movies.iloc[i[0]].title for i in movies_list]
    except Exception:
        return []

def filter_movies_from_state():
    df = movies.copy()
    genre = st.session_state.get('filter_genre', '-- Select Genre --')
    actor = st.session_state.get('filter_actor', '-- Select Actor --')
    director = st.session_state.get('filter_director', '-- Select Director --')
    years = st.session_state.get('filter_years')
    rating = st.session_state.get('filter_rating', 0.0)
    sort_by = st.session_state.get('filter_sort_by', 'popularity')

    if genre != "-- Select Genre --":
        df = df[df['genres_flat'].apply(lambda x: genre in x if isinstance(x, list) else False)]
    if actor != "-- Select Actor --":
        df = df[df['cast_flat'].apply(lambda x: actor in x if isinstance(x, list) else False)]
    if director != "-- Select Director --":
        df = df[df['director_flat'].apply(lambda x: director in x if isinstance(x, list) else False)]
    if years and 'year' in df.columns:
        df = df[(df['year'] >= years[0]) & (df['year'] <= years[1])]
    if rating > 0:
        df = df[df['vote_average'] >= rating]
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=False)

    return df

@st.cache_data
def get_top_movies(n=50, sort_by='weighted_rating'):
    return movies.sort_values(by=sort_by, ascending=False).head(n)

# --- UI Display Functions ---
def display_movie_cards(movie_titles):
    cols = st.columns(5)
    for i, title in enumerate(movie_titles):
        with cols[i % 5]:
            encoded_title = urllib.parse.quote_plus(title)
            prev_view = st.session_state.get('view', 'home')
            prev_page = st.session_state.get('current_page', 1)
            
            st.markdown(f"""
            <a href="?movie={encoded_title}&prev_view={prev_view}&prev_page={prev_page}" target="_self" style="text-decoration: none;">
                <div class="movie-card">
                    <img class="movie-poster" src="{fetch_poster(title)}" style="width: 100%; height: 250px; object-fit: cover; border-radius: 10px; margin-bottom: 1rem;">
                    <div class="movie-title">{title}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-header'>🔎 Filter Movies</h2>", unsafe_allow_html=True)
    
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
        st.session_state.filtered_movies = filter_movies_from_state()
        st.session_state.view = 'filtered_results'
        st.session_state.current_page = 1

    st.markdown("<h2 class='sidebar-header'>🏆 Top Movies</h2>", unsafe_allow_html=True)
    if st.button("Show Top Movies"):
        st.session_state.top_movies = get_top_movies()
        st.session_state.view = 'top_movies'
        st.session_state.current_page = 1

# --- Main Page Content ---
st.markdown("<a href='/?view=home' target='_self' class='nav-btn home-btn'>🏠 Home</a>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>🎬 CineMatch</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Your Ultimate Movie Recommendation System</p>", unsafe_allow_html=True)

# --- View Routing Logic ---
# Use experimental_get_query_params for Streamlit compatibility
params = st.experimental_get_query_params()

# Update session state from query parameters
if 'view' in params:
    st.session_state.view = params['view'][0]
if 'page' in params:
    st.session_state.current_page = int(params['page'][0])
if 'movie' in params:
    st.session_state.view = 'details'
    st.session_state.selected_movie = params['movie'][0]
    if 'prev_view' in params:
        st.session_state.previous_view = params['prev_view'][0]
    if 'prev_page' in params:
        st.session_state.previous_page = int(params['prev_page'][0])

# --- Page Display Logic ---
if st.session_state.view == 'home':
    st.subheader("Get Instant Recommendations")
    selected_movie_name = st.selectbox("Select a movie you like:", movies['title'].values, key="main_selector")
    if st.button('Get Recommendations'):
        st.session_state.recommendations = recommend(selected_movie_name)
        st.session_state.selected_for_rec = selected_movie_name

    if st.session_state.recommendations:
        st.subheader(f"Because you liked '{st.session_state.selected_for_rec}':")
        display_movie_cards(st.session_state.recommendations)

    st.markdown("---")
    st.subheader("🔥 Top Picks For Today")
    top_picks = get_top_movies(n=5)
    display_movie_cards(top_picks['title'].tolist())

elif st.session_state.view == 'top_movies':
    st.header("Top Rated Movies")
    
    # Fix for pandas truth value error
    if st.session_state.top_movies is None:
        movie_df = get_top_movies()
    else:
        movie_df = st.session_state.top_movies
        
    if not movie_df.empty:
        MOVIES_PER_PAGE = 10
        total_pages = math.ceil(len(movie_df) / MOVIES_PER_PAGE)
        page = st.session_state.current_page
        start_idx = (page - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE
        paginated_titles = movie_df['title'].iloc[start_idx:end_idx].tolist()

        display_movie_cards(paginated_titles)
        
        # Pagination controls
        c1, c2, c3 = st.columns([3, 1, 3])
        if c1.button("⬅️ Previous", use_container_width=True, disabled=(page <= 1)):
            st.session_state.current_page = page - 1
            st.experimental_set_query_params(view='top_movies', page=str(st.session_state.current_page))
        c2.markdown(f"<div style='text-align: center; margin-top: 0.5rem;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
        if c3.button("Next ➡️", use_container_width=True, disabled=(page >= total_pages)):
            st.session_state.current_page = page + 1
            st.experimental_set_query_params(view='top_movies', page=str(st.session_state.current_page))

elif st.session_state.view == 'filtered_results':
    st.header("Filtered Movie Results")
    
    # Get filtered movies
    if st.session_state.filtered_movies is None:
        filtered_df = filter_movies_from_state()
        st.session_state.filtered_movies = filtered_df
    else:
        filtered_df = st.session_state.filtered_movies
    
    if not filtered_df.empty:
        MOVIES_PER_PAGE = 10
        total_pages = math.ceil(len(filtered_df) / MOVIES_PER_PAGE)
        page = st.session_state.current_page
        start_idx = (page - 1) * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE
        paginated_titles = filtered_df['title'].iloc[start_idx:end_idx].tolist()

        display_movie_cards(paginated_titles)
        
        # Pagination controls
        c1, c2, c3 = st.columns([3, 1, 3])
        if c1.button("⬅️ Previous", use_container_width=True, disabled=(page <= 1)):
            st.session_state.current_page = page - 1
            st.experimental_set_query_params(view='filtered_results', page=str(st.session_state.current_page))
        c2.markdown(f"<div style='text-align: center; margin-top: 0.5rem;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
        if c3.button("Next ➡️", use_container_width=True, disabled=(page >= total_pages)):
            st.session_state.current_page = page + 1
            st.experimental_set_query_params(view='filtered_results', page=str(st.session_state.current_page))
    else:
        st.warning("No movies found with the current filters. Please try different options.")

elif st.session_state.view == 'details':
    # Decode the movie title from the URL
    decoded_movie_title = urllib.parse.unquote_plus(st.session_state.selected_movie)
    details = fetch_movie_details(decoded_movie_title)
    
    if details:
        back_view = st.session_state.get('previous_view', 'home')
        back_page = st.session_state.get('previous_page', 1)
        
        # Back button
        if st.button("⬅️ Back to List"):
            st.session_state.view = back_view
            st.session_state.current_page = back_page
            st.experimental_set_query_params(view=back_view, page=str(back_page))

        # Movie details
        st.markdown(f"""
        <div class="details-container">
            <div style="display: flex; gap: 2rem;">
                <div style="flex: 1;">
                    <img src="{details['poster']}" style="width: 100%; border-radius: 10px;">
                </div>
                <div style="flex: 2;">
                    <h1>{details['title']}</h1>
                    <p><strong>Rating:</strong> ⭐ {details['vote_average']:.1f}/10</p>
                    <p><strong>Release Date:</strong> {details['release_date']}</p>
                    <p><strong>Runtime:</strong> {details['runtime']} minutes</p>
                    <p><strong>Genres:</strong> {', '.join(details['genres'])}</p>
                    <p><strong>Cast:</strong> {', '.join(details['cast'])}</p>
                    <p><strong>Director(s):</strong> {', '.join(details['directors'])}</p>
                    <h3>Overview</h3>
                    <p>{details['overview']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("Could not load movie details.")
        if st.button("⬅️ Back to Home"):
            st.session_state.view = 'home'
            st.experimental_set_query_params(view='home')

# --- Footer ---
st.markdown(
    """
    <div class="footer">
        <p>Nikhil More | nikhil.030304@gmail.com</p>
        <p>CineMatch © 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)
