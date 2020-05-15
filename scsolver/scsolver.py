#!/usr/bin/env python
# coding: utf-8
import logging
import optparse
from collections import deque

import geopandas as geo
import pandas as pd

log = logging.getLogger(__name__)


class VilleNotFound(Exception):
    pass


class VilleMultiples(Exception):
    pass


class MauvaiseExtension(Exception):
    pass


def check_suffixe_fichier(fichier, exts):
    from pathlib import Path
    suf = Path(fichier).suffix
    if suf not in exts:
        raise MauvaiseExtension('Format inconnu : ' + suf)


def bfs(init, data_villes, adj_matrix, pop=50000, toutes_solutions=False):
    # Pour trouver le plus court chemin (en nombre de sauts) : un BFS
    visited = {}
    solutions = []
    distance = 36000
    queue = deque()
    depart = init
    for v in adj_matrix[depart]:
        queue.appendleft([v])
    while len(queue) > 0:
        chemin = queue.pop()
        ville = chemin[-1]
        if ville['id'] not in visited and len(chemin) <= distance:
            try:
                voisin = data_villes.loc[ville['id']]
                if voisin['Population totale'] >= pop:
                    if toutes_solutions:
                        solutions.append(chemin)
                        distance = len(chemin)
                    else:
                        return [chemin]
                for v in adj_matrix[ville['id']]:
                    prochain = chemin[:]
                    prochain.append(v)
                    queue.appendleft(prochain)
            except KeyError:
                pass
            visited[ville['id']] = 1
    return solutions


def check_ville(ville, data_villes):
    c = data_villes.loc[data_villes['Nom de la commune'] == ville].shape[0]
    if c == 0:
        raise VilleNotFound("Ville introuvable")
    if c > 1:
        raise VilleMultiples(
            "Plusieurs villes (" + str(c) + ") trouvées, précisez la recherche avec l'option -n VILLE_VOISINE")


def solve(donnees, ville_depart, voisin, pop_cible, mono_sol, verbose=False):
    # Chargement des données
    insee, adjac, geofile = donnees
    # On charge les données INSEE pour avoir les populations
    if verbose:
        log.info("Chargement des données INSEE...")
    with open(insee, 'rb') as ensemble:
        data_villes = pd.read_excel(ensemble, 4, header=7,
                                    dtype={0: int, 3: int, 5: int, 7: int, 8: int, 9: int,
                                           1: str, 2: str, 4: str, 6: str})
        data_villes['code_insee'] = data_villes['Code département'] + data_villes['Code commune'].apply(
            lambda x: '{:03d}'.format(x))
        data_villes.set_index('code_insee', inplace=True)
    # On charge les adjacences entre villes
    if verbose:
        log.info("Chargement des données d'ajacence...")
    with open(adjac, 'r') as adjacence:
        pre_data_adj = pd.read_csv(adjacence)

    # On construit la matrice d'adjacence sous forme de dict

    adj_matrix = {}

    for index, row in pre_data_adj.iterrows():
        voisins = []
        liste_v = row['insee_voisins'].split('|')
        liste_cap = row['as$'].split('|')
        for i in range(row['nb_voisins']):
            voisins.append({'id': liste_v[i], 'cap': liste_cap[i]})
        adj_matrix[row['insee']] = voisins

    # On charge les données de géolocalisation
    if verbose:
        log.info("Chargement des données OSM...")
    geodata = geo.read_file(geofile)
    geodata.set_index('insee', inplace=True)
    geodata.crs = "EPSG:4326"

    # Résolution

    # On a les paramètres :
    #
    #  - **depart** : la ville d'où le joueur part
    #  - **population_cible** : la taille de ville qu'on vise
    #  - **toutes_solution** : est-ce que l'on veut afficher tous les chemins les plus courts ou juste le premier

    depart = ville_depart
    liste_id_start = []
    try:
        check_ville(depart, data_villes)
        liste_id_start.append(data_villes.loc[data_villes['Nom de la commune'] == depart].index.values[0])
    except VilleMultiples:
        if voisin is not None:
            check_ville(voisin, data_villes)
            id_voisin_pot = data_villes.loc[data_villes['Nom de la commune'] == voisin].index.values[0]
            for potentiel in adj_matrix[id_voisin_pot]:
                ville_pot = data_villes.loc[potentiel['id']]
                if ville_pot['Nom de la commune'] == depart:
                    liste_id_start.append(potentiel['id'])
            if len(liste_id_start) == 0:
                raise VilleNotFound("Villes non voisines")
        else:
            liste = data_villes.loc[data_villes['Nom de la commune'] == depart]
            for ville_pot in liste.iterrows():
                liste_id_start.append(ville_pot[0])

    population_cible = pop_cible
    toutes_solutions = not mono_sol

    # On résoud
    if len(liste_id_start) > 1:
        log.warning("Il y a plusieurs villes de départ possibles. "
                    "Pour n'en afficher qu'une, précisez la recherche avec l'option -n VILLE_VOISINE")
    for id_start in liste_id_start:

        chemins = bfs(id_start, data_villes, adj_matrix, population_cible, toutes_solutions)

        g_start = geodata.loc[id_start]['geometry']
        p_start = g_start.centroid

        # On construit le chemin

        chem_str_tab = []
        for chemin in chemins:
            chem_str = depart
            ants = [[p_start.y, p_start.x]]

            for ville in chemin:
                id = ville['id']
                g = geodata.loc[id]['geometry']
                p = g.centroid
                ants.append([p.y, p.x])
                data = data_villes.loc[id]
                nom = data['Nom de la commune']
                chem_str += '->' + nom

            chem_str_tab.append(chem_str)

        # Et le chemin solution est :

        for chem in chem_str_tab:
            print(chem)


