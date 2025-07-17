-- Create Customers table
CREATE TABLE Customers (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    City VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Products table
CREATE TABLE Products (
    ProductID INT AUTO_INCREMENT PRIMARY KEY,
    ProductName VARCHAR(100) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    StockQuantity INT DEFAULT 0,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Orders table
CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NOT NULL,
    OrderDate DATE NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    Status VARCHAR(20) DEFAULT 'Pending',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Create OrderDetails table
CREATE TABLE OrderDetails (
    OrderDetailID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Create Payments table
CREATE TABLE Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    PaymentMethod VARCHAR(50) NOT NULL,
    PaymentAmount DECIMAL(10, 2) NOT NULL,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

-- Insert 20 Customers
INSERT INTO Customers (FirstName, LastName, Email, City) VALUES
('John', 'Doe', 'john.doe@email.com', 'New York'),
('Jane', 'Smith', 'jane.smith@email.com', 'Los Angeles'),
('Bob', 'Johnson', 'bob.johnson@email.com', 'New York'),
('Alice', 'Williams', 'alice.williams@email.com', 'Chicago'),
('Charlie', 'Brown', 'charlie.brown@email.com', 'Miami'),
('Diana', 'Davis', 'diana.davis@email.com', 'Seattle'),
('Frank', 'Wilson', 'frank.wilson@email.com', 'Boston'),
('Grace', 'Garcia', 'grace.garcia@email.com', 'Austin'),
('Henry', 'Miller', 'henry.miller@email.com', 'Denver'),
('Ivy', 'Moore', 'ivy.moore@email.com', 'Phoenix'),
('Jack', 'Taylor', 'jack.taylor@email.com', 'San Francisco'),
('Kelly', 'Anderson', 'kelly.anderson@email.com', 'Portland'),
('Leo', 'Thomas', 'leo.thomas@email.com', 'Las Vegas'),
('Mia', 'Jackson', 'mia.jackson@email.com', 'Atlanta'),
('Noah', 'White', 'noah.white@email.com', 'Dallas'),
('Olivia', 'Harris', 'olivia.harris@email.com', 'Houston'),
('Paul', 'Martin', 'paul.martin@email.com', 'Philadelphia'),
('Quinn', 'Thompson', 'quinn.thompson@email.com', 'San Diego'),
('Ruby', 'Garcia', 'ruby.garcia@email.com', 'Orlando'),
('Sam', 'Rodriguez', 'sam.rodriguez@email.com', 'Detroit');

-- Insert 20 Products
INSERT INTO Products (ProductName, Category, Price, StockQuantity) VALUES
('iPhone 15', 'Electronics', 999.99, 50),
('Samsung Galaxy S24', 'Electronics', 899.99, 45),
('MacBook Pro', 'Electronics', 1999.99, 25),
('Dell XPS 13', 'Electronics', 1299.99, 30),
('iPad Air', 'Electronics', 599.99, 60),
('AirPods Pro', 'Electronics', 249.99, 100),
('Sony TV 55"', 'Electronics', 799.99, 20),
('LG OLED TV', 'Electronics', 1499.99, 15),
('Coffee Maker Deluxe', 'Home Appliances', 149.99, 80),
('Blender Pro', 'Home Appliances', 89.99, 75),
('Microwave 1000W', 'Home Appliances', 199.99, 60),
('Air Fryer XL', 'Home Appliances', 129.99, 90),
('Dishwasher Compact', 'Home Appliances', 449.99, 25),
('Vacuum Cleaner Robot', 'Home Appliances', 299.99, 40),
('Washing Machine', 'Home Appliances', 699.99, 20),
('Refrigerator Side-by-Side', 'Home Appliances', 1199.99, 15),
('Gaming Chair', 'Furniture', 299.99, 35),
('Office Desk', 'Furniture', 199.99, 50),
('Bookshelf', 'Furniture', 149.99, 40),
('Dining Table', 'Furniture', 599.99, 20);

-- Insert Orders (Fixed to match sum of order details)
INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, Status) VALUES
(1, '2024-01-15', 999.99, 'Completed'),        -- Order 1: 999.99
(2, '2024-01-20', 989.98, 'Completed'),        -- Order 2: 899.99 + 89.99 = 989.98
(3, '2024-02-05', 149.99, 'Pending'),          -- Order 3: 149.99
(4, '2024-02-10', 339.98, 'Completed'),        -- Order 4: 249.99 + 89.99 = 339.98
(5, '2024-02-14', 799.99, 'Shipped'),          -- Order 5: 799.99
(6, '2024-03-01', 1999.99, 'Completed'),       -- Order 6: 1999.99
(7, '2024-03-05', 379.98, 'Completed'),        -- Order 7: 249.99 + 129.99 = 379.98
(8, '2024-03-10', 599.99, 'Pending'),          -- Order 8: 599.99
(9, '2024-03-15', 89.99, 'Completed'),         -- Order 9: 89.99
(10, '2024-04-01', 1299.99, 'Shipped'),        -- Order 10: 1299.99
(11, '2024-04-05', 449.99, 'Completed'),       -- Order 11: 449.99
(12, '2024-04-10', 199.99, 'Completed'),       -- Order 12: 199.99
(13, '2024-04-15', 899.99, 'Pending'),         -- Order 13: 899.99
(14, '2024-04-20', 299.99, 'Completed'),       -- Order 14: 299.99
(15, '2024-05-01', 699.99, 'Shipped'),         -- Order 15: 699.99
(16, '2024-05-05', 1199.99, 'Completed'),      -- Order 16: 1199.99
(17, '2024-05-10', 149.99, 'Completed'),       -- Order 17: 149.99
(18, '2024-05-15', 599.99, 'Pending'),         -- Order 18: 599.99
(19, '2024-05-20', 249.99, 'Completed'),       -- Order 19: 249.99
(20, '2024-05-25', 1499.99, 'Shipped');        -- Order 20: 1499.99

-- Insert OrderDetails (Fixed to match product prices * quantities)
INSERT INTO OrderDetails (OrderID, ProductID, Quantity, Price) VALUES
(1, 1, 1, 999.99),                    -- iPhone 15: 999.99 * 1 = 999.99
(2, 2, 1, 899.99),                    -- Samsung Galaxy S24: 899.99 * 1 = 899.99
(2, 10, 1, 89.99),                    -- Blender Pro: 89.99 * 1 = 89.99
(3, 9, 1, 149.99),                    -- Coffee Maker Deluxe: 149.99 * 1 = 149.99
(4, 6, 1, 249.99),                    -- AirPods Pro: 249.99 * 1 = 249.99
(4, 10, 1, 89.99),                    -- Blender Pro: 89.99 * 1 = 89.99
(5, 7, 1, 799.99),                    -- Sony TV 55": 799.99 * 1 = 799.99
(6, 3, 1, 1999.99),                   -- MacBook Pro: 1999.99 * 1 = 1999.99
(7, 6, 1, 249.99),                    -- AirPods Pro: 249.99 * 1 = 249.99
(7, 12, 1, 129.99),                   -- Air Fryer XL: 129.99 * 1 = 129.99
(8, 5, 1, 599.99),                    -- iPad Air: 599.99 * 1 = 599.99
(9, 10, 1, 89.99),                    -- Blender Pro: 89.99 * 1 = 89.99
(10, 4, 1, 1299.99),                  -- Dell XPS 13: 1299.99 * 1 = 1299.99
(11, 13, 1, 449.99),                  -- Dishwasher Compact: 449.99 * 1 = 449.99
(12, 18, 1, 199.99),                  -- Office Desk: 199.99 * 1 = 199.99
(13, 2, 1, 899.99),                   -- Samsung Galaxy S24: 899.99 * 1 = 899.99
(14, 14, 1, 299.99),                  -- Vacuum Cleaner Robot: 299.99 * 1 = 299.99
(15, 15, 1, 699.99),                  -- Washing Machine: 699.99 * 1 = 699.99
(16, 16, 1, 1199.99),                 -- Refrigerator Side-by-Side: 1199.99 * 1 = 1199.99
(17, 19, 1, 149.99),                  -- Bookshelf: 149.99 * 1 = 149.99
(18, 20, 1, 599.99),                  -- Dining Table: 599.99 * 1 = 599.99
(19, 6, 1, 249.99),                   -- AirPods Pro: 249.99 * 1 = 249.99
(20, 8, 1, 1499.99);                  -- LG OLED TV: 1499.99 * 1 = 1499.99

-- Insert Payments (Fixed to match order totals)
INSERT INTO Payments (OrderID, PaymentMethod, PaymentAmount) VALUES
(1, 'Credit Card', 999.99),
(2, 'PayPal', 989.98),
(3, 'Credit Card', 149.99),
(4, 'Debit Card', 339.98),
(5, 'Credit Card', 799.99),
(6, 'PayPal', 1999.99),
(7, 'Credit Card', 379.98),
(8, 'Debit Card', 599.99),
(9, 'Credit Card', 89.99),
(10, 'PayPal', 1299.99),
(11, 'Credit Card', 449.99),
(12, 'Debit Card', 199.99),
(13, 'Credit Card', 899.99),
(14, 'Apple Pay', 299.99),
(15, 'Credit Card', 699.99),
(16, 'PayPal', 1199.99),
(17, 'Debit Card', 149.99),
(18, 'Credit Card', 599.99),
(19, 'Apple Pay', 249.99),
(20, 'Credit Card', 1499.99);
