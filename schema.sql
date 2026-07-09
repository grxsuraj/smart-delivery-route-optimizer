-- ============================================
-- Smart Delivery Route Optimizer - SQL Schema
-- ============================================

DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS delay_history;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS delivery_points;

-- 1. Delivery Points (cities/nodes in the graph)
CREATE TABLE delivery_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- 2. Routes (edges in the graph, with travel time as weight)
CREATE TABLE routes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    distance_km FLOAT NOT NULL,
    avg_time_min FLOAT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES delivery_points(id),
    FOREIGN KEY (destination_id) REFERENCES delivery_points(id)
);

-- 3. Delay History (past delivery records per route)
CREATE TABLE delay_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    actual_delay_min FLOAT NOT NULL,
    delivery_date DATE NOT NULL,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

-- 4. Alerts (logged when predicted delay crosses threshold)
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id INTEGER NOT NULL,
    predicted_delay FLOAT NOT NULL,
    status VARCHAR(20) DEFAULT 'sent',   -- 'sent', 'logged'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES routes(id)
);

-- ============================================
-- Sample Data: 10 Indian Cities
-- ============================================
INSERT INTO delivery_points (name, latitude, longitude) VALUES
('Hyderabad', 17.3850, 78.4867),
('Bangalore', 12.9716, 77.5946),
('Chennai',   13.0827, 80.2707),
('Pune',      18.5204, 73.8567),
('Mumbai',    19.0760, 72.8777),
('Delhi',     28.7041, 77.1025),
('Kolkata',   22.5726, 88.3639),
('Nagpur',    21.1458, 79.0882),
('Ahmedabad', 23.0225, 72.5714),
('Jaipur',    26.9124, 75.7873);

-- ============================================
-- Sample Data: Routes (edges) — time in minutes, distance in km
-- Graph is not fully connected (mimics real road network gaps)
-- ============================================
INSERT INTO routes (source_id, destination_id, distance_km, avg_time_min) VALUES
(1, 2, 570, 480),   -- Hyderabad -> Bangalore
(1, 3, 625, 510),   -- Hyderabad -> Chennai
(1, 4, 560, 470),   -- Hyderabad -> Pune
(1, 8, 500, 420),   -- Hyderabad -> Nagpur
(2, 3, 350, 300),   -- Bangalore -> Chennai
(2, 9, 980, 720),   -- Bangalore -> Ahmedabad
(3, 4, 1170, 900),  -- Chennai -> Pune
(4, 5, 150, 180),   -- Pune -> Mumbai
(4, 8, 720, 540),   -- Pune -> Nagpur
(5, 9, 530, 420),   -- Mumbai -> Ahmedabad
(5, 6, 1400, 1080), -- Mumbai -> Delhi
(6, 10, 280, 300),  -- Delhi -> Jaipur
(6, 7, 1500, 1200), -- Delhi -> Kolkata
(8, 6, 890, 660),   -- Nagpur -> Delhi
(8, 7, 1000, 780),  -- Nagpur -> Kolkata
(9, 10, 660, 540),  -- Ahmedabad -> Jaipur
(10, 6, 280, 300);  -- Jaipur -> Delhi

-- ============================================
-- Sample Data: Delay History (past deliveries per route)
-- ============================================
INSERT INTO delay_history (route_id, actual_delay_min, delivery_date) VALUES
(1, 20, '2026-06-01'), (1, 35, '2026-06-05'), (1, 15, '2026-06-10'),
(2, 10, '2026-06-02'), (2, 12, '2026-06-08'), (2, 8,  '2026-06-12'),
(3, 40, '2026-06-01'), (3, 45, '2026-06-06'), (3, 38, '2026-06-11'),
(4, 25, '2026-06-03'), (4, 30, '2026-06-09'),
(5, 5,  '2026-06-04'), (5, 7,  '2026-06-10'),
(6, 60, '2026-06-02'), (6, 55, '2026-06-07'),
(7, 90, '2026-06-01'), (7, 85, '2026-06-06'),
(8, 10, '2026-06-05'), (8, 12, '2026-06-11'),
(9, 20, '2026-06-03'), (9, 18, '2026-06-09'),
(10, 15, '2026-06-04'), (10, 20, '2026-06-10'),
(11, 70, '2026-06-01'), (11, 65, '2026-06-08'),
(12, 25, '2026-06-02'), (12, 22, '2026-06-09'),
(13, 95, '2026-06-01'), (13, 100,'2026-06-07'),
(14, 40, '2026-06-03'), (14, 45, '2026-06-10'),
(15, 60, '2026-06-02'), (15, 55, '2026-06-09'),
(16, 30, '2026-06-04'), (16, 28, '2026-06-11'),
(17, 20, '2026-06-05'), (17, 18, '2026-06-12');
