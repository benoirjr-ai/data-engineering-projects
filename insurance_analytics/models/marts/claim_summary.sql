{{ config(materialized='table') }}

-- Business-facing summary of insurance claims.
-- This model uses the cleaned staging layer rather than the source table directly.

select 
    claim_type,
    count(*) as total_claims,
    round(sum(claim_amount), 2) as total_claim_value,
    round(avg(claim_amount), 2) as average_claim_value,
    sum(
        case 
            when high_value_claim then 1
            else 0
        end
    ) as high_value_claim_count

from {{ ref('stg_claims') }}
group by claim_type
order by claim_type