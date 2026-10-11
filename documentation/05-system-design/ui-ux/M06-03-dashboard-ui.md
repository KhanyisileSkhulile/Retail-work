# M06-03 — Dashboard UI Design

## 1. Purpose
Provide shop owners with a clear overview of sales, inventory,
forecasting, and AI-generated decision support.

## 2. Visual Design
- Theme: dark mode
- Background: near-black
- Cards: dark charcoal with subtle borders
- Text: high-contrast white and grey
- Accent colours: restrained blue and teal
- Layout: responsive desktop-first dashboard

## 3. Navigation
- Dashboard
- Sales
- Inventory
- Forecasting
- Restocking
- AI Assistant
- Reports
- Settings

## 4. Dashboard Components

### KPI Cards
- Total sales for the selected period
- Units sold
- Current inventory value, when available
- Products requiring attention

Each KPI must show its reporting period and data source.
Unavailable values must be labelled rather than invented.

### Sales Overview
- Daily or weekly sales trend
- Date-range selector
- Comparison with a previous period when data exists

### Forecasting Summary
- Forecasted demand for a selected horizon
- Forecast horizon and last-updated timestamp
- Model or forecast status
- Clear indication when forecasts are unavailable

### Inventory Alerts
- Low-stock products based on configured thresholds
- Stockout risks where supported by available data
- Clear alert severity and recommended next step

### AI Assistant
- Chat entry point for natural-language questions
- Suggested prompts about sales, demand, and inventory
- Responses grounded in available data
- Clear distinction between forecasts, observations, and suggestions

### Recent Activity
- Recent sales or inventory events when available
- Loading, empty, and error states

## 5. Interaction Requirements
- Navigation items open their corresponding sections.
- Date filters update the displayed period.
- KPI cards provide access to relevant detail views.
- Alert actions open the affected product or inventory view.
- The AI Assistant accepts a question and presents its response.
- Provide visible loading, empty, and error states.

## 6. Data Integrity
- Do not display invented sales, inventory, or forecast figures.
- Show units, currency, time period, and timestamps where applicable.
- Distinguish actual sales from forecasted demand.
- Do not assume supplier lead times or expiry dates are available.
- Present restocking as decision support; the shop owner makes the final decision.

## 7. Accessibility and Responsiveness
- Maintain readable contrast and text sizes.
- Do not communicate alert severity using colour alone.
- Support keyboard navigation and visible focus indicators.
- Reflow cards and charts for smaller screens.

## 8. Verification Checklist
- [ ] Dashboard layout documented
- [ ] Dashboard wireframe created
- [ ] Navigation aligned with M06-02
- [ ] Data integrity rules documented
- [ ] Empty, loading, and error states represented
- [ ] Files reviewed and rendered correctly
