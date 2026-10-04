{{ config(materialized='table') }}

-- Investigation-oriented analytical dataset.
--
-- This model brings the risk score together with the
-- underlying observable features that contributed to it.
--
-- It does not determine whether fraud occurred.

select
    customer_id,

    risk_score,
    risk_level,

    claim_count,
    total_claim_value,
    average_claim_value,
    maximum_claim_value,

    distinct_claim_types,
    distinct_countries,

    high_value_claim_count,
    total_risk_indicators,

    claims_last_7_days,
    claims_last_30_days

from {{ ref('fraud_risk_scores') }}

order by
    risk_score desc,
    total_risk_indicators desc