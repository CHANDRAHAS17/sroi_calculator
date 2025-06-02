import streamlit as st
import os
import sys

# ✅ Helper to get correct path when packaged with PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ✅ Set page config
st.set_page_config(
    page_title="NIRMAAN SROI Calculator",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 
col1, col2 = st.columns([1, 4])
with col1:
    st.image(resource_path("NIRMAAN_logo.png"), width=350)
with col2:
    st.title("NIRMAAN'S SROI Calculator")
    st.markdown("*Estimate the social value created by your project in just a few steps!*")

# EXPANDER: What is SROI?
with st.expander("ℹ️ What is SROI?"):
    st.markdown("""
    Social return on investment (SROI) is a principles-based method for measuring extra-financial value 
    (such as environmental or social value) not otherwise reflected or involved in conventional financial accounts. 
    
    The method can be used by any entity to evaluate impact on stakeholders, identify ways to improve performance, 
    and enhance the performance of investments.
    """)

# Sidebar Inputs
st.sidebar.header("📊 Project Inputs")
st.sidebar.markdown("Adjust your values to calculate SROI.")

total_cost = st.sidebar.number_input("💰 Total Project Cost (₹)", min_value=0.0, step=100.0)
num_outcomes = st.sidebar.number_input("📦 Number of Outcomes", min_value=1, step=1, value=1)

# Outcome Details
st.markdown("## 📦 Outcome Details")

net_adjusted_value = 0

for i in range(int(num_outcomes)):
    with st.container():
        st.markdown(f"### Outcome {i+1}")

        col1, col2 = st.columns(2)

        with col1:
            quantity = st.number_input(f"👥 Quantity for Outcome {i+1}", min_value=0.0, key=f"qty_{i}")
            deadweight = st.number_input(
                f"🎯 Deadweight (0-1)", min_value=0.0, max_value=1.0, value=0.1, key=f"dw_{i}",
                help="Deadweight is the % of outcome that would have happened anyway."
            )
            dropoff = st.number_input(
                f"📉 Drop-off (0-1)", min_value=0.0, max_value=1.0, value=0.1, key=f"do_{i}",
                help="Drop-off is the reduction in outcomes over time."
            )

        with col2:
            value = st.number_input(f"💸 Value per Unit (₹)", min_value=0.0, key=f"val_{i}")
            attribution = st.number_input(
                f"🙋 Attribution (0-1)", min_value=0.0, max_value=1.0, value=0.8, key=f"att_{i}",
                help="Attribution is the % of outcome caused by your intervention."
            )
            displacement = st.number_input(
                f"🔄 Displacement (0-1)", min_value=0.0, max_value=1.0, value=0.0, key=f"disp_{i}",
                help="Displacement is how much your outcome displaced something else."
            )

        # Adjusted value calculation
        adjusted = (
            quantity
            * value
            * (1 - deadweight)
            * attribution
            * (1 - dropoff)
            * (1 - displacement)
        )

        net_adjusted_value += adjusted

# Final Results Section
st.markdown("---")
st.subheader("📈 Final Results")

with st.spinner("Calculating your SROI..."):
    if total_cost > 0:
        sroi = net_adjusted_value / total_cost
    else:
        sroi = 0

    st.metric("Total Net Adjusted Value", f"₹ {net_adjusted_value:,.2f}")
    st.success(f"💡 Final SROI: {sroi:.4f}")

    # 🎉 Only show balloons for strong SROI
    if sroi >= 1:
        st.balloons()

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Chandrahas Jandhyala")
