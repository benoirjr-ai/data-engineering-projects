-- =========================================================
-- Insurance Claims Warehouse Analytics
-- =========================================================
-- Purpose:
--   Manual SQL queries for exploring the claims warehouse.
--
-- Database:
--   warehouse/insurance_analytics.duckdb
--
-- Main table:
--   claims
-- =========================================================


-- =========================================================
-- 1. Inspect the claims dataset
-- =========================================================
-- Use this query to inspect the complete enriched dataset.

SELECT
    *
FROM claims;


-- =========================================================
-- 2. Claim volume by claim type
-- =========================================================
-- Shows how many claims exist for each insurance category.

SELECT
    claim_type,
    COUNT(*) AS claim_count
FROM claims
GROUP BY claim_type
ORDER BY claim_type;


-- =========================================================
-- 3. Total claim value by claim type
-- =========================================================
-- Shows the total financial value of claims in each category.

SELECT
    claim_type,
    ROUND(SUM(claim_amount), 2) AS total_claim_value
FROM claims
GROUP BY claim_type
ORDER BY total_claim_value DESC;


-- =========================================================
-- 4. High-value claims
-- =========================================================
-- Identifies claims flagged as high value by the Spark
-- enrichment layer.

SELECT
    claim_id,
    claim_type,
    claim_amount,
    country
FROM claims
WHERE high_value_claim = TRUE
ORDER BY claim_amount DESC;


-- =========================================================
-- 5. Claims with multiple risk indicators
-- =========================================================
-- Finds claims where two or more risk indicators were
-- triggered during Spark enrichment.

SELECT
    claim_id,
    claim_type,
    claim_amount,
    risk_indicator_count
FROM claims
WHERE risk_indicator_count >= 2
ORDER BY risk_indicator_count DESC;