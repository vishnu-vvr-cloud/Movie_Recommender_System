import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def fetch_poster_retry(movie_id):
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get('https://api.themoviedb.org/3/movie/{}?api_key=6c7425b7c5cc64bafce75604b521dd6b&language=en-US'.format(movie_id))
        response.raise_for_status()
        data = response.json()
        return "https://image.tmdb.org/t/p/original" + data['poster_path']
    except requests.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return None

def recommend(movie, movies, similarity):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    recommended_movies_poster = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster_retry(movie_id))
    return recommended_movies, recommended_movies_poster

# Load data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title('Movie Recommender System')
selected_movie_name = st.selectbox('Can I suggest some movies?', movies['title'].values)

if st.button('Search'):
    names, posters = recommend(selected_movie_name, movies, similarity)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                st.text("No poster available")
