use zomato_analysis;
select*from new_zomato_analytics;
SET SQL_SAFE_UPDATES=0;
UPDATE `clean zomato analysis`
SET restaurant_time = REPLACE(restaurant_time, 'â€“', '-');
UPDATE `clean zomato analysis`
SET restaurant_time = REPLACE(restaurant_time, '–', '-');

SELECT restaurant_time
FROM `clean zomato analysis`
WHERE restaurant_time LIKE '%â€“%';

alter table `clean zomato analysis`
drop column payment_mode;
ALTER TABLE `clean zomato analysis`
ADD COLUMN payment_mode VARCHAR(20);
UPDATE `clean zomato analysis`
SET payment_mode = 'Cash & Card'
WHERE highlights LIKE '%Cash%'
AND (highlights LIKE '%Credit Card%' OR highlights LIKE '%Debit Card%');

UPDATE `clean zomato analysis`
SET payment_mode = 'Cash Only'
WHERE payment_mode IS NULL
AND highlights LIKE '%Cash%';

UPDATE `clean zomato analysis`
SET payment_mode = 'Card Only'
WHERE payment_mode IS NULL
AND (highlights LIKE '%Credit Card%' OR highlights LIKE '%Debit Card%');

UPDATE `clean zomato analysis`
SET payment_mode = 'UPI'
WHERE payment_mode IS NULL;

SELECT payment_mode, COUNT(*) AS Total_Restaurants
FROM `clean zomato analysis`
GROUP BY payment_mode;

select payment_mode from `clean zomato analysis`
group by payment_mode;

UPDATE `clean zomato analysis`
SET restaurant_type = NULL;

UPDATE `clean zomato analysis`
SET restaurant_type = 'Bar'
WHERE highlights LIKE '%Alcohol%'
   OR establishment = 'Bar';
   
UPDATE `clean zomato analysis`
SET restaurant_type = 'Pure Veg'
WHERE restaurant_type IS NULL
AND (
    cuisines LIKE '%South Indian%'
    OR cuisines LIKE '%Jain%'
    OR cuisines LIKE '%Vegetarian%'
    OR cuisines LIKE '%Veg%'
);

UPDATE `clean zomato analysis`
SET restaurant_type = 'Cafe'
WHERE restaurant_type IS NULL
AND (
    establishment = 'Café'
    OR establishment = 'Cafe'
    OR cuisines LIKE '%Cafe%'
);

UPDATE `clean zomato analysis`
SET restaurant_type = 'Family Restaurant'
WHERE restaurant_type IS NULL
AND establishment IN ('Casual Dining','Fine Dining');

UPDATE `clean zomato analysis`
SET restaurant_type = 'Other'
WHERE restaurant_type IS NULL;

SELECT restaurant_type, COUNT(*) AS Total
FROM `clean zomato analysis`
GROUP BY restaurant_type
ORDER BY Total DESC;

UPDATE `clean zomato analysis`
SET restaurant_type = 'Multi Cuisine'
WHERE restaurant_type = 'Other';

UPDATE `clean zomato analysis`
SET restaurant_type = NULL
WHERE restaurant_type = 'Bar';

UPDATE `clean zomato analysis`
SET restaurant_type = 'Bar'
WHERE highlights LIKE '%Alcohol%'
AND highlights NOT LIKE '%No Alcohol%';

UPDATE `clean zomato analysis`
SET restaurant_type = 'Family Restaurant'
WHERE restaurant_type IS NULL;


select restaurant_type ,count(*) from  `clean zomato analysis`
group by restaurant_type;

UPDATE `clean zomato analysis`
SET restaurant_type = NULL;

UPDATE `clean zomato analysis`
SET restaurant_type = 'Fast Food'
WHERE establishment IN ('Quick Bites', 'Food Court', 'Kiosk');

UPDATE `clean zomato analysis`
SET restaurant_type = 'Bakery'
WHERE restaurant_type IS NULL
AND establishment IN ('Bakery', 'Dessert Parlour', 'Sweet Shop');

UPDATE `clean zomato analysis`
SET restaurant_type = 'Cafe'
WHERE restaurant_type IS NULL
AND establishment IN ('Café', 'Beverage Shop');

UPDATE `clean zomato analysis`
SET restaurant_type = 'Bar'
WHERE restaurant_type IS NULL
AND establishment IN ('Bar', 'Pub');

UPDATE `clean zomato analysis`
SET restaurant_type = 'Fine Dining'
WHERE restaurant_type IS NULL
AND establishment = 'Fine Dining';

UPDATE `clean zomato analysis`
SET restaurant_type = 'Casual Dining'
WHERE restaurant_type IS NULL;

SELECT restaurant_type, COUNT(*) AS Total
FROM `clean zomato analysis`
GROUP BY restaurant_type
ORDER BY Total DESC;

UPDATE `clean zomato analysis`
SET payment_mode = NULL;

