# M6-B1 — Analyse de performance et détection de dérive Pyrenex

Analyse du modèle de scoring crédit `pyrenex_risk_v2` après trois mois de production.
Le projet compare les données de référence aux dossiers reçus entre mars et mai 2026,
mesure l'évolution des performances et propose une action à Sophie Léger, côté Pyrenex.

L'objectif est de comprendre si les changements viennent des dossiers entrants, d'une
perte de capacité du modèle à distinguer les risques ou de probabilités devenues moins
fiables. Le dépôt regroupe le notebook d'analyse, les fonctions de calcul et les documents
de synthèse qui justifient la recommandation client.

## Données

Les trois CSV nécessaires à l'analyse sont fournis dans le dépôt.

| Fichier | Volume | Contenu |
|---|---:|---|
| [`data/reference_set.csv`](./data/reference_set.csv) | 1 500 lignes | Jeu témoin pour mesurer la dérive |
| [`data/prod_3months.csv`](./data/prod_3months.csv) | 3 000 lignes | Dossiers de production du 2 mars au 24 mai 2026 |
| [`data/predictions_log.csv`](./data/predictions_log.csv) | 3 000 lignes | Dates, prédictions, probabilités de défaut et labels réels |

L'analyse porte sur 14 variables explicatives : 8 numériques et 6 catégorielles.
La cible `loan_status` est exclue de la comparaison des variables d'entrée.
Le jeu de référence de 1 500 lignes est propre à cette analyse M6 : il ne doit pas être
remplacé par le jeu d'évaluation de 500 lignes du projet M5.

## Analyse

Le [`notebook M6_B1_alex_franck_etienne.ipynb`](./notebooks/M6_B1_alex_franck_etienne.ipynb)
constitue le fil conducteur : il charge les CSV, appelle les fonctions de `src/` et
présente les tableaux, graphiques et interprétations. L'analyse suit cinq étapes,
de l'exploration des données à la recommandation.

### 1. Explorer les données

La première section du notebook compare le jeu de référence aux trois mois de production.
Les 8 variables numériques sont décrites par des statistiques et des histogrammes avec
les mêmes bornes de classes. Les histogrammes sont normalisés pour comparer les formes
malgré les volumes différents des deux jeux. Les 6 variables catégorielles sont comparées
en proportions.

Cette exploration sert à repérer les distributions qui changent avant de leur appliquer
des tests. Les graphiques et leur lecture sont conservés dans le notebook : ils font
ressortir notamment les taux d'intérêt, l'utilisation du crédit renouvelable et les grades.

### 2. Mesurer la dérive

[`src/drift_detection.py`](./src/drift_detection.py) rassemble les méthodes utilisées
pour vérifier ces premiers constats. Le PSI mesure l'ampleur du déplacement des variables
numériques, avec des classes définies à partir des quantiles de la référence. Le test KS
complète cette mesure ; le Chi² compare les fréquences des catégories.

La fonction `drift_report` applique ces calculs aux 14 variables et produit un tableau
avec les scores, les p-values et les verdicts. Les repères du PSI sont 0,10 et 0,25 ;
le seuil statistique retenu est de 5 %. Croiser ces mesures permet de distinguer un écart
statistiquement détectable d'un changement de distribution important.
Le rapport par variable est repris dans [`drift_summary.md`](./drift_summary.md).

### 3. Vérifier la calibration

La troisième section exploite les probabilités et les labels réels de
[`predictions_log.csv`](./data/predictions_log.csv). Elle compare les semaines 1–4 aux
semaines 9–12 pour vérifier si les risques annoncés correspondent encore aux défauts observés.

Dans [`src/calibration.py`](./src/calibration.py), `reliability_table` regroupe les
probabilités en 10 tranches et calcule, pour chacune, l'effectif, le risque moyen annoncé
et le taux de défaut réel. Le notebook trace les diagrammes correspondants ;
`expected_calibration_error` résume les écarts absolus en les pondérant par les effectifs.
Le même découpage est utilisé sur les deux périodes pour comparer leur calibration.

### 4. Suivre l'évolution dans le temps

La quatrième section du notebook calcule chaque semaine l'AUC, le F1 macro et les parts
de défauts prédits et observés. L'AUC décrit la capacité à classer les dossiers par risque,
tandis que le F1 renseigne sur les classes effectivement prédites. Leur comparaison aide
à comprendre ce qui se dégrade dans le comportement du modèle.

L'analyse est complétée par un PSI calculé par fenêtres de deux semaines pour `int_rate`,
`revol_util` et `annual_inc`, à l'aide de `population_stability_index` dans
[`src/drift_detection.py`](./src/drift_detection.py). Les courbes permettent de dater
l'apparition des écarts et de voir si la dérive est progressive ou brutale, ce que le
score global sur trois mois ne montre pas.

### 5. Construire le diagnostic et recommander une action

