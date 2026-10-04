-- Staging model for insurance claims.
-- This model creates a clean dbt-facing view of the raw claims table.

select
    claim_id,
    customer_id,
    customer_name,
    claim_type,
    claim_amount,
    country,
    incident_date,
    created_at,
    claim_amount_band,
    incident_age_days,
    reporting_delay_days,
    high_value_claim,
    weekend_incident,
    long_reporting_delay,
    risk_indicator_count

from {{ source('insurance', 'claims') }}