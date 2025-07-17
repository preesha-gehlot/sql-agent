-- Create Claims Database Schema

-- Create Policyholders table
CREATE TABLE policyholders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Adjusters table
CREATE TABLE adjusters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    specialization VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Policies table
CREATE TABLE policies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    policyholder_id INT NOT NULL,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    policy_type VARCHAR(50) NOT NULL,
    coverage_amount DECIMAL(12, 2) NOT NULL,
    premium_amount DECIMAL(10, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (policyholder_id) REFERENCES policyholders(id)
);

-- Create Claims table
CREATE TABLE claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    policy_id INT NOT NULL,
    adjuster_id INT,
    claim_date DATE NOT NULL,
    claim_amount DECIMAL(12, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (policy_id) REFERENCES policies(id),
    FOREIGN KEY (adjuster_id) REFERENCES adjusters(id)
);

-- Create Claim Status table
CREATE TABLE claim_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (claim_id) REFERENCES claims(id)
);

-- Insert 20 Policyholders
INSERT INTO policyholders (full_name, email, phone, address) VALUES
('Alice Johnson', 'alice.johnson@email.com', '555-0101', '123 Main St, New York, NY'),
('Bob Smith', 'bob.smith@email.com', '555-0102', '456 Oak Ave, Los Angeles, CA'),
('Carol Williams', 'carol.williams@email.com', '555-0103', '789 Pine Rd, Chicago, IL'),
('David Brown', 'david.brown@email.com', '555-0104', '321 Elm St, Houston, TX'),
('Eva Davis', 'eva.davis@email.com', '555-0105', '654 Maple Dr, Phoenix, AZ'),
('Frank Miller', 'frank.miller@email.com', '555-0106', '987 Cedar Ln, Philadelphia, PA'),
('Grace Wilson', 'grace.wilson@email.com', '555-0107', '147 Birch St, San Antonio, TX'),
('Henry Moore', 'henry.moore@email.com', '555-0108', '258 Walnut Ave, San Diego, CA'),
('Ivy Taylor', 'ivy.taylor@email.com', '555-0109', '369 Cherry Rd, Dallas, TX'),
('Jack Anderson', 'jack.anderson@email.com', '555-0110', '741 Spruce Dr, San Jose, CA'),
('Karen Thomas', 'karen.thomas@email.com', '555-0111', '852 Ash St, Austin, TX'),
('Leo Jackson', 'leo.jackson@email.com', '555-0112', '963 Poplar Ave, Jacksonville, FL'),
('Mia White', 'mia.white@email.com', '555-0113', '159 Hickory Ln, San Francisco, CA'),
('Noah Harris', 'noah.harris@email.com', '555-0114', '357 Dogwood Rd, Columbus, OH'),
('Olivia Martin', 'olivia.martin@email.com', '555-0115', '486 Magnolia Dr, Fort Worth, TX'),
('Paul Thompson', 'paul.thompson@email.com', '555-0116', '624 Sycamore St, Charlotte, NC'),
('Quinn Garcia', 'quinn.garcia@email.com', '555-0117', '791 Willow Ave, Seattle, WA'),
('Ruby Rodriguez', 'ruby.rodriguez@email.com', '555-0118', '135 Redwood Rd, Denver, CO'),
('Sam Martinez', 'sam.martinez@email.com', '555-0119', '246 Fir St, El Paso, TX'),
('Tina Lopez', 'tina.lopez@email.com', '555-0120', '579 Juniper Dr, Detroit, MI');

