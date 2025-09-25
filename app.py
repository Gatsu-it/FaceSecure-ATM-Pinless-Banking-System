import streamlit as st
import pandas as pd
from database import (
    init_db, 
    authenticate_user, 
    get_balance, 
    update_balance, 
    add_transaction, 
    get_transactions
)

# -------------------- Initialize Database -------------------- #
init_db()

# -------------------- Session State Initialization -------------------- #
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = None

# -------------------- Sidebar Authentication -------------------- #
st.sidebar.title("User Authentication")
user_name_input = st.sidebar.text_input("Username")
password_input = st.sidebar.text_input("Password", type='password')

if st.sidebar.button("Login"):
    user = authenticate_user(user_name_input, password_input)
    if user:
        st.sidebar.success("Authentication successful!")
        st.session_state.authenticated = True
        st.session_state.user_id = user[0]
        st.session_state.user_name = user_name_input
    else:
        st.sidebar.error("Authentication failed. Try again.")
        st.session_state.authenticated = False

# -------------------- Main ATM Interface -------------------- #
def atm_interface():
    st.title(f"Welcome, {st.session_state.user_name}!")
    menu = ["Balance Inquiry", "Deposit", "Withdraw", "Transaction History", "Logout"]
    choice = st.radio("Select an option", menu)

    if choice == "Balance Inquiry":
        st.subheader("Check Balance")
        balance = get_balance(st.session_state.user_id)
        st.success(f"Your current balance is: ${balance:.2f}")

    elif choice == "Deposit":
        st.subheader("Deposit Money")
        amount = st.number_input("Enter amount to deposit", min_value=0.01, step=0.01)
        if st.button("Deposit"):
            if amount > 0:
                new_balance = get_balance(st.session_state.user_id) + amount
                update_balance(st.session_state.user_id, new_balance)
                add_transaction(st.session_state.user_id, "Deposit", amount)
                st.success(f"Deposited ${amount:.2f}. New balance: ${new_balance:.2f}")
            else:
                st.warning("Enter a valid deposit amount.")

    elif choice == "Withdraw":
        st.subheader("Withdraw Money")
        amount = st.number_input("Enter amount to withdraw", min_value=0.01, step=0.01)
        if st.button("Withdraw"):
            current_balance = get_balance(st.session_state.user_id)
            if amount > current_balance:
                st.error("Insufficient funds!")
            elif amount <= 0:
                st.warning("Enter a valid withdrawal amount.")
            else:
                new_balance = current_balance - amount
                update_balance(st.session_state.user_id, new_balance)
                add_transaction(st.session_state.user_id, "Withdraw", amount)
                st.success(f"Withdrew ${amount:.2f}. New balance: ${new_balance:.2f}")

    elif choice == "Transaction History":
        st.subheader("Transaction History")
        transactions = get_transactions(st.session_state.user_id)
        if transactions:
            df = pd.DataFrame(transactions, columns=["Type", "Amount", "Date"])
            st.dataframe(df)
        else:
            st.info("No transactions found.")

    elif choice == "Logout":
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.sidebar.success("Logged out successfully!")
        st.experimental_rerun()

# -------------------- Run Interface -------------------- #
if st.session_state.authenticated:
    atm_interface()
else:
    st.title("Secure ATM Interface")
    st.info("Please log in using the sidebar to access ATM functions.")
