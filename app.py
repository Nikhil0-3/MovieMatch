import pickle
import streamlit as st
import requests
import pandas as pd
import math
import urllib.parse

# --- Load TMDB API Key from Streamlit Secrets ---
TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")

# Page configuration
st.set_page_config(
    page_title="🎬 MovieMatch - Movie Recommendation System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Enhanced CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
.stApp { background-color: #000; color: #fff; font-family: 'Poppins', sans-serif; }
/* Aurora Animation & Stars */
.aurora-container { position: fixed; top:0; left:0; width:100vw; height:100vh; z-index:-1; pointer-events:none; }
.aurora { position:absolute; border-radius:50%; mix-blend-mode: screen; animation: aurora-anim 12s infinite linear; }
@keyframes aurora-anim {0% {transform: translate(-50%, -50%) scale(1); opacity:0.5;} 50% {transform: translate(50%,50%) scale(1.5); opacity:0.3;} 100% {transform: translate(-50%,-50%) scale(1); opacity:0.5;} }
.aurora-1 { width:80vmax; height:80vmax; top:50%; left:50%; background: radial-gradient(circle, #00f2ea 0%, rgba(0,242,234,0)70%); animation-duration:15s; }
.aurora-2 { width:60vmax; height:60vmax; top:20%; left:20%; background: radial-gradient(circle,#8f94fb 0%,rgba(143,148,251,0)70%); animation-duration:12s; animation-direction:reverse; }
.aurora-3 { width:70vmax; height:70vmax; top:80%; left:80%; background: radial-gradient(circle,#4e54c8 0%, rgba(78,84,200,0)70%); animation-duration:18s; }
.starfall-container { pointer-events:none; position:fixed; top:0; left:0; width:100vw; height:120px; z-index:100; }
.star { position:absolute; border-radius:50%; opacity:0.7; width:8px; height:8px; animation: fall 3s linear infinite; }
.star.s1 { left:5vw; animation-duration:1.3s; background:#ffd700;}
.star.s2 { left:15vw; animation-duration:2s; background:#4a90e2;}
.star.s3 { left:25vw; animation-duration:2.7s; background:#ff69b4;}
.star.s4 { left:35vw; animation-duration:2.2s; background:#43c6ac;}
.star.s5 { left:45vw; animation-duration:2.8s; background:#fff;}
.star.s6 { left:55vw; animation-duration:2.4s; background:#ffd700;}
.star.s7 { left:65vw; animation-duration:2s; background:#4a90e2;}
.star.s8 { left:75vw; animation-duration:1.9s; background:#ff69b4;}
.star.s9 { left:85vw; animation-duration:2.2s; background:#43c6ac;}
.star.s10 { left:95vw; animation-duration:1.8s; background:#fff;}
@keyframes fall {0% {top:0; opacity:0.8;} 80% {opacity:0.8;} 100% {top:110px; opacity:0;}}

/* Buttons */
.stButton > button { border-radius:8px; border:1px solid #00f2ea; background:transparent; color:#00f2ea; transition: all 0.3s ease-in-out; padding:0.5rem 1rem; }
.stButton > button:hover { background:#00f2ea; color:#1a1a2e; border-color:#00f2ea; box-shadow:0 0 15px #00f2ea; }
.nav-btn { background: rgba(0,0,0,0.3); backdrop-filter: blur(5px); color:white !important; text-decoration:none; border-radius:10px; padding:0.5rem 1.5rem; font-weight:600; cursor:pointer; z-index:2000; border:1px solid rgba(255,25,255,0.2); transition: all 0.2s ease-in-out; }
.nav-btn:hover { background: rgba(0,242,234,0.8); box-shadow:0 0 15px #00f2ea; color:#0f0c29 !important; }
.home-btn { top:60px; left:200px; } .back-btn { display:inline-block; margin-bottom:1rem; }

/* Movie Cards */
.movie-card { background: rgba(255,255,255,0.05); border-radius:15px; padding:1rem; margin:10px 0; transition:all 0.3s ease; border:1px solid transparent; min-height:400px; backdrop-filter: blur(5px); }
a:hover .movie-card { transform: translateY(-8px); box-shadow:0 10px 20px rgba(0,0,0,0.4); border-color:#00f2ea; }
.movie-poster { border-radius:10px; width:100%; height:250px; object-fit:cover; margin-bottom:1rem; }
.movie-title { font-weight:600; font-size:1.1rem; color:#fff; text-align:center; height:3.3em; overflow:hidden; }

/* Headers */
.main-header { font-size:3.5rem; text-align:center; background:linear-gradient(45deg,#8f94fb,#00f2ea); -webkit-background-clip:text; -webkit-text-fill-color:transparent; padding-top:5rem; font-weight:700; }
.sidebar-header { font-size:1.5rem; font-weight:700; margin-bottom:1.5rem; text-align:center; padding:10px; background: rgba(0,242,234,0.1); border-radius:10px; }

/* Details Page */
.details-container { position:relative; background:rgba(0,0,0,0.3); backdrop-filter:blur(10px); padding:2rem; border-radius:15px; border:1px solid rgba(255,255,255,0.2); overflow:hidden; }
.details-container::before { content: ''; position:absolute; top:0; left:0; right:0; bottom:0; background-image: var(--bg-image); background-size:cover; background-position:center; filter:blur(20px) brightness(0.4); z-index:-1; transform: scale(1.2); }

/* Footer */
.footer { text-align:center; padding:2rem; margin-top:3rem; color:#ccc; border-top:1px solid #4e54c8; }
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


# --- Load Data ---
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
for key, default in [('view', 'home'), ('selected_movie', None), ('current_page', 1)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Helper Functions ---
@st.cache_data
def fetch_poster(title):
    try:
        movie_id = movies[movies['title'] == title]['movie_id'].values[0]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except:
        pass
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_movie_details(title):
    try:
        movie_data = movies[movies['title']==title].iloc[0]
        return {
            'title': movie_data['title'],
            'overview': movie_data.get('overview','No overview available.'),
            'release_date': movie_data.get('release_date','N/A'),
            'runtime': movie_data.get('runtime','N/A'),
            'vote_average': movie_data.get('vote_average',0),
            'genres': movie_data.get('genres_flat',[]),
            'cast': movie_data.get('cast_flat',[])[:5],
            'directors': movie_data.get('director_flat',[]),
            'poster': fetch_poster(title)
        }
    except:
        return None

def recommend(movie):
    try:
        idx = movies[movies['title']==movie].index[0]
        dist = similarity[idx]
        recs = sorted(list(enumerate(dist)), reverse=True, key=lambda x:x[1])[1:6]
        return [movies.iloc[i[0]].title for i in recs]
    except:
        return []

def filter_movies_from_state():
    df = movies.copy()
    g = st.session_state.get('filter_genre',"-- Select Genre --")
    a = st.session_state.get('filter_actor',"-- Select Actor --")
    d = st.session_state.get('filter_director',"-- Select Director --")
    y = st.session_state.get('filter_years')
    r = st.session_state.get('filter_rating',0.0)
    s = st.session_state.get('filter_sort_by','popularity')
    if g!="-- Select Genre --": df = df[df['genres_flat'].apply(lambda x:g in x)]
    if a!="-- Select Actor --": df = df[df['cast_flat'].apply(lambda x:a in x)]
    if d!="-- Select Director --": df = df[df['director_flat'].apply(lambda x:d in x)]
    if y and 'year' in df.columns: df = df[(df['year']>=y[0]) & (df['year']<=y[1])]
    if r>0: df = df[df['vote_average']>=r]
    if s: df = df.sort_values(by=s,ascending=False)
    return df

@st.cache_data
def get_top_movies(n=50, sort_by='weighted_rating'):
    return movies.sort_values(by=sort_by, ascending=False).head(n)

def display_movie_cards(titles):
    cols = st.columns(5)
    for i,title in enumerate(titles):
        with cols[i%5]:
            encoded_title = urllib.parse.quote_plus(title)
            prev_view = st.session_state.get('view','home')
            prev_page = st.session_state.get('current_page',1)
            st.markdown(f"""
            <a href="?movie={encoded_title}&prev_view={prev_view}&prev_page={prev_page}" target="_self" style="text-decoration:none;">
                <div class="movie-card">
                    <img class="movie-poster" src="{fetch_poster(title)}">
                    <div class="movie-title">{title}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

# --- Sidebar Filters ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-header'>🔎 Filter Movies</h2>", unsafe_allow_html=True)
    st.selectbox("Genre", ["-- Select Genre --"] + genres, key='filter_genre')
    st.selectbox("Actor", ["-- Select Actor --"] + actors, key='filter_actor')
    st.selectbox("Director", ["-- Select Director --"] + directors, key='filter_director')
    if 'year' in movies.columns:
        st.slider("Year Range", int(movies['year'].min()), int(movies['year'].max()), (int(movies['year'].min()), int(movies['year'].max())), key='filter_years')
    else:
        st.session_state.filter_years = None
    st.slider("Minimum Rating", 0.0,10.0,0.0,step=0.5,key='filter_rating')
    st.selectbox("Sort By", ["popularity",'release_date','vote_average','weighted_rating'], key='filter_sort_by')
    if st.button("Apply Filters"):
        st.session_state.view='filtered_results'; st.session_state.current_page=1
    if st.button("Show Top Movies"):
        st.session_state.top_movies = get_top_movies(); st.session_state.view='top_movies'; st.session_state.current_page=1

# --- Main Content ---
st.markdown("<a href='/?view=home' target='_self' class='nav-btn home-btn'>🏠 Home</a>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>🎬 CineMatch</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Ultimate Movie Recommendation System</p>", unsafe_allow_html=True)

# --- Query Params ---
params = st.query_params
st.session_state.view = params.get('view',[st.session_state.view])[0]
st.session_state.current_page = int(params.get('page',[st.session_state.current_page])[0])
if 'movie' in params:
    st.session_state.view='details'
    st.session_state.selected_movie=params['movie'][0]
    st.session_state.previous_view = params.get('prev_view',['home'])[0]
    st.session_state.previous_page = int(params.get('prev_page',['1'])[0])

# --- Page Logic ---
if st.session_state.view=='home':
    st.subheader("Get Instant Recommendations")
    sel = st.selectbox("Select a movie you like:", movies['title'].values, key="main_selector")
    if st.button("Get Recommendations"):
        st.session_state.recommendations = recommend(sel)
        st.session_state.selected_for_rec = sel
    if 'recommendations' in st.session_state and st.session_state.recommendations:
        st.subheader(f"Because you liked '{st.session_state.selected_for_rec}':")
        display_movie_cards(st.session_state.recommendations)

    st.markdown("---")
    st.subheader("🔥 Top Picks For Today")
    display_movie_cards(get_top_movies(n=5)['title'].tolist())

elif st.session_state.view=='top_movies':
    df = st.session_state.get('top_movies', get_top_movies())
    MOVIES_PER_PAGE = 10
    total_pages = math.ceil(len(df)/MOVIES_PER_PAGE)
    page = st.session_state.current_page
    start, end = (page-1)*MOVIES_PER_PAGE, page*MOVIES_PER_PAGE
    display_movie_cards(df['title'].iloc[start:end].tolist())
    c1,c2,c3 = st.columns([3,1,3])
    if c1.button("⬅️ Previous", disabled=(page<=1)): st.query_params['page']=[str(page-1)]
    c2.markdown(f"<div style='text-align:center;margin-top:0.5rem;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
    if c3.button("Next ➡️", disabled=(page>=total_pages)): st.query_params['page']=[str(page+1)]

elif st.session_state.view=='filtered_results':
    st.header("Filtered Movie Results")
    filtered_df = filter_movies_from_state()
    if not filtered_df.empty:
        MOVIES_PER_PAGE=10
        total_pages = math.ceil(len(filtered_df)/MOVIES_PER_PAGE)
        page = st.session_state.current_page
        start,end = (page-1)*MOVIES_PER_PAGE, page*MOVIES_PER_PAGE
        display_movie_cards(filtered_df['title'].iloc[start:end].tolist())
        c1,c2,c3 = st.columns([3,1,3])
        if c1.button("⬅️ Previous", disabled=(page<=1)): st.query_params['page']=[str(page-1)]
        c2.markdown(f"<div style='text-align:center;margin-top:0.5rem;'>Page {page} of {total_pages}</div>", unsafe_allow_html=True)
        if c3.button("Next ➡️", disabled=(page>=total_pages)): st.query_params['page']=[str(page+1)]
    else:
        st.warning("No movies found with current filters. Please try different options.")

elif st.session_state.view=='details':
    details = fetch_movie_details(st.session_state.selected_movie)
    if details:
        st.markdown(f"<a href='/?view={st.session_state.previous_view}&page={st.session_state.previous_page}' target='_self' class='nav-btn back-btn'>⬅️ Back to List</a>", unsafe_allow_html=True)
        st.markdown(f"<style>.details-container::before{{--bg-image:url({details['poster']});}}</style>", unsafe_allow_html=True)
        with st.container():
            st.markdown('<div class="details-container">', unsafe_allow_html=True)
            col1,col2 = st.columns([1,2])
            with col1: st.image(details['poster'], use_container_width=True)
            with col2:
                st.title(details['title'])
                st.markdown(f"**Rating:** ⭐ {details['vote_average']:.1f}/10")
                if details['runtime'] != 'N/A': st.markdown(f"**Runtime:** {details['runtime']} mins")
                st.markdown(f"**Release Date:** {details['release_date']}")
                st.markdown(f"**Genres:** {', '.join(details['genres']) if details['genres'] else 'N/A'}")
                st.markdown(f"**Cast:** {', '.join(details['cast']) if details['cast'] else 'N/A'}")
                st.markdown(f"**Director(s):** {', '.join(details['directors']) if details['directors'] else 'N/A'}")
                st.markdown(f"**Overview:** {details['overview']}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("Movie details not found.")

# --- Footer ---
st.markdown('<div class="footer">Developed by Nikhil More | Powered by Streamlit & TMDB API</div>', unsafe_allow_html=True)
