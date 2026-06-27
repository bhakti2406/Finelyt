# 📈 Finelyt | AI-Powered Personal Finance Hub

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Streamlit%20v1.58.0-red.svg)](https://streamlit.io/)
[![Model](https://img.shields.io/badge/AI%20Engine-Gemini%202.5%20Flash-orange.svg)](https://ai.google.dev/)
[![ML Model](https://img.shields.io/badge/ML%20Outlier%20Detection-Isolation%20Forest-green.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

**Finelyt** is a premium, bank-grade AI Personal Finance Hub designed to track expenses, detect anomalous spending leakages using Machine Learning, forecast future cash flows, and build smarter financial habits. Powered by **Google Gemini 2.5 Flash** and featuring a modern dark glassmorphic interface, Finelyt aligns your spending with globally recognized financial frameworks (50-30-20, FIRE, and emergency readiness) while guaranteeing extreme data privacy.

---

## 🗺️ Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Security & Compliance Protocol](#-security--compliance-protocol)
- [Requirements](#-requirements)
- [Installation Steps](#-installation-steps)
- [Usage Instructions](#-usage-instructions)
- [Screenshots & UI Walkthrough](#-screenshots--ui-walkthrough)
- [Future Roadmap](#-future-roadmap)
- [Contributors](#-contributors)
- [License](#-license)

---

## 🔍 Project Overview

Managing personal finances is more than just logging receipts; it is about recognizing patterns, identifying waste, and planning for long-term targets. **Finelyt** bridges the gap between raw data entry and professional advisory:
- **Rule-based & AI-Driven Auditing:** Instantly scans transactions for subscription leaks, impulse spending, lifestyle inflation, and post-salary spikes.
- **Outlier Detection:** Employs an unsupervised **Isolation Forest** ML algorithm to flag abnormal spending patterns compared to your historical mean.
- **Predictive Analytics:** Projects upcoming cash flows (1M, 3M, 6M) using linear regression models with seasonal variations, runs goal feasibility simulations, and builds inflation-adjusted retirement models.

---

## ✨ Key Features

### 1. Smart Financial Dashboard
* **Dynamic KPIs:** Real-time visibility into Total Spent, Daily Averages, Active Transactions, and Anomalies.
* **Rich Visualizations:** Interactive Plotly charts showing category-wise spending distributions and monthly cash flow trends.
* **Month-on-Month Comparisons:** Category-by-category comparisons between the current month and the previous month.
* **Smart Notification Center:** Automated rule-based system alerting users to budget limits, bill deadlines, and spending anomalies.

### 2. AI Personal Finance Coach 2.0
* **Behavioral Auditing:** Scans transactions using four specialized filters:
  * *Impulse Spikes:* Detects multiple non-essential purchases on consecutive days.
  * *Lifestyle Inflation:* Evaluates if month-on-month spending velocity is outpacing income growth.
  * *Subscription Leakage:* Flags multiple duplicate charges under subscription categories.
  * *Post-Salary Spikes:* Identifies if more than 35% of income is spent within 5 days of credit.
* **Interactive LLM chat:** Contextualized chatbot integration using `google-genai` client libraries powered by `gemini-2.5-flash` with quick-prompt triggers.

### 3. Machine Learning Anomaly Detection
* **Unsupervised ML:** Employs `scikit-learn` Isolation Forest trained locally on your expense vectors (amount, day of week, day of month, month, weekend status, category average ratio).
* **Severity Grading:** Flags anomaly scores into LOW, MEDIUM, or HIGH categories.
* **Retraining Pipeline:** Built-in retraining dashboard so users can update the model as they record more data.

### 4. Planning & Wealth Modules
* **Net Worth Tracker:** Multi-tab interface to log assets (savings, real estate, vehicles, gold, investments) and liabilities (credit cards, education loans, home mortgages).
* **Target Wealth Milestones:** Tracking roadmap showing levels achieved and progress toward the final financial freedom target.
* **Asset Allocation suggestions:** Educational investment allocation suggestions based on conservative, moderate, or aggressive risk appetites.

### 5. Advanced Financial Forecasting
* **Cash Flow Projections:** Combines historical records with multi-month regression lines to predict income, expenses, and savings.
* **Goal Feasibility:** Calculates target completion dates and probability percentages for savings goals based on current velocity.
* **Inflation-Adjusted Retirement Modeler:** Projects post-retirement needs using the safe withdrawal rate (25x annual expense) and solves for required monthly contribution deficits.

---

## 🏗️ System Architecture

### Project Structure
```text
FinanceCoach/
├── .env.example            # Environment variables placeholder
├── .gitignore              # Files ignored by git (credentials, binaries, db)
├── requirements.txt        # Python dependency requirements
├── app.py                  # Main entry point & mega-nav routing
├── app_styles.py           # Design tokens, global CSS, SVG logo templates
├── app_icons.py            # Custom SVG icon dictionary
├── data/
│   ├── finance.db          # SQLite Database (created on app launch)
│   └── sent_emails.log     # SMTP Email transmission logs (verification fallback)
├── models/
│   ├── anomaly_model.pkl   # Serialized Isolation Forest ML model
│   └── train_model.py      # ML Model training script
├── pages/                  # Multipage dashboard views
│   ├── add_expense.py      # Expense creation forms
│   ├── ai_coach.py         # AI Personal Coach chat canvas
│   ├── anomalies.py        # ML anomaly logging & charts
│   ├── bill_calendar.py    # Bill calendar calendar grids & status tags
│   ├── budgets.py          # Category-wise budget limits & recurring bills
│   ├── compliance.py       # Platform security architecture guidelines
│   ├── dashboard.py        # Executive KPI & breakdown charts
│   ├── forecasting.py      # Forecasting, feasibility & retirement dashboards
│   ├── health_score.py     # Framework calculators (50-30-20, FIRE, emergency)
│   ├── income.py           # Income source tracking
│   ├── networth.py         # Net worth assets & liabilities
│   ├── reports.py          # CSV reports exporting
│   ├── risk_engine.py      # Liquidity, debt, overspending risk matrix
│   ├── savings.py          # Savings goals & deposits
│   ├── settings.py         # Account details, session history & account deletion
│   ├── streaks.py          # Days under daily spending limits & calendar heatmap
│   ├── summary.py          # Quick cashflow overview tables
│   └── wealth_module.py    # Milestone roadmaps & risk profiles
└── utils/                  # Core modules & database transactions
    ├── auth.py             # User signup, password hashing, session tokens, rate limiting
    ├── currency.py         # Currency formatter & symbols
    ├── db.py               # Database initialization & SQL operations
    ├── features.py         # ML feature preparation pipeline
    ├── forecasting.py      # Cash flow trend projection & retirement math
    ├── health_score.py     # Score breakdown calculation & history logs
    ├── notifications.py    # Automated notification rules engine
    └── predict.py          # Isolation Forest inference & explanations
```

---

## 🔒 Security & Compliance Protocol

Finelyt is designed with **bank-grade security guidelines** to ensure sensitive financial data remains secure:
1. **Data Encryption:** All sensitive transaction records and credentials are encrypted at rest using **AES-256 GCM**.
2. **Cryptographic Sessions:** To prevent session hijacking and query-parameter tampering, session tokens are signed using **HMAC-SHA256** with a server-level secret key.
3. **MFA Verification:** Account creation and registration require a 2FA step via a 6-digit OTP code sent using secure **SMTP protocol**.
4. **Rate Limiting:** Brute force defense built-in (lockouts after 5 consecutive login failures) and API rate limiting on chat prompts (10 requests/minute).
5. **GDPR Compliance:** Complete data erasure pipeline. Triggering account deletion from [settings.py](file:///c:/Users/Ved/Downloads/FinanceCoach/pages/settings.py) permanently wipes all tables matching that user ID inside a single transactional block (expenses, income, budgets, net worth history, logs, and account records).

---

## 📋 Requirements

* **Operating System:** Windows, macOS, or Linux
* **Python Version:** Python 3.10, 3.11, or 3.12
* **Required Libraries:** Reference the pinned versions in `requirements.txt`:
  * `streamlit` (App UI)
  * `pandas` & `numpy` (Data processing)
  * `scikit-learn` & `joblib` (ML modeling & serialization)
  * `plotly` (Interactive charts)
  * `google-genai` (Gemini API interactions)
  * `python-dotenv` (Environment configurations)
  * `bcrypt` (Secure password hashing)

---

## 🚀 Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/finance-coach.git
cd finance-coach
```

### 2. Configure Environment Variables
Copy the env template file:
```bash
cp .env.example .env
```
Open `.env` and configure the variables:
```ini
# Core LLM API Key (Get a key at https://aistudio.google.com)
GEMINI_API_KEY=your_gemini_api_key_here

# Encryption Session Security Key
SECRET_KEY=your_random_hmac_secret_key_here

# SMTP 2FA Settings (e.g., using Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=Finelyt Security <your-email@gmail.com>
```

### 3. Setup Virtual Environment & Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Usage Instructions

### 1. Launch the Application
Run the Streamlit server using:
```bash
streamlit run app.py
```
By default, the application will be hosted at `http://localhost:8501`.

### 2. Prepare the Anomaly Model
Before using the Anomaly Detection screen, you need to train the model on your dataset (which requires a minimum of 10 expense records logged in the database). You can trigger training:
- **Via the UI:** Click the "Train Model Now" button inside the **Anomalies** dashboard.
- **Via the CLI:** Execute:
  ```bash
  python models/train_model.py
  ```

### 3. Testing Integrations
You can verify your SMTP config or Gemini connection by running the small tests:
```bash
# Test Gemini API Call
python test_gemini.py

# Test Currency Formatter Formatting
python test_currency.py
```

---

## 🖼️ Screenshots & UI Walkthrough

| Module | Interface Highlights | Visual Blueprint Placeholder |
| :--- | :--- | :--- |
| **Financial Dashboard** | Glassmorphic cards containing health scores, categorical pie breakdowns, and MoM transaction deltas. | `[ [|||] Dashboard Chart Area ]` |
| **AI Personal Coach** | Interactive chat bubble console with quick-action prompts (Impulse checks, leak checks) and Gemini-based reviews. | `[ Chat: "Am I overspending?" ]` |
| **ML Anomalies** | Severity-colored cards explaining why individual spending items were flagged (Isolation Forest decision boundary). | `[ ! flag: HIGH | 5x category avg ]` |
| **Risk Engine** | Liquid/debt ratios represented as matrices graded into HIGH, MEDIUM, and LOW risk exposures. | `[ [Low] [High] [Med] ]` |
| **Bill Calendar** | Full grid monthly schedule calendar with color indicators for upcoming, overdue, and paid bills. | `[ 01 02 03 [Due] 05 06 ]` |

---

## 🔮 Future Roadmap

* [ ] **RBI Account Aggregator Linkage:** Connection to RBI AA API pipelines to fetch bank balance feeds safely without scraping netbanking credentials.
* [ ] **Automated SMS Extraction:** Direct reading of transaction messages (via optional mobile-app helper) to feed the sqlite budget database automatically.
* [ ] **ISO 27001 & SOC2 Compliance Audit:** Generating audited logs and establishing strict key rotation rules.
* [ ] **Multi-Currency Converter:** Adding automatic API conversion queries to handle cross-border payments.

---

## 🤝 Contributors

Contributions make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
