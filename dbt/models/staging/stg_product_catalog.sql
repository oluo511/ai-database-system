/*
  WHY: Products, Categories, and Suppliers are spread across three tables.
  Every downstream model needs this join. Centralizing it here means if
  a column name changes, we fix it in one place — not in every mart.

  Note: CTE names are prefixed with 'src_' to avoid SQLite's case-insensitive
  name collision with the source tables (Products, Categories, Suppliers).
*/

with src_products as (
    select * from Products
),

src_categories as (
    select * from Categories
),

src_suppliers as (
    select * from Suppliers
)

select
    p.ProductID,
    p.ProductName,
    p.ManufacturerID,
    p.SupplierID,
    p.CategoryID,
    c.CategoryName,
    s.SupplierName,
    s.City       as SupplierCity,
    s.State      as SupplierState,
    s.SupplierType

from src_products p
left join src_categories c on p.CategoryID = c.CategoryID
left join src_suppliers  s on p.SupplierID = s.SupplierID
