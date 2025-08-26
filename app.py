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

# --- Enhanced CSS with Aurora Animation and Professional UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    /* --- Base & Background --- */
    .stApp {
        background-color: #000 !important;
        color: #fff !important;
        font-family: 'Poppins', sans-serif !important;
    }

    /* --- Aurora Background Animation --- */
    .aurora-container {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1;
        pointer-events: none;
    }
    .aurora {
        position: absolute;
        border-radius: 50%;
        mix-blend-mode: screen;
        animation: aurora-anim 12s infinite linear;
    }
    @keyframes aurora-anim {
        0% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
        50% { transform: translate(50%, 50%) scale(1.5); opacity: 0.3; }
        100% { transform: translate(-50%, -50%) scale(1); opacity: 0.5; }
    }
    .aurora-1 { width: 80vmax; height: 80vmax; top: 50%; left: 50%; background: radial-gradient(circle, #00f2ea 0%, rgba(0,242,234,0) 70%); animation-duration: 15s; }
    .aurora-2 { width: 60vmax; height: 60vmax; top: 20%; left: 20%; background: radial-gradient(circle, #8f94fb 0%, rgba(143,148,251,0) 70%); animation-duration: 12s; animation-direction: reverse; }
    .aurora-3 { width: 70vmax; height: 70vmax; top: 80%; left: 80%; background: radial-gradient(circle, #4e54c8 0%, rgba(78,84,200,0) 70%); animation-duration: 18s; }

    .starfall-container {
        position: fixed; top: 0; left: 0; width: 100vw; height: 120px;
        pointer-events: none; z-index: 100;
    }
    .star {
        position: absolute; border-radius: 50%; opacity: 0.7;
        width: 8px; height: 8px; animation: fall 3s linear infinite;
    }
    .star.s1 { left: 5vw; animation-duration: 1.3s; background: #ffd700; }
    .star.s2 { left: 15vw; animation-duration: 2s; background: #4a90e2; }
    .star.s3 { left: 25vw; animation-duration: 2.7s; background: #ff69b4; }
    .star.s4 { left: 35vw; animation-duration: 2.2s; background: #43c6ac; }
    .star.s5 { left: 45vw; animation-duration: 2.8s; background: #fff; }
    .star.s6 { left: 55vw; animation-duration: 2.4s; background: #ffd700; }
    .star.s7 { left: 65vw; animation-duration: 2s; background: #4a90e2; }
    .star.s8 { left: 75vw; animation-duration: 1.9s; background: #ff69b4; }
    .star.s9 { left: 85vw; animation-duration: 2.2s; background: #43c6ac; }
    .star.s10 { left: 95vw; animation-duration: 1.8s; background: #fff; }
    @keyframes fall {
        0% { top: 0; opacity: 0.8; }
        80% { opacity: 0.8; }
        100% { top: 110px; opacity: 0; }
    }

    /* --- Buttons & Interactive Elements --- */
    .stButton > button {
        border-radius: 8px; border: 1px solid #00f2ea;
        background-color: transparent; color: #00f2ea;
        transition: all 0.3s ease-in-out; padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #00f2ea; color: #1a1a2e;
        box-shadow: 0 0 15px #00f2ea;
    }
    .nav-btn {
        position: relative; display: inline-block;
        background: rgba(0,0,0,0.3); backdrop-filter: blur(5px);
        color: #fff; text-decoration: none; border-radius: 10px;
        padding: 0.5rem 1.5rem; font-weight: 600; z-index: 2000;
        border: 1px solid rgba(255,25,255,0.2); transition: all 0.2s ease-in-out;
    }
    .nav-btn:hover {
        background: rgba(0,242,234,0.8); box-shadow: 0 0 15px #00f2ea; color: #0f0c29;
    }
    .home-btn { top: 60px; left: 200px; }
    .back-btn { margin-bottom: 1rem; }

    /* --- Movie Cards --- */
    .movie-card {
        background: rgba(255,255,255,0.05); border-radius: 15px;
        padding: 1rem; margin: 10px 0; transition: all 0.3s ease;
        border: 1px solid transparent; min-height: 400px;
        backdrop-filter: blur(5px);
    }
    a:hover .movie-card {
        transform: translateY(-8px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        border-color: #00f2ea;
    }
    .movie-poster {
        border-radius: 10px; width: 100%; height: 250px;
        object-fit: cover; margin-bottom: 1rem;
    }
    .movie-title {
        font-weight: 600; font-size: 1.1rem; color: #fff;
        text-align: center; height: 3.3em; overflow: hidden;
    }

    /* --- Headers & Layout --- */
    .main-header {
        font-size: 3.5rem; text-align: center;
        background: linear-gradient(45deg, #8f94fb, #00f2ea);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        padding-top: 5rem; font-weight: 700;
    }
    .sidebar-header {
        font-size: 1.5rem; font-weight: 700; text-align: center;
        padding: 10px; background: rgba(0,242,234,0.1); border-radius: 10px;
        margin-bottom: 1.5rem;
    }

    /* --- Details Page --- */
    .details-container {
        position: relative; background: rgba(0,0,0,0.3);
        backdrop-filter: blur(10px); padding: 2rem; border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2); overflow: hidden;
    }
    .details-container::before {
        content: ''; position: absolute; top:0; left:0; right:0; bottom:0;
        background-image: var(--bg-image); background-size: cover;
        background-position: center; filter: blur(20px) brightness(0.4);
        transform: scale(1.2); z-index: -1;
    }

    /* --- Footer --- */
    .footer {
        text-align: center; padding: 2rem; margin-top: 3rem; color: #ccc;
        border-top: 1px solid #4e54c8;
    }
</style>

<div class="aurora-container">
    <div class="aurora aurora-1"></div>
    <div class="aurora aurora-2"></div>
    <div class="aurora aurora-3"></div>
</div>
<div class="starfall-container">
    <div class="star s1"></div><div class="star s2"></div>
    <div class="star s3"></div><div class="star s4"></div>
    <div class="star s5"></div><div class="star s6"></div>
    <div class="star s7"></div><div class="star s8"></div>
    <div class="star s9"></div><div class="star s10"></div>
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

# --- Session State Initialization ---
for key, default in {
    'view': 'home',
    'selected_movie': None,
    'current_page': 1,
    'previous_view': 'home',
    'previous_page': 1,
    'recommendations': [],
    'selected_for_rec': '',
    'top_movies': None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Query Params Helpers ---
def get_query_params():
    try:
        return dict(st.query_params)
    except:
        return st.experimental_get_query_params()

def set_query_params(**kwargs):
    try:
        for k, v in kwargs.items():
            st.query_params[k] = str(v)
    except:
        st.experimental_set_query_params(**kwargs)

# --- API Helpers ---
@st.cache_data
def fetch_poster(title):
    try:
        movie_id = movies[movies['title']==title]['movie_id'].iat[0]
        api_key = st.secrets["TMDB_API_KEY"]
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        data = requests.get(url).json()
        path = data.get('poster_path')
        if path:
            return "https://image.tmdb.org/t/p/w500/"+path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def fetch_movie_details(title):
    try:
        row = movies[movies['title']==title].iloc[0]
        return {
            'title': row['title'],
            'overview': " ".join(row.get('overview',[])) if isinstance(row.get('overview'),list) else row.get('overview','No overview'),
            'runtime': row.get('runtime','N/A'),
            'vote_average': row.get('vote_average',0),
            'genres': row.get('genres_flat',[]),
            'cast': row.get('cast_flat',[])[:5],
            'directors': row.get('director_flat',[]),
            'poster': fetch_poster(title)
        }
    except:
        return None

def recommend(title):
    try:
        idx = movies[movies['title']==title].index[0]
        sims = similarity[idx]
        top5 = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[1:6]
        return [movies.iloc[i[0]].title for i in top5]
    except:
        return []

def filter_movies_from_state():
    df = movies.copy()
    g = st.session_state.get('filter_genre','-- Select Genre --')
    a = st.session_state.get('filter_actor','-- Select Actor --')
    d = st.session_state.get('filter_director','-- Select Director --')
    yrs = st.session_state.get('filter_years')
    r = st.session_state.get('filter_rating',0.0)
    s = st.session_state.get('filter_sort_by','popularity')
    if g!="-- Select Genre --":
        df = df[df['genres_flat'].apply(lambda x: g in x if isinstance(x,list) else False)]
    if a!="-- Select Actor --":
        df = df[df['cast_flat'].apply(lambda x: a in x if isinstance(x,list) else False)]
    if d!="-- Select Director --":
        df = df[df['director_flat'].apply(lambda x: d in x if isinstance(x,list) else False)]
    if yrs and 'year' in df.columns:
        df = df[(df['year']>=yrs[0]) & (df['year']<=yrs[1])]
    if r>0:
        df = df[df['vote_average']>=r]
    if s:
        df = df.sort_values(by=s,ascending=False)
    return df

@st.cache_data
def get_top_movies(n=50, sort_by='weighted_rating'):
    return movies.sort_values(by=sort_by,ascending=False).head(n)

def display_movie_cards(titles):
    cols = st.columns(5)
    for i, t in enumerate(titles):
        with cols[i%5]:
            et = urllib.parse.quote_plus(t)
            pv = st.session_state.view
            pp = st.session_state.current_page
            st.markdown(f"""
                <a href="?movie={et}&prev_view={pv}&prev_page={pp}" style="text-decoration:none;">
                  <div class="movie-card">
                    <img class="movie-poster" src="{fetch_poster(t)}">
                    <div class="movie-title">{t}</div>
                  </div>
                </a>
            """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-header'>🔎 Filter Movies</h2>", unsafe_allow_html=True)
    st.selectbox("Genre", ["-- Select Genre --"]+genres, key='filter_genre')
    st.selectbox("Actor", ["-- Select Actor --"]+actors, key='filter_actor')
    st.selectbox("Director", ["-- Select Director --"]+directors, key='filter_director')
    if 'year' in movies.columns:
        mi, ma = int(movies['year'].min()), int(movies['year'].max())
        st.slider("Year Range", mi, ma, (mi,ma), key='filter_years')
    else:
        st.session_state.filter_years = None
    st.slider("Minimum Rating",0.0,10.0,0.0,step=0.5,key='filter_rating')
    st.selectbox("Sort By",["popularity",'release_date','vote_average','weighted_rating'],key='filter_sort_by')
    if st.button("Apply Filters"):
        set_query_params(view='filtered_results', page=1)
        st.rerun()
    st.markdown("<h2 class='sidebar-header'>🏆 Top Movies</h2>", unsafe_allow_html=True)
    if st.button("Show Top Movies"):
        st.session_state.top_movies = get_top_movies()
        set_query_params(view='top_movies', page=1)
        st.rerun()

# --- Main Content ---
st.markdown("<a href='/?view=home' class='nav-btn home-btn'>🏠 Home</a>", unsafe_allow_html=True)
st.markdown("<h1 class='main-header'>🎬 CineMatch</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Ultimate Movie Recommendation System</p>", unsafe_allow_html=True)

# --- Routing ---
params = get_query_params()
view = params.get('view',['home'])[0]
pg   = int(params.get('page',['1'])[0])
st.session_state.view = view
st.session_state.current_page = pg
if 'movie' in params:
    st.session_state.view = 'details'
    st.session_state.selected_movie = params['movie'][0]
    st.session_state.previous_view = params.get('prev_view',['home'])[0]
    st.session_state.previous_page = int(params.get('prev_page',['1'])[0])

# --- Display Logic ---
if st.session_state.view=='home':
    st.subheader("Get Instant Recommendations")
    sel = st.selectbox("Select a movie you like:", movies['title'].values, key="main_selector")
    if st.button("Get Recommendations"):
        st.session_state.recommendations = recommend(sel)
        st.session_state.selected_for_rec = sel
        st.rerun()
    if st.session_state.recommendations:
        st.subheader(f"Because you liked '{st.session_state.selected_for_rec}':")
        display_movie_cards(st.session_state.recommendations)
    st.markdown("---")
    st.subheader("🔥 Top Picks For Today")
    display_movie_cards(get_top_movies(n=5)['title'].tolist())

elif st.session_state.view=='top_movies':
    st.header("Top Rated Movies")
    df = st.session_state.top_movies or get_top_movies()
    npp = 10
    tot = math.ceil(len(df)/npp)
    p = st.session_state.current_page
    sub = df['title'].iloc[(p-1)*npp : p*npp].tolist()
    display_movie_cards(sub)
    c1,c2,c3=st.columns([3,1,3])
    if c1.button("⬅️ Previous",disabled=(p<=1)): 
        set_query_params(view='top_movies',page=p-1); st.rerun()
    c2.markdown(f"<div style='text-align:center;margin-top:0.5rem;'>Page {p} of {tot}</div>",unsafe_allow_html=True)
    if c3.button("Next ➡️",disabled=(p>=tot)): 
        set_query_params(view='top_movies',page=p+1); st.rerun()

elif st.session_state.view=='filtered_results':
    st.header("Filtered Movie Results")
    df = filter_movies_from_state()
    npp=10; tot=math.ceil(len(df)/npp)
    p=st.session_state.current_page
    sub=df['title'].iloc[(p-1)*npp:p*npp].tolist()
    if sub:
        display_movie_cards(sub)
        c1,c2,c3=st.columns([3,1,3])
        if c1.button("⬅️ Previous",disabled=(p<=1)): 
            set_query_params(view='filtered_results',page=p-1); st.rerun()
        c2.markdown(f"<div style='text-align:center;margin-top:0.5rem;'>Page {p} of {tot}</div>",unsafe_allow_html=True)
        if c3.button("Next ➡️",disabled=(p>=tot)): 
            set_query_params(view='filtered_results',page=p+1); st.rerun()
    else:
        st.warning("No movies found with the current filters.")

elif st.session_state.view=='details':
    title = urllib.parse.unquote_plus(st.session_state.selected_movie)
    details = fetch_movie_details(title)
    if details:
        if st.button("⬅️ Back to List",key="back"):
            set_query_params(view=st.session_state.previous_view,page=st.session_state.previous_page)
            st.rerun()
        st.markdown(f"<style>.details-container::before{{--bg-image:url({details['poster']});}}</style>",unsafe_allow_html=True)
        st.markdown('<div class="details-container">',unsafe_allow_html=True)
        col1,col2=st.columns([1,2])
        with col1:
            st.image(details['poster'], use_column_width=True)
        with col2:
            st.title(details['title'])
            st.markdown(f"**Rating:** ⭐ {details['vote_average']:.1f}/10")
            if details['runtime']!='N/A':
                st.markdown(f"**Runtime:** {details['runtime']} minutes")
            st.markdown(f"**Genres:** {', '.join(details['genres'])}")
            st.markdown(f"**Cast:** {', '.join(details['cast'])}")
            st.markdown(f"**Director(s):** {', '.join(details['directors'])}")
            st.subheader("Overview")
            st.write(details['overview'])
        st.markdown('</div>',unsafe_allow_html=True)
    else:
        st.error("Could not load movie details.")
        if st.button("⬅️ Back to Home"):
            set_query_params(view='home',page=1)
            st.rerun()

# --- Footer ---
st.markdown("""
<div class="footer">
    <p>Nikhil More | nikhil.030304@gmail.com</p>
    <p>CineMatch © 2025</p>
</div>
""", unsafe_allow_html=True)
