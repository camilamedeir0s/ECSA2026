# Structural co-location patterns across three regimes

## Reproducible cutoffs

- Knee detected in the Pareto set (sorted by `score`): pareto_rank=20
- Mapping to global ranking: knee_global_pos=878
- Last global position covered by the Pareto set: last_pareto_global_pos=44503
- Global tail: worst 1.00% ⇒ 1160 configurations (rank 114816..115975)

## TOP

**Recurring co-location patterns (p ≥ 0.80):**
- (currency, main) — p=1.000
- (currency, productcat) — p=1.000
- (main, productcat) — p=1.000
- (currency, recommendation) — p=0.885
- (main, recommendation) — p=0.885
- (productcat, recommendation) — p=0.885

Total: 6 pairs

**Strong separation patterns (p ≤ 0.20):**
- (checkout, productcat) — p=0.153
- (checkout, currency) — p=0.153
- (checkout, main) — p=0.153
- (main, payment) — p=0.154
- (currency, email) — p=0.154
- (email, productcat) — p=0.154
- (email, main) — p=0.154
- (payment, productcat) — p=0.154
- (currency, payment) — p=0.154
- (checkout, recommendation) — p=0.186
- (email, recommendation) — p=0.187
- (payment, recommendation) — p=0.187
- (main, shipping) — p=0.188
- (productcat, shipping) — p=0.188
- (currency, shipping) — p=0.188
- (cart, currency) — p=0.189
- (cart, main) — p=0.189
- (cart, productcat) — p=0.189

Total: 18 pairs

## POST-KNEE (still inside the Pareto-covered region)

**Recurring co-location patterns (p ≥ 0.80):**
- (none)
**Strong separation patterns (p ≤ 0.20):**
- (currency, productcat) — p=0.108
- (currency, recommendation) — p=0.153
- (productcat, recommendation) — p=0.157
- (checkout, main) — p=0.167
- (checkout, recommendation) — p=0.167
- (email, main) — p=0.170
- (email, recommendation) — p=0.171
- (main, payment) — p=0.173
- (payment, recommendation) — p=0.173
- (main, shipping) — p=0.174
- (cart, main) — p=0.174
- (recommendation, shipping) — p=0.175
- (cart, recommendation) — p=0.175
- (ad, currency) — p=0.185
- (ad, productcat) — p=0.185
- (ad, checkout) — p=0.188
- (ad, email) — p=0.191
- (ad, shipping) — p=0.192
- (ad, cart) — p=0.192
- (ad, payment) — p=0.192
- (payment, shipping) — p=0.195
- (cart, payment) — p=0.195
- (email, payment) — p=0.195
- (cart, shipping) — p=0.195
- (cart, email) — p=0.196
- (email, shipping) — p=0.196
- (cart, productcat) — p=0.197
- (productcat, shipping) — p=0.197
- (cart, currency) — p=0.197
- (currency, shipping) — p=0.198

Total: 37 pairs

## GLOBAL TAIL (worst 1.00%)

**Recurring co-location patterns (p ≥ 0.80):**
- (none)
**Strong separation patterns (p ≤ 0.20):**
- (main, productcat) — p=0.000
- (main, recommendation) — p=0.000
- (currency, main) — p=0.000
- (ad, main) — p=0.026
- (productcat, recommendation) — p=0.043
- (email, recommendation) — p=0.052
- (email, productcat) — p=0.053
- (currency, email) — p=0.053
- (checkout, currency) — p=0.059
- (checkout, productcat) — p=0.061
- (checkout, recommendation) — p=0.061
- (payment, productcat) — p=0.072
- (currency, payment) — p=0.072
- (payment, recommendation) — p=0.072
- (ad, email) — p=0.078
- (ad, checkout) — p=0.079
- (ad, payment) — p=0.098
- (recommendation, shipping) — p=0.108
- (currency, shipping) — p=0.114
- (productcat, shipping) — p=0.120
- (ad, shipping) — p=0.126
- (cart, currency) — p=0.134
- (cart, productcat) — p=0.134
- (cart, recommendation) — p=0.134
- (ad, cart) — p=0.149
- (cart, shipping) — p=0.162

Total: 26 pairs


## TOP patterns that break in the POST-KNEE regime

- (currency, main): top p=1.000 → post-knee p=0.465
- (currency, productcat): top p=1.000 → post-knee p=0.108
- (main, productcat): top p=1.000 → post-knee p=0.465
- (currency, recommendation): top p=0.885 → post-knee p=0.153
- (main, recommendation): top p=0.885 → post-knee p=0.292
- (productcat, recommendation): top p=0.885 → post-knee p=0.157

## TOP patterns that break in the GLOBAL TAIL

- (currency, main): top p=1.000 → tail p=0.000
- (currency, productcat): top p=1.000 → tail p=0.253
- (main, productcat): top p=1.000 → tail p=0.000
- (currency, recommendation): top p=0.885 → tail p=0.253
- (main, recommendation): top p=0.885 → tail p=0.000
- (productcat, recommendation): top p=0.885 → tail p=0.043