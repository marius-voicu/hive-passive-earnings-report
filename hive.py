import requests
from datetime import datetime
import pandas as pd

def fetch_passive_income():
    print("=== Universal Hive Passive Earnings Extractor ===")
    
    account_name = input("Enter your Hive username [default: steemmillionaire]: ").strip()
    if not account_name:
        account_name = "steemmillionaire"
        
    start_str = input("Enter start date (YYYY-MM-DD) [default: 60 days ago]: ").strip()
    end_str = input("Enter stop date (YYYY-MM-DD) [default: today]: ").strip()
    
    end_date = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.now()
    start_date = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.fromordinal(end_date.toordinal() - 60)
    
    print(f"\nFetching transactions for @{account_name} from {start_date.date()} to {end_date.date()}...\n")

    # Known sources
    known_sources = ["tokenpimp", "eds-pay", "edsi-pay"]
    print(f"Default known passive sources: {known_sources}")
    print("Universal Discovery Mode active (using generic financial keywords only).")
    
    url = "https://api.hive.blog"
    payload = {
        "jsonrpc": "2.0",
        "method": "condenser_api.get_account_history",
        "params": [account_name, -1, 1000],
        "id": 1
    }
    
    print("Querying Hive blockchain node...")
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        if "result" not in result:
            print("Error from Hive node:", result)
            return
        history = result["result"]
    except Exception as e:
        print(f"Connection error: {e}")
        return

    extracted_records = []
    
    # Strictly generic passive income keywords (brand names removed)
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
            
        if tx_date < start_date or tx_date > end_date:
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
        print("\nNo passive reward transactions found in this date range.")
        return

    df = pd.DataFrame(extracted_records)
    df['numeric_amount'] = df['amount'].apply(lambda x: float(x.split()[0]))
    
    print("\n" + "="*50)
    print("--- DETAILED PASSIVE TRANSACTIONS ---")
    print("="*50)
    print(df[['date', 'source', 'amount', 'memo']].to_string(index=False))
    
    print("\n" + "="*50)
    print("--- EXECUTIVE SUMMARY BY SOURCE ---")
    print("="*50)
    summary = df.groupby('source')['numeric_amount'].agg(
        Total_Earned='sum',
        Transaction_Count='count'
    )
    summary['Share (%)'] = (summary['Total_Earned'] / summary['Total_Earned'].sum()) * 100
    print(summary.round(4).to_string())
    
    grand_total = df['numeric_amount'].sum()
    print(f"\nGrand Total Passive Earnings: {grand_total:.3f} HIVE")
    print("="*50)

if __name__ == "__main__":
    fetch_passive_income()