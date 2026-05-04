/*
  WHY: This is the analytical layer that makes cross-supplier price comparison
  possible. By joining the parsed unit data with product info, we can answer
  questions like "which supplier has the cheapest Smoked Salmon per kg?" —
  a query that was impossible against the raw ProductUnits table because
  units were mixed (grams vs pounds).

  Standard units used:
    - Weight  → price per KG   (multiply per-gram price by 1000)
    - Volume  → price per LITER (multiply per-ml price by 1000)
    - Count   → price per UNIT  (direct division)

  This table is materialized (not a view) so the analyst agent gets
  fast reads without re-running the CASE logic on every query.
*/

with product_units as (
    select * from {{ ref('stg_product_units') }}
),

products as (
    select * from {{ ref('stg_product_catalog') }}
)

select
    p.ProductID,
    p.ProductName,
    p.CategoryName,
    p.SupplierName,
    p.SupplierCity,
    p.SupplierState,
    p.SupplierType,

    pu.Unit                  as OriginalUnit,
    pu.unit_type,
    pu.raw_quantity,
    pu.quantity_in_base_unit,
    pu.Cost,
    pu.ListPrice,
    pu.AvailableQuantity,

    -- ----------------------------------------------------------------
    -- NORMALIZED PRICE COLUMNS
    -- These are the columns your analyst agent should query.
    -- NULL when the unit type doesn't apply (e.g., no price_per_liter
    -- for a weight-based product) — keeps comparisons honest.
    -- ----------------------------------------------------------------

    -- Price per KG (weight products only)
    case
        when pu.unit_type = 'weight' and pu.quantity_in_base_unit > 0
            then round((pu.ListPrice / pu.quantity_in_base_unit) * 1000, 4)
        else null
    end as list_price_per_kg,

    case
        when pu.unit_type = 'weight' and pu.quantity_in_base_unit > 0
            then round((pu.Cost / pu.quantity_in_base_unit) * 1000, 4)
        else null
    end as cost_per_kg,

    -- Price per LITER (volume products only)
    case
        when pu.unit_type = 'volume' and pu.quantity_in_base_unit > 0
            then round((pu.ListPrice / pu.quantity_in_base_unit) * 1000, 4)
        else null
    end as list_price_per_liter,

    case
        when pu.unit_type = 'volume' and pu.quantity_in_base_unit > 0
            then round((pu.Cost / pu.quantity_in_base_unit) * 1000, 4)
        else null
    end as cost_per_liter,

    -- Price per UNIT (count products only)
    case
        when pu.unit_type = 'count' and pu.quantity_in_base_unit > 0
            then round(pu.ListPrice / pu.quantity_in_base_unit, 4)
        else null
    end as list_price_per_unit,

    case
        when pu.unit_type = 'count' and pu.quantity_in_base_unit > 0
            then round(pu.Cost / pu.quantity_in_base_unit, 4)
        else null
    end as cost_per_unit,

    -- ----------------------------------------------------------------
    -- MARGIN
    -- Useful for the analyst agent to answer "which SKU has the best margin?"
    -- ----------------------------------------------------------------
    round(pu.ListPrice - pu.Cost, 2)                              as gross_margin,
    round((pu.ListPrice - pu.Cost) / nullif(pu.ListPrice, 0), 4) as margin_pct

from product_units pu
inner join products p on pu.ProductID = p.ProductID
