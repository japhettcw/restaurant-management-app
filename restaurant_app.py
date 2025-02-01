# Import Required Libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json  # For saving and loading menu items
import smtplib
import os  # For checking file existence
import time  # Useful for debugging delays
import warnings  # Suppress unnecessary warnings
from fpdf import FPDF
from scipy.stats import zscore
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from statsmodels.tsa.holtwinters import ExponentialSmoothing  # For predictive waste analytics
from faker import Faker
import random

# Email configuration (To be set up if needed)
EMAIL_ADDRESS = "your_email@example.com"  # Replace with your email address
EMAIL_PASSWORD = "your_password"          # Replace with your email password
SMTP_SERVER = "smtp.gmail.com"            # Replace with your email provider's SMTP server
SMTP_PORT = 587                            # Typically 587 for TLS

# Function to send email alerts
def send_email(subject, body, to_email):
    try:
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        # Add email body
        msg.attach(MIMEText(body, "plain"))

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print(f"Email sent to {to_email}!")
    except Exception as e:
        print(f"Error sending email: {e}")


# File to store menu items
MENU_FILE = "menu_items.json"

# Load Dataset
df = pd.read_csv("restaurant_dataset.csv")

# Function to load menu items from file
def load_menu_items():
    try:
        with open(MENU_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

# Function to save menu items to file
def save_menu_items(menu_items):
    with open(MENU_FILE, "w") as file:
        json.dump(menu_items, file)

# File to store inventory data
INVENTORY_FILE = "inventory.json"

# Function to load inventory from file
def load_inventory():
    try:
        with open(INVENTORY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

# Function to save inventory to file
def save_inventory(data):
    with open(INVENTORY_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to check for restocking alerts
def check_restocking(inventory):
    low_stock_items = [item for item in inventory if item["Quantity"] <= 10]
    return low_stock_items

# Load inventory data
inventory = load_inventory()


# Custom divider function
def divider():
    st.markdown("---")

# Set Page Configuration
st.set_page_config(page_title="Restaurant Management App", layout="wide")

# --- Define Roles and Permissions ---
USER_ROLES = {
    "Owner": {
        "Business_Intelligence": True,  # Tab 1
        "Menu_Management": True,  # Tab 2
        "BI_Reports": True,  # Tab 3
        "Inventory_Tracking": True,  # Tab 4
        "Waste_Management": True,  # Tab 5
        "Staff_Scheduling": True,  # Tab 6
    },
    "Manager": {
        "Business_Intelligence": True,  # Tab 1
        "Menu_Management": True,  # Tab 2
        "BI_Reports": True,  # Tab 3
        "Inventory_Tracking": True,  # Tab 4
        "Waste_Management": True,  # Tab 5
        "Staff_Scheduling": True,  # Tab 6
    },
    "Staff": {
        "Business_Intelligence": False,  # Tab 1
        "Menu_Management": True,  # Tab 2
        "BI_Reports": False,  # Tab 3
        "Inventory_Tracking": False,  # Tab 4
        "Waste_Management": False,  # Tab 5
        "Staff_Scheduling": True,  # Tab 6 (View Only)
    }
}

# 📌 Function to Check Permissions
def has_permission(role, feature):
    return USER_ROLES.get(role, {}).get(feature, False)

import streamlit as st

# 📌 Define Tabs
tabs = {
    "🏠 Dashboard": "Dashboard",
    "🍽️ Menu Management": "Menu_Management",
    "📜 Reports": "Reports",
    "📦 Inventory": "Inventory",
    "♻️ Waste Analytics": "Waste_Analytics",
    "📅 Staff Scheduling": "Staff_Scheduling"
}

# 🔹 Get the selected tab from query parameters (default to Dashboard)
query_params = st.experimental_get_query_params()
default_tab = query_params.get("tab", ["🏠 Dashboard"])[0]

# 🔹 Ensure default_tab is valid; otherwise, fallback to Dashboard
if default_tab not in tabs.keys():
    default_tab = "🏠 Dashboard"

# 🚀 Sidebar Navigation
with st.sidebar:
    st.image("logo.png", width=50)  # Adjust logo size
    st.title("📊 Restaurant Management")
    st.markdown("""
    Efficiently manage restaurant operations with real-time insights.
    
    📈 **Track Business Growth**
    📦 **Monitor Inventory**
    ♻️ **Reduce Waste & Costs**
    """)

    # 🔐 User Role Selection
    st.title("🔑 User Login")
    user_role = st.selectbox("Select Your Role", ["Owner", "Manager", "Staff"])

    # 📌 Navigation Menu
    st.title("📌 Navigation")
    selected_tab = st.radio(
        "Navigate",
        list(tabs.keys()),
        index=list(tabs.keys()).index(default_tab)
    )

# 🔄 Update URL query parameters when tab changes
st.experimental_set_query_params(tab=selected_tab)

# ✅ Create Tabs using `st.tabs()`
tab_list = list(tabs.keys())
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tab_list)

# ✅ Display Content Based on Selected Tab
if selected_tab == "🏠 Dashboard":
    with tab1:
        st.header("🏠 Business Intelligence Dashboard")
        st.write("Welcome to the **Business Intelligence Dashboard!**")

elif selected_tab == "🍽️ Menu Management":
    with tab2:
        st.header("🍽️ Menu Management")
        st.write("Manage your restaurant's **menu** here.")

elif selected_tab == "📜 Reports":
    with tab3:
        st.header("📜 Reports & Insights")
        st.write("Generate and analyze **business reports.**")

elif selected_tab == "📦 Inventory":
    with tab4:
        st.header("📦 Inventory Management")
        st.write("Track and manage **inventory levels**.")

elif selected_tab == "♻️ Waste Analytics":
    with tab5:
        st.header("♻️ Waste Analytics")
        st.write("Monitor and reduce **food waste.**")

elif selected_tab == "📅 Staff Scheduling":
    with tab6:
        st.header("📅 Staff Scheduling")
        st.write("Schedule and manage **staff shifts.**")




# 📌 Custom UI/UX Styling
st.markdown(
    """
    <style>
    /* Global Background */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Style Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }

    /* Style Buttons */
    div.stButton > button:first-child {
        background-color: #007BFF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #0056b3;
    }

    /* Improve Sidebar Styling */
    .stSidebar {
        background-color: #ffffff;
        padding: 15px;
        border-right: 2px solid #ddd;
    }

    /* Card Styling for KPIs */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }

    /* Tables */
    .stDataFrame {
        border-radius: 10px;
        border: 1px solid #ccc;
        background-color: white;
    }

    /* Tooltips for better guidance */
    .tooltip {
        font-size: 14px;
        color: #555;
        padding: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 📊 Business Intelligence Dashboard Tab
with tab1:
    st.header("📊 Business Dashboard")

    # 🚦 Check Permissions
    if not has_permission(user_role, "Business_Intelligence"):
        st.error("🚫 You don't have permission to access the Business Intelligence Dashboard.")
    else:
        st.write("✅ Access granted: Viewing Business Reports")

        # 📅 Date Range Filter
        st.subheader("📆 Select Time Period")
        start_date = st.date_input("Start Date", value=pd.to_datetime(df["Date"].min()), key="dashboard_start_date")
        end_date = st.date_input("End Date", value=pd.to_datetime(df["Date"].max()), key="dashboard_end_date")

        if start_date > end_date:
            st.error("🚨 Start date must be before end date.")
        else:
            filtered_df = df[(df["Date"] >= str(start_date)) & (df["Date"] <= str(end_date))]

            # 📌 Key Performance Metrics
            st.subheader("📈 Key Business Insights")
            col1, col2, col3 = st.columns(3)

            total_revenue = filtered_df["Revenue"].sum()
            total_expenses = filtered_df["Total Expenses"].sum()
            net_profit = filtered_df["Net Profit"].sum()

            with col1:
                st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
            with col2:
                st.metric("📉 Total Expenses", f"${total_expenses:,.2f}")
            with col3:
                st.metric("💵 Net Profit", f"${net_profit:,.2f}")

            # 📊 Weekly KPI Comparisons
            st.subheader("📊 Weekly KPI Comparisons")
            current_week_number = pd.Timestamp.today().isocalendar()[1]
            last_week_number = current_week_number - 1

            current_week = filtered_df[pd.to_datetime(filtered_df["Date"]).dt.isocalendar().week == current_week_number]
            last_week = filtered_df[pd.to_datetime(filtered_df["Date"]).dt.isocalendar().week == last_week_number]

            def calculate_percentage_change(current, previous):
                return ((current - previous) / previous * 100) if previous != 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                current_revenue = current_week["Revenue"].sum()
                last_week_revenue = last_week["Revenue"].sum()
                revenue_change = calculate_percentage_change(current_revenue, last_week_revenue)
                st.metric("📈 Revenue Change", f"${current_revenue:,.2f}", f"{revenue_change:+.2f}%")
            with col2:
                current_expenses = current_week["Total Expenses"].sum()
                last_week_expenses = last_week["Total Expenses"].sum()
                expenses_change = calculate_percentage_change(current_expenses, last_week_expenses)
                st.metric("📉 Expenses Change", f"${current_expenses:,.2f}", f"{expenses_change:+.2f}%")
            with col3:
                current_profit = current_week["Net Profit"].sum()
                last_week_profit = last_week["Net Profit"].sum()
                profit_change = calculate_percentage_change(current_profit, last_week_profit)
                st.metric("💵 Profit Change", f"${current_profit:,.2f}", f"{profit_change:+.2f}%")

            # 📊 Revenue vs. Expenses Chart
            st.subheader("📊 Revenue vs. Expenses")
            fig = px.line(
                filtered_df, x="Date", y=["Revenue", "Total Expenses"],
                title="📉 Revenue & Expenses Trend",
                labels={"value": "Amount ($)", "variable": "Metric"},
            )
            st.plotly_chart(fig, use_container_width=True)

            # 📈 Predictive Sales Trends
            st.subheader("🔮 Predictive Sales Trends")
            if len(filtered_df) > 5:
                x = np.arange(len(filtered_df))
                y = filtered_df["Revenue"].values

                # Polynomial Trendline (degree=2 for better accuracy)
                coefficients = np.polyfit(x, y, 2)
                trendline = np.poly1d(coefficients)

                # Predict next 7 days
                future_x = np.arange(len(filtered_df), len(filtered_df) + 7)
                future_y = trendline(future_x)

                # Create DataFrame for visualization
                future_dates = pd.date_range(start=filtered_df["Date"].iloc[-1], periods=8, freq="D")[1:]
                future_df = pd.DataFrame({"Date": future_dates, "Predicted Revenue": future_y})

                combined_df = pd.concat([filtered_df[["Date", "Revenue"]], future_df.rename(columns={"Predicted Revenue": "Revenue"})])

                # Visualize actual vs. predicted revenue
                fig_prediction = px.line(
                    combined_df, x="Date", y="Revenue",
                    title="📊 Actual vs. Predicted Revenue",
                    labels={"Revenue": "Amount ($)"}
                )
                st.plotly_chart(fig_prediction, use_container_width=True)
            else:
                st.info("📌 Not enough data for prediction.")

            # 📊 Revenue by Category
            st.subheader("📊 Revenue Breakdown by Category")
            if "Category" in filtered_df.columns:
                category_revenue = filtered_df.groupby("Category")["Revenue"].sum()
                fig_category = px.pie(
                    names=category_revenue.index,
                    values=category_revenue,
                    title="📌 Revenue Distribution by Category"
                )
                st.plotly_chart(fig_category, use_container_width=True)
            else:
                st.info("📌 No category-level data available.")

            # 📊 Expense Breakdown
            st.subheader("📉 Expense Breakdown")
            expense_types = ["Food Costs", "Labor Costs", "Utilities", "Miscellaneous Expenses"]
            if all(col in filtered_df.columns for col in expense_types):
                expense_data = filtered_df[expense_types].sum().reset_index()
                expense_data.columns = ["Expense Type", "Amount"]

                fig_expense = px.bar(
                    expense_data, x="Expense Type", y="Amount",
                    title="📌 Expense Breakdown",
                    labels={"Amount": "Amount ($)"}
                )
                st.plotly_chart(fig_expense, use_container_width=True)
            else:
                st.info("📌 Expense breakdown data not available.")

        # 🚨 Business Health Check
            st.subheader("🚨 Business Health Check")
            avg_revenue = filtered_df["Revenue"].mean()
            avg_expenses = filtered_df["Total Expenses"].mean()

            revenue_threshold = avg_revenue * 0.9  # Warning if revenue drops 10% below average
            expense_limit = avg_expenses * 1.1  # Warning if expenses increase 10% above average

            if total_revenue < revenue_threshold:
                st.warning(
                    f"⚠️ **Revenue Alert:** Expected at least **${revenue_threshold:,.2f}**, but current revenue is **${total_revenue:,.2f}**."
                )

            if total_expenses > expense_limit:
                st.error(
                    f"🚨 **Expense Alert:** Expected max **${expense_limit:,.2f}**, but current expenses are **${total_expenses:,.2f}**."
                )








# 📌 Menu Management Tab (With Role-Based Access Control)
with tab2:
    st.header("🍽️ Menu Management")

    # 🚦 Check Permissions
    if not has_permission(user_role, "Menu_Management"):
        st.error("🚫 You don't have permission to access Menu Management.")
    else:
        # Load Menu Items
        menu_items = load_menu_items()

        # Display Menu Items with Delete Buttons
        st.subheader("📜 Current Menu Items")
        if menu_items:  # Ensure menu_items is not empty before iterating
            for index, item in enumerate(menu_items):
                cols = st.columns([3, 1])  # Columns for item details and delete button
                with cols[0]:
                    st.write(f"**{item['Name']}** - 💲{item['Price']:.2f}")
                    st.write(f"*{item['Description']}*")
                with cols[1]:
                    if st.button(f"🗑️ Delete {item['Name']}", key=f"delete_{index}"):
                        menu_items.pop(index)
                        save_menu_items(menu_items)  # Save changes after deletion
                        st.success(f"✅ Deleted '{item['Name']}' successfully!")
                        st.experimental_rerun()  # Refresh the app to show updated menu
        else:
            st.info("📌 No menu items available. Please add new items.")

        divider()

        # Form to Add New Menu Items
        st.subheader("➕ Add a New Menu Item")
        with st.form("add_menu_item_form", clear_on_submit=True):
            name = st.text_input("📌 Item Name", placeholder="Enter the name of the item")
            price = st.number_input("💰 Price", min_value=0.0, format="%.2f", step=0.01)
            description = st.text_area("📝 Description", placeholder="Enter a description for the item")
            submitted = st.form_submit_button("✅ Add Item")

            if submitted and name:
                # Append the new item to the menu_items list
                menu_items.append({"Name": name, "Price": price, "Description": description})
                save_menu_items(menu_items)  # Save changes after addition
                st.success(f"✅ Menu item '{name}' added successfully!")
                st.experimental_rerun()  # Refresh the app

        divider()

        # Display Updated Menu Items
        st.subheader("📜 Updated Menu Items")
        if menu_items:
            menu_df = pd.DataFrame(menu_items)
            st.dataframe(menu_df, use_container_width=True)
        else:
            st.info("📌 No menu items available.")




# 📌 Reports Tab (With Role-Based Access Control)
with tab3:
    st.header("📊 Business Reports & Insights")

    # 🚦 Check Permissions
    if not has_permission(user_role, "BI_Reports"):
        st.error("🚫 You don't have permission to access Business Reports.")
    else:
        # 📅 Date Selection
        st.subheader("📆 Select Time Period")
        start_date = st.date_input("Start Date", value=pd.to_datetime(df["Date"].min()), key="report_start_date")
        end_date = st.date_input("End Date", value=pd.to_datetime(df["Date"].max()), key="report_end_date")

        if start_date > end_date:
            st.error("🚨 Start date must be before end date.")
        else:
            # Filter data based on selected date range
            filtered_df = df[(df["Date"] >= str(start_date)) & (df["Date"] <= str(end_date))]

            # 📊 Key Performance Metrics
            st.subheader("📈 Key Business Insights")
            col1, col2, col3 = st.columns(3)

            total_revenue = filtered_df["Revenue"].sum()
            total_expenses = filtered_df["Total Expenses"].sum()
            net_profit = filtered_df["Net Profit"].sum()

            col1.metric("📌 Total Revenue", f"${total_revenue:,.2f}")
            col2.metric("📉 Total Expenses", f"${total_expenses:,.2f}")
            col3.metric("💰 Net Profit", f"${net_profit:,.2f}")

            # 📊 Revenue & Expense Trends
            st.subheader("📊 Revenue vs. Expenses")
            fig = px.line(
                filtered_df, x="Date", y=["Revenue", "Total Expenses"],
                title="📊 Revenue & Expenses Over Time",
                labels={"value": "Amount ($)", "variable": "Metric"},
            )
            st.plotly_chart(fig, use_container_width=True)

            # 🚨 Unusual Trends Detection
            st.subheader("🚨 Anomaly Detection (Outliers in Revenue & Expenses)")

            if len(filtered_df) > 5:
                # Calculate z-scores for revenue & expenses
                filtered_df["Revenue Z-Score"] = zscore(filtered_df["Revenue"])
                filtered_df["Expenses Z-Score"] = zscore(filtered_df["Total Expenses"])

                # Identify anomalies
                unusual_revenue = filtered_df[(filtered_df["Revenue Z-Score"].abs() > 2)]
                unusual_expenses = filtered_df[(filtered_df["Expenses Z-Score"].abs() > 2)]

                # Display anomalies
                st.write("### 📌 Revenue Anomalies")
                if not unusual_revenue.empty:
                    st.dataframe(unusual_revenue[["Date", "Revenue", "Revenue Z-Score"]])
                else:
                    st.success("✅ No unusual revenue trends detected.")

                st.write("### 📌 Expense Anomalies")
                if not unusual_expenses.empty:
                    st.dataframe(unusual_expenses[["Date", "Total Expenses", "Expenses Z-Score"]])
                else:
                    st.success("✅ No unusual expense trends detected.")
            else:
                st.info("📌 Not enough data points for anomaly detection.")

            # 🔥 Top-Performing & Underperforming Menu Items
            st.subheader("🍽️ Best & Worst Selling Items")

            if "Item" in filtered_df.columns:
                item_performance = filtered_df.groupby("Item")["Revenue"].sum().sort_values(ascending=False)

                col1, col2 = st.columns(2)
                with col1:
                    st.write("### 🏆 Top 5 Best-Performing Items")
                    st.dataframe(item_performance.head(5))

                with col2:
                    st.write("### ⬇️ Top 5 Underperforming Items")
                    st.dataframe(item_performance.tail(5))
            else:
                st.info("📌 No item-level data available for performance analysis.")

            # 📤 Export Report as PDF
            st.subheader("📜 Generate PDF Report")

            def generate_pdf_report(data, total_revenue, total_expenses, net_profit, period):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                pdf.cell(200, 10, txt="📊 Business Profit & Loss Report", ln=True, align="C")
                pdf.ln(10)

                # Report Period
                pdf.cell(200, 10, txt=f"📅 Period: {period}", ln=True)
                pdf.ln(10)

                # Business Insights
                pdf.cell(200, 10, txt=f"💰 Total Revenue: ${total_revenue:,.2f}", ln=True)
                pdf.cell(200, 10, txt=f"📉 Total Expenses: ${total_expenses:,.2f}", ln=True)
                pdf.cell(200, 10, txt=f"💵 Net Profit: ${net_profit:,.2f}", ln=True)
                pdf.ln(10)

                # Add Table Header
                pdf.cell(40, 10, "Date", 1)
                pdf.cell(40, 10, "Revenue", 1)
                pdf.cell(40, 10, "Expenses", 1)
                pdf.cell(40, 10, "Profit", 1)
                pdf.ln(10)

                # Add Data Rows
                for _, row in data.iterrows():
                    pdf




# 📦 Inventory Management Tab (With Role-Based Access Control)
with tab4:
    st.header("📦 Inventory Management")

    # 🚦 Check Permissions
    if not has_permission(user_role, "Inventory_Tracking"):
        st.error("🚫 You don't have permission to access Inventory Management.")
        st.stop()  # Ensure app stops further execution after displaying the error

    # 📊 Display Inventory
    st.subheader("📊 Current Inventory")
    if inventory:
        inventory_df = pd.DataFrame(inventory)
        inventory_df.index += 1  # Start index from 1 for readability
        st.dataframe(inventory_df, use_container_width=True)
    else:
        st.write("📌 No inventory data available.")

    # ⚠️ Inventory Alerts
    st.subheader("⚠️ Inventory Alerts")
    low_stock_items = check_restocking(inventory)
    upcoming_expirations = [
        item for item in inventory if datetime.strptime(item["Expiration"], "%Y-%m-%d") <= datetime.today() + timedelta(days=7)
    ]

    if low_stock_items or upcoming_expirations:
        for item in low_stock_items:
            st.warning(f"⚠️ Low stock: **{item['Item']}** (Only {item['Quantity']} left)")
        for item in upcoming_expirations:
            st.error(f"🚨 Nearing expiration: **{item['Item']}** (Expires on {item['Expiration']})")
    else:
        st.success("✅ No low stock or expiration alerts.")

    # ➕ Add New Inventory Item
    st.subheader("➕ Add Inventory Item")
    if has_permission(user_role, "Inventory_Tracking"):  # Ensure the user has permission to modify inventory
        with st.form("add_inventory_form", clear_on_submit=True):
            item_name = st.text_input("📌 Item Name", placeholder="Enter item name")
            quantity = st.number_input("📦 Quantity", min_value=0, step=1)
            expiration = st.date_input("⏳ Expiration Date")
            submitted = st.form_submit_button("✅ Add Item")

            if submitted and item_name:
                new_item = {
                    "Item": item_name,
                    "Quantity": quantity,
                    "Expiration": str(expiration),
                    "Status": "Good Stock" if quantity > 10 else "Low Stock" if quantity > 0 else "Out of Stock"
                }
                inventory.append(new_item)
                save_inventory(inventory)
                st.success(f"✅ Item '{item_name}' added successfully!")
                st.experimental_rerun()

    # 🔄 Update Stock Levels
    st.subheader("🔄 Update Stock Levels")
    if has_permission(user_role, "Inventory_Tracking"):
        with st.form("update_stock_form"):
            item_list = [item["Item"] for item in inventory]
            if item_list:
                selected_item = st.selectbox("📌 Select Item to Update", item_list)
                new_quantity = st.number_input("📦 New Quantity", min_value=0, step=1)
                update_submitted = st.form_submit_button("🔄 Update Stock")

                if update_submitted:
                    for item in inventory:
                        if item["Item"] == selected_item:
                            item["Quantity"] = new_quantity
                            item["Status"] = "Good Stock" if new_quantity > 10 else "Low Stock" if new_quantity > 0 else "Out of Stock"
                            break
                    save_inventory(inventory)
                    st.success(f"✅ Stock for '{selected_item}' updated to {new_quantity}!")
                    st.experimental_rerun()
            else:
                st.write("📌 No items available to update.")

    # 🗑️ Remove an Inventory Item
    st.subheader("🗑️ Remove Inventory Item")
    if has_permission(user_role, "Inventory_Tracking"):
        with st.form("delete_inventory_form"):
            if item_list:
                delete_item = st.selectbox("📌 Select Item to Delete", item_list)
                delete_submitted = st.form_submit_button("🗑️ Delete Item")

                if delete_submitted:
                    inventory = [item for item in inventory if item["Item"] != delete_item]
                    save_inventory(inventory)
                    st.success(f"✅ Item '{delete_item}' removed successfully!")
                    st.experimental_rerun()
            else:
                st.write("📌 No items available to delete.")

    # 📩 Email Alerts for Low Stock & Expiring Items
    st.subheader("📩 Send Inventory Alerts")
    recipient_email = st.text_input("📧 Notification Email", placeholder="Enter email for alerts")

    if st.button("📬 Send Alerts"):
        alert_messages = []
        for item in low_stock_items:
            alert_messages.append(f"⚠️ Low stock alert: {item['Item']} (Quantity: {item['Quantity']})")
        for item in upcoming_expirations:
            alert_messages.append(f"🚨 Nearing expiration alert: {item['Item']} (Expires on {item['Expiration']})")

        if alert_messages and recipient_email:
            email_body = "\n".join(alert_messages)
            send_email(
                subject="📦 Inventory Alerts from Restaurant Management App",
                body=email_body,
                to_email=recipient_email
            )
            st.success(f"✅ Alerts sent to {recipient_email}!")
        elif not alert_messages:
            st.info("✅ No alerts to send.")
        elif not recipient_email:
            st.error("❌ Please enter an email address to receive alerts.")


# ♻️ Waste Analytics Tab (With Role-Based Access Control)
with tab5:
    st.header("♻️ Waste Analytics")

    # 🚦 Check Permissions
    if not has_permission(user_role, "Waste_Management"):
        st.error("🚫 You don't have permission to access Waste Analytics.")
        st.stop()  # Ensure app stops further execution after the message

    # ✅ Load Waste Data from File
    def load_waste_data():
        try:
            with open("waste_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # Return empty list if file doesn't exist

    def save_waste_data(data):
        with open("waste_data.json", "w") as file:
            json.dump(data, file, indent=4)

    # Fetch the waste data
    waste_data = load_waste_data()

    # 📜 Display Logged Waste Items
    st.subheader("📜 Logged Waste Items")
    if waste_data:
        waste_df = pd.DataFrame(waste_data)
        st.dataframe(waste_df, use_container_width=True)
    else:
        st.write("📌 No waste data logged yet.")

    # 📝 Log Waste Item Form
    st.subheader("📝 Log Waste Item")
    with st.form("log_waste_form", clear_on_submit=True):
        item_name = st.text_input("📌 Item Name", placeholder="Enter the name of the wasted item")
        quantity = st.number_input("📦 Quantity", min_value=0, step=1)
        reason = st.selectbox("❓ Reason for Waste", ["Spoiled", "Over-Prepared", "Other"])
        date_logged = st.date_input("📅 Date", value=pd.Timestamp.today())
        submitted = st.form_submit_button("✅ Log Waste")

        if submitted and item_name:
            # Add the new waste entry
            new_waste_entry = {
                "Item": item_name,
                "Quantity": quantity,
                "Reason": reason,
                "Date": str(date_logged)
            }
            waste_data.append(new_waste_entry)
            save_waste_data(waste_data)  # ✅ Save changes
            st.success(f"✅ Waste item '{item_name}' logged successfully!")
            st.experimental_rerun()

    # 📊 Visualize Waste Trends
    st.subheader("📊 Waste Trends")
    if waste_data:
        waste_df = pd.DataFrame(waste_data)
        waste_df["Date"] = pd.to_datetime(waste_df["Date"])
        waste_trends = waste_df.groupby(["Date", "Reason"]).sum()["Quantity"].unstack().fillna(0)
        st.bar_chart(waste_trends)

        # 🔮 Predictive Waste Trends
        st.subheader("🔮 Predictive Waste Trends")
        if len(waste_df) > 5:  # Ensure enough data points for prediction
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            # Aggregate waste data by date
            daily_waste = waste_df.groupby("Date").sum()["Quantity"]

            # Fit predictive model
            model = ExponentialSmoothing(daily_waste, trend="add", seasonal=None, seasonal_periods=7)
            fit = model.fit()

            # Forecast the next 7 days
            future_dates = pd.date_range(start=daily_waste.index[-1], periods=8, freq="D")[1:]
            future_predictions = fit.forecast(7)

            # Combine actual and predicted data
            prediction_df = pd.DataFrame({"Date": future_dates, "Predicted Waste": future_predictions})
            combined_df = pd.concat([daily_waste.reset_index(), prediction_df.rename(columns={"Predicted Waste": "Quantity"})])

            # 📈 Plot actual vs. predicted waste
            fig_prediction = px.line(
                combined_df,
                x="Date",
                y="Quantity",
                title="📊 Actual and Predicted Waste Trends",
                labels={"Quantity": "Waste Quantity"}
            )
            st.plotly_chart(fig_prediction, use_container_width=True)
        else:
            st.info("📌 Not enough data for waste prediction.")
    else:
        st.write("📌 No data available to display trends.")

    # 🔥 Suggestions for Waste Reduction
    st.subheader("🔥 Suggestions for Waste Reduction")
    if waste_data:
        high_waste_items = waste_df.groupby("Item")["Quantity"].sum().sort_values(ascending=False).head(3)
        st.write("### 🏆 Top Items with Highest Waste:")
        for item, waste in high_waste_items.items():
            st.write(f"- **{item}**: {waste} units wasted")

    st.write("""
    - ✅ **Monitor inventory** to prevent overstocking.
    - ✅ **Train staff** to minimize over-preparation.
    - ✅ **Optimize portion sizes** to reduce plate waste.
    - ✅ **Use leftovers creatively** to minimize waste.
    """)





# 📅 Staff Rota Scheduling Tab (With Role-Based Access Control)
with tab6:
    st.header("📅 Staff Rota Scheduling")

    # 🚦 Check Permissions
    if not has_permission(user_role, "Staff_Scheduling"):
        st.error("🚫 You don't have permission to access Staff Scheduling.")
        st.stop()  # Ensure app stops further execution after the message

    # ✅ Load Staff Rota Data (Using Previous Method)
    def load_rota():
        try:
            with open("staff_rota.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # Return an empty list if the file doesn't exist

    # ✅ Save Staff Rota Data
    def save_rota(data):
        with open("staff_rota.json", "w") as file:
            json.dump(data, file)

    # 📜 Fetch Staff Rota Data
    staff_rota = load_rota()

    # 📜 Display Current Staff Schedule
    st.subheader("📜 Current Staff Schedule")
    if staff_rota:
        rota_df = pd.DataFrame(staff_rota)
        st.dataframe(rota_df, use_container_width=True)
    else:
        st.write("📌 No staff schedules have been added yet.")

    # 📝 Form to Add Staff Shifts
    st.subheader("📝 Add a Staff Shift")
    with st.form("add_shift_form", clear_on_submit=True):
        staff_name = st.text_input("📌 Staff Name", placeholder="Enter the staff member's name")
        shift_date = st.date_input("📅 Shift Date", value=pd.Timestamp.today())
        shift_time = st.time_input("⏰ Shift Time")
        role = st.selectbox("👨‍🍳 Role", ["Chef", "Waiter", "Manager", "Cleaner", "Other"])
        submitted = st.form_submit_button("✅ Add Shift")

        if submitted and staff_name:
            # ✅ Add the new shift
            new_shift = {
                "Name": staff_name,
                "Date": str(shift_date),
                "Time": shift_time.strftime("%H:%M"),
                "Role": role
            }
            staff_rota.append(new_shift)
            save_rota(staff_rota)  # ✅ Save updated rota
            st.success(f"✅ Shift for '{staff_name}' added successfully!")
            st.experimental_rerun()  # Refresh to show changes

    # 📢 Notifications Placeholder
    st.subheader("📢 Notifications")
    st.write("📌 Feature to notify staff about schedule changes is coming soon!")
