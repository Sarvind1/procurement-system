-- Create admin user
INSERT INTO users (email, hashed_password, full_name, role, is_active, is_superuser)
VALUES ('admin@example.com', 'hashed_password_here', 'System Administrator', 'ADMIN', true, true)
ON CONFLICT (email) DO NOTHING;

-- Create initial categories
INSERT INTO category (name, description)
VALUES 
    ('Raw Materials', 'Basic materials used in manufacturing'),
    ('Components', 'Pre-manufactured parts and assemblies'),
    ('Finished Goods', 'Ready-to-sell products'),
    ('Packaging', 'Materials used for product packaging'),
    ('Office Supplies', 'General office materials and equipment'),
    ('IT Equipment', 'Computers, servers, and networking equipment'),
    ('Maintenance', 'Tools and supplies for maintenance'),
    ('Services', 'Professional and technical services')
ON CONFLICT (name) DO NOTHING;

-- Create initial suppliers
INSERT INTO supplier (name, code, category, status, tax_id, payment_terms, credit_limit, currency, is_preferred)
VALUES 
    ('Global Manufacturing Inc.', 'GMI001', 'MANUFACTURER', 'ACTIVE', '123456789', 30, 100000.00, 'USD', true),
    ('Tech Distributors Ltd.', 'TDL002', 'DISTRIBUTOR', 'ACTIVE', '987654321', 45, 50000.00, 'USD', false),
    ('Office Supplies Co.', 'OSC003', 'WHOLESALER', 'ACTIVE', '456789123', 30, 25000.00, 'USD', false)
ON CONFLICT (code) DO NOTHING; 