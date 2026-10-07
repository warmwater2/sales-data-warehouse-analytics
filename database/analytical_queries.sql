-- 1. Total Sales
SELECT 
    SUM(sales_amount) AS total_sales
FROM fact_sales;


-- 2. Total Profit
SELECT 
    SUM(profit) AS total_profit
FROM fact_sales;


-- 3. Sales by Category
SELECT
    p.category,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_sales DESC;


-- 4. Sales by Region
SELECT
    l.region,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY l.region
ORDER BY total_sales DESC;


-- 5. Top 5 Products by Sales
SELECT
    p.product_name,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
GROUP BY p.product_name
ORDER BY total_sales DESC
LIMIT 5;

-- OLAP: ROLL-UP
SELECT
    l.region,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY l.region
ORDER BY l.region;


-- OLAP: DRILL-DOWN
SELECT
    l.region,
    l.state,
    l.city,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_location l
    ON f.location_key = l.location_key
GROUP BY l.region, l.state, l.city
ORDER BY l.region, l.state, total_sales DESC;


-- OLAP: SLICE
SELECT
    p.category,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
WHERE p.category = 'Technology'
GROUP BY p.category;


-- OLAP: DICE
SELECT
    p.category,
    l.region,
    SUM(f.sales_amount) AS total_sales
FROM fact_sales f
JOIN dim_product p
    ON f.product_key = p.product_key
JOIN dim_location l
    ON f.location_key = l.location_key
WHERE p.category IN ('Technology', 'Furniture')
AND l.region IN ('West', 'East')
GROUP BY p.category, l.region
ORDER BY p.category, l.region;