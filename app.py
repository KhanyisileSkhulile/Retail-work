import html
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ============================================================
# RETAILAI STREAMLIT DASHBOARD
# Lecturer Dataset Version
# ============================================================

st.set_page_config(
    page_title="RetailAI Dashboard",
    page_icon="📦",
    layout="wide"
)


# ============================================================
# FILES
# ============================================================

DATA_FILE = "retail_store_inventory.csv"
FORECAST_FILE = "retailai_forecasts.csv"
MODEL_FILE = "retailai_model_evaluation.csv"
RESTOCK_FILE = "retailai_restocking_recommendations.csv"
ALERT_FILE = "retailai_inventory_alerts.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_csv(filename):

    if Path(filename).exists():
        return pd.read_csv(filename)

    return None


sales_df = load_csv(DATA_FILE)
forecast_df = load_csv(FORECAST_FILE)
model_df = load_csv(MODEL_FILE)
restock_df = load_csv(RESTOCK_FILE)
alerts_df = load_csv(ALERT_FILE)


if sales_df is None:

    st.error(
        "retail_store_inventory.csv was not found."
    )

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

sales_df["Date"] = pd.to_datetime(
    sales_df["Date"],
    errors="coerce"
)


if forecast_df is not None:

    forecast_df["Date"] = pd.to_datetime(
        forecast_df["Date"],
        errors="coerce"
    )


# ============================================================
# TITLE
# ============================================================

st.title("📦 RetailAI")

st.caption(
    "AI Powered Inventory Demand Forecasting "
    "and Smart Restocking System"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("RetailAI Navigation")


page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Sales Analysis",
        "AI Forecasting",
        "Smart Restocking",
        "Inventory Alerts",
        "AI Chatbot",
        "Model Performance"
    ]
)


st.sidebar.markdown("---")


st.markdown(
    """
<style>

.chat-container {
    display: flex;
    flex-direction: column;
    gap: 8px;

    width: 100%;
    max-width: 900px;

    /* Scrollable conversation area */
    max-height: 520px;
    overflow-y: auto;
    overflow-x: hidden;

    margin-left: auto;
    margin-right: auto;
    margin-top: 12px;
    margin-bottom: 12px;

    padding: 10px 12px;

    scroll-behavior: smooth;
}

.chat-container::-webkit-scrollbar {
    width: 7px;
}

.chat-container::-webkit-scrollbar-track {
    background: transparent;
}

.chat-container::-webkit-scrollbar-thumb {
    background: #6b7280;
    border-radius: 10px;
}

.chat-container::-webkit-scrollbar-thumb:hover {
    background: #9ca3af;
}

.retail-chat-row {
    display: flex;
    width: 100%;
    margin: 2px 0;
    padding: 0;
}

.retail-chat-row.user {
    justify-content: flex-end;
}

.retail-chat-row.assistant {
    justify-content: flex-start;
}

.retail-chat-row.user {
    justify-content: flex-end;
}

.retail-chat-row.assistant {
    justify-content: flex-start;
}

.user-bubble {
    background: #2563eb;
    color: white;

    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;

    width: fit-content;
    max-width: 55%;

    font-size: 14px;
    line-height: 1.5;
}

.assistant-bubble {
    background: #1f2937;
    color: white;

    padding: 12px 16px;
    border-radius: 16px 16px 16px 4px;

    width: 65%;
    max-width: 65%;

    font-size: 14px;
    line-height: 1.6;

    border: 1px solid #374151;
    box-sizing: border-box;
}

</style>
    """,
    unsafe_allow_html=True
)


# Store filter
stores = sorted(
    sales_df[
        "Store ID"
    ].dropna().unique()
)


selected_store = st.sidebar.selectbox(
    "Store Filter",
    [
        "All Stores"
    ] + list(stores)
)


# ============================================================
# FILTER DATA BY STORE
# ============================================================

if selected_store == "All Stores":

    filtered_sales = sales_df.copy()

