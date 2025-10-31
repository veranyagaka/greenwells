import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose
# import calendar # This import is not used, so we can remove it.

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Ugunja Intelligence Engine",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. CUSTOM CSS (The "Wow" Factor) ---
# This injects custom CSS to brand your app with Ugunja's colors
st.markdown(
    """
    <style>
    /* --- HIDE STREAMLIT BRANDING --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- DEFINE BRAND COLORS (UGUNJA ORANGE) --- */
    :root {
        --primary-color: #FFA500; /* Ugunja Orange */
        --background-color: #0E1117; /* Streamlit Dark BG */
        --secondary-background-color: #1a1f2b; /* Card BG */
        --text-color: #FAFAFA;
    }

    /* --- APPLY BRAND COLOR TO WIDGETS --- */
    /* Slider Track */
    div[data-baseweb="slider"] > div:nth-child(2) > div {
        background: var(--primary-color) !important;
    }
    /* Slider Thumb */
    div[data-baseweb="slider"] > div:nth-child(3) {
        background: var(--primary-color) !important;
    }
    /* Radio buttons */
    div[data-baseweb="radio"] > div > label > div[role="radio"] {
        background: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }
    
    /* --- STYLE METRICS TO BE HIGH-IMPACT --- */
    div[data-testid="stMetricValue"] {
        font-size: 2.75rem; /* Make the number bigger */
        font-weight: 700;
        color: var(--primary-color); /* Make the metric value ORANGE */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* --- MODERN "CARD" LAYOUT --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--secondary-background-color);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* --- STYLE TABS --- */
    button[data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
    }
    
    /* --- STYLE SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #141820; /* Slightly different dark for sidebar */
    }
    [data-testid="stSidebar"] .st-emotion-cache-16txtl3 { /* Sidebar radio labels */
        font-size: 1.1rem;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- 3. DATA LOADING & CACHING ---
@st.cache_data
def load_data():
    try:
        # Using the ./data/ path as specified in your code
        demand_df = pd.read_csv('./data/demand_forecasting.csv')
        maintenance_df = pd.read_csv('./data/predictive_maintenance.csv')
        route_df = pd.read_csv('./data/route_optimization.csv')
        
        demand_df['date'] = pd.to_datetime(demand_df['date'])
        maintenance_df['date'] = pd.to_datetime(maintenance_df['date'])
        
        return demand_df, maintenance_df, route_df
    except FileNotFoundError:
        st.error("FATAL ERROR: Make sure your CSV files are in a folder named 'data' (e.g., './data/demand_forecasting.csv')")
        return None, None, None

demand_df, maintenance_df, route_df = load_data()

if demand_df is None:
    st.stop()

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.image("https://i.imgur.com/83ww43k.png", width=200) # Placeholder for Ugunja Logo
st.sidebar.title("Ugunja: The Intelligence Engine")

page = st.sidebar.radio(
    "Select a Model's Insights",
    [
        "💸 Route Optimization (ROI)", # Lead with the "money" page
        "🔧 Predictive Maintenance",
        "📈 Demand Forecasting",
    ],
    label_visibility="collapsed"
)

st.sidebar.info(
    "This dashboard demonstrates the live insights from our AI models. "
    "The data is a simulation of a real-world Greenwells fleet."
)


# --- 5. PAGE: ROUTE OPTIMIZATION (THE "MONEY SHOT") ---
if page == "💸 Route Optimization (ROI)":

    st.title("💸 Route Optimization Insights")
    st.markdown("This is our **business proposal**. It shows how our AI directly saves costs by optimizing routes.")
    
    # --- ADVANCED EDA 5: Interactive ROI Calculator (HERO SECTION) ---
    with st.container(border=True):
        st.header("Interactive ROI Calculator")
        st.markdown("Use the sliders to match your business costs and see the **real-time savings** our AI generates.")
        
        # Calculate total savings from the data
        savings_df = route_df.groupby('route_type').sum(numeric_only=True)
        total_km_saved = savings_df.loc['Standard_Route']['total_distance_km'] - savings_df.loc['Ugunja_AI_Route']['total_distance_km']
        total_hours_saved = savings_df.loc['Standard_Route']['total_time_hours'] - savings_df.loc['Ugunja_AI_Route']['total_time_hours']
        num_routes = int(len(route_df)/2)

        col1, col2 = st.columns(2)
        with col1:
            cost_per_km_ksh = st.slider("Fuel/Maint. Cost per KM (KSh)", 20, 100, 40)
        with col2:
            cost_per_hour_ksh = st.slider("Driver Labor Cost per Hour (KSh)", 300, 1000, 500)
        
        # Calculate total savings
        total_fuel_savings = total_km_saved * cost_per_km_ksh
        total_labor_savings = total_hours_saved * cost_per_hour_ksh
        total_savings = total_fuel_savings + total_labor_savings
        
        st.divider()
        st.subheader(f"Estimated Total Savings (from this {num_routes}-route dataset)")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(label="Fuel/Maint. Savings", value=f"KSh {total_fuel_savings:,.0f}")
        col_m2.metric(label="Labor Savings", value=f"KSh {total_labor_savings:,.0f}")
        col_m3.metric(label="TOTAL SAVINGS", value=f"KSh {total_savings:,.0f}")

    # --- ADVANCED EDA 6 & 7: Waterfall and Efficiency Plots ---
    with st.container(border=True):
        st.header("How We Achieve These Savings")
        tab1, tab2 = st.tabs(["The 'Financial Breakdown' (Waterfall)", "The 'Efficiency Frontier' (Scatter)"])
        
        with tab1:
            st.markdown("This chart breaks down the *source* of the savings from the calculator above.")
            fig_waterfall = go.Figure(go.Waterfall(
                name = "Savings", orientation = "v",
                measure = ["relative", "relative", "total"],
                x = ["Fuel/Maint. Savings (from KM)", "Labor Savings (from Hours)", "Total Savings"],
                text = [f"KSh {total_fuel_savings:,.0f}", f"KSh {total_labor_savings:,.0f}", f"KSh {total_savings:,.0f}"],
                textposition="auto",
                y = [total_fuel_savings, total_labor_savings, total_savings],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
                increasing = {"marker":{"color":"#FFA500"}}, # Ugunja Orange
                totals = {"marker":{"color":"#00B050"}} # Green for total
            ))
            fig_waterfall.update_layout(title = "Financial Breakdown of Savings", showlegend = False, template="plotly_dark")
            st.plotly_chart(fig_waterfall, use_container_width=True)

        with tab2:
            st.markdown("This proves our AI is smarter. 'Standard' routes are a scattered cloud (inefficient). 'Ugunja AI' routes form a tight, optimal line (the 'Efficiency Frontier').")
            fig_frontier = px.scatter(
                route_df, x="total_distance_km", y="total_time_hours",
                color="route_type",
                title="Ugunja AI vs. Standard Routes",
                color_discrete_map={'Standard_Route': 'grey', 'Ugunja_AI_Route': '#FFA500'}, # Ugunja Orange
                hover_data=['route_id']
            )
            fig_frontier.update_layout(template="plotly_dark")
            st.plotly_chart(fig_frontier, use_container_width=True)


# --- 6. PAGE: PREDICTIVE MAINTENANCE ---
elif page == "🔧 Predictive Maintenance":

    st.title("🔧 Predictive Maintenance Insights")
    st.markdown("Preventing costly breakdowns *before* they happen. This is our 'insurance policy' for the fleet.")

    # --- KPIs ---
    with st.container(border=True):
        high_risk_vehicles = maintenance_df[maintenance_df['predicted_risk_score'] > 0.8]['vehicle_id'].nunique()
        total_fleet_size = maintenance_df['vehicle_id'].nunique()
        avg_fleet_risk = maintenance_df['predicted_risk_score'].mean()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Fleet Size", f"{total_fleet_size} Vehicles")
        col2.metric("🔴 Vehicles at High Risk (>80%)", f"{high_risk_vehicles}")
        col3.metric("Avg. Fleet Risk Score", f"{avg_fleet_risk:.2%}")

    # --- ADVANCED EDA 3: Fleet Risk Treemap ---
    with st.container(border=True):
        st.header("At-a-Glance Fleet Risk Overview (Treemap)")
        st.markdown("See your entire fleet in one view. **Size** = Vehicle Mileage. **Color** = Risk Score. Instantly spot the high-risk, high-use vehicles.")
        
        latest_fleet_data = maintenance_df.sort_values('date').drop_duplicates('vehicle_id', keep='last')
        
        fig_tree = px.treemap(
            latest_fleet_data,
            path=[px.Constant("All Vehicles"), 'predicted_failure_type', 'vehicle_id'], # Hierarchy!
            values='mileage',
            color='predicted_risk_score',
            color_continuous_scale='OrRd', # Orange-Red is perfect for risk
            hover_data={'predicted_failure_type': True, 'predicted_risk_score': ':.2f', 'mileage': True}
        )
        fig_tree.update_layout(margin = dict(t=25, l=25, r=25, b=25), template="plotly_dark")
        st.plotly_chart(fig_tree, use_container_width=True)

    # --- ADVANCED EDA 4: Anomaly Detection ---
    with st.container(border=True):
        st.header("Finding the 'Needle in the Haystack'")
        st.markdown("Our model spots the *one* bad truck out of the *entire* healthy fleet.")
        
        tab1, tab2 = st.tabs(["Fleet-Wide Anomaly (Scatter)", "Risk Distribution (Box Plot)"])
        
        with tab1:
            fig_scatter = px.scatter(
                maintenance_df, x="avg_fuel_consumption_l_100km", y="predicted_risk_score",
                color="vehicle_id", hover_data=['date', 'predicted_failure_type'],
                title="Outlier Detection: Fuel Use vs. Risk"
            )
            fig_scatter.update_layout(template="plotly_dark")
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab2:
            fig_box = px.box(
                maintenance_df, x="vehicle_id", y="predicted_risk_score",
                color="vehicle_id", title="Vehicle Risk Score Distribution"
            )
            fig_box.update_layout(template="plotly_dark")
            st.plotly_chart(fig_box, use_container_width=True)
    
    # --- Drill-down on a specific vehicle ---
    with st.container(border=True):
        st.header("Vehicle-Specific Anomaly Trend (The 'Proof')")
        all_vehicles = maintenance_df['vehicle_id'].unique()
        anomalous_vehicle = 'KDC 456Y' if 'KDC 456Y' in all_vehicles else all_vehicles[0]
        
        selected_vehicle = st.selectbox(
            "Select a Vehicle to Analyze",
            options=all_vehicles,
            index=list(all_vehicles).index(anomalous_vehicle) # Default to the anomalous one
        )
        
        vehicle_df = maintenance_df[maintenance_df['vehicle_id'] == selected_vehicle]
        
        col1, col2 = st.columns(2)
        with col1:
            fig_fuel_trend = px.line(vehicle_df, x='date', y='avg_fuel_consumption_l_100km', title=f"Fuel Consumption Trend")
            fig_fuel_trend.update_layout(template="plotly_dark")
            st.plotly_chart(fig_fuel_trend, use_container_width=True)
        with col2:
            fig_risk_trend = px.line(vehicle_df, x='date', y='predicted_risk_score', title=f"Predicted Risk Score Trend")
            fig_risk_trend.update_yaxes(range=[0, 1])
            fig_risk_trend.update_layout(template="plotly_dark")
            st.plotly_chart(fig_risk_trend, use_container_width=True)


# --- 7. PAGE: DEMAND FORECASTING ---
elif page == "📈 Demand Forecasting":

    st.title("📈 Demand Forecasting Insights")
    st.markdown("Predicting demand to move from a *reactive* to a *predictive* supply chain.")

    # --- KPIs ---
    with st.container(border=True):
        total_predicted = demand_df['predicted_demand_cylinders'].sum()
        highest_demand_zone = demand_df.groupby('neighborhood')['predicted_demand_cylinders'].sum().idxmax()
        peak_day = demand_df.groupby('day_of_week')['predicted_demand_cylinders'].sum().idxmax()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Predicted Demand (Dataset)", f"{total_predicted:,} Cylinders")
        col2.metric("Projected Hotspot", highest_demand_zone)
        col3.metric("Projected Peak Day", peak_day)

    # --- ADVANCED EDA 1: Calendar Heatmap ---
    with st.container(border=True):
        st.header("Daily Demand Pattern (Calendar Heatmap)")
        st.markdown("This shows daily demand intensity. Our model sees that demand peaks on weekends and holidays.")
        
        try:
            daily_demand = demand_df.groupby('date')['predicted_demand_cylinders'].sum().reset_index()
            daily_demand['day_of_week'] = daily_demand['date'].dt.day_name()
            daily_demand['week_of_year'] = daily_demand['date'].dt.isocalendar().week
            daily_demand['month_name'] = daily_demand['date'].dt.month_name()
            daily_demand['month_num'] = daily_demand['date'].dt.month
            
            # Sort by month number for correct faceting
            daily_demand = daily_demand.sort_values('month_num')
            
            fig_cal = px.density_heatmap(
                daily_demand, x="week_of_year", y="day_of_week", z="predicted_demand_cylinders",
                histfunc="avg", title="Average Predicted Demand by Day of Week",
                color_continuous_scale="OrRd",
                facet_col="month_name", facet_col_wrap=4,
                labels={'predicted_demand_cylinders': 'Avg Demand'}
            )
            fig_cal.update_layout(coloraxis_showscale=False, template="plotly_dark", height=700)
            st.plotly_chart(fig_cal, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not generate calendar heatmap: {e}")

    # --- ADVANCED EDA 2: Decomposition & Correlation ---
    with st.container(border=True):
        st.header("Understanding the 'Why' of Demand")
        tab1, tab2 = st.tabs(["Time Series Decomposition", "Demand Driver Correlation"])

        with tab1:
            st.markdown("We break down demand into its core components: the **Trend** (long-term), **Seasonality** (weekly pattern), and **Residuals** (noise).")
            daily_demand_ts = demand_df.groupby('date')['predicted_demand_cylinders'].sum().reset_index().set_index('date')
            if not daily_demand_ts.empty and len(daily_demand_ts) > 14: # Need enough data to decompose
                decomposition = seasonal_decompose(daily_demand_ts['predicted_demand_cylinders'], model='additive', period=7)
                
                fig_decomp = make_subplots(
                    rows=4, cols=1, shared_xaxes=True,
                    subplot_titles=("1. Observed", "2. Trend", "3. Seasonal (Weekly)", "4. Residual")
                )
                fig_decomp.add_trace(go.Scatter(x=decomposition.observed.index, y=decomposition.observed, mode='lines', name='Observed'), row=1, col=1)
                fig_decomp.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend, mode='lines', name='Trend', line=dict(color='orange')), row=2, col=1)
                fig_decomp.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal, mode='lines', name='Seasonal', line=dict(color='green')), row=3, col=1)
                fig_decomp.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid, mode='markers', name='Residual', marker=dict(size=2, color='gray')), row=4, col=1)
                fig_decomp.update_layout(height=700, showlegend=False, margin=dict(t=100), template="plotly_dark")
                st.plotly_chart(fig_decomp, use_container_width=True)

        with tab2:
            st.markdown("This matrix shows what drives demand. A high number (e.g., 0.8) means a strong link. **(Weekend = 6, 7)**.")
            df_corr = demand_df.copy()
            day_map = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
            df_corr['day_of_week_num'] = df_corr['day_of_week'].map(day_map)
            weather_map = {'Rainy': 0, 'Cloudy': 1, 'Sunny': 2}
            df_corr['weather_num'] = df_corr['weather'].map(weather_map)
            
            corr_df = df_corr[['predicted_demand_cylinders', 'day_of_week_num', 'weather_num', 'is_holiday']]
            corr_matrix = corr_df.corr()

            fig_heatmap = px.imshow(
                corr_matrix, text_auto=".2f", aspect="auto",
                color_continuous_scale='OrRd', labels=dict(color="Correlation"),
                title="Correlation: What Drives Demand?"
            )
            fig_heatmap.update_xaxes(side="top")
            fig_heatmap.update_layout(template="plotly_dark")
            st.plotly_chart(fig_heatmap, use_container_width=True)