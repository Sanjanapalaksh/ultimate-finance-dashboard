import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="Ultimate Finance Dashboard", layout="wide")

# --- Session State Initialization ---
if "users" not in st.session_state:
    st.session_state.users = {}  # username -> {password, salary}
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "expenses" not in st.session_state:
    st.session_state.expenses = {}  # username -> month -> category -> amount
if "goals" not in st.session_state:
    st.session_state.goals = {}     # username -> month -> goal
if "current_month" not in st.session_state:
    st.session_state.current_month = datetime.now().strftime("%Y-%m")

categories = ["Rent", "Food", "Transport", "Utilities", "Entertainment", "Other"]

# --- CSS for professional background ---
st.markdown("""
<style>
body {
    background-image: url('https://images.unsplash.com/photo-1581091215369-4b2b0cfccdfb?auto=format&fit=crop&w=1470&q=80');
    background-size: cover;
    background-attachment: fixed;
    color: white;
    font-family: 'Arial', sans-serif;
}
h1,h2,h3,h4,h5,h6 {color: #fff;}
.stButton>button {background-color:#1f77b4;color:white;}
.metric-card {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color:white;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.metric-card:hover {transform: scale(1.05);}
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def register_user(username, password):
    if username in st.session_state.users:
        st.error("Username already exists")
    else:
        st.session_state.users[username] = {"password": password, "salary": 0.0}
        st.success("Registered successfully! Please login.")

def login_user(username, password):
    user = st.session_state.users.get(username)
    if user and user["password"] == password:
        st.session_state.logged_in_user = username
        return True
    else:
        st.error("Invalid username/password")
        return False

def save_salary(salary):
    st.session_state.users[st.session_state.logged_in_user]["salary"] = float(salary)

def save_expenses(exp_dict):
    month = st.session_state.current_month
    if st.session_state.logged_in_user not in st.session_state.expenses:
        st.session_state.expenses[st.session_state.logged_in_user] = {}
    st.session_state.expenses[st.session_state.logged_in_user][month] = exp_dict

def save_goal(goal):
    user = st.session_state.logged_in_user
    if user not in st.session_state.goals:
        st.session_state.goals[user] = {}
    st.session_state.goals[user][st.session_state.current_month] = float(goal)

def get_month_data(month):
    user = st.session_state.logged_in_user
    salary = float(st.session_state.users[user]["salary"])
    expenses = st.session_state.expenses.get(user, {}).get(month, {cat:0.0 for cat in categories})
    goal = float(st.session_state.goals.get(user, {}).get(month, 0.0))
    return salary, expenses, goal

# --- Login/Register ---
if st.session_state.logged_in_user is None:
    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.experimental_rerun = True  # legacy safe, will rerun
    with tab2:
        username_r = st.text_input("Username (register)")
        password_r = st.text_input("Password (register)", type="password")
        if st.button("Register"):
            if username_r and password_r:
                register_user(username_r, password_r)
            else:
                st.warning("Enter username and password")

# --- Dashboard / Finance Input ---
else:
    st.title("📊 Ultimate Finance Dashboard")
    month = st.session_state.current_month

    # Sidebar: month selection & savings goal
    st.sidebar.subheader("📅 Month & Goal")
    months_user = list(st.session_state.expenses.get(st.session_state.logged_in_user, {}).keys())
    months_user.append(month)
    month_selected = st.sidebar.selectbox("Month", sorted(list(set(months_user))))
    st.session_state.current_month = month_selected

    salary, expenses, goal = get_month_data(month_selected)

    # Savings Goal input
    goal_input = st.sidebar.number_input("Savings Goal", value=float(goal), min_value=0.0, format="%.2f")
    if st.sidebar.button("Save Goal"):
        save_goal(goal_input)
        st.success("Savings goal saved!")

    # Salary input if not set
    if salary <= 0:
        salary_input = st.number_input("Enter your Monthly Salary", min_value=0.0, format="%.2f")
        if st.button("Save Salary"):
            if salary_input > 0:
                save_salary(salary_input)
                st.success("Salary saved!")
                st.experimental_rerun = True
            else:
                st.warning("Salary must be > 0")
    else:
        # Expenses Input
        st.subheader("💰 Enter Monthly Expenses")
        expense_inputs = {}
        for cat in categories:
            expense_inputs[cat] = st.number_input(f"{cat} Expense", min_value=0.0, value=float(expenses.get(cat,0.0)), format="%.2f")
        if st.button("Save Expenses"):
            save_expenses(expense_inputs)
            st.success("Expenses saved!")
            st.experimental_rerun = True

        # --- Dashboard Metrics ---
        total_expense = sum(expense_inputs.values())
        savings = salary - total_expense

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #2ecc71, #27ae60);'><h4>💵 Salary</h4><h3>₹{salary:,.2f}</h3></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #e74c3c, #c0392b);'><h4>💸 Expenses</h4><h3>₹{total_expense:,.2f}</h3></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #3498db, #2980b9);'><h4>💰 Savings</h4><h3>₹{savings:,.2f}</h3></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #f1c40f, #f39c12);'><h4>💡 Remaining Budget</h4><h3>₹{salary - total_expense:,.2f}</h3></div>", unsafe_allow_html=True)
        col5.markdown(f"<div class='metric-card' style='background: linear-gradient(135deg, #9b59b6, #8e44ad);'><h4>🎯 Savings Goal</h4><h3>₹{goal_input:,.2f}</h3></div>", unsafe_allow_html=True)

        # --- Progress Bars ---
        st.subheader("📊 Budget & Savings Progress")
        st.write("Budget Utilization")
        st.progress(min(max(total_expense / salary,0),1))
        st.write("Savings vs Goal")
        if goal_input > 0:
            st.progress(min(max(savings/goal_input,0),1))

        # --- Expense Bar Chart ---
        st.subheader("📊 Expense Breakdown")
        df_exp = pd.DataFrame(list(expense_inputs.items()), columns=["Category","Amount"])
        if not df_exp.empty:
            st.bar_chart(df_exp.set_index("Category"))

        # --- Recommendations ---
        st.subheader("💡 Recommendations")
        if total_expense > salary:
            excess = total_expense - salary
            st.warning(f"Overspending by ₹{excess:,.2f}!")
        elif goal_input > 0 and savings < goal_input:
            deficit = goal_input - savings
            st.warning(f"⚠ ₹{deficit:,.2f} below your savings goal!")

            # Suggest categories to reduce
            sorted_exp = sorted(expense_inputs.items(), key=lambda x: x[1], reverse=True)
            st.subheader("💡 Suggested Expense Reductions")
            for cat, amt in sorted_exp:
                if amt <= 0:
                    continue
                st.write(f"- Reduce **{cat}** by ₹{min(amt, deficit):,.2f}")
                deficit -= amt
                if deficit <= 0:
                    break
        else:
            st.success(f"✅ On track! Savings: ₹{savings:,.2f}")

        # --- Logout ---
        if st.button("🔒 Logout"):
            st.session_state.logged_in_user = None