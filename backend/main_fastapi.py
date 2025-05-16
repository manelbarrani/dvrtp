
from dotenv import load_dotenv
import os
load_dotenv()

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from .schemas import SummaryRequest, SummaryResponse


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func
from typing import List

from . import database, models
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

# Pydantic Models
class ActorBase(BaseModel):
    actor_name: str

class MovieBase(BaseModel):
    title: str
    year: int
    director: str
    actors: List[ActorBase]

class ActorPublic(BaseModel):
    id: int
    actor_name: str
    class Config:
        orm_mode = True

class MoviePublic(BaseModel):
    id: int
    title: str
    year: int
    director: str
    actors: List[ActorPublic]
    class Config:
        orm_mode = True

# POST /movies/
@app.post("/movies/", response_model=MoviePublic)
def create_movie(movie: MovieBase, db: Session = Depends(database.get_db)):
    db_movie = models.Movies(
        title=movie.title,
        year=movie.year,
        director=movie.director
    )
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    for actor in movie.actors:
        db_actor = models.Actors(actor_name=actor.actor_name, movie_id=db_movie.id)
        db.add(db_actor)
    
    db.commit()
    db.refresh(db_movie)
    return db_movie

# GET /movies/random/
@app.get("/movies/random/", response_model=MoviePublic)
def get_random_movie(db: Session = Depends(database.get_db)):
    movie = db.query(models.Movies).options(joinedload(models.Movies.actors))\
        .order_by(func.random()).first()
    if not movie:
        raise HTTPException(status_code=404, detail="No movies found")
    return movie
@app.post("/generate_summary/", response_model=SummaryResponse)
def generate_summary(request: SummaryRequest, db: Session = Depends(get_db)):
    # Récupérer le film avec ses acteurs
    movie = db.query(models.Movies)\
        .options(joinedload(models.Movies.actors))\
        .filter(models.Movies.id == request.movie_id)\
        .first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Créer la liste des acteurs
    actor_names = ', '.join([actor.actor_name for actor in movie.actors])

    # Préparer le prompt
    prompt = PromptTemplate.from_template(
        "Generate a short, engaging summary for the movie '{title}' ({year}), directed by {director} and starring {actors}."
    )
    filled_prompt = prompt.format(
        title=movie.title,
        year=movie.year,
        director=movie.director,
        actors=actor_names
    )

    # Initialiser le modèle LLM
    groq_api_key = os.getenv("GROQ_API_KEY")
    llm = ChatGroq(temperature=0.7, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

    # Générer le résumé
    summary_text = llm.invoke(filled_prompt)

    return {"summary_text": summary_text}