# Hive Passive Earnings Extractor

A universal, automated Python tool designed to fetch, analyze, and report passive income payouts (such as staking and dividend rewards) directly from the **Hive blockchain** using the official JSON-RPC API.

## Features
- **Direct Node Integration:** Bypasses library constraints by querying `condenser_api.get_account_history` via `requests`.
- **Known Sources Tracking:** Automatically groups rewards from known projects like `tokenpimp`, `eds-pay`, and `edsi-pay`.
- **Universal Auto-Discovery:** Scans incoming transfers for generic financial keywords (`stake`, `reward`, `payout`, `dividend`, `holding`, `ranked`) to flag unexpected or newly discovered reward sources.
- **Executive Summary:** Generates clean terminal reports showing transaction counts, individual earnings, percentage share breakdown, and grand totals.

## Requirements
- Python 3.x
- `requests`
- `pandas`

## Installation & Usage
1. Clone the repository:
   git clone [https://github.com/marius-voicu/hive-passive-earnings-report.git](https://github.com/marius-voicu/hive-passive-earnings-report.git)
   cd hive-passive-earnings-report
2. Install dependencies:
   pip install -r requirements.txt
3. Run the script:
   python3 hive.py