-- Insert 20 Adjusters
INSERT INTO adjusters (name, email, phone, specialization) VALUES
('John Adjuster', 'john.adjuster@company.com', '555-1001', 'Property'),
('Jane Reviewer', 'jane.reviewer@company.com', '555-1002', 'Auto'),
('Mike Assessor', 'mike.assessor@company.com', '555-1003', 'Liability'),
('Sarah Evaluator', 'sarah.evaluator@company.com', '555-1004', 'Property'),
('Tom Inspector', 'tom.inspector@company.com', '555-1005', 'Cyber'),
('Lisa Investigator', 'lisa.investigator@company.com', '555-1006', 'Health'),
('Chris Analyst', 'chris.analyst@company.com', '555-1007', 'Auto'),
('Amy Specialist', 'amy.specialist@company.com', '555-1008', 'Property'),
('Dan Expert', 'dan.expert@company.com', '555-1009', 'Liability'),
('Kate Processor', 'kate.processor@company.com', '555-1010', 'Cyber'),
('Ryan Handler', 'ryan.handler@company.com', '555-1011', 'Health'),
('Emma Reviewer', 'emma.reviewer@company.com', '555-1012', 'Auto'),
('Alex Adjuster', 'alex.adjuster@company.com', '555-1013', 'Property'),
('Sophie Assessor', 'sophie.assessor@company.com', '555-1014', 'Liability'),
('Mark Evaluator', 'mark.evaluator@company.com', '555-1015', 'Cyber'),
('Rachel Inspector', 'rachel.inspector@company.com', '555-1016', 'Health'),
('Kevin Analyst', 'kevin.analyst@company.com', '555-1017', 'Auto'),
('Jessica Specialist', 'jessica.specialist@company.com', '555-1018', 'Property'),
('Tyler Expert', 'tyler.expert@company.com', '555-1019', 'Liability'),
('Melissa Handler', 'melissa.handler@company.com', '555-1020', 'Cyber');

-- Insert 20 Policies
INSERT INTO policies (policyholder_id, policy_number, policy_type, coverage_amount, premium_amount, start_date, end_date, status) VALUES
(1, 'POL-2024-001', 'Auto Insurance', 50000.00, 1200.00, '2024-01-01', '2024-12-31', 'Active'),
(2, 'POL-2024-002', 'Home Insurance', 300000.00, 2400.00, '2024-01-15', '2025-01-15', 'Active'),
(3, 'POL-2024-003', 'Cyber Liability', 100000.00, 1800.00, '2024-02-01', '2025-02-01', 'Active'),
(4, 'POL-2024-004', 'Health Insurance', 75000.00, 3600.00, '2024-01-01', '2024-12-31', 'Active'),
(5, 'POL-2024-005', 'Liability Insurance', 200000.00, 1500.00, '2024-03-01', '2025-03-01', 'Active'),
(6, 'POL-2024-006', 'Auto Insurance', 60000.00, 1400.00, '2024-01-01', '2024-12-31', 'Active'),
(7, 'POL-2024-007', 'Home Insurance', 250000.00, 2000.00, '2024-02-15', '2025-02-15', 'Active'),
(8, 'POL-2024-008', 'Cyber Liability', 150000.00, 2200.00, '2024-03-01', '2025-03-01', 'Active'),
(9, 'POL-2024-009', 'Health Insurance', 80000.00, 3800.00, '2024-01-01', '2024-12-31', 'Active'),
(10, 'POL-2024-010', 'Liability Insurance', 175000.00, 1350.00, '2024-04-01', '2025-04-01', 'Active'),
(11, 'POL-2024-011', 'Auto Insurance', 45000.00, 1100.00, '2024-01-01', '2024-12-31', 'Active'),
(12, 'POL-2024-012', 'Home Insurance', 400000.00, 2800.00, '2024-03-15', '2025-03-15', 'Active'),
(13, 'POL-2024-013', 'Cyber Liability', 125000.00, 1900.00, '2024-04-01', '2025-04-01', 'Active'),
(14, 'POL-2024-014', 'Health Insurance', 70000.00, 3400.00, '2024-01-01', '2024-12-31', 'Active'),
(15, 'POL-2024-015', 'Liability Insurance', 225000.00, 1650.00, '2024-05-01', '2025-05-01', 'Active'),
(16, 'POL-2024-016', 'Auto Insurance', 55000.00, 1300.00, '2024-01-01', '2024-12-31', 'Active'),
(17, 'POL-2024-017', 'Home Insurance', 350000.00, 2600.00, '2024-04-15', '2025-04-15', 'Active'),
(18, 'POL-2024-018', 'Cyber Liability', 175000.00, 2400.00, '2024-05-01', '2025-05-01', 'Active'),
(19, 'POL-2024-019', 'Health Insurance', 85000.00, 4000.00, '2024-01-01', '2024-12-31', 'Active'),
(20, 'POL-2024-020', 'Liability Insurance', 190000.00, 1450.00, '2024-06-01', '2025-06-01', 'Active');

