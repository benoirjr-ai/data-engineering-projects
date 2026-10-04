{{ config(materialized='table') }}

-- Analytical customer risk scoring model.
--
-- This model does NOT determine whether fraud occurred.
-- It assigns a transparent score based on observable claim patterns.

with scored_customers as (

    select
        customer_id,

        claim_count,
        total_claim_value,
        average_claim_value,
        maximum_claim_value,
        distinct_claim_types,
        distinct_countries,
        high_value_claim_count,
        total_risk_indicators,
        claims_last_7_days,
        claims_last_30_days,

        (
            case
                when claim_count >= 5
                then 1
                else 0
            end

            +

            case
                when claims_last_7_days >= 3
                then 2
                else 0
            end

            +

            case
                when high_value_claim_count >= 2
                then 2
                else 0
            end

            +

            case
                when maximum_claim_value >= 20000
                then 2
                else 0
            end

            +

            case
                when total_risk_indicators >= 6
                then 2
                else 0
            end

            +

            case
                when distinct_countries >= 3
                then 1
                else 0
            end

        ) as risk_score

    from {{ ref('fraud_features') }}

)

select
    *,

    case
        when risk_score <= 2
            then 'LOW'

        when risk_score <= 5
            then 'MEDIUM'

        else 'HIGH'
    end as risk_level

from scored_customers