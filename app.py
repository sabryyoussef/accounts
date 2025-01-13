import streamlit as st
import pandas as pd
import os
import pyperclip  # For clipboard functionality

# CSV file for persistence
CSV_FILE = "accounts.csv"

# Initialize session state for accounts and groups
if "accounts" not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            df.columns = df.columns.str.strip().str.lower()
            accounts = {}
            for _, row in df.iterrows():
                group = row["group"]
                account = {"email": row["email"], "password": row["password"], "note": row["note"]}
                if group in accounts:
                    accounts[group].append(account)
                else:
                    accounts[group] = [account]
            st.session_state.accounts = accounts
        except Exception as e:
            st.error(f"Error loading CSV file: {e}")
            st.session_state.accounts = {}
    else:
        st.session_state.accounts = {
            "General": [{"email": "ah2@gmail.com", "password": "Shabab28jan", "note": "For vendor communication"}],
            "Google": [
                {"email": "abhorya@gmail.com", "password": "Shabab28jan", "note": "Primary email"},
                {"email": "abhorya80@gmail.com", "password": "Shabab28jan", "note": "Backup email"}
            ]
        }

if "selected_group" not in st.session_state:
    st.session_state.selected_group = None

if "selected_account" not in st.session_state:
    st.session_state.selected_account = None

# Function to save accounts to a CSV file
def save_to_csv():
    try:
        data = []
        for group, accounts in st.session_state.accounts.items():
            for account in accounts:
                data.append({"Group": group, **account})
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE, index=False)
        st.success("Accounts saved successfully!")
    except Exception as e:
        st.error(f"Error saving to CSV: {e}")

# Streamlit app layout
st.title("🔐 Account Manager")

# Account Selection
st.subheader("📁 My Accounts")
groups = list(st.session_state.accounts.keys())
selected_group = st.selectbox("Select Group", groups, key="group_select")
st.session_state.selected_group = selected_group

if selected_group:
    accounts = st.session_state.accounts[selected_group]
    selected_email = st.selectbox("Select Account", [account["email"] for account in accounts], key="email_select")
    for account in accounts:
        if account["email"] == selected_email:
            st.session_state.selected_account = account
            break

    # Display email and password with copy buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"📧 **Email:** `{selected_email}`")
    with col2:
        if st.button("📋 Copy Email", key="copy_email"):
            pyperclip.copy(selected_email)
            st.success("Email copied to clipboard!")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"🔑 **Password:** `{st.session_state.selected_account['password']}`")
    with col2:
        if st.button("📋 Copy Password", key="copy_password"):
            pyperclip.copy(st.session_state.selected_account["password"])
            st.success("Password copied to clipboard!")

# Edit Account Details
st.subheader("📝 Edit Account Details")
if st.session_state.selected_account:
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email", value=st.session_state.selected_account["email"], key="email_input")
    with col2:
        password = st.text_input("Password", value=st.session_state.selected_account["password"], key="password_input")
    note = st.text_area("Note", value=st.session_state.selected_account["note"], key="note_input")

    if st.button("💾 Save Changes", key="save_changes"):
        st.session_state.selected_account["email"] = email
        st.session_state.selected_account["password"] = password
        st.session_state.selected_account["note"] = note
        save_to_csv()
        st.success("Account details updated successfully!")
else:
    st.write("Select an account to view or edit details.")

# Add New Account
st.subheader("➕ Add a New Account")
col1, col2 = st.columns(2)
with col1:
    new_group = st.text_input("Group (Account Type)", key="new_group")
with col2:
    new_email = st.text_input("Email", key="new_email")
new_password = st.text_input("Password (default: Shabab28jan)", value="Shabab28jan", type="password", key="new_password")
new_note = st.text_area("Note", key="new_note")

if st.button("✅ Add Account", key="add_account"):
    if new_group and new_email:
        duplicate = any(account["email"] == new_email for group in st.session_state.accounts.values() for account in group)
        if duplicate:
            st.error("An account with this email already exists!")
        else:
            new_account = {"email": new_email, "password": new_password, "note": new_note}
            if new_group in st.session_state.accounts:
                st.session_state.accounts[new_group].append(new_account)
            else:
                st.session_state.accounts[new_group] = [new_account]
            save_to_csv()
            st.success(f"Account for {new_email} added successfully!")
    else:
        st.error("Please fill in all required fields.")

# Change Account Group
st.subheader("🔄 Change Account Group")
if st.session_state.selected_account:
    new_group = st.selectbox("Select New Group", groups, key="new_group_select")
    if st.button("🚀 Move Account", key="move_account"):
        if new_group != st.session_state.selected_group:
            st.session_state.accounts[st.session_state.selected_group].remove(st.session_state.selected_account)
            if new_group in st.session_state.accounts:
                st.session_state.accounts[new_group].append(st.session_state.selected_account)
            else:
                st.session_state.accounts[new_group] = [st.session_state.selected_account]
            save_to_csv()
            st.session_state.selected_group = new_group
            st.success(f"Account moved to {new_group} successfully!")
        else:
            st.error("Account is already in the selected group.")
else:
    st.write("Select an account to change its group.")

# Delete Account
st.subheader("🗑️ Delete Account")
if st.session_state.selected_account:
    if st.button("❌ Delete Account", key="delete_account"):
        st.session_state.accounts[st.session_state.selected_group].remove(st.session_state.selected_account)
        save_to_csv()
        st.session_state.selected_account = None
        st.success("Account deleted successfully!")
else:
    st.write("Select an account to delete it.")