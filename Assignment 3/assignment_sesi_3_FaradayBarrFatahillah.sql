#TASK 1.1
SELECT 
    order_id,
    company_name,
    first_name|| ' ' ||last_name AS employee_name,
    order_date
FROM orders o
JOIN customers c using(customer_id)
JOIN employees e using(employee_id)
ORDER BY order_date DESC
LIMIT 20;

#TASK 1.2
SELECT
    customer_id,
    company_name
FROM customers
LEFT JOIN orders USING(customer_id)
WHERE order_id IS NULL;

SELECT
    customer_id,
    company_name
FROM orders
RIGHT JOIN customers USING(customer_id)
WHERE order_id IS NULL;

#TASK 1.3
-- Terdapat 2 pelanggan yang belum pernah order

#TASK 2.1
SELECT
    company_name,
    country,
    ROUND(SUM(unit_price * quantity * (1-discount))::NUMERIC, 2) as revenue
FROM customers
JOIN orders USING (customer_id)
JOIN order_details USING (order_id)
GROUP BY 1, 2
ORDER BY revenue DESC;

#TASK 2.2
SELECT
    company_name,
    country,
    ROUND(SUM(unit_price * quantity * (1-discount))::NUMERIC, 2) as revenue
FROM customers
JOIN orders USING (customer_id)
JOIN order_details USING (order_id)
WHERE country in ('USA', 'Germany')
GROUP BY 1, 2
HAVING (ROUND(SUM(unit_price * quantity * (1-discount))::NUMERIC, 2) >= 10000) 
ORDER BY revenue DESC;

#TASK 2.3
-- Normal Subquery
SELECT
    country,
    ROUND(AVG(revenue)) AS rata2_revenue,
    COUNT(company_name) AS jumlah_company
FROM (
    SELECT
        company_name,
        country,
        ROUND(SUM(unit_price * quantity * (1-discount))::NUMERIC, 2) as revenue
    FROM customers
    JOIN orders USING (customer_id)
    JOIN order_details USING (order_id)
    GROUP BY 1, 2
    ORDER BY revenue DESC
)
GROUP BY country
ORDER BY rata2_revenue DESC
LIMIT 10;

-- with CTE
WITH base AS (
    SELECT
        company_name,
        country,
        ROUND(SUM(unit_price * quantity * (1-discount))::NUMERIC, 2) as revenue
    FROM customers c
    JOIN orders USING (customer_id)
    JOIN order_details USING (order_id)
    GROUP BY 1, 2
    ORDER BY revenue DESC
)
SELECT
    country,
    ROUND(AVG(revenue),2) AS rata2_revenue,
    COUNT(company_name) AS jumlah_company
FROM base
GROUP BY 1
ORDER BY rata2_revenue DESC
LIMIT 10;

#TASK 3.1
SELECT
    product_name,
    unit_price,
    category_name
FROM products
LEFT JOIN categories USING (category_id)
WHERE unit_price > (
    SELECT AVG(unit_price)
    FROM products)
ORDER BY unit_price DESC;

#TASK 3.2
SELECT 
    product_id,
    SUM(quantity) AS total_kuantitas
FROM order_details
GROUP BY product_id
HAVING (SUM(quantity)) > (
    SELECT
        AVG(total_qty)
    FROM (
        SELECT 
            product_id,
            SUM(quantity) as total_qty
        FROM order_details
        GROUP BY product_id
    ) 
)

#TASK 3.3
SELECT
    product_name,
    product_id,
    total_kuantitas
FROM(
    SELECT
        product_id,
        SUM(quantity) AS total_kuantitas
    FROM order_details
    GROUP BY product_id
    HAVING (SUM(quantity)) > (
        SELECT
            AVG(total_qty)
        FROM (
            SELECT 
                product_id,
                SUM(quantity) as total_qty
            FROM order_details
            GROUP BY product_id
        ) 
    )
)
JOIN products USING (product_id)
ORDER BY total_kuantitas DESC;

#TASK 4.1
SELECT 
    company_name,
    COUNT(product_id) AS total_produk
FROM suppliers
JOIN products USING (supplier_id)
GROUP BY supplier_id, company_name
HAVING (COUNT(product_id)>2)
ORDER BY total_produk DESC;

#TASK 4.2
SELECT 
    company_name,
    category_name,
    COUNT(product_id) AS total_produk
FROM suppliers
JOIN products USING (supplier_id)
JOIN categories USING (category_id)
WHERE supplier_id IN (
    SELECT supplier_id
    FROM products
    GROUP BY supplier_id
    HAVING (COUNT(product_id)>2)
)
GROUP BY company_name, category_name
ORDER BY total_produk DESC;

#TASK 4.3
SELECT
    company_name,
    AVG(unit_price) AS avg_price
FROM suppliers
JOIN products USING (supplier_id)
GROUP BY supplier_id, company_name
ORDER BY avg_price DESC
LIMIT 1;

SELECT *  FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY
            company_name
        ORDER BY avg_price DESC
    ) as rn
    FROM (
        SELECT 
            company_name,
            product_name,
            AVG(unit_price) as avg_price
        FROM suppliers
        JOIN products USING (supplier_id)
        GROUP BY 1, 2
        ORDER BY 1 ASC, 3 DESC
    )
)
WHERE rn = 1

#Task 5
SELECT
    product_name,
    category_name,
    ROUND(SUM(od.unit_price * quantity * (1-discount))::NUMERIC, 2) as revenue
FROM customers
JOIN orders USING (customer_id)
JOIN order_details od USING (order_id)
JOIN products USING (product_id)
JOIN categories USING (category_id)
GROUP BY product_name, category_name
ORDER BY revenue DESC
LIMIT 5;
