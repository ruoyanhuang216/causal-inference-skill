# Example: Cereal Demand Estimation and Merger Simulation (BLP)

This example shows how the skill guides a researcher through structural demand estimation and merger counterfactual analysis — the classic marketing science / IO workflow.

---

## Conversation

### User
```
/causal-inference I work at an antitrust agency and need to evaluate a proposed merger between two cereal manufacturers. I need to estimate how the merger would change prices and consumer welfare. I have scanner data on cereal market shares, prices, and product characteristics across many markets.
```

### Phase 1: Problem Framing

**Skill identifies:**
> This is a **structural estimation** problem, not a reduced-form causal inference question. Here's why:
>
> - You need to predict the effect of a **counterfactual that has never occurred** (the merger hasn't happened yet)
> - You need **equilibrium effects**: when the merged firm raises prices, competitors respond, consumers substitute — the full system matters
> - You need **welfare analysis**: consumer surplus changes
>
> This is a textbook application of **BLP demand estimation + merger simulation**.
>
> - **Research question**: How much would prices rise and consumer surplus fall if Firm A acquires Firm B?
> - **Data**: Market-level scanner data (market shares, prices, product characteristics, across cities × quarters)
> - **Unit**: Product × market (e.g., Cheerios in Chicago in Q1 2023)
> - **Key challenge**: Price is endogenous — unobserved product quality (promotions, shelf placement, brand equity) affects both demand and prices

---

### Phase 2: Why Structural (Not Reduced-Form)?

**Skill explains the trade-off:**
> A reduced-form approach (e.g., DiD using past mergers as natural experiments) could estimate the causal effect of *past* mergers on prices. But your question is about a *specific proposed* merger — you need:
>
> 1. **Product-level substitution patterns** (which products lose share when one product's price rises?)
> 2. **Firm-level pricing incentives** (the merged firm internalizes cannibalization)
> 3. **Equilibrium price predictions** (competitors also respond)
>
> Only a structural model delivers all three. The standard approach:
>
> | Step | What | Method |
> |------|------|--------|
> | 1. Demand | Estimate consumer preferences and substitution patterns | BLP (Random Coefficients Logit) |
> | 2. Supply | Recover marginal costs from pre-merger pricing FOCs | Nash-Bertrand assumption |
> | 3. Merger | Change ownership matrix, solve for new equilibrium prices | Fixed-point iteration |
> | 4. Welfare | Compute change in consumer surplus and firm profits | From estimated demand |

---

### Phase 3: Method Selection

**Skill recommends BLP and explains why:**

> **BLP (Berry, Levinsohn & Pakes 1995)** is the right demand model because:
> - You have **aggregate market share data** (not individual-level purchases)
> - There are **many products** (dozens of cereals) — need flexible substitution
> - **Price is endogenous** — you need instruments
> - Standard logit would impose **IIA** (proportional substitution), which is unrealistic for differentiated products
>
> **Random coefficients** (in BLP) allow different consumers to have different price sensitivities and brand preferences → realistic substitution: when Cheerios gets expensive, consumers switch disproportionately to similar cereals (other oat-based, same segment), not proportionally to all cereals.
>
> **Instruments for price:**
> - **BLP instruments**: Number of competing products; sum of rivals' characteristics
> - **Cost shifters**: Input costs (wheat, sugar, packaging), shipping distances
> - **Gandhi-Houde differentiation IVs**: Measures of product similarity to competitors (captures local competition in characteristic space)
>
> I recommend using **PyBLP** (Conlon & Gortmaker 2020) — the standard Python implementation.

---

### Phase 4: Diagnostics

> **Before trusting your counterfactuals, validate the model:**
>
> **Demand estimation checks:**
> - [ ] **First-stage F-statistic** for price instruments (must be strong)
> - [ ] **Sign and magnitude of price coefficient**: Must be negative and economically reasonable
> - [ ] **Own-price elasticities**: Should be negative, typically between -1 and -6 for CPG
> - [ ] **Cross-price elasticities**: Close substitutes (e.g., two kids' cereals) should have higher cross-elasticities than distant products
> - [ ] **In-sample fit**: Predicted shares should closely match observed shares
> - [ ] **Random coefficient significance**: Are there meaningful taste heterogeneity (Sigma)?
>
> **Supply-side checks:**
> - [ ] **Marginal costs**: Recovered costs must be positive and economically reasonable. Negative costs = model misspecification.
> - [ ] **Cost patterns**: Should correlate with observable cost drivers (product size, ingredients, shelf space)
> - [ ] **Markup distribution**: Reasonable given industry (CPG markups typically 30-50%)
>
> **Instrument checks:**
> - [ ] **Compare instrument sets**: Do BLP IVs, cost shifters, and differentiation IVs give similar elasticities?
> - [ ] **Overidentification (Hansen J)**: If using GMM, test over-identifying restrictions
>
> **Counterfactual robustness:**
> - [ ] **Alternative demand models**: Run merger simulation under logit, nested logit, and full BLP. How different are price predictions?
> - [ ] **Alternative conduct**: What if firms collude pre-merger? What if merger creates efficiencies (lower MC)?
> - [ ] **Confidence intervals**: Bootstrap or delta-method CIs on predicted price changes

---

### Phase 5: Implementation

```python
import pyblp
import numpy as np
import pandas as pd

# ═══════════════════════════════════════════
# Step 1: Data Preparation
# ═══════════════════════════════════════════
# product_data: one row per product-market
# Required columns:
#   market_ids: market identifier (e.g., city-quarter)
#   shares: observed market shares (must sum to < 1; remainder is outside good)
#   prices: product prices
#   x1, x2, ...: product characteristics (sugar, fiber, calories, brand dummies)
#   firm_ids: which firm owns each product
#   demand_instruments0, demand_instruments1, ...: instruments for price

# ── Construct BLP instruments ──
# Sum of rivals' characteristics in the same market
for char in ['sugar', 'fiber', 'calories']:
    product_data[f'rival_sum_{char}'] = product_data.groupby('market_ids')[char].transform('sum') - product_data[char]
    product_data[f'own_sum_{char}'] = product_data.groupby(['market_ids', 'firm_ids'])[char].transform('sum') - product_data[char]

# ═══════════════════════════════════════════
# Step 2: Define and Estimate BLP Demand
# ═══════════════════════════════════════════

# Linear parameters (X1): absorbed into delta
# Random coefficients (X2): taste heterogeneity
formulation = (
    pyblp.Formulation('0 + prices + sugar + fiber + calories', absorb='C(brand_id)'),  # X1
    pyblp.Formulation('0 + prices + sugar + fiber'),  # X2: random coefficients on these
)

# Integration for simulating heterogeneity
integration = pyblp.Integration('halton', size=500, specification_options={'seed': 42})

problem = pyblp.Problem(formulation, product_data, integration=integration)
print(problem)

# Initial sigma (diagonal = independent random coefficients)
initial_sigma = np.diag([1.0, 0.5, 0.5])

# Solve
results = problem.solve(
    sigma=initial_sigma,
    optimization=pyblp.Optimization('bfgs', {'gtol': 1e-8}),
    iteration=pyblp.Iteration('squarem', {'atol': 1e-14}),
    method='2s'  # two-step efficient GMM
)
print(results)

# ═══════════════════════════════════════════
# Step 3: Validate Demand Estimates
# ═══════════════════════════════════════════

# Own-price elasticities
elasticities = results.compute_elasticities()
own_elast = results.extract_diagonal_means(elasticities)
print(f'Own-price elasticities:')
print(f'  Mean: {own_elast.mean():.3f}')
print(f'  Median: {np.median(own_elast):.3f}')
print(f'  Range: [{own_elast.min():.3f}, {own_elast.max():.3f}]')

# All should be negative; typical CPG range: -1 to -6

# Cross-price elasticities for a specific market
market0 = product_data['market_ids'].unique()[0]
mask = product_data['market_ids'] == market0
products = product_data.loc[mask, 'product_ids'].values
cross_elast = pd.DataFrame(
    elasticities[mask][:, mask],
    index=products, columns=products
).round(3)
print(f'\nCross-price elasticity matrix (market {market0}):')
print(cross_elast)

# In-sample share fit
predicted_shares = results.compute_shares()
actual_shares = product_data['shares'].values
share_corr = np.corrcoef(predicted_shares.flatten(), actual_shares)[0, 1]
share_rmse = np.sqrt(np.mean((predicted_shares.flatten() - actual_shares) ** 2))
print(f'\nShare fit: correlation = {share_corr:.4f}, RMSE = {share_rmse:.6f}')

# ═══════════════════════════════════════════
# Step 4: Recover Marginal Costs (Supply Side)
# ═══════════════════════════════════════════

# Assuming Nash-Bertrand pricing
costs = results.compute_costs()
markups = results.compute_markups()

print(f'\nMarginal costs:')
print(f'  Mean: {costs.mean():.2f}')
print(f'  Std: {costs.std():.2f}')
print(f'  Negative: {(costs < 0).sum()} / {len(costs)}')  # should be 0

print(f'\nMarkups:')
print(f'  Mean: {markups.mean():.3f}')
print(f'  As % of price: {(markups / product_data["prices"].values).mean():.1%}')

# ═══════════════════════════════════════════
# Step 5: Merger Simulation
# ═══════════════════════════════════════════

# Suppose firm_id=1 (General Mills) acquires firm_id=2 (Kellogg's)
merger_data = product_data.copy()
merger_data.loc[merger_data['firm_ids'] == 2, 'firm_ids'] = 1

# Solve for new equilibrium prices
merger_results = results.solve_approximate_merger(
    merger_data[['firm_ids']],
    iteration=pyblp.Iteration('simple', {'atol': 1e-12})
)

# Price changes
price_changes = merger_results.product_data['prices'] - product_data['prices']
pct_changes = price_changes / product_data['prices'] * 100

print('\nMerger price effects:')
print(f'  Mean price change: ${price_changes.mean():.3f} ({pct_changes.mean():.2f}%)')
print(f'  Merging firms only: ${price_changes[product_data["firm_ids"].isin([1,2])].mean():.3f} '
      f'({pct_changes[product_data["firm_ids"].isin([1,2])].mean():.2f}%)')
print(f'  Non-merging rivals: ${price_changes[~product_data["firm_ids"].isin([1,2])].mean():.3f} '
      f'({pct_changes[~product_data["firm_ids"].isin([1,2])].mean():.2f}%)')

# ═══════════════════════════════════════════
# Step 6: Welfare Analysis
# ═══════════════════════════════════════════

# Consumer surplus before and after
cs_pre = results.compute_consumer_surpluses()
cs_post = results.compute_consumer_surpluses(
    prices=merger_results.product_data['prices']
)
cs_change = cs_post - cs_pre

print(f'\nConsumer welfare:')
print(f'  Mean CS change per market: ${cs_change.mean():.2f}')
print(f'  Total CS change: ${cs_change.sum():.0f}')

# ═══════════════════════════════════════════
# Step 7: Robustness
# ═══════════════════════════════════════════

# Scenario: merger with 5% marginal cost efficiencies
costs_efficient = costs.copy()
merging_mask = product_data['firm_ids'].isin([1, 2])
costs_efficient[merging_mask] *= 0.95  # 5% cost reduction

merger_w_eff = results.solve_approximate_merger(
    merger_data[['firm_ids']],
    costs=costs_efficient,
    iteration=pyblp.Iteration('simple', {'atol': 1e-12})
)
price_changes_eff = merger_w_eff.product_data['prices'] - product_data['prices']
pct_eff = price_changes_eff / product_data['prices'] * 100
print(f'\nWith 5% cost efficiencies:')
print(f'  Mean price change: {pct_eff.mean():.2f}%')
print(f'  Merging firms: {pct_eff[merging_mask].mean():.2f}%')
```

> **Reporting recommendations for antitrust:**
> 1. Report demand estimates: price coefficient, random coefficient SDs, key elasticities
> 2. Validate: own-price elasticities in reasonable range; no negative marginal costs; good share fit
> 3. Present merger price predictions with confidence intervals
> 4. Report consumer surplus change (the headline number for antitrust)
> 5. Show sensitivity: different instrument sets, different demand models (logit vs. nested vs. BLP), with/without efficiencies
> 6. Compare merging firms' price increases vs. rivals' competitive responses
> 7. Discuss limitations: static model (no dynamic entry/exit response), assumed conduct (Nash-Bertrand), no product repositioning
