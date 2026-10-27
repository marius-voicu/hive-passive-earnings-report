import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Hive Passive Earnings Report", page_icon="🪙", layout="centered")

st.title("🪙 Hive Passive Earnings Extractor")
st.markdown("Fetch, analyze, and discover passive income payouts directly from the **Hive blockchain**.")

# Sidebar Inputs for User Configuration
st.sidebar.header("Configuration")
account_name = st.sidebar.text_input("Hive Username", value="steemmillionaire").strip()

# Date range selection
default_end = datetime.now()
default_start = datetime.fromordinal(default_end.toordinal() - 60)

start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Convert dates to datetime objects for comparison
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

# Known sources
known_sources = ["tokenpimp", "eds-pay", "edsi-pay"]

if st.sidebar.button("Run Report", type="primary"):
    with st.spinner(f"Querying Hive node for @{account_name}..."):
        url = "https://api.hive.blog"
        payload = {
            "jsonrpc": "2.0",
            "method": "condenser_api.get_account_history",
            "params": [account_name, -1, 1000],
            "id": 1
        }
        
        try:
            response = requests.post(url, json=payload)
            result = response.json()
            if "result" not in result:
                st.error(f"Error from Hive node: {result}")
                st.stop()
            history = result["result"]
        except Exception as e:
            st.error(f"Connection error: {e}")
            st.stop()

        extracted_records = []
        passive_keywords = ["stake", "reward", "payout", "dividend", "holding", "ranked"]

        for item in history:
            tx_data = item[1]
            timestamp_str = tx_data.get("timestamp")
            if not timestamp_str:
                continue
                
            try:
                tx_date = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
                
            if tx_date < start_dt or tx_date > end_dt:
                continue
                
            op = tx_data.get("op", ["unknown", {}])
            op_type = op[0]
            op_payload = op[1]
            
            if op_type == "transfer":
                sender = op_payload.get("from")
                receiver = op_payload.get("to")
                amount = op_payload.get("amount")
                memo = op_payload.get("memo", "").lower()
                
                if receiver == account_name:
                    is_known = sender in known_sources
                    has_reward_memo = any(keyword in memo for keyword in passive_keywords)
                    
                    if is_known or has_reward_memo:
                        source_label = sender if is_known else f"{sender} (Discovered)"
                        extracted_records.append({
                            "date": tx_date.strftime("%Y-%m-%d"),
                            "source": source_label,
                            "amount": amount,
                            "memo": op_payload.get("memo", "")
                        })

        if not extracted_records:
            st.warning("No passive reward transactions found in this date range.")
        else:
            df = pd.DataFrame(extracted_records)
            df['numeric_amount'] = df['amount'].apply(lambda x: float(x.split()[0]))
            
            grand_total = df['numeric_amount'].sum()
            
            # Display Metric Header
            st.metric(label="Grand Total Passive Earnings", value=f"{grand_total:.3f} HIVE")
            
            # Executive Summary Section
            st.subheader("📊 Executive Summary by Source")
            summary = df.groupby('source')['numeric_amount'].agg(
                Total_Earned='sum',
                Transaction_Count='count'
            )
            summary['Share (%)'] = (summary['Total_Earned'] / summary['Total_Earned'].sum()) * 100
            st.dataframe(summary.round(4), use_container_width=True)
            
            # Detailed Transactions Section
            st.subheader("📜 Detailed Passive Transactions")
            st.dataframe(df[['date', 'source', 'amount', 'memo']], use_container_width=True)