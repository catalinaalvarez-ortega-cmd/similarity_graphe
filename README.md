# Influence de la taille de la fenêtre sur des embeddings statiques par cooccurrences

## Présentation
Ce projet a été réalisé dans le cadre d’un travail en **sémantique distributionnelle**.  
L’objectif est d’observer l’influence de la **taille de la fenêtre de contexte** sur la construction de représentations lexicales fondées sur le **comptage de cooccurrences**.

Le projet repose sur deux volets :

- une **analyse principale** par comptage explicite des cooccurrences, avec calcul de la **similarité cosinus** entre mots ;
- une **variante complémentaire** avec des modèles **Word2Vec (Skip-gram)** entraînés sur les mêmes données prétraitées.

## Corpus
Le corpus est composé de quatre romans en français, récupérés au format texte brut puis nettoyés avant traitement.

## Structure du projet
- `code2.py` : pipeline principal
  - nettoyage des fichiers
  - segmentation en phrases
  - tokenisation et lemmatisation avec spaCy
  - filtrage des mots
  - calcul des cooccurrences pour plusieurs tailles de fenêtre
  - calcul de la similarité cosinus et extraction des voisins proches

- `vecteur.py` : variante complémentaire
  - entraînement de modèles Word2Vec
  - comparaison des voisinages selon plusieurs tailles de fenêtre

- `graphe.py` : visualisation exploratoire
  - construction d’un graphe de similarité entre termes
  - export HTML interactif
  - export CSV des relations de similarité


## Visualisation en graphe
Une visualisation complémentaire a été produite sous forme de **graphe de similarité cosinus** entre termes.  
Cette partie reste exploratoire et sert surtout à faire apparaître des regroupements lexicaux ou thématiques.

## Crédit
La partie liée à la **visualisation du graphe de similarité cosinus** s’inspire d’un script publié dans le dépôt GitHub **`stephane1109/Similarit-_cosinus`**, fichier `main.py`. :contentReference[oaicite:0]{index=0}

## Remarque
L’analyse principale du projet repose sur le **comptage explicite des cooccurrences**.  
Les variantes Word2Vec et le graphe de similarité sont proposées comme extensions complémentaires.