def main():
    """
        Point d'entrée pour le découpage de fichier.

        :return: codes de sortie standards.
        """
    # noinspection SpellCheckingInspection
    usage = 'usage: %prog [-p POPULATION_CIBLE>] [-s VOISIN] <fichier donnees insee.xls> <fichier adjacences.csv> <fichier donnees geodata.(json|shp)> <ville de départ>'
    parser = optparse.OptionParser(usage=usage, add_help_option=False)
    parser.add_option('-p', dest="pop_cible", help="Population cible (défaut : 50000).", metavar="POPULATION_CIBLE",
                      default=50000, type=int)
    parser.add_option('-s', dest="single", action="store_true", default=False, help="Ne retourner qu'une solution.")
    parser.add_option('-n', dest="voisin", metavar="VOISIN", default=None,
                      help="Aide à identifier la commune en cas d'homonymes.")
    parser.add_option('-v', dest="verbose", action="store_true", default=False, help="Affiche la progression.")
    parser.add_option('-h', '--help', action='help',
                      help="Affiche ce message d'aide et termine.")
    (opt, args) = parser.parse_args()
    if len(args) != 4:
        parser.error("Mauvais nombre de paramètres.")

    insee = args[0]
    check_suffixe_fichier(insee, ['.xls'])
    adjac = args[1]
    check_suffixe_fichier(adjac, ['.csv'])
    geofile = args[2]
    check_suffixe_fichier(geofile, ['.json', '.shp'])
    ville_depart = args[3]
    voisin = opt.voisin
    verbose = opt.verbose
    pop_cible = opt.pop_cible
    mono_sol = opt.single
    if verbose:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7.7s %(message)s")
    else:
        logging.basicConfig(level=logging.WARN, format="%(asctime)s %(levelname)-7.7s %(message)s")
    try:
        solve((insee, adjac, geofile), ville_depart, voisin, pop_cible, mono_sol, verbose)
    except VilleNotFound as e:
        log.error("Erreur : " + e.args[0])
        exit(1)


if __name__ == '__main__':
    main()
