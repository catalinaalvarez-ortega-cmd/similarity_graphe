from pathlib import Path
import spacy
from collections import defaultdict, Counter
import math
import csv


"""Nettoyer les fichiers Project Gutenberg avant la segmentation."""

def nettoyer_gutenberg(chemin_fichier, debut_reel=None):
    texte = Path(chemin_fichier).read_text(encoding="utf-8")
    
    # Recherche des marqueurs de début et de fin Project Gutenberg
    debut = texte.find("*** START OF THE PROJECT GUTENBERG EBOOK")
    if debut != -1:
        # Chercher le premier saut de ligne \n à partir de la position "debut".
        # On ajoute + 1 pour se placer juste après le saut de ligne"
        texte = texte[texte.find("\n", debut) + 1:]

    fin = texte.find("*** END OF THE PROJECT GUTENBERG EBOOK")
    if fin != -1:
        texte = texte[:fin]

    # Si un début réel du texte littéraire est fourni,
    # on supprime le paratexte restant jusqu'à ce point
    if debut_reel is not None:
        position = texte.find(debut_reel)
        if position != -1:
            texte = texte[position:]

    # Normalisation des blancs et les apostrophes dans le texte
    texte = " ".join(texte.split())
    texte = texte.replace("’", "'")

    return texte.strip()


# -------------- Segmentation et tokenization -------------- #

nlp = spacy.load("fr_core_news_sm")

def segmenter_et_tokeniser(texte):
    doc = nlp(texte)
    phrases_tokenisees = []

    for sent in doc.sents:
        tokens = [
            token.lemma_.lower()
            for token in sent
            if not token.is_stop
            and not token.is_punct
            and not token.is_space
            and token.is_alpha
            and token.pos_ in {"NOUN", "VERB", "ADJ", "PROPN"}
        ]
        phrases_tokenisees.append(tokens)

    return phrases_tokenisees


# ------------ coocurrences ----------------- #

def compter_cooccurrences(phrases_tokenisees, fenetre=2):
    cooccurrences = defaultdict(Counter)

    # On va traiter une phrase à la fois.
    for phrase in phrases_tokenisees:
        longueur = len(phrase)

        # On prend chaque mot de la phrase comme mot-cible.
        for i, mot_cible in enumerate(phrase):
            # Définit le bord gauche de la fenêtre, sans descendre sous 0.
            debut = max(0, i - fenetre)
            # ne depasse pas la longueur de la phrase
            fin = min(longueur, i + fenetre + 1)

            for j in range(debut, fin):
                # On évite de compte le mot avec lui-même
                if j != i:
                    mot_contexte = phrase[j]
                    # Incrémentation du compteur de co-occurrence.
                    cooccurrences[mot_cible][mot_contexte] += 1

    return cooccurrences

# ---------------- frequence ---------------- #

def mots_frequents_texte(texte, top_n=20):
    doc = nlp(texte)

    mots_a_exclure = {"mme", "page"}
    verbes_trop_generaux = {"faire", "voir", "aller", "venir", "dire", "savoir"}

    lemmes = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and token.is_alpha
        and token.pos_ in {"NOUN", "VERB", "ADJ", "PROPN"}
        and token.lemma_.lower() not in mots_a_exclure
        and token.lemma_.lower() not in verbes_trop_generaux
        
    ]

    return Counter(lemmes).most_common(top_n)


# ------------ similarite cosinus ----------------- #

def similarite_cosinus(compteur1, compteur2):
    produit_scalaire = 0
    for mot in compteur1:
        if mot in compteur2:
            produit_scalaire += compteur1[mot] * compteur2[mot]

    norme1 = math.sqrt(sum(valeur ** 2 for valeur in compteur1.values()))
    norme2 = math.sqrt(sum(valeur ** 2 for valeur in compteur2.values()))

    if norme1 == 0 or norme2 == 0:
        return 0.0

    return produit_scalaire / (norme1 * norme2)


def voisins_proches(mot_cible, cooccurrences, top_n=20):
    if mot_cible not in cooccurrences:
        return []

    vecteur_cible = cooccurrences[mot_cible]
    scores = []

    for autre_mot, vecteur_autre in cooccurrences.items():
        if autre_mot != mot_cible:
            score = similarite_cosinus(vecteur_cible, vecteur_autre)
            scores.append((autre_mot, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_n]


def construire_corpus():
    debuts_reels = {
        "dostoievski.txt": "Sa retraite prise, mon oncle",
        "cleves.txt": "La magnificence et la galanterie",
        "proust.txt": "Longtemps, je me suis couché de bonne heure.",
        "flaubert.txt": "Le 15 septembre 1840, vers six heures du matin,"
    }

    fenetres = [2, 5, 20]

    corpus_nettoye = {}
    corpus_tokenise = {}
    cooc_par_roman = {}

    for nom_fichier, debut in debuts_reels.items():
        chemin = Path("corpus_fr") / nom_fichier
        texte = nettoyer_gutenberg(chemin, debut)
        corpus_nettoye[nom_fichier] = texte

        phrases_tokenisees = segmenter_et_tokeniser(texte)
        corpus_tokenise[nom_fichier] = phrases_tokenisees

        cooc_par_roman[nom_fichier] = {}

        for fenetre in fenetres:
            cooc_par_roman[nom_fichier][fenetre] = compter_cooccurrences(
                phrases_tokenisees,
                fenetre=fenetre
            )

    return corpus_nettoye, corpus_tokenise, cooc_par_roman


if __name__ == "__main__":
    corpus_nettoye, corpus_tokenise, cooc_par_roman = construire_corpus()


# ------------ création tableau des fenêtres --------------- #

mots_final = ["amour", "temps", "jalousie", "bonheur", "musique", "porte", "soleil", "femme", "colonel", "prince"]

with open("resultats_voisins.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["roman", "fenetre", "mot_cible", "voisin", "score"])

    for mot in mots_final:
        for nom_fichier in cooc_par_roman:
            for fenetre in [2, 5, 20]:
                cooc = cooc_par_roman[nom_fichier][fenetre]
                voisins = voisins_proches(mot, cooc, top_n=10)

                if voisins:
                    for voisin, score in voisins:
                        writer.writerow([nom_fichier, fenetre, mot, voisin, round(score, 4)])
                else:
                    writer.writerow([nom_fichier, fenetre, mot, "mot absent", ""])

