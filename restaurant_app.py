# Import Required Libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json  # For saving and loading menu items
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
EMAIL_ADDRESS = "your_email@example.com"  # Replace with your email address
EMAIL_PASSWORD = "your_password"          # Replace with your email password
SMTP_SERVER = "smtp.gmail.com"            # Replace with your email provider's SMTP server
SMTP_PORT = 587                           # Typically 587 for TLS

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

# Function to load inventory from file
def load_inventory():
    try:
        with open("inventory.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

# Function to save inventory to file
def save_inventory(data):
    with open("inventory.json", "w") as file:
        json.dump(data, file)

# Custom divider function
def divider():
    st.markdown("---")

# App Title and Branding
st.title("Restaurant Management App")
st.image("logo.png", width=150)  # Display logo (place logo.png in the same directory)

# Add custom CSS for theming
st.markdown(
    """
    <style>
    /* Change background color */
    .stApp {
        background-color: #f7f7f7;
    }

    /* Style headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
    }

    /* Style buttons */
    button {
        background-color: #3498db;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px;
    }

    button:hover {
        background-color: #2980b9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Business Intelligence Dashboard", "Menu Management", "Reports", "Inventory Tracking", "Waste Analytics", "Staff Rota Scheduling"])

# Business Intelligence Dashboard Tab
with tab1:
    st.header("Business Intelligence Dashboard")

    # Interactive Date Range Filter
    st.subheader("Filter by Date Range")
    start_date = st.date_input("Start Date", value=pd.to_datetime(df["Date"].min()), key="dashboard_start_date")
    end_date = st.date_input("End Date", value=pd.to_datetime(df["Date"].max()), key="dashboard_end_date")

    if start_date > end_date:  # Align this block properly
        st.error("Start date must be before end date.")
    else:
        filtered_df = df[(df["Date"] >= str(start_date)) & (df["Date"] <= str(end_date))]

        # KPIs
        st.subheader("Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_revenue = filtered_df["Revenue"].sum()
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with col2:
            total_expenses = filtered_df["Total Expenses"].sum()
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        with col3:
            net_profit = filtered_df["Net Profit"].sum()
            st.metric("Net Profit", f"${net_profit:,.2f}")
        with col4:
            waste_df = pd.read_json("waste_data.json") if "waste_data.json" else pd.DataFrame(columns=["Quantity"])
            total_waste = waste_df["Quantity"].sum() if not waste_df.empty else 0
            st.metric("Total Waste (Qty)", f"{total_waste:.0f}")

        # Divider
        divider()

        # Revenue vs. Expenses Chart
        st.subheader("Revenue vs. Expenses")
        st.plotly_chart(
            px.line(
                filtered_df,
                x="Date",
                y=["Revenue", "Total Expenses"],
                title="Revenue vs. Expenses",
                labels={"value": "Amount ($)", "variable": "Metric"}
            ).update_layout(height=400),  # Set a consistent height for the chart
            use_container_width=True
        )

        # Divider
        divider()

        # Inventory Status
        st.subheader("Inventory Status")
        inventory = load_inventory()
        inventory_df = pd.DataFrame(inventory)
        inventory_status = inventory_df.groupby("Status").size().reset_index(name="Count")
        st.plotly_chart(
            px.pie(
                inventory_status,
                names="Status",
                values="Count",
                title="Inventory Status"
            ).update_layout(height=400),  # Consistent height for the chart
            use_container_width=True
        )

        # Divider
        divider()

        # Waste Trends Chart
        st.subheader("Waste Trends")
        if not waste_df.empty:
            waste_df["Date"] = pd.to_datetime(waste_df["Date"])
            waste_trends = waste_df.groupby("Date").sum()["Quantity"]
            st.plotly_chart(
                px.bar(
                    waste_trends,
                    x=waste_trends.index,
                    y="Quantity",
                    title="Waste Trends Over Time",
                    labels={"Quantity": "Waste Quantity", "x": "Date"}
                ).update_layout(height=400),  # Consistent height for the chart
                use_container_width=True
            )
        else:
            st.write("No waste data to display.")

# Menu Management Tab
with tab2:
    st.header("Menu Management")

    # Load menu items from file
    menu_items = load_menu_items()

    # Display menu items with delete buttons
    st.subheader("Current Menu Items")
    for index, item in enumerate(menu_items):
        cols = st.columns([3, 1])  # Columns for item details and delete button
        with cols[0]:
            st.write(f"**{item['Name']}** - ${item['Price']:.2f}")
            st.write(f"*{item['Description']}*")
        with cols[1]:
            if st.button(f"Delete {item['Name']}", key=f"delete_{index}"):
                menu_items.pop(index)
                save_menu_items(menu_items)  # Save changes after deletion
                st.success(f"Deleted '{item['Name']}' successfully!")
                st.experimental_rerun()  # Refresh the app to show updated menu

    divider()

    # Form to Add New Menu Items
    st.subheader("Add a New Menu Item")
    with st.form("add_menu_item_form", clear_on_submit=True):
        name = st.text_input("Item Name", placeholder="Enter the name of the item")
        price = st.number_input("Price", min_value=0.0, format="%.2f", step=0.01)
        description = st.text_area("Description", placeholder="Enter a description for the item")
        submitted = st.form_submit_button("Add Item")

        if submitted:
            # Append the new item to the menu_items list
            menu_items.append({"Name": name, "Price": price, "Description": description})
            save_menu_items(menu_items)  # Save changes after addition
            st.success(f"Menu item '{name}' added successfully!")

    # Display the updated menu items after adding
    st.subheader("Updated Menu Items")
    menu_df = pd.DataFrame(menu_items)
    st.dataframe(menu_df, use_container_width=True)

# Reports Tab
with tab3:
    st.header("Reports")

    # Date Range Filter
    st.subheader("Select Date Range for Report")
    start_date = st.date_input("Start Date", value=pd.to_datetime(df["Date"].min()))
    end_date = st.date_input("End Date", value=pd.to_datetime(df["Date"].max()))

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter dataset based on selected date range
        filtered_df = df[(df["Date"] >= str(start_date)) & (df["Date"] <= str(end_date))]

        # Generate summary metrics
        total_revenue = filtered_df["Revenue"].sum()
        total_expenses = filtered_df["Total Expenses"].sum()
        net_profit = filtered_df["Net Profit"].sum()

        # Display summary metrics in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Revenue", f"${total_revenue:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        with col3:
            st.metric("Net Profit", f"${net_profit:,.2f}")

        divider()

        # Display filtered data
        st.subheader("Filtered Data")
        st.dataframe(filtered_df, use_container_width=True)

        # Download filtered report
        st.subheader("Download Report")
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name="filtered_report.csv",
            mime="text/csv"
        )

# Inventory Tracking Tab
with tab4:
    st.header("Inventory Tracking")

    # Load inventory data
    inventory = load_inventory()

    # Display inventory table
    st.subheader("Current Inventory")
    inventory_df = pd.DataFrame(inventory)
    st.dataframe(inventory_df, use_container_width=True)

    # Add new inventory item
    st.subheader("Add Inventory Item")
    with st.form("add_inventory_form", clear_on_submit=True):
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        expiration = st.date_input("Expiration Date")
        submitted = st.form_submit_button("Add Item")

        if submitted:
            # Add the new item
            new_item = {
                "Item": item_name,
                "Quantity": quantity,
                "Expiration": str(expiration),
                "Status": "Good Stock" if quantity > 10 else "Low Stock" if quantity > 0 else "Out of Stock"
            }
            inventory.append(new_item)
            save_inventory(inventory)  # Save updated inventory
            st.success(f"Item '{item_name}' added successfully!")
            st.experimental_rerun()

    # Alerts for low stock or nearing expiration
st.subheader("Alerts")
recipient_email = st.text_input("Notification Email", placeholder="Enter your email for alerts")

if st.button("Send Alerts"):
    alert_messages = []
    for item in inventory:
        if item["Quantity"] <= 10:
            message = f"Low stock alert: {item['Item']} (Quantity: {item['Quantity']})"
            st.warning(message)
            alert_messages.append(message)
        if pd.to_datetime(item["Expiration"]) <= pd.Timestamp.today() + pd.Timedelta(days=7):
            message = f"Nearing expiration alert: {item['Item']} (Expiration: {item['Expiration']})"
            st.error(message)
            alert_messages.append(message)

    # Send email if there are alerts
    if alert_messages and recipient_email:
        email_body = "\n".join(alert_messages)
        send_email(
            subject="Inventory Alerts from Restaurant Management App",
            body=email_body,
            to_email=recipient_email
        )
        st.success(f"Alerts sent to {recipient_email}!")
    elif not alert_messages:
        st.info("No alerts to send.")
    elif not recipient_email:
        st.error("Please enter an email address to receive alerts.")

# Waste Analytics Tab
with tab5:
    st.header("Waste Analytics")

    # Load waste data from a file
    def load_waste_data():
        try:
            with open("waste_data.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # Return an empty list if the file doesn't exist

    # Save waste data to a file
    def save_waste_data(data):
        with open("waste_data.json", "w") as file:
            json.dump(data, file)

    # Fetch waste data
    waste_data = load_waste_data()

    # Display waste data
    st.subheader("Logged Waste Items")
    if waste_data:
        waste_df = pd.DataFrame(waste_data)
        st.dataframe(waste_df, use_container_width=True)
    else:
        st.write("No waste data logged yet.")

    # Form to log waste items
    st.subheader("Log Waste Item")
    with st.form("log_waste_form", clear_on_submit=True):
        item_name = st.text_input("Item Name", placeholder="Enter the name of the wasted item")
        quantity = st.number_input("Quantity", min_value=0, step=1)
        reason = st.selectbox("Reason for Waste", ["Spoiled", "Over-Prepared", "Other"])
        date_logged = st.date_input("Date", value=pd.Timestamp.today())
        submitted = st.form_submit_button("Log Waste")

        if submitted:
            # Add the new waste entry
            new_waste_entry = {
                "Item": item_name,
                "Quantity": quantity,
                "Reason": reason,
                "Date": str(date_logged)
            }
            waste_data.append(new_waste_entry)
            save_waste_data(waste_data)  # Save updated waste data
            st.success(f"Waste item '{item_name}' logged successfully!")
            st.experimental_rerun()

    # Visualize waste trends
    st.subheader("Waste Trends")
    if waste_data:
        waste_df = pd.DataFrame(waste_data)
        waste_df["Date"] = pd.to_datetime(waste_df["Date"])
        waste_trends = waste_df.groupby(["Date", "Reason"]).sum()["Quantity"].unstack().fillna(0)
        st.bar_chart(waste_trends)
    else:
        st.write("No data available to display trends.")

    # Suggestions for reducing waste
    st.subheader("Suggestions for Waste Reduction")
    st.write("""
    - Monitor inventory regularly to avoid overstocking.
    - Train staff to minimize over-preparation.
    - Optimize portion sizes to reduce plate waste.
    - Use leftover ingredients creatively in new dishes.
    """)
    # Staff Rota Scheduling Tab
with tab6:
    st.header("Staff Rota Scheduling")

    # Load staff rota from a file
    def load_rota():
        try:
            with open("staff_rota.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return []  # Return an empty list if the file doesn't exist

    # Save staff rota to a file
    def save_rota(data):
        with open("staff_rota.json", "w") as file:
            json.dump(data, file)

    # Fetch staff rota
    staff_rota = load_rota()

    # Display rota data
    st.subheader("Current Staff Schedule")
    if staff_rota:
        rota_df = pd.DataFrame(staff_rota)
        st.dataframe(rota_df, use_container_width=True)
    else:
        st.write("No staff schedules have been added yet.")

    # Form to add staff shifts
    st.subheader("Add a Staff Shift")
    with st.form("add_shift_form", clear_on_submit=True):
        staff_name = st.text_input("Staff Name", placeholder="Enter the staff member's name")
        shift_date = st.date_input("Shift Date", value=pd.Timestamp.today())
        shift_time = st.time_input("Shift Time")
        role = st.selectbox("Role", ["Chef", "Waiter", "Manager", "Cleaner", "Other"])
        submitted = st.form_submit_button("Add Shift")

        if submitted:
            # Add the new shift
            new_shift = {
                "Name": staff_name,
                "Date": str(shift_date),
                "Time": shift_time.strftime("%H:%M"),
                "Role": role
            }
            staff_rota.append(new_shift)
            save_rota(staff_rota)  # Save updated rota
            st.success(f"Shift for '{staff_name}' added successfully!")
            st.experimental_rerun()

    # Notifications placeholder
    st.subheader("Notifications")
    st.write("Feature to notify staff about schedule changes is coming soon!")
