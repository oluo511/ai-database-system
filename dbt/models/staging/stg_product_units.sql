/*
  WHY: ProductUnits stores unit sizes as raw strings like "1lb Pack", "500g Pack",
  "720ml Bottle", "6-Pack". This makes cross-supplier price comparison impossible
  without manual math. This staging model parses those strings into structured
  numeric columns so the mart can apply conversion factors consistently.

  Unit families we handle:
    - Weight:  g, kg, lb  -- normalize to grams
    - Volume:  ml, L      -- normalize to milliliters
    - Count:   pcs, Sheets, X-Pack -- normalize to individual units
*/

with source as (
    select
        ProductID,
        Unit,
        Cost,
        ListPrice,
        AvailableQuantity
    from ProductUnits
),

parsed as (
    select
        ProductID,
        Unit,
        Cost,
        ListPrice,
        AvailableQuantity,

        -- ----------------------------------------------------------------
        -- UNIT TYPE DETECTION
        -- Classify each row into a measurement family so the mart knows
        -- which conversion formula to apply
        -- ----------------------------------------------------------------
        case
            when lower(Unit) like '%kg%'       then 'weight'
            when lower(Unit) like '%lb%'       then 'weight'
            when lower(Unit) like '%g pack%'   then 'weight'
            when lower(Unit) like '%g%'        then 'weight'
            when lower(Unit) like '%ml%'       then 'volume'
            when lower(Unit) like '%.%l%'      then 'volume'  -- catches 1.8L, 18L
            when lower(Unit) like '%l bottle%' then 'volume'
            when lower(Unit) like '%l%'        then 'volume'
            when lower(Unit) like '%pcs%'      then 'count'
            when lower(Unit) like '%sheets%'   then 'count'
            when lower(Unit) like '%pack%'     then 'count'   -- covers "500g Pack" and "6-Pack"
            else 'unknown'
        end as unit_type,

        -- ----------------------------------------------------------------
        -- QUANTITY EXTRACTION
        -- Pull the leading numeric value out of the unit string.
        -- SQLite lacks regex, so we split on the first space OR hyphen.
        -- Examples: "500g Pack" -> 500, "1.8L Bottle" -> 1.8, "6-Pack" -> 6
        -- ----------------------------------------------------------------
        cast(
            case
                -- Has a space: grab everything before it ("1lb Pack" -> "1lb" -> 1)
                when instr(Unit, ' ') > 0
                    then trim(substr(Unit, 1, instr(Unit, ' ') - 1))
                -- Has a hyphen but no space: grab everything before it ("6-Pack" -> "6")
                when instr(Unit, '-') > 0
                    then trim(substr(Unit, 1, instr(Unit, '-') - 1))
                else Unit
            end
        as real) as raw_quantity,

        -- ----------------------------------------------------------------
        -- STANDARD UNIT SIZE (in base units: grams, milliliters, or pieces)
        -- Uses the same extraction logic as raw_quantity above.
        -- ----------------------------------------------------------------
        case
            -- Weight: convert to grams
            when lower(Unit) like '%kg%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real) * 1000
            when lower(Unit) like '%lb%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real) * 453.592
            when lower(Unit) like '%g pack%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real)
            when lower(Unit) like '%g%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real)
            -- Volume: convert to milliliters
            when lower(Unit) like '%ml%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real)
            when lower(Unit) like '%l bottle%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real) * 1000
            when lower(Unit) like '%l%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real) * 1000
            -- Count: pieces as-is
            -- "6-Pack" has no space so we split on hyphen
            when lower(Unit) like '%pack%' and instr(Unit, '-') > 0
                then cast(trim(substr(Unit, 1, instr(Unit, '-') - 1)) as real)
            when lower(Unit) like '%pcs%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real)
            when lower(Unit) like '%sheets%'
                then cast(trim(substr(Unit, 1, instr(Unit, ' ') - 1)) as real)
            else null
        end as quantity_in_base_unit

    from source
)

select * from parsed
