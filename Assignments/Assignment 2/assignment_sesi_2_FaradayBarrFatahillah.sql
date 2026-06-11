#TASK 1.1
SELECT product_name, unit_price, units_in_stock 
FROM products 
ORDER BY unit_price DESC
LIMIT 10;

#TASK 1.2
SELECT product_name, unit_price, units_in_stock 
FROM products 
WHERE units_in_stock < 10;

#TASK 1.3
SELECT COUNT(*) AS discontinued_products
FROM products 
WHERE discontinued=1;

#TASK 2.1
SELECT
    categories.category_name, COUNT(products.product_id) AS jumlah_produk
FROM categories
JOIN products ON products.category_id=categories.category_id
GROUP BY categories.category_name
ORDER BY jumlah_produk DESC;

#TASK 2.2
SELECT
    categories.category_name,
    ROUND(SUM(products.unit_price * products.units_in_stock)::NUMERIC,2) AS total_nilai 
FROM categories
JOIN products ON products.category_id=categories.category_id
GROUP BY categories.category_id
ORDER BY total_nilai DESC;

#TASK 2.3
SELECT 
    categories.category_name,
    ROUND(SUM(products.unit_price * products.units_in_stock)::NUMERIC,2) total_nilai 
FROM categories
JOIN products ON products.category_id=categories.category_id
GROUP BY categories.category_id
HAVING ROUND(SUM(products.unit_price * products.units_in_stock)::NUMERIC,2) >= 10000;

#TASK 3.1
SELECT 
    EXTRACT(YEAR FROM orders.order_date) AS year,
    EXTRACT(MONTH FROM orders.order_date) AS month,
    COUNT(*) total_order
FROM orders
GROUP BY year, month
ORDER BY total_order DESC;

#TASK 3.2
SELECT 
    EXTRACT(MONTH FROM orders.order_date) AS month,
    COUNT(*) total_order
FROM orders
GROUP BY month
ORDER BY total_order DESC;
# Karena stok saat winter sudah habis, jadi pesan lagi untuk memenuhi kebutuhan di spring

#TASK 3.3 
SELECT 
    ship_country, 
    ROUND(AVG(freight)::NUMERIC,2) rata2_freight 
FROM orders 
GROUP BY ship_country 
ORDER BY rata2_freight DESC 
LIMIT 5;

#TASK 4.1
SELECT 
    employees.employee_id,
    employees.first_name,
    employees.last_name,
    COUNT(orders.employee_id) AS jumlah_order_employee
FROM employees
JOIN orders ON orders.employee_id=employees.employee_id
GROUP BY employees.employee_id
ORDER BY jumlah_order_employee DESC;

#TASK 4.2
SELECT 
    employees.employee_id,
    employees.first_name,
    employees.last_name,
    COUNT(orders.employee_id) AS jumlah_order_employee
FROM employees
JOIN orders ON orders.employee_id=employees.employee_id
GROUP BY employees.employee_id
HAVING COUNT(orders.employee_id) > 100 
ORDER BY jumlah_order_employee DESC;

#TASK 4.3
-- Karyawan dengan order terbanyak adalah 
-- Margaret Peacock dengan jumlah order sebanyak 156

#TASK 5.1
-- Seafood, karena menurut saya seafood adalah 
-- luxury item yang dimakan saat special occasions 
-- seperti paskah, new years christmas, dst.

#TASK 5.2
-- Ada, dengan 4 bulan pertama (januari, februari, maret, dan april) 
-- paling sering mengalami pengiriman