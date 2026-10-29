-- M12-04: Inventory Validation Queries


-- 1. Check for Negative Inventory Levels (Invalid Data)
SELECT Record_ID, Store_ID, Product_ID, Inventory_Level
FROM INVENTORY_RECORD
WHERE Inventory_Level < 0;

-- 2. Check for Negative Units Sold or Units Ordered (Invalid Data)
SELECT Record_ID, Store_ID, Product_ID, Units_Sold, Units_Ordered
FROM INVENTORY_RECORD
WHERE Units_Sold < 0 OR Units_Ordered < 0;

-- 3. Check for Missing/Orphaned Foreign Keys (Referential Integrity)

SELECT i.Record_ID
FROM INVENTORY_RECORD i
LEFT JOIN STORE s ON i.Store_ID = s.Store_ID
LEFT JOIN PRODUCT p ON i.Product_ID = p.Product_ID
WHERE s.Store_ID IS NULL OR p.Product_ID IS NULL;

-- 4. Check for extreme outliers in Demand Forecast vs Actual Units Sold

SELECT Record_ID, Store_ID, Product_ID, Demand_Forecast, Units_Sold
FROM INVENTORY_RECORD
WHERE Demand_Forecast > (Units_Sold * 5) 
  AND Units_Sold > 0;