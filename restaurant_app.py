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

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        filtered_df = df[(df["Date"] >= str(start_date)) & (df["Date"] <= str(end_date))]

        # KPIs
        st.subheader("Key Performance Indicators")

        # Weekly Comparisons
        st.subheader("Weekly KPI Comparisons")
        current_week_number = pd.Timestamp.today().isocalendar()[1]  # Extract current week number
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
            st.metric("Revenue Change", f"${current_revenue:,.2f}", f"{revenue_change:+.2f}%")
        with col2:
            current_expenses = current_week["Total Expenses"].sum()
            last_week_expenses = last_week["Total Expenses"].sum()
            expenses_change = calculate_percentage_change(current_expenses, last_week_expenses)
            st.metric("Expenses Change", f"${current_expenses:,.2f}", f"{expenses_change:+.2f}%")
        with col3:
            current_profit = current_week["Net Profit"].sum()
            last_week_profit = last_week["Net Profit"].sum()
            profit_change = calculate_percentage_change(current_profit, last_week_profit)
            st.metric("Profit Change", f"${current_profit:,.2f}", f"{profit_change:+.2f}%")

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
            ).update_layout(height=400),
            use_container_width=True
        )

        # Predictive Sales Trends
        st.subheader("Predictive Sales Trends")
        if len(filtered_df) > 5:  # Ensure enough data points for prediction
            x = np.arange(len(filtered_df))  # Generate indices for the data
            y = filtered_df["Revenue"].values

            # Fit a polynomial trendline (degree=2 for simplicity)
            coefficients = np.polyfit(x, y, 2)
            trendline = np.poly1d(coefficients)

            # Predict for the next 7 days
            future_x = np.arange(len(filtered_df), len(filtered_df) + 7)
            future_y = trendline(future_x)

            # Create a combined DataFrame for visualization
            future_dates = pd.date_range(start=filtered_df["Date"].iloc[-1], periods=8, freq="D")[1:]
            future_df = pd.DataFrame({"Date": future_dates, "Predicted Revenue": future_y})

            combined_df = pd.concat([filtered_df[["Date", "Revenue"]], future_df.rename(columns={"Predicted Revenue": "Revenue"})])

            # Visualize actual vs. predicted revenue
            fig_prediction = px.line(
                combined_df,
                x="Date",
                y="Revenue",
                title="Actual and Predicted Revenue",
                labels={"Revenue": "Amount ($)"}
            )
            st.plotly_chart(fig_prediction, use_container_width=True)
        else:
            st.info("Not enough data for prediction.")

        # Divider
        divider()

        # Revenue by Category
        st.subheader("Revenue by Category")
        if "Category" in filtered_df.columns:  # Ensure category-level data exists
            category_revenue = filtered_df.groupby("Category").sum()["Revenue"]
            fig_category_revenue = px.pie(
                category_revenue,
                names=category_revenue.index,
                values=category_revenue,
                title="Revenue Distribution by Category",
                labels={"value": "Revenue ($)", "names": "Category"}
            )
            st.plotly_chart(fig_category_revenue, use_container_width=True)
        else:
            st.info("Category-level data is not available.")

        # Divider
        divider()

        # Expense Breakdown
        st.subheader("Expense Breakdown")
        expense_types = ["Food Costs", "Labor Costs", "Utilities", "Miscellaneous Expenses"]
        if all(col in filtered_df.columns for col in expense_types):  # Ensure all expense columns exist
            expense_data = filtered_df[expense_types].sum().reset_index()
            expense_data.columns = ["Expense Type", "Amount"]

            fig_expense_breakdown = px.bar(
                expense_data,
                x="Expense Type",
                y="Amount",
                title="Expense Breakdown",
                labels={"Amount": "Amount ($)", "Expense Type": "Type"}
            )
            st.plotly_chart(fig_expense_breakdown, use_container_width=True)
        else:
            st.info("Expense breakdown data is not available.")

        # Divider
        divider()

        # Real-Time Insights
        st.subheader("Real-Time Insights")

        # Define revenue and expense thresholds
        revenue_threshold = 5000  # Example threshold
        expense_limit = 7000  # Example limit

        # Check thresholds
        if "total_revenue" not in locals():
            total_revenue = filtered_df["Revenue"].sum()
        if "total_expenses" not in locals():
            total_expenses = filtered_df["Total Expenses"].sum()

        if total_revenue < revenue_threshold:
            st.warning(f"Revenue is below the target threshold of ${revenue_threshold:,.2f}.")

        if total_expenses > expense_limit:
            st.error(f"Expenses exceeded the limit of ${expense_limit:,.2f}.")




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

    # Select Metrics for the Report
    st.subheader("Select Metrics to Include")
    include_revenue = st.checkbox("Include Revenue", value=True)
    include_expenses = st.checkbox("Include Expenses", value=True)
    include_profit = st.checkbox("Include Net Profit", value=True)

    # Custom Time Period
    st.subheader("Select Time Period")
    start_date = st.date_input("Start Date", value=pd.to_datetime(df["Date"].min()), key="report_start_date")
    end_date = st.date_input("End Date", value=pd.to_datetime(df["Date"].max()), key="report_end_date")

    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        # Filter dataset based on selected time period
        filtered_df = df[(df["Date"] >= str(start_date)) & (df["Date"] <= str(end_date))]

        # Generate PnL Summary
        st.subheader("Profit & Loss Summary")
        summary = {}
        if include_revenue:
            total_revenue = filtered_df["Revenue"].sum()
            summary["Total Revenue"] = f"${total_revenue:,.2f}"
        if include_expenses:
            total_expenses = filtered_df["Total Expenses"].sum()
            summary["Total Expenses"] = f"${total_expenses:,.2f}"
        if include_profit:
            net_profit = filtered_df["Net Profit"].sum()
            summary["Net Profit"] = f"${net_profit:,.2f}"

        # Display Summary
        for metric, value in summary.items():
            st.write(f"**{metric}:** {value}")

        # Unusual Trends in Revenue or Expenses
        st.subheader("Unusual Trends")
        if len(filtered_df) > 5:  # Ensure enough data points for analysis
            from scipy.stats import zscore

            # Calculate z-scores for revenue and expenses
            filtered_df["Revenue Z-Score"] = zscore(filtered_df["Revenue"])
            filtered_df["Expenses Z-Score"] = zscore(filtered_df["Total Expenses"])

            # Highlight anomalies (z-score > 2 or < -2)
            unusual_revenue = filtered_df[(filtered_df["Revenue Z-Score"] > 2) | (filtered_df["Revenue Z-Score"] < -2)]
            unusual_expenses = filtered_df[(filtered_df["Expenses Z-Score"] > 2) | (filtered_df["Expenses Z-Score"] < -2)]

            st.write("### Revenue Anomalies")
            if not unusual_revenue.empty:
                st.dataframe(unusual_revenue[["Date", "Revenue", "Revenue Z-Score"]])
            else:
                st.write("No unusual revenue trends detected.")

            st.write("### Expense Anomalies")
            if not unusual_expenses.empty:
                st.dataframe(unusual_expenses[["Date", "Total Expenses", "Expenses Z-Score"]])
            else:
                st.write("No unusual expense trends detected.")
        else:
            st.info("Not enough data for anomaly detection.")

        # Item Performance Analysis
        st.subheader("Item Performance Analysis")
        if "Item" in filtered_df.columns:  # Ensure item-level data exists
            item_performance = filtered_df.groupby("Item").sum()["Revenue"].sort_values(ascending=False)

            st.write("### Top 5 Best-Performing Items")
            st.dataframe(item_performance.head(5))

            st.write("### Top 5 Underperforming Items")
            st.dataframe(item_performance.tail(5))
        else:
            st.info("No item-level data available for performance analysis.")

        # Display Filtered Data
        st.subheader("Filtered Data")
        st.dataframe(filtered_df, use_container_width=True)

        # Generate PDF Report
        st.subheader("Generate PDF Report")
        from fpdf import FPDF

        def generate_pdf_report(data, metrics, period):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Custom Profit & Loss Report", ln=True, align="C")

            # Add Period
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Period: {period}", ln=True)

            # Add Summary
            pdf.ln(10)
            pdf.cell(200, 10, txt="Summary:", ln=True)
            for metric, value in metrics.items():
                pdf.cell(200, 10, txt=f"{metric}: {value}", ln=True)

            # Add Table Header
            pdf.ln(10)
            pdf.cell(40, 10, "Date", 1)
            pdf.cell(40, 10, "Revenue", 1)
            pdf.cell(40, 10, "Expenses", 1)
            pdf.cell(40, 10, "Profit", 1)
            pdf.ln(10)

            # Add Data Rows
            for _, row in data.iterrows():
                pdf.cell(40, 10, str(row["Date"]), 1)
                pdf.cell(40, 10, f"${row['Revenue']:.2f}", 1)
                pdf.cell(40, 10, f"${row['Total Expenses']:.2f}", 1)
                pdf.cell(40, 10, f"${row['Net Profit']:.2f}", 1)
                pdf.ln(10)

            return pdf.output(dest="S").encode("latin1")

        # Generate and Download PDF
        period = f"{start_date} to {end_date}"
        if st.button("Download PDF Report"):
            pdf_data = generate_pdf_report(filtered_df, summary, period)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="Custom_PnL_Report.pdf",
                mime="application/pdf",
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

    # Predictive Restocking Suggestions
    st.subheader("Predictive Restocking Suggestions")
    if not inventory_df.empty:
        # Simulate usage data (replace with actual usage if available)
        inventory_df["Usage"] = np.random.randint(1, 10, size=len(inventory_df))

        # Forecast future stock levels
        inventory_df["Predicted Stock (Next Week)"] = inventory_df["Quantity"] - (inventory_df["Usage"] * 7)

        # Suggest restocking for items predicted to run out
        restock_items = inventory_df[inventory_df["Predicted Stock (Next Week)"] < 0]

        if not restock_items.empty:
            st.write("### Items Needing Restocking Next Week:")
            for _, row in restock_items.iterrows():
                st.write(f"- **{row['Item']}**: Predicted stock will be {row['Predicted Stock (Next Week)']:.0f} units.")
        else:
            st.write("All items are sufficiently stocked for the next week.")
    else:
        st.write("No inventory data available for restocking predictions.")

    # Inventory Trends Over Time
    st.subheader("Inventory Trends Over Time")
    if not inventory_df.empty:
        # Simulate stock level history (replace with real data if available)
        inventory_df["Stock History"] = [np.random.randint(50, 200) for _ in range(len(inventory_df))]
        stock_trends = pd.DataFrame({
            "Date": pd.date_range(start=pd.Timestamp.today() - pd.Timedelta(days=30), periods=30),
            "Stock Level": np.random.randint(50, 200, size=30),
            "Item": np.random.choice(inventory_df["Item"], size=30)
        })

        # Line chart for stock trends
        fig_stock_trends = px.line(
            stock_trends,
            x="Date",
            y="Stock Level",
            color="Item",
            title="Inventory Stock Levels Over Time"
        )
        st.plotly_chart(fig_stock_trends, use_container_width=True)
    else:
        st.write("No inventory data available for trend visualization.")

    # Stock Turnover Visualization
    st.subheader("Stock Turnover Rates")
    if not inventory_df.empty:
        # Simulate turnover data (replace with actual turnover rates if available)
        inventory_df["Turnover Rate"] = np.random.uniform(0.5, 2.0, size=len(inventory_df))

        fig_turnover = px.bar(
            inventory_df,
            x="Item",
            y="Turnover Rate",
            title="Stock Turnover Rates",
            labels={"Turnover Rate": "Turnover Rate (per week)"}
        )
        st.plotly_chart(fig_turnover, use_container_width=True)
    else:
        st.write("No inventory data available for turnover visualization.")


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

        # Predictive Waste Trends
        st.subheader("Predictive Waste Trends")
        if len(waste_df) > 5:  # Ensure enough data points for prediction
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            # Aggregate waste data by date
            daily_waste = waste_df.groupby("Date").sum()["Quantity"]

            # Fit the model
            model = ExponentialSmoothing(daily_waste, trend="add", seasonal=None, seasonal_periods=7)
            fit = model.fit()

            # Predict the next 7 days
            future_dates = pd.date_range(start=daily_waste.index[-1], periods=8, freq="D")[1:]
            future_predictions = fit.forecast(7)

            # Combine actual and predicted data
            prediction_df = pd.DataFrame({
                "Date": future_dates,
                "Predicted Waste": future_predictions
            })
            combined_df = pd.concat([daily_waste.reset_index(), prediction_df.rename(columns={"Predicted Waste": "Quantity"})])

            # Visualize actual vs. predicted waste
            fig_prediction = px.line(
                combined_df,
                x="Date",
                y="Quantity",
                title="Actual and Predicted Waste Trends",
                labels={"Quantity": "Waste Quantity"}
            )
            st.plotly_chart(fig_prediction, use_container_width=True)
        else:
            st.info("Not enough data for waste prediction.")
    else:
        st.write("No data available to display trends.")

    # Suggestions for reducing waste
    st.subheader("Suggestions for Waste Reduction")
    if waste_data:
        high_waste_items = waste_df.groupby("Item")["Quantity"].sum().sort_values(ascending=False).head(3)
        st.write("### Items with Highest Waste:")
        for item, waste in high_waste_items.items():
            st.write(f"- **{item}**: {waste} units wasted")

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
