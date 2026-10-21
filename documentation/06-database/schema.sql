-- ============================================================
-- Retail-X-AI — Database Schema
-- M07-01: Define Database Entities and Data Requirements
-- Author:  @KhanyisileSkhulile614
-- Date:    2026-10-12
-- Based on: M02-04 Data Dictionary + retail_store_inventory.csv
-- ============================================================

DROP TABLE IF EXISTS Inventory_Record;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Store;
DROP TABLE IF EXISTS Date_Dim;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS Region;

-- 1. Category
CREATE TABLE Category (
    Category_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
    Category_Name VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Region
CREATE TABLE Region (
    Region_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
    Region_Name VARCHAR(50) NOT NULL UNIQUE
);

-- 3. Store
CREATE TABLE Store (
    Store_ID   VARCHAR(10)  PRIMARY KEY,
    Region_ID  INTEGER      NOT NULL,
    Store_Name VARCHAR(100) NOT NULL,
    FOREIGN KEY (Region_ID) REFERENCES Region(Region_ID)
);

-- 4. Product
CREATE TABLE Product (
    Product_ID   VARCHAR(10)   PRIMARY KEY,
    Category_ID  INTEGER       NOT NULL,
    Product_Name VARCHAR(100)  NOT NULL,
    Unit_Price   DECIMAL(10,2) NOT NULL CHECK (Unit_Price > 0),
    Discount     DECIMAL(5,2)  DEFAULT 0 CHECK (Discount BETWEEN 0 AND 100),
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
);

-- 5. Date_Dim
CREATE TABLE Date_Dim (
    Date_ID   INTEGER     PRIMARY KEY AUTOINCREMENT,
    Full_Date DATE        NOT NULL UNIQUE,
    Day       INTEGER     NOT NULL CHECK (Day   BETWEEN 1 AND 31),
    Month     INTEGER     NOT NULL CHECK (Month BETWEEN 1 AND 12),
    Year      INTEGER     NOT NULL,
    Season    VARCHAR(20) NOT NULL
        CHECK (Season IN ('Spring','Summer','Autumn','Winter'))
);

-- 6. Inventory_Record (fact table)
CREATE TABLE Inventory_Record (
    Record_ID          INTEGER       PRIMARY KEY AUTOINCREMENT,
    Date_ID            INTEGER       NOT NULL,
    Store_ID           VARCHAR(10)   NOT NULL,
    Product_ID         VARCHAR(10)   NOT NULL,
    Inventory_Level    INTEGER       NOT NULL CHECK (Inventory_Level >= 0),
    Units_Sold         INTEGER       NOT NULL CHECK (Units_Sold >= 0),
    Units_Ordered      INTEGER       NOT NULL CHECK (Units_Ordered >= 0),
    Demand_Forecast    DECIMAL(10,2) NOT NULL CHECK (Demand_Forecast >= 0),
    Competitor_Pricing DECIMAL(10,2) CHECK (Competitor_Pricing > 0),
    Weather_Condition  VARCHAR(20)
        CHECK (Weather_Condition IN ('Rainy','Sunny','Cloudy','Snowy')),
    Holiday_Promotion  BOOLEAN DEFAULT 0,
    Seasonality        VARCHAR(20)
        CHECK (Seasonality IN ('Spring','Summer','Autumn','Winter')),
    UNIQUE (Date_ID, Store_ID, Product_ID),
    FOREIGN KEY (Date_ID)    REFERENCES Date_Dim(Date_ID),
    FOREIGN KEY (Store_ID)   REFERENCES Store(Store_ID),
    FOREIGN KEY (Product_ID) REFERENCES Product(Product_ID)
);

-- Indexes
CREATE INDEX idx_inv_date    ON Inventory_Record(Date_ID);
CREATE INDEX idx_inv_store   ON Inventory_Record(Store_ID);
CREATE INDEX idx_inv_product ON Inventory_Record(Product_ID);
CREATE INDEX idx_inv_weather ON Inventory_Record(Weather_Condition);
CREATE INDEX idx_inv_season  ON Inventory_Record(Seasonality);
CREATE INDEX idx_inv_promo   ON Inventory_Record(Holiday_Promotion);

-- Seed lookups
INSERT INTO Category (Category_Name) VALUES
    ('Groceries'), ('Toys'), ('Electronics'), ('Furniture'), ('Clothing');
INSERT INTO Region (Region_Name) VALUES
    ('North'), ('South'), ('East'), ('West');
INSERT INTO Store (Store_ID, Region_ID, Store_Name) VALUES
    ('S001', 1, 'Store S001'),
    ('S002', 2, 'Store S002'),
    ('S003', 3, 'Store S003'),
    ('S004', 4, 'Store S004'),
    ('S005', 1, 'Store S005');
