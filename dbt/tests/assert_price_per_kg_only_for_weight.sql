/*
  SINGULAR TEST: Price normalization logic correctness

  WHY: The mart uses CASE WHEN to assign list_price_per_kg only to weight-type
  products. If this leaks into volume or count products, the normalization is
  broken and cross-supplier comparisons would be invalid.

  This test returns rows that FAIL the assertion.
  dbt expects 0 rows returned = test passes.
*/

select *
from {{ ref('mart_product_pricing') }}
where
    -- list_price_per_kg should ONLY be populated for weight products
    (unit_type != 'weight' and list_price_per_kg is not null)
    or
    -- list_price_per_liter should ONLY be populated for volume products
    (unit_type != 'volume' and list_price_per_liter is not null)
    or
    -- list_price_per_unit should ONLY be populated for count products
    (unit_type != 'count' and list_price_per_unit is not null)
