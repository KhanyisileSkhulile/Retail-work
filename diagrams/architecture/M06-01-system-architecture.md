
# M06-01 — Retail-X-AI Logical System Architecture

## Purpose

This diagram describes the proposed logical architecture of Retail-X-AI. It separates user-facing functionality, application coordination, domain services, AI/ML capabilities, logical data stores, and external data inputs.

The diagram is technology-neutral and describes logical interactions rather than a confirmed deployment or technology stack.

## Architecture Diagram

```mermaid
flowchart TB
    USER["Shop Owner / Manager"]

    subgraph PRESENTATION["1. Presentation Layer"]
        UI["Web or Application Interface"]
        DASH["Dashboard and Alerts UI"]
        CHAT["Conversational Assistant UI"]
    end

    subgraph APPLICATION["2. Application Layer"]
        API["Application API / Request Coordination"]
        AUTH["Authentication and Access Control"]
        VALIDATE["Request and Input Validation"]
    end

    subgraph SERVICES["3. Domain Services Layer"]
        SALES["Sales and Inventory Management"]
        IMPORT["Historical Data Import and Validation"]
        ANALYTICS["Retail Data Analysis"]
        FORECAST["Demand Forecasting Service / Orchestrator"]
        RISK["Stockout-Risk Assessment"]
        RESTOCK["Restocking Recommendations"]
        REPORT["Dashboard and Reporting"]
        ASSIST["AI Assistant Orchestration"]
    end

    subgraph AIML["4. AI / ML Capabilities"]
        PREP["Forecast Data Preparation and Feature Selection"]
        MODEL["Forecast Model"]
        RESPONSE["Grounded Response Generation"]
    end

    subgraph DATA["5. Logical Data Layer"]
        PRODUCT[("D1 Product Data")]
        INVENTORY[("D2 Sales and Inventory Data")]
        RESULTS[("D3 Forecast and Analytics Data")]
        ALERTS[("D4 Recommendations and Alerts")]
    end

    DATASET[("External Historical Retail Dataset")]
    OPERATOR["External Model or AI Provider, if approved"]

    USER --> UI
    UI --> DASH
    UI --> CHAT

    DASH --> API
    CHAT --> API
    API --> AUTH
    AUTH --> VALIDATE

    VALIDATE --> SALES
    VALIDATE --> IMPORT
    VALIDATE --> ANALYTICS
    VALIDATE --> FORECAST
    VALIDATE --> RISK
    VALIDATE --> RESTOCK
    VALIDATE --> REPORT
    VALIDATE --> ASSIST

    DATASET --> IMPORT
    IMPORT -->|"Validated records"| INVENTORY
    SALES <--> PRODUCT
    SALES <--> INVENTORY

    PRODUCT --> ANALYTICS
    INVENTORY --> ANALYTICS
    ANALYTICS --> RESULTS

    FORECAST -->|"Request prepared training data"| PREP
    INVENTORY --> PREP
    PREP -->|"Selected, prepared features and target"| MODEL
    MODEL -->|"Generated predictions"| FORECAST
    FORECAST -->|"Persist forecast outputs"| RESULTS

    INVENTORY --> RISK
    RESULTS -->|"Forecasts and analysis only"| RISK
    RISK --> ALERTS

    INVENTORY --> RESTOCK
    RESULTS --> RESTOCK
    ALERTS --> RESTOCK
    RESTOCK --> ALERTS

    INVENTORY --> REPORT
    RESULTS --> REPORT
    ALERTS --> REPORT
    REPORT --> DASH

    PRODUCT --> ASSIST
    INVENTORY --> ASSIST
    RESULTS --> ASSIST
    ALERTS --> ASSIST
    ASSIST --> RESPONSE
    RESPONSE --> CHAT
    RESPONSE -. "Optional integration; approval required" .-> OPERATOR

    AUTH -. "Cross-cutting security" .-> API
    AUTH -. "Access restrictions at protected data operations" .-> DATA
```

## Forecasting and Data-Quality Boundaries

The initial forecasting target is `Units Sold`, as documented in M05-03. Potential leakage fields identified in the data analysis — including `Demand Forecast`, `Units Ordered`, and `Inventory Level` — must not automatically be treated as valid forecasting features. Feature selection must follow the approved data-analysis decisions.

Inventory information remains available to separate stock monitoring, stockout-risk, and restocking functions where appropriate. Excluding a field from model features does not prohibit its use by another system function.

Imported records must be validated and prepared before use. The selected dataset must not be assumed to contain supplier lead times or product expiry dates. Missing information must be identified rather than invented. Restocking suggestions are decision support; the shop owner or manager retains final purchasing authority.

## Security Boundary

Authentication and authorization are cross-cutting concerns. The interface is not itself a security boundary: protected services and data operations must enforce access restrictions. Imported records and user inputs must be validated, and sensitive information must not be unnecessarily exposed in logs, errors, or external AI prompts.

## Important Boundaries

This is a logical component view, not a deployment diagram. It does not specify a programming language, web framework, cloud platform, database product, model provider, network topology, or physical server arrangement.
