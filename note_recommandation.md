# Note de recommandation — Dérive `pyrenex_risk_v2`

**Pour :** Sophie Léger (Lead Data, Pyrenex)  **De :** FastIA — Alex-Frank-Etienne

## Constat (chiffré)
Depuis mars 2026, les dossiers que reçoit le modèle ne sont plus les mêmes que ceux sur lesquels il a été entraîné.
Le taux d'intérêt est la variable la plus touchée (de 12.6 % a 15.5%)
Le modèle annonce de plus en plus de risque (7% en plus) alors que les défauts réellement constatés n'ont pas bougé.
La conséquence directe est que la part des dossiers que le modèle classe en défaut a augmenté de 38% a 62% en 12 semaines alors que le risque réel n'a pas bougé.
Et le problème s'aggrave de jour en jour.

## Diagnostic
Ce sont les dossiers entrants qui ont changé.
Il classe toujours aussi bien les dossiers du moins au plus risqué : son
indicateur de tri est resté à 0.742 puis 0.746 sur les 12 semaines.
Parcontre l'écart moyen entre risque annoncé et risque constaté est passé de 24 à 31.5 points.
Le modèle est donc devenu trop frileux alors que le profil des emprunteurs n'a pas bougé.

## Recommandation
Réentraîner le modèle sur les derniers dossiers tout simplement, avec la mise en place d'un monitoring en temps réel pour prendre en charge plus rapidement ce même genre de problème à l'avenir

## Coût estimé
2 jours/homme, risque faible, la chaine CI/CD en place bloque la mise en prod si les performances se dégradent.
Il serait judicieux d'intervenir au plus tôt, la dérive s'accélère de jour en jour.

## Décision suggérée
Lancer un réentraînement encadré du model pyrenex_risk_v2 sur les données de mars à mai 2026, le plus rapidement possible.