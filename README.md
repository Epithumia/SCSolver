SCSolver
========

Solveur pour le jeu [Saute-Canton](https://sautecanton.fr/)

Coming soon

Pré-requis
----------

 - Le [fichier des données de population des communes de France](https://www.insee.fr/fr/statistiques/4265429?sommaire=4265511#consulter) au format xls
 - Le [fichier des adjacences entre villes](https://www.data.gouv.fr/fr/datasets/liste-des-adjacences-des-communes-francaises/)

Version ligne de commande : l'installation devrait récupérer toutes les librairies nécessaires

Version Notebook :

 - Pandas
 - Geopandas
 - Folium
 - Le(s) [fichier(s) des contours des communes](https://www.data.gouv.fr/en/datasets/decoupage-administratif-communal-francais-issu-d-openstreetmap/) :
   - Soit *Export de janvier 2019* (plus léger et rapide)
   - Soit *Export simple du 1er janvier 2020* (plus lourd mais plus précis)
 - (Optionnel) Selenium
 - (Si Selenium) Geckodriver
 - (Si Selenium) Firefox

Installation
------------

```
git clone https://github.com/Epithumia/SCSolver.git
pip install SCSolver
```

Le NoteBook se trouve dans le Dossier SCSolver/NoteBook dans une future révision

Utilisation
-----------

Usage: scsolver \[-p POPULATION_CIBLE>\] \[-s VOISIN\] <fichier donnees insee.xls> <fichier adjacences.csv> <ville de départ>

Options:
  -p POPULATION_CIBLE  Population cible (défaut : 50000).
  -s                   Ne retourner qu'un solution.
  -n VOISIN            Aide à identifier la commune en cas d'homonymes.
  -v                   Affiche la progression.
  -h, --help           Affiche ce message d'aide et termine.

Exemple :

```
scsolver -v ensemble.xls adjacences.csv Nérac -p 40000
```
