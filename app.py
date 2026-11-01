import html
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from application.backend.chatbot.service import process_project_message
from application.backend.forecasts.service import (
    build_daily_summary,
    filter_forecasts,
    load_forecast_metadata,
    load_forecasts,
    summarize_forecasts,
    validate_forecast_metadata,
)

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

    try:
        forecast_data = load_forecasts()
        forecast_metadata = load_forecast_metadata()
        validate_forecast_metadata(
            forecast_data,
            forecast_metadata
        )

    except (FileNotFoundError, ValueError, OSError) as error:

        st.error(
            f"Forecast integration is unavailable: {error}"
        )

        st.info(
            "Check that the M11-06 forecast CSV and metadata exist, "
            "then run python-ai/forecasting/integrate_forecasts.py."
        )

    else:

        st.caption(
            f"{forecast_metadata['model_name']} | "
            f"{forecast_metadata['forecasting_method']}"
        )

        st.info(
            "These are rolling one-step-ahead predictions from the "
            "chronological holdout period. They compare actual and "
            "predicted demand; they are not a new 7-day future forecast."
        )

        stores_forecast = sorted(
            forecast_data["Store ID"].unique()
        )

        forecast_store = st.selectbox(
            "Select Store",
            stores_forecast,
            key="m14_03_forecast_store"
        )

        products_forecast = sorted(
            forecast_data.loc[
                forecast_data["Store ID"] == forecast_store,
                "Product ID"
            ].unique()
        )

        forecast_product = st.selectbox(
            "Select Product",
            products_forecast,
            key="m14_03_forecast_product"
        )

        min_forecast_date = forecast_data["Date"].min().date()
        max_forecast_date = forecast_data["Date"].max().date()

        selected_date_range = st.date_input(
            "Forecast date range",
            value=(min_forecast_date, max_forecast_date),
            min_value=min_forecast_date,
            max_value=max_forecast_date,
            key="m14_03_forecast_date_range"
        )

        if (
            isinstance(selected_date_range, (tuple, list))
            and len(selected_date_range) == 2
        ):
            forecast_start_date, forecast_end_date = selected_date_range
        else:
            forecast_start_date = selected_date_range
            forecast_end_date = selected_date_range

        forecast_view = filter_forecasts(
            forecast_data,
            store_id=forecast_store,
            product_id=forecast_product,
            start_date=forecast_start_date,
            end_date=forecast_end_date
        )

        if forecast_view.empty:

            st.warning(
                "No forecast records match the selected filters."
            )

        else:

            forecast_summary = summarize_forecasts(
                forecast_view
            )

            metric1, metric2, metric3 = st.columns(3)

            metric1.metric(
                "Forecast Records",
                f"{forecast_summary['records']:,}"
            )

            metric2.metric(
                "Mean Absolute Error",
                f"{forecast_summary['mae']:.2f} units"
            )

            metric3.metric(
                "Root Mean Squared Error",
                f"{forecast_summary['rmse']:.2f} units"
            )

            st.markdown("---")

            st.subheader(
                "📈 Actual Demand vs AI Forecast"
            )

            comparison_data = forecast_view[
                [
                    "Date",
                    "Actual Units Sold",
                    "Forecast Units Sold"
                ]
            ].melt(
                id_vars=["Date"],
                var_name="Demand Type",
                value_name="Units"
            )

            comparison_chart = px.line(
                comparison_data,
                x="Date",
                y="Units",
                color="Demand Type",
                markers=True,
                title=(
                    f"{forecast_store} - "
                    f"{forecast_product}"
                )
            )

            st.plotly_chart(
                comparison_chart,
                use_container_width=True
            )

            st.subheader(
                "📅 Daily Demand Summary"
            )

            daily_forecast = build_daily_summary(
                forecast_view
            )

            daily_chart = px.line(
                daily_forecast,
                x="Date",
                y=[
                    "Actual Demand Total",
                    "Forecast Demand Total"
                ],
                markers=True,
                title="Daily Actual and Forecast Demand"
            )

            st.plotly_chart(
                daily_chart,
                use_container_width=True
            )

            st.subheader(
                "Forecast Records"
            )

            st.dataframe(
                forecast_view,
                hide_index=True,
                use_container_width=True
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
    # CHATBOT SERVICE
    # --------------------------------------------------------

    def chatbot_answer(question):
        """Send the user's question to the existing chatbot backend."""

        result = process_project_message(question)

        if not isinstance(result, dict):
            return "Sorry, the chatbot returned an unexpected response."

        response = result.get("response")

        if not response:
            return "Sorry, I could not generate a response to that question."

        return str(response)


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