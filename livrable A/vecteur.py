from gensim.models import Word2Vec
from code2 import construire_corpus

corpus_nettoye, corpus_tokenise, cooc_par_roman = construire_corpus()

fenetres = [2, 5, 10]
modeles_w2v = {}

for nom_fichier, phrases_tokenisees in corpus_tokenise.items():
    modeles_w2v[nom_fichier] = {}

    for fenetre in fenetres:
        modele = Word2Vec(
            sentences=phrases_tokenisees,
            vector_size=100,
            min_count=5,
            window=fenetre,
            sg=1,
            workers=3,
        )
        modeles_w2v[nom_fichier][fenetre] = modele

mot_test = "amour"

for nom_fichier in modeles_w2v:
    print(f"\n===== {nom_fichier} =====")
    for fenetre in fenetres:
        modele = modeles_w2v[nom_fichier][fenetre]
        if mot_test in modele.wv:
            print(f"Fenêtre {fenetre} : {modele.wv.most_similar(mot_test, topn=10)}")
        else:
            print(f"Fenêtre {fenetre} : mot absent")