
import uuid
from datetime import date
from decimal import Decimal

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from api_client import API_BASE_URL, api_request


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="FinanceAI | Personal Finance Assistant",
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #f8f8ff, #f1f2ff);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #21175c, #38247d);
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .brand {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .brand span {
        color: #c2aaff;
    }

    .muted {
        color: #747b99;
        font-size: 14px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e8e8f8;
        border-radius: 18px;
        padding: 20px;
        min-height: 140px;
        box-shadow: 0 5px 20px rgba(45, 36, 115, 0.05);
    }

    .metric-label {
        color: #737895;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .metric-value {
        color: #242252;
        font-size: 25px;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: #777b96;
        font-size: 12px;
        margin-top: 10px;
    }

    div[data-testid="stChatMessage"] {
        background: white;
        border: 1px solid #e9e7fa;
        border-radius: 14px;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #e8e8f8;
        padding: 20px;
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================
DEFAULTS = {
    "access_token": None,
    "user_name": "",
    "auth_page": "Login",
    "chat_history": [],
    "chat_session_id": str(uuid.uuid4()),
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# API HELPERS
# =========================================================
def api_get(endpoint):
    return api_request(
        "GET",
        endpoint,
        token=st.session_state.access_token,
    )


def api_post(endpoint, payload):
    return api_request(
        "POST",
        endpoint,
        token=st.session_state.access_token,
        json_data=payload,
    )


def api_put(endpoint, payload):
    return api_request(
        "PUT",
        endpoint,
        token=st.session_state.access_token,
        json_data=payload,
    )


def api_delete(endpoint):
    return api_request(
        "DELETE",
        endpoint,
        token=st.session_state.access_token,
    )


def money(value):
    return f"₹{float(value or 0):,.2f}"


def safe_list(value):
    return value if isinstance(value, list) else []


def show_api_error(error):
    st.error(str(error))


# =========================================================
# AUTHENTICATION
# =========================================================
def login_page():
    st.markdown(
        '<p class="brand">✦ Finance<span>AI</span></p>',
        unsafe_allow_html=True,
    )
    st.markdown("## Welcome back 👋")
    st.markdown(
        '<p class="muted">Your money, your future. Sign in to continue.</p>',
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Login", "Create account"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email address")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(
                "Sign in",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not email.strip() or not password:
                st.warning("Please enter your email and password.")
            else:
                try:
                    # The /auth/login endpoint accepts the UserLogin JSON schema.
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        json={
                            "email": email.strip(),
                            "password": password,
                        },
                        timeout=20,
                    )
                    response.raise_for_status()
                    result = response.json()

                    token = result.get("access_token")
                    if not token:
                        st.error(
                            "Login response did not contain access_token."
                        )
                    else:
                        st.session_state.access_token = token
                        st.session_state.user_name = email.strip()
                        st.session_state.chat_history = []
                        st.rerun()

                except requests.RequestException as error:
                    st.error(
                        f"Login failed. Check your credentials and backend: {error}"
                    )

    with register_tab:
        st.caption(
            "Registration fields must match your backend UserRegister schema."
        )

        with st.form("register_form"):
            name = st.text_input("Full name")
            email = st.text_input("Registration email")
            password = st.text_input(
                "Create password",
                type="password",
                key="register_password",
            )
            confirm = st.text_input(
                "Confirm password",
                type="password",
            )
            submitted = st.form_submit_button(
                "Create account",
                use_container_width=True,
            )

        if submitted:
            if not name.strip() or not email.strip() or not password:
                st.warning("Please complete all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    result = api_request(
                        "POST",
                        "/auth/register",
                        json_data={
                            "name": name.strip(),
                            "email": email.strip(),
                            "password": password,
                        },
                    )
                    st.success(
                        "Registration successful. Please sign in."
                    )
                except Exception as error:
                    show_api_error(error)


# =========================================================
# AUTH CHECK
# =========================================================
if not st.session_state.access_token:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        login_page()
    st.stop()


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown(
        '<p class="brand">✦ Finance<span>AI</span></p>',
        unsafe_allow_html=True,
    )
    st.caption("Your Personal Finance Assistant")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "💳 Transactions",
            "📊 Budgets",
            "🎯 Savings Goals",
            "🤖 AI Finance Chat",
        ],
    )

    st.divider()
    st.markdown("### 💜 Your financial journey")
    st.caption("Small steps today, stronger finances tomorrow.")

    st.divider()
    st.caption(f"Signed in as {st.session_state.user_name}")

    if st.button("Log out", use_container_width=True):
        st.session_state.access_token = None
        st.session_state.user_name = ""
        st.session_state.chat_history = []
        st.session_state.chat_session_id = str(uuid.uuid4())
        st.rerun()


# =========================================================
# HEADER
# =========================================================
st.markdown("## Your Money, Your Future ✨")
st.markdown(
    '<p class="muted">Understand your money. Make smarter decisions.</p>',
    unsafe_allow_html=True,
)
st.write("")


# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":
    st.markdown("### Your Financial Overview")

    try:
        data = api_get("/dashboard/")

        cards = [
            ("💚 Total Income", data.get("total_income", 0)),
            ("🩷 Total Expenses", data.get("total_expenses", 0)),
            ("💜 Available Balance", data.get("balance", 0)),
            ("💙 Current Savings", data.get("total_savings_current", 0)),
        ]

        columns = st.columns(4)

        for column, (label, value) in zip(columns, cards):
            with column:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{money(value)}</div>
                        <div class="metric-note">From your account data</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.write("")
        target = float(data.get("total_savings_target", 0) or 0)
        current = float(data.get("total_savings_current", 0) or 0)
        progress = min(current / target, 1.0) if target > 0 else 0.0

        with st.container(border=True):
            st.markdown("### 🎯 Overall Savings Progress")
            st.progress(progress)
            st.caption(
                f"{progress:.1%} complete · "
                f"{money(current)} saved out of {money(target)}"
            )

        st.write("")
        left, right = st.columns(2)

        with left:
            st.markdown("### Spending by Category")
            try:
                category_data = safe_list(
                    api_get("/analytics/category-expenses")
                )
                if category_data:
                    df = pd.DataFrame(category_data)
                    fig = px.pie(
                        df,
                        names="category_name",
                        values="total_expenses",
                        hole=0.65,
                        color_discrete_sequence=[
                            "#6847F5",
                            "#A16CFF",
                            "#FF668C",
                            "#FFAD5C",
                            "#49C99B",
                        ],
                    )
                    fig.update_layout(
                        height=350,
                        margin=dict(t=15, b=15, l=5, r=5),
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No expense records available yet.")
            except Exception as error:
                show_api_error(error)

        with right:
            st.markdown("### Monthly Income vs Expenses")
            try:
                monthly_data = safe_list(api_get("/analytics/monthly"))
                if monthly_data:
                    df = pd.DataFrame(monthly_data)
                    chart_df = df.melt(
                        id_vars=["month"],
                        value_vars=["total_income", "total_expenses"],
                        var_name="Type",
                        value_name="Amount",
                    )
                    chart_df["Type"] = chart_df["Type"].map(
                        {
                            "total_income": "Income",
                            "total_expenses": "Expenses",
                        }
                    )
                    fig = px.bar(
                        chart_df,
                        x="month",
                        y="Amount",
                        color="Type",
                        barmode="group",
                        color_discrete_map={
                            "Income": "#42C99A",
                            "Expenses": "#8057F5",
                        },
                    )
                    fig.update_layout(
                        height=350,
                        margin=dict(t=15, b=15, l=5, r=5),
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis_title="Month",
                        yaxis_title="Amount (₹)",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Add transactions to see monthly analytics.")
            except Exception as error:
                show_api_error(error)

    except Exception as error:
        show_api_error(error)


# =========================================================
# TRANSACTIONS
# =========================================================
elif page == "💳 Transactions":
    st.markdown("## 💳 Transactions")
    st.caption("Record and manage your income and expenses.")

    try:
        categories = safe_list(api_get("/categories/"))
        category_options = {
            f"{item['name']} ({item['type']})": item
            for item in categories
        }

        with st.expander("➕ Add transaction", expanded=True):
            with st.form("transaction_form"):
                title = st.text_input("Transaction title")
                amount = st.number_input(
                    "Amount (₹)",
                    min_value=0.01,
                    value=100.0,
                    step=100.0,
                )
                kind = st.selectbox("Type", ["expense", "income"])
                tx_date = st.date_input("Transaction date", value=date.today())
                description = st.text_area("Description")

                matching_categories = {
                    label: item
                    for label, item in category_options.items()
                    if item["type"].lower() == kind
                }

                selected_category = st.selectbox(
                    "Category",
                    ["No category"] + list(matching_categories.keys()),
                )

                submitted = st.form_submit_button(
                    "Save transaction",
                    type="primary",
                )

                if submitted:
                    category_id = None
                    if selected_category != "No category":
                        category_id = matching_categories[
                            selected_category
                        ]["id"]

                    payload = {
                        "title": title.strip(),
                        "amount": str(Decimal(str(amount)).quantize(
                            Decimal("0.01")
                        )),
                        "type": kind,
                        "category_id": category_id,
                        "transaction_date": tx_date.isoformat(),
                        "description": description.strip() or None,
                    }

                    try:
                        api_post("/transactions/", payload)
                        st.success("Transaction added successfully.")
                        st.rerun()
                    except Exception as error:
                        show_api_error(error)

        transaction_data = safe_list(api_get("/transactions/"))

        if transaction_data:
            df = pd.DataFrame(transaction_data)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No transactions found. Add your first transaction.")

    except Exception as error:
        show_api_error(error)


# =========================================================
# BUDGETS
# =========================================================
elif page == "📊 Budgets":
    st.markdown("## 📊 Monthly Budgets")
    st.caption("Plan your expenses and keep your spending on track.")

    try:
        categories = safe_list(api_get("/categories/"))
        expense_categories = [
            category for category in categories
            if category["type"].lower() == "expense"
        ]

        with st.expander("➕ Create a budget"):
            with st.form("budget_form"):
                name = st.text_input("Budget name")
                amount = st.number_input(
                    "Budget amount (₹)",
                    min_value=0.01,
                    value=5000.0,
                )
                month = st.date_input(
                    "Budget month (select its first day)",
                    value=date.today().replace(day=1),
                )

                options = {
                    f"{c['name']} (ID {c['id']})": c
                    for c in expense_categories
                }

                selected = st.selectbox(
                    "Expense category",
                    list(options.keys()),
                )

                submitted = st.form_submit_button("Create budget")

                if submitted:
                    if month.day != 1:
                        st.error("Select the first day of the month.")
                    elif not selected:
                        st.error("Create an expense category first.")
                    else:
                        payload = {
                            "name": name.strip(),
                            "amount": str(amount),
                            "month": month.isoformat(),
                            "category_id": options[selected]["id"],
                        }
                        try:
                            api_post("/budgets/", payload)
                            st.success("Budget created.")
                            st.rerun()
                        except Exception as error:
                            show_api_error(error)

        budgets = safe_list(api_get("/budgets/"))

        if budgets:
            for budget in budgets:
                with st.container(border=True):
                    st.markdown(f"### {budget['name']}")
                    st.metric(
                        "Budget limit",
                        money(budget["amount"]),
                    )
                    st.caption(
                        f"Month: {budget['month']} · "
                        f"Category ID: {budget['category_id']}"
                    )
                    st.caption(
                        "Actual spending comparison can be added using "
                        "transaction data for this category and month."
                    )
        else:
            st.info("No budgets yet. Create your first budget above.")

    except Exception as error:
        show_api_error(error)


# =========================================================
# SAVINGS GOALS
# =========================================================
elif page == "🎯 Savings Goals":
    st.markdown("## 🎯 Your Savings Goals")
    st.caption("Every rupee saved brings you closer to your goals.")

    with st.expander("➕ Create savings goal"):
        with st.form("savings_form"):
            name = st.text_input("Goal name")
            target = st.number_input(
                "Target amount (₹)",
                min_value=0.01,
                value=25000.0,
            )
            current = st.number_input(
                "Already saved (₹)",
                min_value=0.0,
                value=0.0,
            )
            target_date = st.date_input(
                "Target date (optional)",
                value=None,
            )

            submitted = st.form_submit_button("Create goal")

            if submitted:
                if current > target:
                    st.error("Current savings cannot exceed target.")
                else:
                    payload = {
                        "name": name.strip(),
                        "target_amount": str(target),
                        "current_amount": str(current),
                        "target_date": (
                            target_date.isoformat()
                            if target_date
                            else None
                        ),
                    }

                    try:
                        api_post("/savings-goals/", payload)
                        st.success("Savings goal created.")
                        st.rerun()
                    except Exception as error:
                        show_api_error(error)

    try:
        goals = safe_list(api_get("/savings-goals/"))

        if not goals:
            st.info("No savings goals yet. Create your first goal above.")

        for goal in goals:
            with st.container(border=True):
                st.markdown(f"### 💜 {goal['name']}")

                current = float(goal["current_amount"])
                target = float(goal["target_amount"])
                progress = min(current / target, 1.0) if target else 0.0

                st.progress(progress)
                st.caption(
                    f"{money(current)} saved of {money(target)} "
                    f"({progress:.1%})"
                )

                remaining = max(target - current, 0)
                st.write(f"**Remaining:** {money(remaining)}")

                if st.button(
                    "Add ₹500 to current savings",
                    key=f"add_saving_{goal['id']}",
                ):
                    updated = {
                        "name": goal["name"],
                        "target_amount": str(goal["target_amount"]),
                        "current_amount": str(
                            min(current + 500, target)
                        ),
                        "target_date": goal.get("target_date"),
                    }

                    try:
                        api_put(
                            f"/savings-goals/{goal['id']}",
                            updated,
                        )
                        st.success("Savings progress updated.")
                        st.rerun()
                    except Exception as error:
                        show_api_error(error)

    except Exception as error:
        show_api_error(error)


# =========================================================
# AI FINANCE CHAT
# =========================================================
elif page == "🤖 AI Finance Chat":
    st.markdown("## 🤖 AI Finance Assistant")
    st.caption(
        "Ask questions about your spending, income, budgets, and savings."
    )

    if st.button("🗑️ New conversation"):
        st.session_state.chat_history = []
        st.session_state.chat_session_id = str(uuid.uuid4())
        st.rerun()

    if not st.session_state.chat_history:
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": (
                    "Hi! 👋 I'm your FinanceAI assistant. "
                    "You can ask me where you spend the most or "
                    "how to save money based on your financial records."
                ),
            }
        )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask something about your finances...")

    if question:
        st.session_state.chat_history.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        # Only recent messages are sent; the server does not persist
        # this Streamlit session history in the database.
        recent_history = [
            message
            for message in st.session_state.chat_history[:-1]
            if message["role"] in ("user", "assistant")
        ][-20:]

        payload = {
            "question": question,
            "session_id": st.session_state.chat_session_id,
            "history": [
                {
                    "role": message["role"],
                    "content": message["content"],
                }
                for message in recent_history
            ],
        }

        with st.chat_message("assistant"):
            with st.spinner("Analyzing your finances..."):
                try:
                    result = api_post("/chat/", payload)
                    answer = result.get(
                        "answer",
                        "The API did not return an answer.",
                    )
                except Exception as error:
                    answer = (
                        "I couldn't get a response from the backend. "
                        f"Details: {error}"
                    )

            st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.caption(
    "FinanceAI · Your personal finances, made simpler 💜"
)
