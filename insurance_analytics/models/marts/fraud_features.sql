{{ config(materialized='table') }}

-- Customer-level fraud analysis features.
--
-- One row represents one customer.
-- These features describe observable claim behavior.
-- They are analytical features, not fraud decisions.

with customer_claims as (

    select
        customer_id,
        claim_type,
        claim_amount,
        country,
        incident_date,
        high_value_claim,
        risk_indicator_count,

        max(incident_date) over (
            partition by customer_id
        ) as latest_incident_date

    from {{ ref('stg_claims') }}

),

customer_features as (

    select
        customer_id,

        count(*) as claim_count,

        round(
            sum(claim_amount),
            2
        ) as total_claim_value,

        round(
            avg(claim_amount),
            2
        ) as average_claim_value,

        round(
            max(claim_amount),
            2
        ) as maximum_claim_value,

        count(
            distinct claim_type
        ) as distinct_claim_types,

        count(
            distinct country
        ) as distinct_countries,

        sum(
            case
                when high_value_claim then 1
                else 0
            end
        ) as high_value_claim_count,

        sum(
            risk_indicator_count
        ) as total_risk_indicators,

        sum(
            case
                when incident_date >= latest_incident_date - interval '7 days'
                then 1
                else 0
            end
        ) as claims_last_7_days,

        sum(
            case
                when incident_date >= latest_incident_date - interval '30 days'
                then 1
                else 0
            end
        ) as claims_last_30_days

    from customer_claims

    group by customer_id

)

select *
from customer_features