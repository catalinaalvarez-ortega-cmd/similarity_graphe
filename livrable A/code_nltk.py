from pathlib import Path
from urllib import request
from nltk.corpus import PlaintextCorpusReader

# créer le dossier s'il n'existe pas
Path("corpus_fr").mkdir(exist_ok=True)

urls = {
    "proust.txt": "https://www.gutenberg.org/cache/epub/2650/pg2650.txt",
    "cleves.txt": "https://www.gutenberg.org/cache/epub/20262/pg20262.txt",
    "dostoievski.txt": "https://www.gutenberg.org/cache/epub/15557/pg15557.txt",
    "flaubert.txt": "https://www.gutenberg.org/cache/epub/49773/pg49773.txt"
}

for nom_fichier, url in urls.items():
    texte = request.urlopen(url).read().decode("utf-8")
    Path("corpus_fr", nom_fichier).write_text(texte, encoding="utf-8")

corpus = PlaintextCorpusReader("corpus_fr", r".*\.txt")

print(corpus.fileids())
print(corpus.raw("cleves.txt")[:1000])