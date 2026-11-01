-- ============================================================
-- Retail-X-AI - Sample Queries
-- M07-01 - demonstrate schema usability
-- ============================================================

-- Q1. Total units sold per store
SELECT s.Store_ID,
       SUM(i.Units_Sold) AS Total_Units_Sold
FROM Inventory_Record i
JOIN Store s ON i.Store_ID = s.Store_ID
GROUP BY s.Store_ID
ORDER BY Total_Units_Sold DESC;

-- Q2. Top 5 best-selling products
SELECT p.Product_ID,
       p.Product_Name,
       SUM(i.Units_Sold) AS Total_Sold
FROM Inventory_Record i
JOIN Product p ON i.Product_ID = p.Product_ID
GROUP BY p.Product_ID, p.Product_Name
ORDER BY Total_Sold DESC
LIMIT 5;

-- Q3. Sales by category
SELECT c.Category_Name,
       SUM(i.Units_Sold) AS Total_Sold,
       ROUND(AVG(i.Units_Sold), 2) AS Avg_Daily_Sales
FROM Inventory_Record i
JOIN Product p ON i.Product_ID = p.Product_ID
JOIN Category c ON p.Category_ID = c.Category_ID
GROUP BY c.Category_Name
ORDER BY Total_Sold DESC;

-- Q4. Weather impact on sales
SELECT Weather_Condition,
       COUNT(*) AS Days,
       ROUND(AVG(Units_Sold), 2) AS Avg_Units_Sold
FROM Inventory_Record
GROUP BY Weather_Condition
ORDER BY Avg_Units_Sold DESC;

-- Q5. Holiday vs non-holiday sales
SELECT Holiday_Promotion,
       COUNT(*) AS Records,
       ROUND(AVG(Units_Sold), 2) AS Avg_Units_Sold
FROM Inventory_Record
GROUP BY Holiday_Promotion;

-- Q6. Demand forecast accuracy (MAE and MAPE)
SELECT
    ROUND(AVG(ABS(Units_Sold - Demand_Forecast)), 2) AS MAE,
    ROUND(100 * AVG(ABS(Units_Sold - Demand_Forecast)
        / NULLIF(Units_Sold, 0)), 2) AS MAPE_Percent
FROM Inventory_Record;

-- Q7. Seasonal sales pattern
SELECT d.Season,
       SUM(i.Units_Sold) AS Total_Sold
FROM Inventory_Record i
JOIN Date_Dim d ON i.Date_ID = d.Date_ID
GROUP BY d.Season
ORDER BY Total_Sold DESC;

-- Q8. Inventory turnover by store
SELECT s.Store_ID,
       ROUND(SUM(i.Units_Sold) * 1.0 / NULLIF(SUM(i.Inventory_Level), 0), 4)
           AS Turnover_Ratio
FROM Inventory_Record i
JOIN Store s ON i.Store_ID = s.Store_ID
GROUP BY s.Store_ID
ORDER BY Turnover_Ratio DESC;
