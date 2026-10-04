import duckdb
import streamlit as st


DB_PATH = "warehouse/insurance_analytics.duckdb"

st.set_page_config(
    page_title="Insurance Fraud Analytics",
    page_icon="🛡️",
    layout="wide",
)

with st.sidebar:

    st.header("🛡️ Insurance Analytics")

    st.markdown(
        """
        ### Pipeline

        **Kafka**
        → **PySpark**
        → **Parquet**
        → **DuckDB**
        → **dbt**
        → **Streamlit**

        ---

        ### Risk Scoring

        **LOW**  
        Score: 0–2

        **MEDIUM**  
        Score: 3–5

        **HIGH**  
        Score: 6–10

        ---

        ### Data

        Synthetic insurance claims

        ### Purpose

        Analytical risk monitoring and
        investigation support.
        """
    )

def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

st.title("🛡️ Insurance Fraud Analytics")

st.caption(
    "Real-time insurance claims pipeline with analytical risk scoring "
    "and customer investigation insights."
)

st.info(
    "Risk levels are based on observable claim patterns in a "
    "synthetic dataset. They are analytical indicators, not confirmed "
    "fraud determinations."
)

connection = get_connection()

summary = connection.execute(
    """
    SELECT
        COUNT(*) AS total_customers,
        SUM(claim_count) AS total_claims,
        ROUND(SUM(total_claim_value), 2) AS total_claim_value,
        SUM(
            CASE
                WHEN risk_level = 'HIGH'
                THEN 1
                ELSE 0
            END
        ) AS high_risk_customers
    FROM risk_investigation
    """
).fetchone()

total_customers = summary[0]
total_claims = summary[1]
total_claim_value = summary[2]
high_risk_customers = summary[3]

st.subheader("Pipeline Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Customers",
        value=f"{total_customers:,}",
    )

with col2:
    st.metric(
        label="Claims",
        value=f"{total_claims:,}",
    )

with col3:
    st.metric(
        label="Total Claim Value",
        value=f"{total_claim_value:,.2f}",
    )

with col4:
    st.metric(
        label="High-Risk Customers",
        value=f"{high_risk_customers:,}",
    )


st.subheader("Pipeline Data Quality")

quality = connection.execute(
    """
    SELECT
        COUNT(*) AS total_claims,
        COUNT(DISTINCT customer_id) AS customers,
        COUNT(*) FILTER (
            WHERE claim_id IS NULL
        ) AS null_claim_ids,
        COUNT(*) FILTER (
            WHERE claim_amount IS NULL
        ) AS null_claim_amounts
    FROM claims
    """
).fetchone()

q1, q2, q3, q4 = st.columns(4)

with q1:
    st.metric(
        label="Claims Loaded",
        value=f"{quality[0]:,}",
    )

with q2:
    st.metric(
        label="Customers",
        value=f"{quality[1]:,}",
    )

with q3:
    st.metric(
        label="Null Claim IDs",
        value=f"{quality[2]:,}",
    )

with q4:
    st.metric(
        label="Null Claim Amounts",
        value=f"{quality[3]:,}",
    )

st.subheader("Risk Level Overview")

risk_data = connection.execute(
    """
    SELECT
        risk_level,
        customer_count,
        total_claims,
        total_claim_value,
        average_risk_score
    FROM risk_level_summary
    ORDER BY
        CASE risk_level
            WHEN 'HIGH' THEN 1
            WHEN 'MEDIUM' THEN 2
            WHEN 'LOW' THEN 3
        END
    """
).fetchdf()

st.bar_chart(
    risk_data,
    x="risk_level",
    y=["customer_count", "total_claims"],
)


st.subheader("Claim Value by Risk Level")

st.bar_chart(
    risk_data,
    x="risk_level",
    y="total_claim_value",
)

st.subheader("Claims by Type")

claim_type_data = connection.execute(
    """
    SELECT
        claim_type,
        COUNT(*) AS claim_count
    FROM claims
    GROUP BY claim_type
    ORDER BY claim_count DESC
    """
).fetchdf()

st.bar_chart(
    claim_type_data,
    x="claim_type",
    y="claim_count",
)

st.subheader("Claim Value by Type")

claim_value_type_data = connection.execute(
    """
    SELECT
        claim_type,
        ROUND(SUM(claim_amount), 2) AS total_claim_value
    FROM claims
    GROUP BY claim_type
    ORDER BY total_claim_value DESC
    """
).fetchdf()

st.bar_chart(
    claim_value_type_data,
    x="claim_type",
    y="total_claim_value",
)

st.subheader("Customers for Investigation")

risk_filter = st.selectbox(
    "Filter by risk level",
    ["ALL", "HIGH", "MEDIUM", "LOW"],
)

if risk_filter == "ALL":

    investigation_data = connection.execute(
        """
        SELECT
            customer_id,
            risk_score,
            risk_level,
            claim_count,
            high_value_claim_count,
            maximum_claim_value,
            total_risk_indicators
        FROM risk_investigation
        ORDER BY
            risk_score DESC,
            total_risk_indicators DESC
        LIMIT 10
        """
    ).fetchdf()

else:

    investigation_data = connection.execute(
        """
        SELECT
            customer_id,
            risk_score,
            risk_level,
            claim_count,
            high_value_claim_count,
            maximum_claim_value,
            total_risk_indicators
        FROM risk_investigation
        WHERE risk_level = ?
        ORDER BY
            risk_score DESC,
            total_risk_indicators DESC
        LIMIT 10
        """,
        [risk_filter],
    ).fetchdf()

st.dataframe(
    investigation_data,
    use_container_width=True,
    hide_index=True,
)


connection.close()