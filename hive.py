import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Hive Passive Earnings Report", page_icon="🪙", layout="centered")

st.title("🪙 Hive Passive Earnings Extractor")
st.markdown("Fetch, analyze, and discover passive income payouts directly from the **Hive blockchain**.")

# Sidebar Inputs for User Configuration
st.sidebar.header("Configuration")
account_name = st.sidebar.text_input("Hive Username", value="steemmillionaire").strip()

# Date range selection (Default changed to 30 days)
default_end = datetime.now()
default_start = default_end - timedelta(days=30)

start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Sidebar Instructions (Directly visible)
st.sidebar.markdown("---")
st.sidebar.markdown("""
    
**🚀 How to Use:**
1. **Enter Username**: Type any valid Hive account name.
2. **Set Date Range**: Choose start and end dates (defaults are 30 days).
3. **Analyze Results**: View your grand total, source breakdown, daily trend bar chart, and detailed transactions ledger.

**🔍 Discovery Engine:**
* **Known Distributors**: Directly tracks payouts from accounts like `tokenpimp`, `eds-pay`, `edsi-pay`.
* **Keyword Detection**: Scans transaction memos for reward terms such as `stake`, `reward`, `dividend`, `payout`, `holding`, `ranked`.
""")

# Convert dates to datetime objects for comparison
start_dt = datetime.combine(start_date, datetime.min.time())
end_dt = datetime.combine(end_date, datetime.max.time())

# Known sources
known_sources = ["tokenpimp", "eds-pay", "edsi-pay"]

# Automatically run when the page loads or inputs change
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
        
        # Executive Summary Section (Custom HTML styling)
        st.subheader("📊 Executive Summary by Source")
        summary = df.groupby('source')['numeric_amount'].agg(
            Total_Earned='sum',
            Transaction_Count='count'
        ).reset_index()
        summary['Share (%)'] = (summary['Total_Earned'] / summary['Total_Earned'].sum()) * 100
        summary['Total_Earned'] = summary['Total_Earned'].round(4).astype(str) + " HIVE"
        summary['Share (%)'] = summary['Share (%)'].round(2).astype(str) + "%"
        
        exec_html = "<div style='max-height: none; overflow-y: visible;'><table style='width: 100%; border-collapse: collapse; font-size: 14px;'>"
        exec_html += "<tr style='border-bottom: 2px solid #ddd; text-align: left; background-color: #f9f9f9;'><th style='padding: 8px; white-space: nowrap;'>Source</th><th style='padding: 8px; white-space: nowrap;'>Total Earned</th><th style='padding: 8px; white-space: nowrap;'>Transaction Count</th><th style='padding: 8px; white-space: nowrap;'>Share (%)</th></tr>"
        
        for _, row in summary.iterrows():
            exec_html += f"<tr style='border-bottom: 1px solid #eee;'><td style='padding: 8px; white-space: nowrap;'>{row['source']}</td><td style='padding: 8px; white-space: nowrap;'>{row['Total_Earned']}</td><td style='padding: 8px; white-space: nowrap;'>{row['Transaction_Count']}</td><td style='padding: 8px; white-space: nowrap;'>{row['Share (%)']}</td></tr>"
            
        exec_html += "</table></div>"
        st.markdown(exec_html, unsafe_allow_html=True)
        
        # Visual Bar Chart Section
        st.subheader("📈 Daily Earnings Trend")
        daily_df = df.groupby('date')['numeric_amount'].sum().reset_index()
        daily_df.columns = ['Date', 'HIVE Earned']
        daily_df = daily_df.set_index('Date')
        st.bar_chart(daily_df)

        # Detailed Transactions Section (Custom HTML styling)
        st.subheader("📜 Detailed Passive Transactions")
        
        html_table = "<div style='max-height: none; overflow-y: visible;'><table style='width: 100%; border-collapse: collapse; font-size: 14px;'>"
        html_table += "<tr style='border-bottom: 2px solid #ddd; text-align: left; background-color: #f9f9f9;'><th style='padding: 8px; width: 50px;'>#</th><th style='padding: 8px; white-space: nowrap;'>Date</th><th style='padding: 8px; white-space: nowrap;'>Source</th><th style='padding: 8px; white-space: nowrap;'>Amount</th><th style='padding: 8px;'>Memo</th></tr>"
        
        for idx, row in df.iterrows():
            html_table += f"<tr style='border-bottom: 1px solid #eee;'><td style='padding: 8px; color: #666;'>{idx}</td><td style='padding: 8px; white-space: nowrap;'>{row['date']}</td><td style='padding: 8px; white-space: nowrap;'>{row['source']}</td><td style='padding: 8px; white-space: nowrap;'>{row['amount']}</td><td style='padding: 8px; overflow-wrap: break-word;'>{row['memo']}</td></tr>"
            
        html_table += "</table></div>"
        
        st.markdown(html_table, unsafe_allow_html=True)