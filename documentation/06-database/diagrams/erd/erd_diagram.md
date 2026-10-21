# Retail-X-AI Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    CATEGORY {
        int Category_ID PK
        string Category_Name
    }
    REGION {
        int Region_ID PK
        string Region_Name
    }
    STORE {
        string Store_ID PK
        int Region_ID FK
        string Store_Name
    }
    PRODUCT {
        string Product_ID PK
        int Category_ID FK
        string Product_Name
        decimal Unit_Price
        decimal Discount
    }
    DATE_DIM {
        int Date_ID PK
        date Full_Date
        int Day
        int Month
        int Year
        string Season
    }
    INVENTORY_RECORD {
        int Record_ID PK
        int Date_ID FK
        string Store_ID FK
        string Product_ID FK
        int Inventory_Level
        int Units_Sold
        int Units_Ordered
        decimal Demand_Forecast
        decimal Competitor_Pricing
        string Weather_Condition
        boolean Holiday_Promotion
        string Seasonality
    }

    REGION ||--|{ STORE : "contains"
    CATEGORY ||--|{ PRODUCT : "categorizes"
    STORE ||--|{ INVENTORY_RECORD : "records"
    PRODUCT ||--|{ INVENTORY_RECORD : "recorded in"
    DATE_DIM ||--|{ INVENTORY_RECORD : "occurs on"