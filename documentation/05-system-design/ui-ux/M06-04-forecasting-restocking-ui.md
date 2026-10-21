# M06-04 — Forecasting and Restocking UI Design

## 1. Purpose

Design forecasting and restocking screens for the Retail-X-AI
system. These screens help small retail shop owners understand
expected product demand, identify stock risks, and make informed
reordering decisions.

This deliverable defines the UI design and expected interactions.
It does not claim that the screens or underlying integrations
have been implemented.

## 2. Design Principles

- Dark theme consistent with M06-03.
- Near-black page background and charcoal content cards.
- High-contrast white text with restrained blue and teal accents.
- Clear distinction between actual data, forecasts, and recommendations.
- Responsive layouts for desktop, tablet, and mobile.
- Accessible labels, keyboard focus, and status indicators.
- No fabricated business metrics or unsupported predictions.

## 3. Forecasting Screen

### Purpose
Help shop owners review expected demand for selected products
and time periods.

### Components
- Page title: Demand Forecasting.
- Filters: date range, product, category, and store where supported.
- Summary cards: forecasted units, forecast horizon, and forecast status.
- Demand chart: historical actual sales and forecasted demand shown
  as visually distinct series.
- Product forecast table: product, historical units sold, predicted
  demand, forecast period, and model status.
- Last-updated timestamp and data-availability message.
- Link to relevant inventory or restocking details.

### Interactions
- Filters update the selected reporting scope.
- Selecting a product opens its forecast details.
- Chart legends distinguish historical observations from predictions.
- Missing forecasts display an explanatory empty state.
- Failed requests display an error message and retry option.
- Loading indicators appear while data is retrieved.

### Data integrity
- Actual sales must not be presented as predictions.
- Every forecast must identify its time horizon and units.
- Forecast values must come from an available model or service.
- Do not display invented accuracy scores or confidence intervals.
- Forecast performance metrics appear only when evaluation results exist.
- The known dataset contains a Demand Forecast field with data-quality
  and leakage risks. It must not be treated as a validated prediction
  merely because the column exists.

## 4. Restocking Screen

### Purpose
Help shop owners identify products that may need replenishment
and review suggested reorder quantities before taking action.

### Components
- Page title: Restocking Recommendations.
- Filters: store, category, stock status, and product where supported.
- Summary cards: low-stock products, stockout-risk products, and
  pending decisions, only when supported by current data.
- Inventory table with product, current stock, status, expected demand,
  suggested reorder quantity, and recommendation explanation.
- Severity labels for low stock and stockout risk.
- Product-level details and a review recommendation action.
- Clear indication of unavailable stock or demand data.

### Interactions
- Filters narrow the displayed product list.
- Selecting a product shows its stock and recommendation details.
- Shop owners can review a recommendation before deciding.
- Any future confirm-order action must require explicit user confirmation.
- Missing supplier, lead-time, or inventory data must be disclosed.
- Empty, loading, and error states must be represented.

### Data integrity and safety
- Reorder quantities must be calculated by a documented method.
- Do not assume supplier lead times, pack sizes, or minimum order
  quantities are known.
- Distinguish a recommendation from a completed purchase order.
- Do not claim that stock has changed unless the inventory service
  confirms the update.
- The shop owner remains responsible for the final reorder decision.

## 5. Navigation and Relationship to M06-03

Both screens are accessible from the dashboard navigation:
- Forecasting
- Restocking

The dashboard may summarize forecast status and stock alerts.
Selecting a summary or alert should open the relevant detailed screen.
The AI Assistant may link to these views but must distinguish factual
inventory data from predictions and suggestions.

## 6. Expected Data Dependencies

| Data | Forecasting | Restocking |
|---|---|---|
| Date and product identifiers | Required | Required |
| Historical units sold | Required for historical comparison | Useful for demand-based decisions |
| Forecast output | Required to display predictions | Required for forecast-based recommendations |
| Current inventory | Optional for forecast display | Required for stock-based recommendations |
| Reorder rules or thresholds | Optional | Required for rule-based recommendations |
| Supplier lead time | Optional | Required only if the method uses lead time |
| Model evaluation results | Optional | Optional |

Where data or services are not available, the screen must show an
honest unavailable state instead of fabricated results.

## 7. Accessibility and Responsive Behaviour

- Use meaningful headings and table column labels.
- Do not communicate severity by colour alone.
- Provide keyboard navigation and visible focus states.
- Maintain readable contrast and text sizes.
- Reflow cards and tables for narrow screens.
- Provide textual summaries for charts.

## 8. Verification Checklist

- [ ] Forecasting screen layout documented.
- [ ] Restocking screen layout documented.
- [ ] SVG wireframe created and checked.
- [ ] Visual style aligned with M06-03.
- [ ] Navigation aligned with M06-02.
- [ ] Actuals, forecasts, and recommendations clearly distinguished.
- [ ] Missing-data, loading, and error states documented.
- [ ] No unsupported business metrics or functionality claimed.
- [ ] Files reviewed before pull request.
