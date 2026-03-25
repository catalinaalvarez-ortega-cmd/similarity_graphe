from code2 import construire_corpus
import itertools
import math
import numpy as np
import pandas as pd
import networkx as nx

from scipy.spatial.distance import cosine
from networkx.algorithms.community import greedy_modularity_communities
from pyvis.network import Network


def construire_vocabulaire(cooccurrences):
    return sorted(cooccurrences.keys())


def construire_vecteurs(cooccurrences, vocabulaire, min_contexte=3):
    """
    Transforme les compteurs de cooccurrences en vecteurs explicites.
    On ne garde que les mots ayant au moins min_contexte cooccurrences distinctes.
    """
    valid_terms = {}

    for mot, compteur in cooccurrences.items():
        if len(compteur) >= min_contexte:
            vecteur = np.array([compteur.get(contexte, 0) for contexte in vocabulaire], dtype=float)
            if np.linalg.norm(vecteur) > 0:
                valid_terms[mot] = vecteur

    return valid_terms


def generer_graphe_similarite(valid_terms, similarity_threshold=0.3):
    graph = nx.Graph()

    for term1, term2 in itertools.combinations(valid_terms.keys(), 2):
        vec1, vec2 = valid_terms[term1], valid_terms[term2]

        # Éviter les vecteurs nuls
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            continue

        similarity = 1 - cosine(vec1, vec2)

        if not math.isnan(similarity) and similarity >= similarity_threshold:
            graph.add_edge(term1, term2, weight=float(similarity))

    # Supprimer les nœuds isolés
    isolated_nodes = [node for node in graph.nodes() if graph.degree(node) == 0]
    graph.remove_nodes_from(isolated_nodes)

    return graph


def generate_color_palette(n):
    colors = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33A8",
        "#A833FF", "#33FFF2", "#FF8C00", "#FFD700"
    ]
    return [colors[i % len(colors)] for i in range(n)]


def visualiser_graphe(graph, term_frequencies, fichier_html="graph_similarite_cosinus.html"):
    communities = list(greedy_modularity_communities(graph))
    community_colors = generate_color_palette(len(communities))

    color_map = {}
    for i, community in enumerate(communities):
        for node in community:
            color_map[node] = community_colors[i]

    net = Network(
        notebook=False,
        height="800px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        directed=False
    )

    for node in graph.nodes():
        net.add_node(
            node,
            size=max(10, graph.degree(node) * 5),
            title=f"{node} : {term_frequencies.get(node, 0)} occurrences",
            label=node,
            color=color_map.get(node, "#FFFFFF"),
            borderWidth=3,
            shadow=True
        )

    for edge in graph.edges(data=True):
        weight = edge[2]["weight"]
        net.add_edge(
            edge[0],
            edge[1],
            value=weight * 5,
            color=f"rgba(255, 255, 255, {min(weight, 1.0)})",
            title=f"Score: {weight:.3f}"
        )

    net.show_buttons(filter_=["physics"])
    net.write_html(fichier_html)

    print(f"Graphe généré : {fichier_html}")


def exporter_similarites_csv(graph, fichier_csv="similarite_termes.csv"):
    similarity_data = []

    for edge in graph.edges(data=True):
        term1, term2, weight = edge[0], edge[1], edge[2]["weight"]
        similarity_data.append([term1, term2, round(weight, 3)])

    df_similarity = pd.DataFrame(
        similarity_data,
        columns=["Terme 1", "Terme 2", "Score Similarité"]
    )

    df_similarity.to_csv(fichier_csv, index=False, encoding="utf-8")
    print(f"CSV enregistré : {fichier_csv}")


if __name__ == "__main__":
    corpus_nettoye, corpus_tokenise, cooc_par_roman = construire_corpus()

    # Choix du roman et de la fenêtre
    roman = "proust.txt"
    fenetre = 5

    cooccurrences = cooc_par_roman[roman][fenetre]

    # Fréquences simples des termes = somme des cooccurrences sortantes
    term_frequencies = {
        mot: sum(compteur.values())
        for mot, compteur in cooccurrences.items()
    }

    vocabulaire = construire_vocabulaire(cooccurrences)
    valid_terms = construire_vecteurs(cooccurrences, vocabulaire, min_contexte=5)

    graph = generer_graphe_similarite(valid_terms, similarity_threshold=0.35)

    visualiser_graphe(
        graph,
        term_frequencies,
        fichier_html=f"graphe_{roman}_fenetre_{fenetre}.html"
    )

    exporter_similarites_csv(
        graph,
        fichier_csv=f"similarite_{roman}_fenetre_{fenetre}.csv"
    )

    