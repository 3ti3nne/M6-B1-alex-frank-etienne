# Drift summary

- **Référence** : `data/reference_set.csv` (1500 lignes)
- **Production** : `data/prod_3months.csv` (3000 lignes, du 02/03 au 24/05/2026)
- **Méthode** : PSI + KS par feature numérique, Chi² par catégorielle (`src/drift_detection.py`)
- **Repères PSI** : < 0.10 signal faible · 0.10–0.25 à investiguer · > 0.25 signal fort
- **p-value** : < 0.05 = écart statistiquement détectable (ne dit pas s'il est important)

| Feature | Type | PSI |              p-value | Verdict             | Commentaire                     |
|---|---|---:|---------------------:|---------------------|---------------------------------|
| `int_rate` | numérique | 0.443619 |    4.627646e-65 (KS) | signal fort         | ...                             |
| `revol_util` | numérique | 0.186596 |    3.818392e-20 (KS) | à investiguer       | ...                             |
| `annual_inc` | numérique | 0.066639 |    2.282912e-09 (KS) | à surveiller        | PSI faible mais KS significatif |
| `installment` | numérique | 0.014692 |    6.625669e-01 (KS) | signal faible       | …                               |
| `dti` | numérique | 0.011406 |    1.104190e-01 (KS) | signal faible       | …                               |
| `fico_range_low` | numérique | 0.006804 |    4.892778e-01 (KS) | signal faible       | …                               |
| `loan_amnt` | numérique | 0.003454 |    9.890912e-01 (KS) | signal faible       | …                               |
| `delinq_2yrs` | numérique | 0.001762 |    8.878996e-01 (KS) | signal faible       | …                               |
| `grade` | catégorielle | — |  3.650607e-07 (Chi²) | écart détecté       | ...                             |
| `purpose` | catégorielle | — |  1.992677e-01 (Chi²) | pas d'écart détecté | …                               |
| `term` | catégorielle | — |  3.164360e-01 (Chi²) | pas d'écart détecté | …                               |
| `emp_length` | catégorielle | — |  4.915755e-01 (Chi²) | pas d'écart détecté | …                               |
| `verification_status` | catégorielle | — |  5.863429e-01 (Chi²) | pas d'écart détecté | …                               |
| `home_ownership` | catégorielle | — |  6.314433e-01 (Chi²) | pas d'écart détecté | …                               |