-- Insert 20 Claims
INSERT INTO claims (policy_id, adjuster_id, claim_date, claim_amount, description) VALUES
(1, 1, '2024-03-15', 5000.00, 'Vehicle collision damage'),
(2, 2, '2024-04-20', 15000.00, 'Water damage to kitchen'),
(3, 5, '2024-05-10', 25000.00, 'Data breach incident'),
(4, 6, '2024-02-28', 3500.00, 'Emergency room visit'),
(5, 3, '2024-06-01', 8000.00, 'Slip and fall accident'),
(6, 7, '2024-04-15', 12000.00, 'Rear-end collision'),
(7, 4, '2024-05-25', 20000.00, 'Storm damage to roof'),
(8, 10, '2024-06-10', 35000.00, 'Ransomware attack'),
(9, 11, '2024-03-20', 2800.00, 'Prescription medication costs'),
(10, 9, '2024-07-05', 6500.00, 'Product liability claim'),
(11, 12, '2024-04-30', 4200.00, 'Windshield replacement'),
(12, 8, '2024-06-15', 18000.00, 'Fire damage to basement'),
(13, 15, '2024-07-20', 28000.00, 'System security breach'),
(14, 16, '2024-05-15', 1500.00, 'Routine surgery'),
(15, 14, '2024-08-01', 9500.00, 'Workplace injury'),
(16, 17, '2024-06-25', 7800.00, 'Multi-vehicle accident'),
(17, 18, '2024-07-10', 22000.00, 'Hail damage to property'),
(18, 19, '2024-08-15', 42000.00, 'Corporate data theft'),
(19, 20, '2024-07-30', 950.00, 'Dental procedure'),
(20, 13, '2024-09-01', 11000.00, 'Professional negligence');

-- Insert 20 Claim Status records
INSERT INTO claim_status (claim_id, status, updated_at, notes) VALUES
(1, 'Approved', '2024-03-20 10:30:00', 'Claim approved for full amount'),
(2, 'Under Review', '2024-04-25 14:15:00', 'Waiting for additional documentation'),
(3, 'Approved', '2024-05-15 09:45:00', 'Cyber security claim validated'),
(4, 'Paid', '2024-03-05 16:20:00', 'Payment processed successfully'),
(5, 'Under Review', '2024-06-05 11:30:00', 'Investigating accident details'),
(6, 'Approved', '2024-04-20 13:45:00', 'Auto claim approved'),
(7, 'Under Review', '2024-05-30 08:15:00', 'Assessing storm damage extent'),
(8, 'Denied', '2024-06-15 15:30:00', 'Policy exclusion applies'),
(9, 'Paid', '2024-03-25 12:00:00', 'Health claim processed'),
(10, 'Approved', '2024-07-10 10:15:00', 'Liability claim approved'),
(11, 'Paid', '2024-05-05 14:30:00', 'Windshield claim paid'),
(12, 'Under Review', '2024-06-20 09:00:00', 'Fire investigation ongoing'),
(13, 'Approved', '2024-07-25 11:45:00', 'Cyber claim approved'),
(14, 'Paid', '2024-05-20 16:15:00', 'Surgery claim processed'),
(15, 'Under Review', '2024-08-05 13:20:00', 'Workplace injury review'),
(16, 'Approved', '2024-06-30 10:45:00', 'Multi-vehicle claim approved'),
(17, 'Denied', '2024-07-15 14:00:00', 'Insufficient coverage'),
(18, 'Under Review', '2024-08-20 09:30:00', 'Data theft investigation'),
(19, 'Paid', '2024-08-02 15:45:00', 'Dental claim processed'),
(20, 'Approved', '2024-09-05 12:30:00', 'Professional negligence approved');