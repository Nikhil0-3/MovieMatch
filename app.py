import pickle
import streamlit as st
import requests
import pandas as pd
import math
import urllib.parse

# ——— Page configuration ———
st.set_page_config(
    page_title="🎬 CineMatch",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ——— CSS & Animated background ———
st.markdown(
    """
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
    """,
    unsafe_allow_html=True,
)

# ——— Load data ———
@st.cache_resource
def load_data():
    m = pickle.load(open("movies_full.pkl","rb"))
    s = pickle.load(open("similarity.pkl","rb"))
    g = pickle.load(open("genres.pkl","rb"))
    a = pickle.load(open("actors.pkl","rb"))
    d = pickle.load(open("directors.pkl","rb"))
    if "year" not in m.columns and "release_date" in m.columns:
        m["year"] = pd.to_datetime(m["release_date"],errors="coerce").dt.year
    return m, s, g, a, d

movies, similarity, genres, actors, directors = load_data()

# ——— Session defaults ———
defaults = {
  "view":"home","movie":None,"page":1,
  "prev_view":"home","prev_page":1,
  "recs":[],"selected":None,
  "filt_df":None,"top_df":None
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ——— Query param helpers ———
def get_qp():
    try: return dict(st.query_params)
    except: return st.experimental_get_query_params()
def set_qp(**kw):
    try:
        for k,v in kw.items():
            st.query_params[k]=str(v)
    except:
        st.experimental_set_query_params(**kw)

# ——— API helpers ———
@st.cache_data
def poster(title):
    try:
        mid = movies[movies.title==title].movie_id.iloc[0]
        key = st.secrets["TMDB_API_KEY"]
        data = requests.get(f"https://api.themoviedb.org/3/movie/{mid}?api_key={key}&language=en-US").json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500/"+data["poster_path"]
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def details(title):
    try:
        r = movies[movies.title==title].iloc[0]
        return {
          "title":r.title,
          "overview":(" ".join(r.overview) if isinstance(r.overview,list) else r.overview or "No overview"),
          "runtime":r.runtime or "N/A","vote":r.vote_average or 0,
          "genres":r.genres_flat,"cast":r.cast_flat[:5],"dir":r.director_flat,
          "poster":poster(title)
        }
    except:
        return None

def recommend_list(title):
    try:
        idx = movies[movies.title==title].index[0]
        sims = similarity[idx]
        top = sorted(enumerate(sims),key=lambda x:x[1],reverse=True)[1:6]
        return [movies.iloc[i[0]].title for i in top]
    except:
        return []

def filter_df():
    df = movies.copy()
    g = st.session_state.get("filter_genre")
    a = st.session_state.get("filter_actor")
    d = st.session_state.get("filter_director")
    yrs = st.session_state.get("filter_years")
    r = st.session_state.get("filter_rating")
    s = st.session_state.get("filter_sort_by")
    if g and g!="-- Select Genre --":
        df=df[df.genres_flat.apply(lambda x:g in x)]
    if a and a!="-- Select Actor --":
        df=df[df.cast_flat.apply(lambda x:a in x)]
    if d and d!="-- Select Director --":
        df=df[df.director_flat.apply(lambda x:d in x)]
    if yrs:
        df=df[(df.year>=yrs[0])&(df.year<=yrs[1])]
    if r>0:
        df=df[df.vote_average>=r]
    if s:
        df=df.sort_values(s,ascending=False)
    return df

@st.cache_data
def get_top(n=50,sort_by="weighted_rating"):
    return movies.sort_values(sort_by,ascending=False).head(n)

def show_cards(titles):
    cols = st.columns(5)
    for i,t in enumerate(titles):
        with cols[i%5]:
            url_title = urllib.parse.quote_plus(t)
            prev = st.session_state.view
            prevp=st.session_state.page
            st.markdown(f"""
              <a href="/?view=details&movie={url_title}&prev_view={prev}&prev_page={prevp}" class="movie-card" style="text-decoration:none;">
                <img src="{poster(t)}" style="width:100%;height:250px;border-radius:10px;"><div class="movie-title">{t}</div>
              </a>
            """,unsafe_allow_html=True)

# ——— Sidebar ———
with st.sidebar:
    st.markdown("<div class='sidebar-header'>🔎 Filter Movies</div>",unsafe_allow_html=True)
    st.selectbox("Genre",["-- Select Genre --"]+genres,key="filter_genre")
    st.selectbox("Actor",["-- Select Actor --"]+actors,key="filter_actor")
    st.selectbox("Director",["-- Select Director --"]+directors,key="filter_director")
    if "year" in movies.columns:
        mn,mx=movies.year.min(),movies.year.max()
        st.slider("Year Range",int(mn),int(mx),(int(mn),int(mx)),key="filter_years")
    else:
        st.session_state.filter_years=None
    st.slider("Minimum Rating",0.0,10.0,0.0,0.5,key="filter_rating")
    st.selectbox("Sort By",["popularity","release_date","vote_average","weighted_rating"],key="filter_sort_by")
    if st.button("Apply Filters"):
        st.session_state.filt_df = filter_df()
        set_qp(view="filtered_results",page=1)
        st.experimental_rerun()
    st.markdown("<div class='sidebar-header'>🏆 Top Movies</div>",unsafe_allow_html=True)
    if st.button("Show Top Movies"):
        st.session_state.top_df = get_top()
        set_qp(view="top_movies",page=1)
        st.experimental_rerun()

# ——— Header & Home ———
st.markdown(f"""<a href="/?view=home&page=1" class="nav-btn">🏠 Home</a>""",unsafe_allow_html=True)
st.markdown("<div class='main-header'>🎬 CineMatch</div>",unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your Ultimate Movie Recommendation System</p>",unsafe_allow_html=True)

# ——— Routing ———
qp = get_qp()
view = qp.get("view",["home"])[0]
page = int(qp.get("page",["1"])[0])
st.session_state.view=view
st.session_state.page=page

if view=="details" and "movie" in qp:
    st.session_state.movie=qp["movie"][0]
    st.session_state.prev_view=qp.get("prev_view",["home"])[0]
    st.session_state.prev_page=int(qp.get("prev_page",["1"])[0])

# ——— Content ———
if st.session_state.view=="home":
    st.subheader("Get Instant Recommendations")
    choice = st.selectbox("Choose a movie:",movies.title.values,key="main_sel")
    if st.button("Get Recommendations"):
        st.session_state.recs = recommend_list(choice)
        st.session_state.selected = choice
        st.experimental_rerun()
    if st.session_state.recs:
        st.subheader(f"Because you liked '{st.session_state.selected}':")
        show_cards(st.session_state.recs)
    st.markdown("---")
    st.subheader("🔥 Top Picks For Today")
    show_cards(get_top(n=5).title.tolist())

elif st.session_state.view=="top_movies":
    st.header("Top Rated Movies")
    df=st.session_state.top_df or get_top()
    per=10; total=math.ceil(len(df)/per); p=st.session_state.page
    subset=df.title.iloc[(p-1)*per:p*per].tolist()
    show_cards(subset)
    c1,c2,c3=st.columns([3,1,3])
    if c1.button("⬅️ Prev",disabled=p<=1):
        set_qp(view="top_movies",page=p-1);st.experimental_rerun()
    c2.markdown(f"Page {p} of {total}")
    if c3.button("Next ➡️",disabled=p>=total):
        set_qp(view="top_movies",page=p+1);st.experimental_rerun()

elif st.session_state.view=="filtered_results":
    st.header("Filtered Movie Results")
    df = st.session_state.filt_df or filter_df()
    per=10; total=math.ceil(len(df)/per); p=st.session_state.page
    subset=df.title.iloc[(p-1)*per:p*per].tolist()
    if subset:
        show_cards(subset)
        c1,c2,c3=st.columns([3,1,3])
        if c1.button("⬅️ Prev",disabled=p<=1):
            set_qp(view="filtered_results",page=p-1);st.experimental_rerun()
        c2.markdown(f"Page {p} of {total}")
        if c3.button("Next ➡️",disabled=p>=total):
            set_qp(view="filtered_results",page=p+1);st.experimental_rerun()
    else:
        st.warning("No movies found.")

elif st.session_state.view=="details":
    d = details(st.session_state.movie)
    if d:
        if st.button("⬅️ Back to List"):
            set_qp(view=st.session_state.prev_view,page=st.session_state.prev_page)
            st.experimental_rerun()
        st.markdown(f"""<div class='details-container'>
          <img src="{d['poster']}" style="width:200px;border-radius:10px;float:left;margin-right:1rem;">
          <h2 style="color:#fff;">{d['title']}</h2>
          <p><strong>Rating:</strong> ⭐ {d['vote']:.1f}/10 &nbsp;
             <strong>Runtime:</strong> {d['runtime']} mins</p>
          <p><strong>Genres:</strong> {", ".join(d['genres'])}</p>
          <p><strong>Cast:</strong> {", ".join(d['cast'])}</p>
          <p><strong>Director(s):</strong> {", ".join(d['dir'])}</p>
          <h3>Overview</h3><p>{d['overview']}</p>
        </div>""",unsafe_allow_html=True)
    else:
        st.error("Details not available.")

# ——— Footer ———
st.markdown(
    """<div class='footer'>
         <p>Nikhil More | nikhil.030304@gmail.com</p>
         <p>© CineMatch 2025</p>
       </div>""",
    unsafe_allow_html=True
)
