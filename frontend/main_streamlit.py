import streamlit as st
import requests

# URL de ton backend FastAPI
API_URL = "http://localhost:8000"

st.set_page_config(page_title="🎬 Movie Explorer", page_icon="🎥")

st.title("🎬 Movie Explorer")
st.write("Clique sur un bouton pour explorer un film aléatoire et obtenir un résumé généré par IA !")

# Initialisation du state
if "movie" not in st.session_state:
    st.session_state.movie = None
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Bouton pour afficher un film aléatoire
if st.button("🎲 Show Random Movie"):
    try:
        response = requests.get(f"{API_URL}/movies/random/")
        if response.status_code == 200:
            st.session_state.movie = response.json()
            st.session_state.summary = ""  # reset summary
        else:
            st.error("❌ Impossible de récupérer un film aléatoire.")
    except Exception as e:
        st.error(f"Erreur de requête : {e}")

# Afficher le film si présent
if st.session_state.movie:
    movie = st.session_state.movie
    st.header(f"{movie['title']} ({movie['year']})")
    st.subheader(f"🎬 Directed by {movie['director']}")

    st.markdown("**Actors:**")
    for actor in movie["actors"]:
        st.markdown(f"- {actor['actor_name']}")

    # Bouton pour générer le résumé
    if st.button("🧠 Get Summary"):
        try:
            payload = {"movie_id": movie["id"]}
            res = requests.post(f"{API_URL}/generate_summary/", json=payload)
            if res.status_code == 200:
                st.session_state.summary = res.json()["summary_text"]
            else:
                st.error("❌ Erreur lors de la génération du résumé.")
        except Exception as e:
            st.error(f"Erreur de requête : {e}")

# Afficher le résumé
if st.session_state.summary:
    st.subheader("💡 Summary")
    st.info(st.session_state.summary)
