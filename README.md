Questions
 Comment formater la liste des acteurs récupérée depuis la base de données en une chaîne de texte simple pour l’inclure dans un prompt LLM ?
Tu peux convertir la liste des acteurs en une chaîne de noms séparés par des virgules :

python
Copier
Modifier
actor_names = ", ".join(actor.actor_name for actor in movie.actors)
Par exemple, si tu as trois acteurs :

python
Copier
Modifier
["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"]
Cela donne :

arduino
Copier
Modifier
"Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page"
✅ Cette chaîne peut ensuite être insérée dans un prompt LLM comme :

python
Copier
Modifier
f"Génère un résumé du film '{movie.title}' avec les acteurs {actor_names}."