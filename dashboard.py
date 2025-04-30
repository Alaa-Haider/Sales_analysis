import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load your combined dataset
@st.cache_data
def load_data():
    df = pd.read_csv("df_combined.csv")
    # Add a Governorate column with "Behaira" as the default value
   
    return df

df = load_data()

st.title("📊 Monthly Product Performance Dashboard")

# Add governorate selector (currently only Behaira, but prepared for future additions)
governorates = ['Behaira', 'Menofia']  # You can add more governorates to this list later
selected_governorate = st.sidebar.selectbox("Select Governorate", governorates)

# Filter by products and months
products = df['Product'].unique()
months = df['Month'].unique()

# Add select all button for products
st.sidebar.write("Product Selection")
select_all_products = st.sidebar.checkbox("Select All Products", value=False)

# Handle product selection based on select all checkbox
if select_all_products:
    selected_products = products
else:
    # Set default to first two products instead of all products
    default_products = products[:2]  # Select first two products as default
    selected_products = st.sidebar.multiselect("Select Product(s)", products, default=default_products)

# Add select all button for months after product selection
st.sidebar.write("Month Selection")
select_all_months = st.sidebar.checkbox("Select All Months", value=False)

# Handle month selection based on select all checkbox
if select_all_months:
    selected_months = months
else:
    selected_months = st.sidebar.multiselect("Select Month(s)", months, default=[])

# Filter the dataframe
filtered_df = df[
    (df['Governorate'] == selected_governorate) & 
    (df['Product'].isin(selected_products)) & 
    (df['Month'].isin(selected_months))
]
# Filter data for selected governorate
trend_df = df[df['Governorate'] == selected_governorate].sort_values(['Product', 'Month'])

# Calculate achievement growth for filtered data
achievement_change_all = trend_df.groupby('Product')['Achievement (%)'].agg(['first', 'last'])

# Compute growth
achievement_change_all['Growth %'] = achievement_change_all.apply(
    lambda x: round(x['last'] - x['first'], 2) if x['first'] != 0 or x['last'] != 0 else 0, 
    axis=1
)

# Get top 10 growing products
top_growth_all = achievement_change_all.sort_values('Growth %', ascending=False).head(10)

# Display summary section
st.header("📈 Top 10 Products by Achievement Growth")
col1, col2 = st.columns([2, 1])

with col1:
    fig_growth = go.Figure(data=[go.Pie(
        labels=top_growth_all.index,
        values=top_growth_all['Growth %'],
        hole=0.3,
        textinfo='label+percent',
        textposition='outside',
        pull=[0.1 if i == 0 else 0 for i in range(len(top_growth_all))],  # Pull out the highest growth slice
    )])
    
    fig_growth.update_layout(
        title='Top 10 Products by Achievement Growth %',
        annotations=[
            dict(
                text=f"Highest Growth:<br>{top_growth_all.index[0]}<br>{top_growth_all['Growth %'].iloc[0]:.1f}%",
                x=0.5, y=0.5,
                font_size=12,
                showarrow=False
            )
        ],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with col2:
    st.subheader("Growth Summary")
    for product, row in top_growth_all.iterrows():
        st.write(f"**{product}**: {row['Growth %']:.1f}%")


# Add new section for Achievement % Bar Chart
st.header("📊 Achievement % for Selected Products")

# Create bar chart for selected products' achievement
fig_achievement = px.bar(
    filtered_df,
    x='Product',
    y='Achievement (%)',
    color='Product',
    title=f'Achievement % by Product ({selected_governorate})',
    barmode='group'
)

fig_achievement.update_layout(
    xaxis_title='Product',
    yaxis_title='Achievement (%)',
    showlegend=True,
    xaxis={'categoryorder':'total descending'}
)

st.plotly_chart(fig_achievement, use_container_width=True)

# Achievement plot over time
fig = px.line(filtered_df, x='Month', y='Achievement (%)', color='Product',
              markers=True, title=f'{selected_governorate} - Achievement % Over Time')
fig.update_layout(xaxis_title='Month', yaxis_title='Achievement (%)')
st.plotly_chart(fig, use_container_width=True)

# Create tabs for Sales and Value
tab1, tab2 = st.tabs(["Sales", "Value"])

with tab1:
    fig_sold = px.line(filtered_df, x='Month', y='Sold', color='Product', 
                       title=f'{selected_governorate} - Units Sold Over Time')
    st.plotly_chart(fig_sold, use_container_width=True)

with tab2:
    fig_value = px.line(filtered_df, x='Month', y='Value', color='Product', 
                       title=f'{selected_governorate} - Sales Value Over Time')
    st.plotly_chart(fig_value, use_container_width=True)
