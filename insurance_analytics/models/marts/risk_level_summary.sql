{{ config(materialized='table') }}

-- Dashboard-facing summary by analytical risk level.
--
-- This model summarizes observable claim behavior.
-- It does not determine whether fraud occurred.

select
    risk_level,

    count(*) as customer_count,

    sum(claim_count) as total_claims,

    round(
        sum(total_claim_value),
        2
    ) as total_claim_value,

    round(
        avg(average_claim_value),
        2
    ) as average_claim_value,

    round(
        avg(risk_score),
        2
    ) as average_risk_score,

    sum(
        high_value_claim_count
    ) as high_value_claim_count

from {{ ref('risk_investigation') }}

group by risk_level

order by
    risk_level