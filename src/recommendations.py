"""Logique de recommandation de remédiation (SQUELETTE À COMPLÉTER).

La remédiation doit être **proportionnée** au diagnostic : réentraîner coûte
cher, on ne le propose que quand ça vaut le coup. Mini-cours :
`02_Data_drift_vs_concept_drift_essentiel.md` (matrice features × AUC).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftDiagnosis:
    """Synthèse du diagnostic pour décider de la remédiation."""

    n_features_drift: int  # nb de features en "dérive" (PSI > 0.25)
    auc_stable: bool  # le pouvoir discriminant tient-il ?
    calibration_degraded: bool  # la confiance a-t-elle dérivé ?
    f1_drop: float  # baisse de F1 macro (early → late)


def diagnose_drift_type(d: DriftDiagnosis) -> str:
    """Oriente vers "data drift" / "concept drift" / "mixte".

    ⚠️ Heuristique d'orientation, pas une preuve : elle formalise la matrice
    du mini-cours 02 (features × AUC) pour produire une hypothèse principale.
    Le verdict final se construit en croisant features, AUC, calibration et
    temporalité — et doit énoncer ce qui manquerait pour trancher.
    """
    if d.n_features_drift > 0 and d.auc_stable:
        return "data drift"
    if d.n_features_drift == 0 and not d.auc_stable:
        return "concept drift"
    return "mixte"



def recommend(d: DriftDiagnosis) -> dict[str, str]:
    """Recommande une action proportionnée au diagnostic.

    Returns:
        dict avec les clés : action / justification / urgence / drift_type.
    """
    drift_type = diagnose_drift_type(d)

    if not d.auc_stable:
        action, urgence = "réentraîner en urgence", "haute"
        justification = "Le modèle ne classe plus aussi bien les dossiers."
    elif d.calibration_degraded:
        action, urgence = "réentraîner sur données récentes", "moyenne"
        justification = "Les pourcentages de risque annoncés ne sont plus fiables."
    elif d.f1_drop > 0:
        action, urgence = "ajuster le seuil de décision", "moyenne"
        justification = "Les décisions dérapent, mais l'ordre des dossiers tient."
    else:
        action, urgence = "surveiller", "faible"
        justification = "Les entrées ont bougé, sans effet mesuré sur les décisions."

    return {
        "action": action,
        "justification": justification,
        "urgence": urgence,
        "drift_type": drift_type,
    }

