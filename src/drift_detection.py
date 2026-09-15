"""Détection de dérive — PSI, KS, Chi² (SQUELETTE À COMPLÉTER).

Trois méthodes complémentaires. Mini-cours : `01_PSI_KS_Chi2_essentiel.md`.
N'inventez pas vos métriques : PSI (formule ci-dessous), KS et Chi² sont dans
scipy.stats.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp

PSI_STABLE = 0.10
PSI_DRIFT = 0.25


def population_stability_index(reference: pd.Series, current: pd.Series, n_bins: int = 10) -> float:
    """PSI entre référence et courant.

    PSI = Σ (p_cur - p_ref) * ln(p_cur / p_ref), bornes des bins = quantiles de
    la référence. ⚠️ pensez au lissage anti-zéro (sinon ln(0) / division par 0).
    """
    ref = reference.dropna()
    cur = current.dropna()
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, n_bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    p_ref = np.histogram(ref, edges)[0] / len(ref)
    p_cur = np.histogram(cur, edges)[0] / len(cur)
    p_ref, p_cur = p_ref + 1e-6, p_cur + 1e-6
    p_ref, p_cur = p_ref / p_ref.sum(), p_cur / p_cur.sum()
    return float(np.sum((p_cur - p_ref) * np.log(p_cur / p_ref)))


def psi_verdict(psi: float) -> str:
    """Traduit un PSI en verdict (stable / suspect / dérive)."""
    if psi <= PSI_STABLE:
        return "stable"
    elif psi <= PSI_DRIFT:
        return "suspect"
    else:
        return "dérive"


def ks_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du test de Kolmogorov-Smirnov (2 échantillons)."""
    return ks_2samp(reference.dropna(), current.dropna()).pvalue



def chi2_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du Chi² sur les fréquences de modalités (aligner les modalités)."""
    ref_counts = reference.value_counts()
    cur_counts = current.value_counts()
    modalites = ref_counts.index.union(cur_counts.index)
    ref_counts = ref_counts.reindex(modalites, fill_value=0) + 1
    cur_counts = cur_counts.reindex(modalites, fill_value=0) + 1
    table = np.array([ref_counts, cur_counts])
    return float(chi2_contingency(table)[1])

def drift_report(
    reference: pd.DataFrame, current: pd.DataFrame,
    numeric_cols: list[str], categorical_cols: list[str],
) -> pd.DataFrame:
    """Tableau de synthèse : feature / type / psi / ks_pvalue / chi2_pvalue / verdict."""
    numeriques = []
    for col in numeric_cols:
        psi = population_stability_index(reference[col], current[col])
        numeriques.append({
            "feature": col, "type": "numérique", "psi": psi,
            "ks_pvalue": ks_pvalue(reference[col], current[col]),
            "chi2_pvalue": None, "verdict": psi_verdict(psi),
        })

    categorielles = []
    for col in categorical_cols:
        p = chi2_pvalue(reference[col], current[col])
        categorielles.append({
            "feature": col, "type": "catégorielle", "psi": None,
            "ks_pvalue": None, "chi2_pvalue": p,
            "verdict": "dérive" if p < 0.05 else "stable",
        })
    return (pd.DataFrame(numeriques + categorielles)
            .sort_values(["psi", "chi2_pvalue"], ascending=[False,True], na_position="last")
            .reset_index(drop=True))



