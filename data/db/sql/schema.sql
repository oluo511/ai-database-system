-- ==========================================================
-- 1. DATABASE STRUCTURE (Schema)
-- ==========================================================

-- Core entities for Manufacturers and Suppliers
CREATE TABLE Manufacturers (
    ManufacturerID INT PRIMARY KEY,
    ManufacturerName VARCHAR(255) NOT NULL,
    Street VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(100),
    Country VARCHAR(100),
    ZipCode VARCHAR(20),
    ManufacturerPhone VARCHAR(20),
    ManufacturerEmail VARCHAR(255),
    ManufacturerType VARCHAR(20) CHECK (ManufacturerType IN ('international', 'domestic'))
);

CREATE TABLE Suppliers (
    SupplierID INT PRIMARY KEY,
    SupplierName VARCHAR(255),
    Street VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(100),
    Country VARCHAR(100),
    ZipCode VARCHAR(20),
    SupplierPhone VARCHAR(50),
    SupplierEmail VARCHAR(100),
    SupplierType VARCHAR(50) CHECK (SupplierType IN ('domestic', 'international'))
);

-- Inventory and Classification
CREATE TABLE Categories (
    CategoryID INT PRIMARY KEY,
    CategoryName VARCHAR(255) NOT NULL
);

CREATE TABLE Products (
    ProductID INT PRIMARY KEY CHECK (ProductID BETWEEN 1000 AND 9999),
    ProductName VARCHAR(255),
    ManufacturerID INT,
    CategoryID INT,
    SupplierID INT,
    FOREIGN KEY (ManufacturerID) REFERENCES Manufacturers(ManufacturerID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID)
);

-- Handles multi-value attributes for units and pricing
CREATE TABLE ProductUnits (
    ProductID INT,
    Unit VARCHAR(50),
    Cost DECIMAL(10, 2),
    ListPrice DECIMAL(10, 2),
    AvailableQuantity INT,
    PRIMARY KEY (ProductID, Unit),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Sales and Operations
CREATE TABLE Clients (
    ClientID INT PRIMARY KEY,
    ClientName VARCHAR(255) NOT NULL,
    Street VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(100),
    Country VARCHAR(100),
    ZipCode VARCHAR(20),
    ClientContact VARCHAR(255),
    ClientPhone VARCHAR(20),
    ClientEmail VARCHAR(255),
    ClientType VARCHAR(20) CHECK (ClientType IN ('grocery store', 'restaurant'))
);

CREATE TABLE SalesPersons (
    SalesPersonID INT PRIMARY KEY,
    SalesPersonName VARCHAR(255) NOT NULL
);

CREATE TABLE SalesOrders (
    OrderID INT PRIMARY KEY,
    ClientID INT,
    SalesPersonID INT,
    OrderDate DATE,
    OrderTotal DECIMAL(10, 2),
    DeliveryMethod VARCHAR(20) CHECK (DeliveryMethod IN ('pickup', 'delivery')),
    DeliveryDate DATE,
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID),
    FOREIGN KEY (SalesPersonID) REFERENCES SalesPersons(SalesPersonID)
);

CREATE TABLE OrderLines (
    OrderID INT,
    ProductID INT,
    Unit VARCHAR(50),
    DiscountRate DECIMAL(5, 2),
    SoldPrice DECIMAL(10, 2),
    PurchaseQuantity INT,
    Amount DECIMAL(10, 2),
    PRIMARY KEY (OrderID, ProductID),
    FOREIGN KEY (OrderID) REFERENCES SalesOrders(OrderID),
    FOREIGN KEY (ProductID, Unit) REFERENCES ProductUnits(ProductID, Unit)
);