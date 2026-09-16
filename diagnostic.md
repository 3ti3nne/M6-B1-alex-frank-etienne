# Diagnostic : dérive `pyrenex_risk_v2`

- **Référence** : `data/reference_set.csv` (1500 lignes)
- **Production** : `data/prod_3months.csv` + `data/predictions_log.csv` (3000 lignes, du 02/03 au 24/05/2026)
- **Détail des calculs** : `drift_summary.md` et `notebooks/M6-B1_template.ipynb`

## 1. Les 4 axes

### Features
- `int_rate` : PSI 0.444 · KS p = 4.6e-65 → **dérive** (repère > 0.25)
- `revol_util` : PSI 0.187 · KS p = 3.8e-20 → **à investiguer** (0.10–0.25)
- `grade` : Chi² p = 3.7e-07 → **écart détecté** (moins de A/B, plus de D/E/F)
- `annual_inc` : PSI 0.067 → faible, mais KS p = 2.3e-09 → **à surveiller**
- Les 10 autres features : stables. En particulier `fico_range_low` (PSI 0.007), `dti` (0.011) et `delinq_2yrs` (0.002) **ne bougent pas**.

### AUC
- AUC début (semaines 1-4) : 0.742
- AUC fin (semaines 9-12) : 0.746
- ΔAUC :  +0.004 → **AUC stable** (|Δ| < 0.03)

…

### Calibration
- Risque prédit moyen : 44.27 % → 51.58 %
- Défauts réellement observés : 20.24 % → 20.06 % (**plats**)
- ECE : 24.03 → 31.52 points (+7.49), même découpage 10 classes
- Reliability diagram : les 2 courbes sont **sous la diagonale**, celle de fin encore plus bas → **sur-confiance qui s'aggrave** (le modèle surestime le risque)
- Part de dossiers prédits « défaut » : 38.9 % (S1) → 61.8 % (S12), pour ~20 % de défauts réels


### Temporalité
- [ X ] tendance progressive 
- [ ] rupture brutale

  PSI d'`int_rate` par fenêtres de 2 semaines (vs référence) :
  0.018 → 0.379 → 1.397 → 1.628 → 2.924 → 3.601

- Départ entre le 16 et le 29 mars 2026 (fenêtre 2), puis montée **continue**
- Démarrages **décalés** (franchissement du repère PSI 0.10) : `int_rate`
  fenêtre 2, `revol_util` fenêtre 4, `annual_inc` fenêtre 5.
- Le PSI global (0.444) **moyenne** les 3 mois : la dernière quinzaine est à
  **3.601**.


## 2. Diagnostic retenu

- [ ] pas de signal significatif
- [ X ] data drift plausible
- [ X ] impact sur la calibration
- [ ] concept drift à investiguer
- [ ] problème de qualité / ETL à investiguer

Data drift qui cause des problèmes sur la calibration, les entrées ont dérivées mais n'ont pas casser l'AUC.
Dérive progressive, fiabilité dégradée : le risque annoncé passe de 44.27 a 51.58% alors que les défauts réels restent les mêmes 
ECE monte de ~7 points

## 3. Preuves qui soutiennent ce diagnostic

**Features** `int_rate` PSI 0.444 (KS p = 4.6e-65),`revol_util` PSI 0.187 (KS p = 3.8e-20), `grade` Chi² p = 3.7e-07.
Les 10 autres features restent sous PSI 0.07.
**AUC tient** 0.742 (S1-4) → 0.746 (S9-12), Δ = +0.004.
**Calibration se dégrade** Risque annoncé 44.27 % → 51.58 % pour 20.24 % → 20.06 % de défauts observés.
**Temporalité en pente** PSI d'`int_rate` par quinzaine de 0.018 à 3.601.
**Le profil emprunteur ne bouge pas** `fico_range_low` PSI 0.007, `dti` 0.011, `delinq_2yrs` 0.002.


## 4. Hypothèses écartées

Pas de concept drift, l'AUC est toujours bon
Pas d'ETL, les erreurs sont progressives et pas écartées
Les emprunteurs sont toujours aussi solide, les changements sont sur les taux d'intérêts et les grades principalement

## 5. Ce qui manquerait pour être certain

- **Des labels plus mûrs.** Un défaut met des mois à être constaté : donc surveillance en retard => grafana.
- **Un réentraînement test sur données récentes.** Résout le problème du data drift
- **Le contexte métier de la hausse des taux.** La hausse d'`int_rate` est-elle une hausse générale du au contexte ou juste des emprunts plus risqués ?

