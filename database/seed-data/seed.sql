-- Seed Data for Dimension Tables

-- 1. Insert Categories
INSERT INTO CATEGORY (Category_Name) VALUES 
('Groceries'), ('Toys'), ('Electronics'), ('Clothing'), ('Furniture');

-- 2. Insert Regions
INSERT INTO REGION (Region_Name) VALUES 
('North'), ('South'), ('East'), ('West');

-- 3. Insert Stores
INSERT INTO STORE (Store_ID, Region_ID, Store_Name) VALUES 
('S001', 1, 'Retail-X North Branch'),
('S002', 2, 'Retail-X South Branch'),
('S003', 3, 'Retail-X East Branch'),
('S004', 4, 'Retail-X West Branch'),
('S005', 1, 'Retail-X North Express');

-- 4. Insert Products (Sample)
INSERT INTO PRODUCT (Product_ID, Category_ID, Product_Name, Unit_Price, Discount) VALUES 
('P0001', 1, 'Organic Apples', 33.50, 20.00),
('P0002', 2, 'Action Figure', 63.01, 20.00),
('P0003', 3, 'Wireless Mouse', 27.99, 10.00);

-- 5. Insert Dates (Sample)
INSERT INTO DATE_DIM (Full_Date, Day, Month, Year, Season) VALUES 
('2022-01-01', 1, 1, 2022, 'Winter'),
('2022-01-02', 2, 1, 2022, 'Winter'),
('2022-01-03', 3, 1, 2022, 'Winter');

-- 6. Insert Inventory Records (Sample Fact Data)
INSERT INTO INVENTORY_RECORD (
    Date_ID, Store_ID, Product_ID, Inventory_Level, Units_Sold, Units_Ordered, 
    Demand_Forecast, Competitor_Pricing, Weather_Condition, Holiday_Promotion, Seasonality
) VALUES 
(1, 'S001', 'P0001', 231, 127, 55, 135.47, 29.69, 'Rainy', FALSE, 'Autumn'),
(1, 'S002', 'P0001', 343, 104, 144, 112.55, 30.78, 'Sunny', TRUE, 'Spring');