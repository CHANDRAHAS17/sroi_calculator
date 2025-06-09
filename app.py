import streamlit as st
import os
import sys
import base64
import pandas as pd
import matplotlib.pyplot as plt
import json
from io import BytesIO
from fpdf import FPDF
from PIL import Image

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_pdf_report(logo_path, chart_bytes, df, net_value, sroi, project_type):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if logo_path:
        pdf.image(logo_path, x=10, y=8, w=40)
        pdf.set_xy(55, 10)
    else:
        pdf.set_xy(10, 10)

    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 0, 128)
    pdf.cell(0, 10, "NIRMAAN SROI Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Project Type: {project_type}", ln=True)
    pdf.cell(0, 10, f"Total Net Adjusted Value: Rs {net_value:,.2f}", ln=True)
    pdf.cell(0, 10, f"Final SROI: {sroi:.4f}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 10, "Outcome Breakdown", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0)

    if 'Project Type' in df.columns:
        df = df.drop(columns=['Project Type'])

    col_names = list(df.columns)
    usable_width = pdf.w - 2 * pdf.l_margin

    base_weights = {
        "Title": 3, "Outcome": 2, "Adjusted Value": 2,
        "Quantity": 1, "Value/Unit (Rs)": 1, "Deadweight": 1,
        "Dropoff": 1, "Attribution": 1, "Displacement": 1
    }
    weights = [base_weights.get(name, 1) for name in col_names]
    weight_sum = sum(weights)
    col_widths = [(w / weight_sum) * usable_width for w in weights]

    pdf.set_fill_color(230, 230, 250)
    for i, name in enumerate(col_names):
        pdf.cell(col_widths[i], 8, name, border=1, fill=True)
    pdf.ln()

    for index, row in df.iterrows():
        for i, name in enumerate(col_names):
            val = row[name]
            if isinstance(val, float):
                val = f"{val:,.2f}"
            else:
                val = str(val)
            pdf.cell(col_widths[i], 8, val, border=1)
        pdf.ln()

    pdf.ln(10)
    if chart_bytes:
        chart_path = "/tmp/chart.png"
        with open(chart_path, "wb") as f:
            f.write(chart_bytes.getbuffer())
        pdf.image(chart_path, x=pdf.l_margin, w=pdf.w - 2 * pdf.l_margin)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

st.set_page_config(page_title="NIRMAAN SROI Calculator", layout="centered")
st.markdown("""
    <style>
        .css-10trblm.e16nr0p30 { text-align: center; }
        section[data-testid="stSidebar"] { background-color: #f0f2f6; }
        div[data-testid="metric-container"] {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
        }
        footer { visibility: hidden; }
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
    </style>
""", unsafe_allow_html=True)

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

st.sidebar.header("📊 Project Inputs")
project_type = st.sidebar.selectbox("🏗️ Project Type", [
    "Education", "Skill Development and Entrepreneurship",
    "Social Leadership", "Environment", "Health", "Rural Development"])

total_cost = st.sidebar.number_input("💰 Total Project Cost (Rs)", min_value=0.0, step=100.0)
num_outcomes = st.sidebar.number_input("📦 Number of Outcomes", min_value=1, step=1, value=1)

uploaded_json = st.sidebar.file_uploader("📤 Load Previous Session (.json)", type=["json"])
if uploaded_json:
    session_data = json.load(uploaded_json)
    total_cost = session_data.get("total_cost", total_cost)
    num_outcomes = session_data.get("num_outcomes", num_outcomes)
    previous_outcomes = session_data.get("outcomes", [])
else:
    previous_outcomes = [{} for _ in range(int(num_outcomes))]

st.markdown("## 📦 Outcome Details")

net_adjusted_value = 0
outcome_data = []

for i in range(int(num_outcomes)):
    st.markdown(f"### Outcome {i+1}")
    prev = previous_outcomes[i] if i < len(previous_outcomes) else {}

    outcome_title = st.text_input(f"✏️ Outcome {i+1} Title", value=prev.get("Title", f"Outcome {i+1}"), key=f"title_{i}")

    col1, col2 = st.columns(2)
    with col1:
        quantity = st.number_input(f"👥 Quantity", min_value=0.0, value=prev.get("Quantity", 0.0), key=f"qty_{i}")
        deadweight = st.number_input(f"🎯 Deadweight (0-1)", 0.0, 1.0, value=prev.get("Deadweight", 0.1), key=f"dw_{i}")
        dropoff = st.number_input(f"📉 Drop-off (0-1)", 0.0, 1.0, value=prev.get("Dropoff", 0.1), key=f"do_{i}")
    with col2:
        value = st.number_input(f"💸 Value per Unit (Rs)", min_value=0.0, value=prev.get("Value/Unit (Rs)", 0.0), key=f"val_{i}")
        attribution = st.number_input(f"🙋 Attribution (0-1)", 0.0, 1.0, value=prev.get("Attribution", 0.8), key=f"att_{i}")
        displacement = st.number_input(f"🔄 Displacement (0-1)", 0.0, 1.0, value=prev.get("Displacement", 0.0), key=f"disp_{i}")

    adjusted = quantity * value * (1 - deadweight) * attribution * (1 - dropoff) * (1 - displacement)
    outcome_data.append({
        "Outcome": f"Outcome {i+1}",
        "Title": outcome_title,
        "Quantity": quantity,
        "Value/Unit (Rs)": value,
        "Deadweight": deadweight,
        "Dropoff": dropoff,
        "Attribution": attribution,
        "Displacement": displacement,
        "Adjusted Value": adjusted,
        "Project Type": project_type
    })
    net_adjusted_value += adjusted

df = pd.DataFrame(outcome_data)
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Outcome Data as CSV", data=csv, file_name="sroi_outcomes.csv", mime="text/csv")

st.markdown("### 📊 Outcome Contribution Breakdown")
if net_adjusted_value > 0:
    labels = [f"{row['Title']}" for row in outcome_data]
    values = [row["Adjusted Value"] for row in outcome_data]
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    chart_bytes = BytesIO()
    fig.savefig(chart_bytes, format="png", bbox_inches="tight")
    st.pyplot(fig)
else:
    chart_bytes = None
    st.info("Enter outcome data to generate chart.")

st.markdown("---")
st.subheader("📈 Final Results")
sroi = net_adjusted_value / total_cost if total_cost > 0 else 0
st.metric("Total Net Adjusted Value", f"Rs {net_adjusted_value:,.2f}")
st.success(f"💡 Final SROI: {sroi:.4f}")
if sroi >= 1:
    st.balloons()

if st.button("📄 Download PDF Report"):
    pdf_bytes_io = generate_pdf_report(logo_path, chart_bytes, df, net_adjusted_value, sroi, project_type)
    st.download_button("⬇️ Download Full Report", data=pdf_bytes_io, file_name="sroi_report.pdf", mime="application/pdf")

session_state = {
    "total_cost": total_cost,
    "num_outcomes": num_outcomes,
    "outcomes": outcome_data
}
session_json = json.dumps(session_state, indent=2)
st.download_button("💾 Save My Session", session_json, file_name="sroi_session.json", mime="application/json")

st.markdown("---")
st.markdown("Made with ❤️ by Chandrahas Jandhyala")