UPDATE `clean zomato analysis`
SET payment_mode = 'Cash & Card'
WHERE payment_mode IS NULL
AND highlights LIKE '%Cash%'
AND (highlights LIKE '%Credit Card%' OR highlights LIKE '%Debit Card%');

UPDATE `clean zomato analysis`
SET payment_mode = 'Cash + UPI'
WHERE payment_mode IS NULL
AND highlights LIKE '%Cash%'
AND (highlights LIKE '%UPI%' OR highlights LIKE '%Digital Payment%' OR highlights LIKE '%Wallet%');

UPDATE `clean zomato analysis`
SET payment_mode = 'Card + UPI'
WHERE payment_mode IS NULL
AND (highlights LIKE '%Credit Card%' OR highlights LIKE '%Debit Card%')
AND (highlights LIKE '%UPI%' OR highlights LIKE '%Digital Payment%' OR highlights LIKE '%Wallet%');

UPDATE `clean zomato analysis`
SET payment_mode = 'Cash Only'
WHERE payment_mode IS NULL
AND highlights LIKE '%Cash%';

UPDATE `clean zomato analysis`
SET payment_mode = 'Card Only'
WHERE payment_mode IS NULL
AND (highlights LIKE '%Credit Card%' OR highlights LIKE '%Debit Card%');

UPDATE `clean zomato analysis`
SET payment_mode = 'UPI'
WHERE payment_mode IS NULL
AND (highlights LIKE '%UPI%' OR highlights LIKE '%Digital Payment%' OR highlights LIKE '%Wallet%');

UPDATE `clean zomato analysis`
SET payment_mode = 'All Accepted'
WHERE highlights LIKE '%Cash%'
AND (highlights LIKE '%Credit Card%' OR highlights LIKE '%Debit Card%')
AND (highlights LIKE '%UPI%' OR highlights LIKE '%Digital Payment%' OR highlights LIKE '%Wallet%');

UPDATE `clean zomato analysis`
SET payment_mode = 'Cash'
WHERE payment_mode IS NULL;

SELECT payment_mode, COUNT(*) AS Total_Restaurants
FROM `clean zomato analysis`
GROUP BY payment_mode
ORDER BY Total_Restaurants DESC;
UPDATE `clean zomato analysis`
SET payment_mode = 'Cash'
WHERE payment_mode = 'Cash Only';

UPDATE `clean zomato analysis`
SET payment_mode = 'Card'
WHERE payment_mode = 'Card Only';

ALTER TABLE `clean zomato analysis` 
ADD COLUMN order_date DATE,
ADD COLUMN total_revenue DECIMAL(10,2),
ADD COLUMN target_revenue DECIMAL(10,2),
ADD COLUMN total_cost DECIMAL(10,2),
ADD COLUMN order_status VARCHAR(20);


use zomato_analysis;
select*from `clean zomato analysis` ;

UPDATE `clean zomato analysis`
SET 
    -- 2023-01-01 se aage 1095 days (3 saal: 23, 24, 25) ki random date
    order_date = DATE_ADD('2023-01-01', INTERVAL FLOOR(RAND() * 1095) DAY),
    
    -- Revenue randomly 3000 se 9000 ke beech (6001 = 9000-3000+1)
    total_revenue = FLOOR(RAND() * 6001) + 3000,
    
    -- Target randomly 4000 se 10000 ke beech (kabhi target hit hoga, kabhi miss)
    target_revenue = FLOOR(RAND() * 6001) + 4000,
    
    -- Cost hamesha revenue ka 40% se 70% ke beech hoga (Logic ke liye)
    total_cost = total_revenue * (0.4 + (RAND() * 0.3)),
    
    -- 75% chance Delivered, 15% Cancelled, 10% Refunded (Real life scenario)
    order_status = CASE 
        WHEN RAND() < 0.75 THEN 'Delivered'
        WHEN RAND() < 0.90 THEN 'Cancelled'
        ELSE 'Refunded'
    END;
    
SET SQL_SAFE_UPDATES=0;

-- Step 1: Columns add karo
ALTER TABLE `clean zomato analysis` 
ADD COLUMN discount_percent INT,
ADD COLUMN delivery_time_mins INT;

-- Step 2: Random data fill karo
UPDATE `clean zomato analysis`
SET 
    -- 0% se 30% tak random discount (Aksar Zomato pe yahi hota hai)
    discount_percent = FLOOR(RAND() * 31),
    
    -- 15 mins se 60 mins tak ka random delivery time
    delivery_time_mins = FLOOR(RAND() * 46) + 15;

ALTER TABLE`clean zomato analysis`
ADD COLUMN profit DECIMAL(12,2) NULL,
ADD COLUMN profit_margin DECIMAL(5,2) NULL,
ADD COLUMN revenue_vs_target DECIMAL(8,2) NULL;

UPDATE `clean zomato analysis` 
SET 
    profit = total_revenue - total_cost,
    profit_margin = ROUND(((total_revenue - total_cost) / total_revenue * 100), 2),
    revenue_vs_target = total_revenue - target_revenue;