[`diagnostic.md`](./diagnostic.md) croise les quatre axes : variables, AUC, calibration
et temporalité. Il rassemble les preuves, les hypothèses retenues ou écartées et les
informations qui manquent pour confirmer l'interprétation.

[`src/recommendations.py`](./src/recommendations.py) formalise cette orientation avec
`DriftDiagnosis`, `diagnose_drift_type` et `recommend`. Le nombre de variables en dérive,
la stabilité de l'AUC, la dégradation de calibration et la baisse du F1 servent à proposer
une action et un niveau d'urgence. Cette règle aide à construire le diagnostic ; elle
ne prouve pas à elle seule le type de dérive.

La [`note_recommandation.md`](./note_recommandation.md) présente ensuite au client le
constat, ses conséquences, l'action proposée et son coût estimé, dans un langage accessible.

## Résultats

| Indicateur | Semaines 1–4 | Semaines 9–12 |
|---|---:|---:|
| ROC-AUC | 0,742 | 0,746 |
| F1 macro | 0,609 | 0,551 |
| Risque prédit moyen | 44,27 % | 51,58 % |
| Défauts observés | 20,24 % | 20,06 % |
| Erreur de calibration ECE | 24,03 points | 31,52 points |

La dérive touche surtout `int_rate` (PSI 0,444), puis `revol_util` et `grade`.
L'AUC reste stable, mais le modèle surestime davantage le risque : le diagnostic retenu
est une **dérive des données avec dégradation de la calibration**.
La note propose un réentraînement sur les données récentes et un suivi renforcé,
pour **2 jours-homme estimés**. Ce réentraînement n'est pas réalisé dans ce dépôt.

## Monitoring Grafana

Le monitoring a été réalisé dans le dépôt
[M6-B2 — alex-franck-etienne](https://github.com/franckcwalter/m6-b2-alex-franck-etienne),
qui prolonge ce travail d'analyse. Dans ce dépôt M6-B1, le fichier
[`pyrenex_drift_TEMPLATE.json`](./grafana/provisioning/dashboards/pyrenex_drift_TEMPLATE.json)
fournit trois panels fondés sur les métriques Prometheus du projet M5 :

| Panel | Utilité |
|---|---|
| Probabilités prédites : médiane et p90 | Suivre le déplacement des risques annoncés |
| Part des dossiers prédits en défaut | Repérer un changement dans les décisions du modèle |
| Volume et erreurs HTTP | Interpréter les signaux avec leur contexte de trafic |

Le fichier conservé ici est le template de départ. L’intégration du monitoring et la
stack associée sont à consulter dans le dépôt M6-B2 lié ci-dessus.

PSI, KS et Chi² restent dans le notebook : ils comparent des lots de données à une
référence et ne sont pas exposés par les métriques live fournies. Le F1 sur les 12 semaines
reste aussi une mesure batch, car il nécessite les labels réels, disponibles avec retard
en production.

## Reproduire l'analyse

Prérequis : Python 3.11 ou supérieur, avec une version compatible avec les dépendances
figées dans `requirements.txt`.

Depuis la racine du dépôt :

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q tests
jupyter notebook notebooks/M6_B1_alex_franck_etienne.ipynb
```

Dans Jupyter, sélectionner l'environnement installé puis exécuter toutes les cellules
dans l'ordre, avec le dossier `notebooks/` comme répertoire de travail : certaines
cellules utilisent les chemins relatifs `../data/`.

Pour un environnement créé avec `uv`, utiliser `uv pip install -r requirements.txt`
à la place de la commande d'installation avec pip.

[`tests/test_smoke.py`](./tests/test_smoke.py) vérifie la présence et la cohérence
des données, les propriétés de base du PSI et un cas de diagnostic.
[`tests/test_calibration.py`](./tests/test_calibration.py) couvre les bornes des
probabilités, la pondération de l'ECE, les valeurs manquantes et les entrées invalides.

## Structure du dépôt

```text
.
├── data/
│   ├── reference_set.csv              # Témoin de 1 500 dossiers
│   ├── prod_3months.csv               # 3 000 dossiers de production
│   └── predictions_log.csv            # Prédictions et labels réels
├── notebooks/
│   └── M6_B1_alex_franck_etienne.ipynb # Analyse et graphiques
├── src/
│   ├── drift_detection.py             # PSI, KS, Chi² et rapport
│   ├── calibration.py                 # Table de calibration et ECE
│   └── recommendations.py             # Orientation et remédiation
├── tests/
│   ├── test_smoke.py                  # Données, PSI et diagnostic
│   └── test_calibration.py            # Calculs et validation des entrées
├── grafana/provisioning/dashboards/
│   └── pyrenex_drift_TEMPLATE.json    # Template de départ du monitoring M6-B2
├── ressources/                        # Mini-cours et liens d'appui
├── drift_summary.md                  # Résultats par variable
├── diagnostic.md                     # Synthèse des quatre axes
├── note_recommandation.md            # Décision proposée au client
└── requirements.txt
```

## Auteurs

Alexandre × Franck × Étienne.
