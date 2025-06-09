import streamlit as st
import os
import sys
import base64
import pandas as pd
import matplotlib.pyplot as plt
import json

# ---------- Helper Functions ---------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="NIRMAAN SROI Calculator",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS Styling ----------
st.markdown("""
    <style>
        .css-10trblm.e16nr0p30 {
            text-align: center;
        }
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }
        footer {
            visibility: hidden;
        }
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Header ----------
col1, col2 = st.columns([1, 4])
with col1:
    logo_path = resource_path("NIRMAAN_logo.png")
    with open(logo_path, "rb") as img_file:
        encoded_logo = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f'<a href="https://nirmaan.org" target="_blank">'
        f'<img src="data:image/png;base64,{encoded_logo}" width="350"></a>',
        unsafe_allow_html=True
    )
with col2:
    st.title("NIRMAAN'S SROI Calculator")
    st.markdown("*Estimate the social value created by your project in just a few steps!*")

# ---------- Information Expanders ----------
with st.expander("ℹ️ What is SROI?"):
    st.markdown("""
    Social return on investment (SROI) is a principles-based method for measuring extra-financial value 
    (such as environmental or social value) not otherwise reflected or involved in conventional financial accounts.
    """)

with st.expander("📘 Definition of Key Terms"):
    st.markdown("""
    - **Deadweight**: The portion of the outcome that would have happened even without the project.
    - **Drop Off**: The decline in the benefits of an outcome over time.
    - **Displacement**: When your project’s benefit unintentionally causes a loss elsewhere.
    - **Attribution**: The extent to which the outcome is directly due to your project, and not others.
    """)

# ---------- Sidebar Inputs ----------
st.sidebar.header("📊 Project Inputs")
st.sidebar.markdown("Adjust your values to calculate SROI.")

total_cost = st.sidebar.number_input("💰 Total Project Cost (₹)", min_value=0.0, step=100.0)
num_outcomes = st.sidebar.number_input("📦 Number of Outcomes", min_value=1, step=1, value=1)

# ---------- Session Import ----------
uploaded_json = st.sidebar.file_uploader("📤 Load Previous Session (.json)", type=["json"])
if uploaded_json:
    session_data = json.load(uploaded_json)
    total_cost = session_data.get("total_cost", total_cost)
    num_outcomes = session_data.get("num_outcomes", num_outcomes)
    previous_outcomes = session_data.get("outcomes", [])
else:
    previous_outcomes = [{} for _ in range(int(num_outcomes))]

# ---------- Outcome Input ----------
st.markdown("## 📦 Outcome Details")

net_adjusted_value = 0
outcome_data = []

for i in range(int(num_outcomes)):
    st.markdown(f"### Outcome {i+1}")
    prev = previous_outcomes[i] if i < len(previous_outcomes) else {}

    col1, col2 = st.columns(2)
    with col1:
        quantity = st.number_input(
            f"👥 Quantity for Outcome {i+1}", min_value=0.0,
            value=prev.get("Quantity", 0.0), key=f"qty_{i}"
        )
        deadweight = st.number_input(
            f"🎯 Deadweight (0-1)", 0.0, 1.0,
            value=prev.get("Deadweight", 0.1), key=f"dw_{i}"
        )
        dropoff = st.number_input(
            f"📉 Drop-off (0-1)", 0.0, 1.0,
            value=prev.get("Dropoff", 0.1), key=f"do_{i}"
        )

    with col2:
        value = st.number_input(
            f"💸 Value per Unit (₹)", min_value=0.0,
            value=prev.get("Value/Unit (₹)", 0.0), key=f"val_{i}"
        )
        attribution = st.number_input(
            f"🙋 Attribution (0-1)", 0.0, 1.0,
            value=prev.get("Attribution", 0.8), key=f"att_{i}"
        )
        displacement = st.number_input(
            f"🔄 Displacement (0-1)", 0.0, 1.0,
            value=prev.get("Displacement", 0.0), key=f"disp_{i}"
        )

    adjusted = (
        quantity
        * value
        * (1 - deadweight)
        * attribution
        * (1 - dropoff)
        * (1 - displacement)
    )

    outcome_data.append({
        "Outcome": f"Outcome {i+1}",
        "Quantity": quantity,
        "Value/Unit (₹)": value,
        "Deadweight": deadweight,
        "Dropoff": dropoff,
        "Attribution": attribution,
        "Displacement": displacement,
        "Adjusted Value": adjusted
    })

    net_adjusted_value += adjusted

# ---------- CSV Export ----------
df = pd.DataFrame(outcome_data)
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Outcome Data as CSV", data=csv, file_name="sroi_outcomes.csv", mime="text/csv")

# ---------- Pie Chart ----------
st.markdown("### 📊 Outcome Contribution Breakdown")
if net_adjusted_value > 0:
    labels = [row["Outcome"] for row in outcome_data]
    values = [row["Adjusted Value"] for row in outcome_data]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
else:
    st.info("Enter outcome data to see the chart.")

# ---------- Final SROI Result ----------
st.markdown("---")
st.subheader("📈 Final Results")

with st.spinner("Calculating your SROI..."):
    sroi = net_adjusted_value / total_cost if total_cost > 0 else 0

    st.metric("Total Net Adjusted Value", f"₹ {net_adjusted_value:,.2f}")
    st.success(f"💡 Final SROI: {sroi:.4f}")
    if sroi >= 1:
        st.balloons()

# ---------- Session Export ----------
session_state = {
    "total_cost": total_cost,
    "num_outcomes": num_outcomes,
    "outcomes": outcome_data
}
session_json = json.dumps(session_state, indent=2)
st.download_button("💾 Save My Session", session_json, file_name="sroi_session.json", mime="application/json")

# ---------- Footer ----------
st.markdown("---")
st.markdown("Made with ❤️ by Chandrahas Jandhyala")
