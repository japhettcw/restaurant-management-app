# Import Required Libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json  # For saving and loading menu items

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
tab1, tab2, tab3 = st.tabs(["Dashboard", "Menu Management", "Reports"])

# Dashboard Tab
with tab1:
    st.header("Business Intelligence Dashboard")
    
    st.subheader("Revenue vs. Expenses")
    fig = px.line(df, x="Date", y=["Revenue", "Total Expenses"], title="Revenue vs. Expenses")
    st.plotly_chart(fig, use_container_width=True)

    divider()

    st.subheader("Top-Selling Menu Items")
    items = ["Pizza", "Burger", "Pasta", "Salad", "Sushi"]
    sales = [120, 90, 80, 60, 50]
    popular_items_data = pd.DataFrame({"Item": items, "Sales": sales})
    st.bar_chart(popular_items_data.set_index("Item"), use_container_width=True)

    divider()

    st.subheader("Insights")
    insights = []
    for _, row in df.iterrows():
        if row["Food Costs"] / row["Revenue"] > 0.3:
            insights.append(f"High food costs on {row['Date']} - consider optimizing inventory.")
        if row["Net Profit"] < 0:
            insights.append(f"Loss recorded on {row['Date']} - review expenses.")
    for insight in insights:
        st.write(f"- {insight}")

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
