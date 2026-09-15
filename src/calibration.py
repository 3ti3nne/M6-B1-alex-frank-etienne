"""Calibration en exploitation : probabilités de défaut et fréquences observées."""
from __future__ import annotations

import numpy as np
import pandas as pd


def reliability_table(proba: pd.Series, true_label: pd.Series, n_bins: int = 10) -> pd.DataFrame:
    """Classes de largeur fixe sur [0, 1], seules les classes occupées sont rendues.

    Les observations sont appariées par position (même ordre requis).
    Les paires incomplètes sont exclues. ecart = probabilité moyenne - taux
    observé : positif signifie une surestimation du risque de défaut.
    """
    if not isinstance(n_bins, int) or isinstance(n_bins, bool) or n_bins < 1:
        raise ValueError("n_bins doit être un entier strictement positif.")
    p = pd.Series(proba).reset_index(drop=True)
    y = pd.Series(true_label).reset_index(drop=True)
    if len(p) != len(y):
        raise ValueError("Les probabilités et labels doivent avoir la même longueur.")
    if not p.dropna().between(0, 1).all():
        raise ValueError("Les probabilités doivent être comprises entre 0 et 1.")
    if not y.dropna().isin([0, 1]).all():
        raise ValueError("Les labels doivent être 0 ou 1.")
    df = pd.DataFrame({"proba": p, "label": y}).dropna()
    if df.empty:
        raise ValueError("Aucune paire probabilité/label disponible.")
    df["bin"] = pd.cut(df["proba"], np.linspace(0, 1, n_bins + 1), include_lowest=True)
    table = df.groupby("bin", observed=True).agg(
        n=("label", "size"), confiance_moyenne=("proba", "mean"),
        taux_observe=("label", "mean"),
    ).reset_index()
    table["ecart"] = table["confiance_moyenne"] - table["taux_observe"]
    return table


def expected_calibration_error(proba: pd.Series, true_label: pd.Series, n_bins: int = 10) -> float:
    """ECE : moyenne des écarts absolus pondérée par les effectifs des classes.

    Entre 0 et 1 ; multiplier par 100 pour exprimer l'erreur en points de
    pourcentage. Dépend du découpage et de la taille de l'échantillon.
    """
    table = reliability_table(proba, true_label, n_bins)
    return float((table["n"] / table["n"].sum() * table["ecart"].abs()).sum())