else:

    filtered_sales = sales_df[
        sales_df[
            "Store ID"
        ] == selected_store
    ].copy()


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.header(
        "📊 Business Overview"
    )


    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total_units = filtered_sales[
        "Units Sold"
    ].sum()


    total_products = filtered_sales[
        "Product ID"
    ].nunique()


    total_stores = filtered_sales[
        "Store ID"
    ].nunique()


    total_revenue = (
        filtered_sales[
            "Units Sold"
        ]
        *
        filtered_sales[
            "Price"
        ]
    ).sum()


    col1, col2, col3, col4 = st.columns(4)


    col1.metric(
        "Stores",
        total_stores
    )


    col2.metric(
        "Products",
        total_products
    )


    col3.metric(
        "Units Sold",
        f"{total_units:,.0f}"
    )


    col4.metric(
        "Estimated Revenue",
        f"R {total_revenue:,.2f}"
    )


    st.markdown("---")


    # --------------------------------------------------------
    # ALERT KPIs
    # --------------------------------------------------------

    if alerts_df is not None:

        alert_data = alerts_df.copy()


        if selected_store != "All Stores":

            alert_data = alert_data[
                alert_data[
                    "Store ID"
                ] == selected_store
            ]


        critical = (
            alert_data[
                "Alert_Severity"
            ] == "CRITICAL"
        ).sum()


        high = (
            alert_data[
                "Alert_Severity"
            ] == "HIGH"
        ).sum()


        medium = (
            alert_data[
                "Alert_Severity"
            ] == "MEDIUM"
        ).sum()


        low = (
            alert_data[
                "Alert_Severity"
            ] == "LOW"
        ).sum()


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Critical Alerts",
            int(critical)
        )


        col2.metric(
            "High Alerts",
            int(high)
        )


        col3.metric(
            "Medium Alerts",
            int(medium)
        )


        col4.metric(
            "Low Alerts",
            int(low)
        )


    # --------------------------------------------------------
    # DAILY SALES
    # --------------------------------------------------------

    st.subheader(
        "📈 Daily Sales Trend"
    )


    daily_sales = (
        filtered_sales
        .groupby(
            "Date"
        )[
            "Units Sold"
        ]
        .sum()
        .reset_index()
    )


    fig = px.line(
        daily_sales,
        x="Date",
        y="Units Sold",
        title="Total Daily Units Sold"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "🏆 Top Selling Products"
        )


        top_products = (
            filtered_sales
            .groupby(
                "Product ID"
            )[
                "Units Sold"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )


        fig = px.bar(
            top_products,
            x="Product ID",
            y="Units Sold"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # CATEGORY SALES
    # --------------------------------------------------------

    with col2:

        st.subheader(
            "📦 Category Performance"
        )


        category_data = (
            filtered_sales
            .groupby(
                "Category"
            )[
                "Units Sold"
            ]
            .sum()
            .reset_index()
        )


        fig = px.pie(
            category_data,
            names="Category",
            values="Units Sold"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# SALES ANALYSIS
# ============================================================

elif page == "Sales Analysis":

    st.header(
        "📊 Sales Analysis"
    )


    products = sorted(
        filtered_sales[
            "Product ID"
        ].dropna().unique()
    )


    selected_product = st.selectbox(
        "Select Product",
        [
            "All Products"
        ] + list(products)
    )


    sales_data = filtered_sales.copy()


    if selected_product != "All Products":

        sales_data = sales_data[
            sales_data[
                "Product ID"
            ] == selected_product
        ]


    total_units = (
        sales_data[
            "Units Sold"
        ].sum()
    )


    avg_sales = (
        sales_data[
            "Units Sold"
        ].mean()
    )


    avg_inventory = (
        sales_data[
            "Inventory Level"
        ].mean()
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Total Units Sold",
        f"{total_units:,.0f}"
    )


    col2.metric(
        "Average Units Sold",
        f"{avg_sales:.2f}"
    )


    col3.metric(
        "Average Inventory",
        f"{avg_inventory:.2f}"
    )


    st.markdown("---")


    daily = (
        sales_data
        .groupby(
            "Date"
        )[
            "Units Sold"
        ]
        .sum()
        .reset_index()
    )


    fig = px.line(
        daily,
        x="Date",
        y="Units Sold",
        title="Sales Trend"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # REGION
    # --------------------------------------------------------

    st.subheader(
        "🌍 Regional Sales"
    )


    region_sales = (
        sales_data
        .groupby(
            "Region"
        )[
            "Units Sold"
        ]
        .sum()
        .reset_index()
    )


    fig = px.bar(
        region_sales,
        x="Region",
        y="Units Sold"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # PROMOTION
    # --------------------------------------------------------

    st.subheader(
        "🎯 Promotion Impact"
    )


    promo_data = (
        sales_data
        .groupby(
            "Holiday/Promotion"
        )[
            "Units Sold"
        ]
        .mean()
        .reset_index()
    )


    promo_data[
        "Promotion"
    ] = promo_data[
        "Holiday/Promotion"
    ].map(
        {
            0: "No Promotion",
            1: "Promotion"
        }
    )


    fig = px.bar(
        promo_data,
        x="Promotion",
        y="Units Sold",
        title="Average Sales With and Without Promotion"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    st.subheader(
        "🌤 Weather Impact"
    )


    weather_data = (
        sales_data
        .groupby(
            "Weather Condition"
        )[
            "Units Sold"
        ]
        .mean()
        .reset_index()
    )


    fig = px.bar(
        weather_data,
        x="Weather Condition",
        y="Units Sold"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AI FORECASTING
# ============================================================

elif page == "AI Forecasting":

    st.header(
        "🤖 AI Demand Forecasting"
    )


    if forecast_df is None:

        st.error(
            "Run forecasting.py first."
        )

    else:

        forecast_data = (
            forecast_df.copy()
        )


        stores_forecast = sorted(
            forecast_data[
                "Store_ID"
            ].unique()
        )


        forecast_store = st.selectbox(
            "Select Store",
            stores_forecast
        )


        products_forecast = sorted(
            forecast_data[
                forecast_data[
                    "Store_ID"
                ] == forecast_store
            ][
                "Product_ID"
            ].unique()
        )


        forecast_product = st.selectbox(
            "Select Product",
            products_forecast
        )


        future = forecast_data[
            (
                forecast_data[
                    "Store_ID"
                ] == forecast_store
            )
            &
            (
                forecast_data[
                    "Product_ID"
                ] == forecast_product
            )
        ].copy()


        historical = sales_df[
            (
                sales_df[
                    "Store ID"
                ] == forecast_store
            )
            &
            (
                sales_df[
                    "Product ID"
                ] == forecast_product
            )
        ].copy()


        historical = (
            historical
            .sort_values(
                "Date"
            )
            .tail(30)
        )


        historical_plot = historical[
            [
                "Date",
                "Units Sold"
            ]
        ].copy()


        historical_plot[
            "Type"
        ] = "Historical"


        historical_plot = (
            historical_plot
            .rename(
                columns={
                    "Units Sold":
                        "Units"
                }
            )
        )


        future_plot = future[
            [
                "Date",
                "Predicted_Units_Sold"
            ]
        ].copy()


        future_plot[
            "Type"
        ] = "AI Forecast"


        future_plot = future_plot.rename(
            columns={
                "Predicted_Units_Sold":
                    "Units"
            }
        )


        chart_data = pd.concat(
            [
                historical_plot,
                future_plot
            ],
            ignore_index=True
        )


        fig = px.line(
            chart_data,
            x="Date",
            y="Units",
            color="Type",
            markers=True,
            title=(
                f"{forecast_store} - "
                f"{forecast_product}"
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.subheader(
            "7-Day AI Forecast"
        )


        st.dataframe(
            future,
            hide_index=True,
            use_container_width=True
        )


        total_forecast = (
            future[
                "Predicted_Units_Sold"
            ].sum()
        )


        st.metric(
            "Predicted 7-Day Sales",
            f"{total_forecast:.0f} units"
        )


# ============================================================
# SMART RESTOCKING
# ============================================================

elif page == "Smart Restocking":

    st.header(
        "📦 Smart Restocking"
    )


    if restock_df is None:

        st.error(
            "Run smart_restocking.py first."
        )

    else:

        restock_data = (
            restock_df.copy()
        )


        if selected_store != "All Stores":

            restock_data = restock_data[
                restock_data[
                    "Store ID"
                ] == selected_store
            ]


        products_to_order = (
            restock_data[
                "Recommended_Order_Quantity"
            ] > 0
        ).sum()


        total_order = (
            restock_data[
                "Recommended_Order_Quantity"
            ].sum()
        )


        urgent = (
            restock_data[
                "Stockout_Risk"
            ].isin(
                [
                    "CRITICAL",
                    "HIGH"
                ]
            )
        ).sum()


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Items to Restock",
            int(products_to_order)
        )


        col2.metric(
            "Units to Order",
            f"{total_order:,.0f}"
        )


        col3.metric(
            "Urgent Items",
            int(urgent)
        )


        st.markdown("---")


        st.subheader(
            "Restocking Recommendations"
        )


        columns = [
            "Store ID",
            "Product ID",
            "Category",
            "Current_Inventory",
            "Daily_Forecast_Demand",
            "Estimated_Days_Remaining",
            "Recommended_Order_Quantity",
            "Stockout_Risk",
            "Status"
        ]


        available = [
            c
            for c in columns
            if c in restock_data.columns
        ]


        st.dataframe(
            restock_data[
                available
            ],
            hide_index=True,
            use_container_width=True
        )


        # ----------------------------------------------------
        # STOCK COVER CHART
        # ----------------------------------------------------

        st.subheader(
            "📅 Days of Stock Remaining"
        )


        fig = px.bar(
            restock_data,
            x="Product ID",
            y="Estimated_Days_Remaining",
            color="Stockout_Risk",
            facet_col="Store ID"
            if selected_store == "All Stores"
            else None
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# INVENTORY ALERTS
# ============================================================

elif page == "Inventory Alerts":

    st.header(
        "🚨 Inventory Alert Centre"
    )


    if alerts_df is None:

        st.error(
            "Run inventory_alerts.py first."
        )

    else:

        alert_data = (
            alerts_df.copy()
        )


        if selected_store != "All Stores":

            alert_data = alert_data[
                alert_data[
                    "Store ID"
                ] == selected_store
            ]


        severity_filter = st.multiselect(
            "Alert Severity",
            [
                "CRITICAL",
                "HIGH",
                "MEDIUM",
                "LOW",
                "NORMAL"
            ],
            default=[
                "CRITICAL",
                "HIGH",
                "MEDIUM"
            ]
        )


        alert_data = alert_data[
            alert_data[
                "Alert_Severity"
            ].isin(
                severity_filter
            )
        ]


        st.dataframe(
            alert_data,
            hide_index=True,
            use_container_width=True
        )


        st.markdown("---")


        st.subheader(
            "Active Alerts"
        )


        active = alert_data[
            alert_data[
                "Alert_Message"
            ] != "NO ALERT"
        ]


        if active.empty:

            st.success(
                "No active alerts."
            )

        else:

            for _, row in active.head(30).iterrows():

                message = (
                    f"{row['Store ID']} - "
                    f"{row['Product ID']}: "
                    f"{row['Alert_Message']}"
                )


                if (
                    row[
                        "Alert_Severity"
                    ] == "CRITICAL"
                ):

                    st.error(
                        message
                    )


                elif (
                    row[
                        "Alert_Severity"
                    ] == "HIGH"
                ):

                    st.warning(
                        message
                    )


                elif (
                    row[
                        "Alert_Severity"
                    ] == "MEDIUM"
                ):

                    st.warning(
                        message
                    )


                else:

                    st.info(
                        message
                    )




# ============================================================
# AI CHATBOT
# ============================================================

elif page == "AI Chatbot":

        # --------------------------------------------------------
    # INITIALIZE CHAT HISTORY
    # --------------------------------------------------------

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am RetailAI Assistant. "
                    "Ask me about inventory and demand."
                )
            }
        ]

    # --------------------------------------------------------
    # CHAT STYLE
    # --------------------------------------------------------
    st.markdown(
        """
    <style>

    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        width: 100%;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .retail-chat-row {
        display: flex;
        width: 100%;
        margin: 0;
        padding: 0;
    }

    .retail-chat-row.user {
        justify-content: flex-end;
    }

    .retail-chat-row.assistant {
        justify-content: flex-start;
    }

    .user-bubble {
        background: #2563eb;
        color: white;
        padding: 10px 14px;
        border-radius: 16px 16px 4px 16px;
        max-width: 60%;
        font-size: 14px;
        line-height: 1.5;
    }

    .assistant-bubble {
        background: #1f2937;
        color: white;
        padding: 10px 14px;
        border-radius: 16px 16px 16px 4px;
        max-width: 70%;
        font-size: 14px;
        line-height: 1.5;
        border: 1px solid #374151;
    }

    .bubble-name {
        font-size: 11px;
        opacity: 0.7;
        margin-bottom: 4px;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)
    st.header("💬 RetailAI Assistant")

    st.write(
        "Ask questions about stores, products, "
        "stock levels, demand and restocking."
    )

    st.info(
        "Try: 'What should S004 reorder?', "
        "'Which products are critical?', "
        "'How much stock does P0012 have at S003?'"
    )

 

    # --------------------------------------------------------
    # DETECT STORE
    # --------------------------------------------------------

    def detect_store(question):

        q = question.upper()

        for store in stores:

            if store.upper() in q:

                return store

        return None


    # --------------------------------------------------------
    # DETECT PRODUCT
    # --------------------------------------------------------

    products_all = sorted(
        sales_df[
            "Product ID"
        ].unique()
    )


    def detect_product(question):

        q = question.upper()

        for product in products_all:

            if product.upper() in q:

                return product

        return None


    # --------------------------------------------------------
    # CHATBOT FUNCTION
    # --------------------------------------------------------

    def chatbot_answer(question):

        q = question.lower()
        store = detect_store(question)
        product = detect_product(question)

        # GREETING
        greeting_words = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening"
        ]

        if q.strip() in greeting_words:
            return (
                "Hello 👋. Ask me about stock, "
                "demand, restocking or alerts."
            )

        # CRITICAL PRODUCTS
        if (
            "critical" in q
            or "urgent" in q
        ):

            if alerts_df is None:
                return (
                    "Inventory alert data is not available."
                )

            data = alerts_df[
                alerts_df[
                    "Alert_Severity"
                ] == "CRITICAL"
            ].copy()

            # Filter by store if user mentions one
            if store:
                data = data[
                    data[
                        "Store ID"
                    ] == store
                ]

            # Filter by product if user mentions one
            if product:
                data = data[
                    data[
                        "Product ID"
                    ] == product
                ]

            if data.empty:
                if store:
                    return (
                        f"No critical inventory alerts "
                        f"were found for {store}."
                    )

                return (
                    "No critical inventory alerts "
                    "were found."
                )

            response = "🚨 **Critical inventory alerts:**\n\n"

            for _, row in data.iterrows():
                response += (
                    f"• **{row['Store ID']} - "
                    f"{row['Product ID']}**\n"
                    f"  - Current inventory: "
                    f"{row['Current_Inventory']:.0f} units\n"
                    f"  - Stockout risk: "
                    f"**{row['Stockout_Risk']}**\n"
                    f"  - Daily demand: "
                    f"{row['Daily_Forecast_Demand']:.0f} units\n\n"
                )

            return response

        # ----------------------------------------------------
        # WHAT TO REORDER
        # ----------------------------------------------------

        if any(
            phrase in q
            for phrase in [
                "what should",
                "reorder",
                "restock",
                "need to order"
            ]
        ):

            data = restock_df[
                restock_df[
                    "Recommended_Order_Quantity"
                ] > 0
            ].copy()

            if store:
                data = data[
                    data[
                        "Store ID"
                    ] == store
                ]

            if product:
                data = data[
                    data[
                        "Product ID"
                    ] == product
                ]

            if data.empty:
                return (
                    "No restocking recommendation "
                    "was found."
                )

            # ----------------------------------------------
            # Sort by risk priority
            # ----------------------------------------------

            risk_priority = {
                "CRITICAL": 1,
                "HIGH": 2,
                "MEDIUM": 3,
                "LOW": 4
            }

            data["Risk_Priority"] = (
                data[
                    "Stockout_Risk"
                ].map(
                    risk_priority
                )
            )

            data = data.sort_values(
                by=[
                    "Risk_Priority",
                    "Recommended_Order_Quantity"
                ],
                ascending=[
                    True,
                    False
                ]
            )

            response = "📦 Restocking recommendations:\n\n"

            for number, (_, row) in enumerate(
                data.head(5).iterrows(),
                start=1
            ):
                response += (
                    f"{number}. {row['Product ID']} at "
                    f"{row['Store ID']}\n"
                    f"   Order: "
                    f"{int(row['Recommended_Order_Quantity'])} units\n"
                    f"   Current stock: "
                    f"{row['Current_Inventory']:.0f} units\n"
                    f"   Days of stock: "
                    f"{row['Estimated_Days_Remaining']:.2f}\n"
                    f"   Risk: {row['Stockout_Risk']}\n\n"
                )

            if len(data) > 5:
                response += (
                    f"\n... plus {len(data) - 5} "
                    f"more recommendations.\n\n"
                    f"View the Smart Restocking page "
                    f"for the full list."
                )

            return response

        # ----------------------------------------------------
        # DAYS OF STOCK
        # ----------------------------------------------------

        if (
            "days" in q
            and "stock" in q
        ):

            if store and product:
                data = restock_df[
                    (
                        restock_df[
                            "Store ID"
                        ] == store
                    )
                    &
                    (
                        restock_df[
                            "Product ID"
                        ] == product
                    )
                ]

                if not data.empty:
                    row = data.iloc[0]
                    return (
                        f"{product} at {store} has "
                        f"approximately "
                        f"{row['Estimated_Days_Remaining']:.2f} "
                        f"days of stock remaining."
                    )

        # ----------------------------------------------------
        # CURRENT INVENTORY
        # ----------------------------------------------------
        if any(
            phrase in q
            for phrase in [
                "current stock",
                "inventory",
                "stock level",
                "how much stock"
            ]
        ):

            if store and product:
                data = restock_df[
                    (
                        restock_df[
                            "Store ID"
                        ] == store
                    )
                    &
                    (
                        restock_df[
                            "Product ID"
                        ] == product
                    )
                ]

                if not data.empty:
                    row = data.iloc[0]
                    return (
                        f"📦 {product} at {store} "
                        f"currently has "
                        f"{row['Current_Inventory']:.0f} "
                        f"units in inventory."
                    )

        # ----------------------------------------------------
        # HIGH DEMAND
        # ----------------------------------------------------

        if (
            "high demand" in q
            or "highest demand" in q
        ):

            data = alerts_df[
                alerts_df[
                    "Demand_Status"
                ] == "HIGH DEMAND"
            ]

            if store:
                data = data[
                    data[
                        "Store ID"
                    ] == store
                ]

            if data.empty:
                return (
                    "No high-demand products "
                    "were found."
                )

            response = "🔥 High-demand products:\n\n"

            for _, row in data.head(5).iterrows():
                response += (
                    f"• {row['Store ID']} - "
                    f"{row['Product ID']}: "
                    f"{row['Daily_Forecast_Demand']:.0f} "
                    f"units/day\n"
                )

            return response

        # ----------------------------------------------------
        # SLOW MOVING
        # ----------------------------------------------------

        if (
            "slow moving" in q
            or "slow-moving" in q
        ):

            data = alerts_df[
                alerts_df[
                    "Movement_Status"
                ] == "SLOW MOVING"
            ]

            if store:
                data = data[
                    data[
                        "Store ID"
                    ] == store
                ]

            if data.empty:
                return (
                    "No slow-moving inventory "
                    "was detected."
                )

            response = "🐢 Slow-moving products:\n\n"

            for _, row in data.iterrows():
                response += (
                    f"• {row['Store ID']} - "
                    f"{row['Product ID']}\n"
                )

            return response

        # ----------------------------------------------------
        # OVERSTOCK
        # ----------------------------------------------------

        if (
            "overstock" in q
            or "too much stock" in q
        ):

            data = alerts_df[
                alerts_df[
                    "Inventory_Position"
                ] == "OVERSTOCKED"
            ]

            if store:
                data = data[
                    data[
                        "Store ID"
                    ] == store
                ]

            if data.empty:
                return (
                    "No overstocked products "
                    "were detected."
                )

            response = "📦 Overstocked products:\n\n"

            for _, row in data.iterrows():
                response += (
                    f"• {row['Store ID']} - "
                    f"{row['Product ID']}\n"
                )

            return response

        # ----------------------------------------------------
        # FORECAST
        # ----------------------------------------------------

        if (
            "forecast" in q
            or "prediction" in q
        ):

            if store and product:
                data = forecast_df[
                    (
                        forecast_df[
                            "Store_ID"
                        ] == store
                    )
                    &
                    (
                        forecast_df[
                            "Product_ID"
                        ] == product
                    )
                ]

                if not data.empty:
                    total = data[
                        "Predicted_Units_Sold"
                    ].sum()

                    return (
                        f"🤖 The Random Forest model "
                        f"predicts approximately "
                        f"{total:.0f} units of "
                        f"{product} at {store} "
                        f"over the next 7 days."
                    )

        # ----------------------------------------------------
        # GENERAL PRODUCT INFORMATION
        # ----------------------------------------------------

        if store and product:
            data = restock_df[
                (
                    restock_df[
                        "Store ID"
                    ] == store
                )
                &
                (
                    restock_df[
                        "Product ID"
                    ] == product
                )
            ]

            if not data.empty:
                row = data.iloc[0]
                return (
                    f"Information for {product} "
                    f"at {store}:\n\n"
                    f"• Current inventory: "
                    f"{row['Current_Inventory']:.0f}\n"
                    f"• Expected daily demand: "
                    f"{row['Daily_Forecast_Demand']:.2f}\n"
                    f"• Days of stock remaining: "
                    f"{row['Estimated_Days_Remaining']:.2f}\n"
                    f"• Recommended order: "
                    f"{int(row['Recommended_Order_Quantity'])}\n"
                    f"• Stockout risk: "
                    f"{row['Stockout_Risk']}"
                )

        return (
            "I could not understand that question. "
            "Try asking:\n\n"
            "• What should S004 reorder?\n"
            "• Which products are critical?\n"
            "• Which products have high demand?\n"
            "• How many days of stock does P0012 "
            "have at S003?\n"
            "• What is the forecast for P0007 at S002?"
        )


        # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    question = st.chat_input(
        "Ask RetailAI..."
    )

    if question:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        answer = chatbot_answer(
            question
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


    # --------------------------------------------------------
    # DISPLAY CHAT
    # --------------------------------------------------------

    chat_parts = [
        '<div class="chat-container">'
    ]

    for message in st.session_state.messages:

        role = message["role"]

        content = html.escape(
            str(message["content"])
        )

        # Keep line breaks
        content = content.replace(
            "\n",
            "<br>"
        )

        # Remove Markdown bold symbols
        content = content.replace(
            "**",
            ""
        )


        # USER MESSAGE - RIGHT
        if role == "user":

            chat_parts.append(
                f'<div class="retail-chat-row user">'
                f'<div class="user-bubble">'
                f'<div class="bubble-name">You</div>'
                f'{content}'
                f'</div>'
                f'</div>'
            )


        # RETAILAI MESSAGE - LEFT
        else:

            chat_parts.append(
                f'<div class="retail-chat-row assistant">'
                f'<div class="assistant-bubble">'
                f'<div class="bubble-name">🤖 RetailAI</div>'
                f'{content}'
                f'</div>'
                f'</div>'
            )


    chat_parts.append(
        '</div>'
    )

    chat_html = "".join(
        chat_parts
    )

    st.markdown(
        chat_html,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat"
    ):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am RetailAI Assistant. "
                    "Ask me about inventory and demand."
                )
            }
        ]

        st.rerun()

# ============================================================
# MODEL PERFORMANCE
# ============================================================

elif page == "Model Performance":

    st.header(
        "🧠 AI Model Performance"
    )


    if model_df is None:

        st.error(
            "Run forecasting.py first."
        )

    else:

        overall = model_df[
            model_df[
                "Product_ID"
            ] == "OVERALL"
        ]


        if not overall.empty:

            overall = (
                overall.iloc[0]
            )


            col1, col2, col3, col4 = st.columns(4)


            col1.metric(
                "Random Forest MAE",
                f"{overall['Our_Model_MAE']:.2f}"
            )


            col2.metric(
                "Random Forest RMSE",
                f"{overall['Our_Model_RMSE']:.2f}"
            )


            col3.metric(
                "Dataset Forecast MAE",
                f"{overall['Dataset_Forecast_MAE']:.2f}"
            )


            col4.metric(
                "Dataset Forecast RMSE",
                f"{overall['Dataset_Forecast_RMSE']:.2f}"
            )


        st.markdown("---")


        st.subheader(
            "Model Comparison by Product"
        )


        product_results = model_df[
            model_df[
                "Product_ID"
            ] != "OVERALL"
        ].copy()


        st.dataframe(
            product_results,
            hide_index=True,
            use_container_width=True
        )


        comparison = product_results[
            [
                "Product_ID",
                "Our_Model_MAE",
                "Dataset_Forecast_MAE"
            ]
        ].melt(
            id_vars="Product_ID",
            var_name="Model",
            value_name="MAE"
        )


        fig = px.bar(
            comparison,
            x="Product_ID",
            y="MAE",
            color="Model",
            barmode="group",
            title="Forecast Error Comparison"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.info(
            "Lower MAE and RMSE values indicate "
            "more accurate forecasts. The supplied "
            "dataset forecast currently performs better "
            "than the experimental Random Forest model."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "RetailAI | Inventory Demand Forecasting "
    "and Smart Restocking System"
)