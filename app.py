import pandas as pd
import streamlit as st
import pickle
from fpdf import FPDF
from datetime import datetime
import io

# 1. Page Configuration & Professional Theme Setup
st.set_page_config(page_title="Delhi NCR Property Valuation Engine", page_icon="🏢", layout="centered")

def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Ingest external premium UI styling sheet
load_css("style.css")

# --- MODULAR ARTIFACT LOADER ENGINE ---
@st.cache_resource
def load_system_artifacts():
    with open("model_artifacts.pkl", "rb") as f:
        return pickle.load(f)

# Instant extraction from serialized binary storage
artifacts = load_system_artifacts()
rf_model = artifacts['rf_model']
rf_r2 = artifacts['metrics']['rf_r2']
lr_r2 = artifacts['metrics']['lr_r2']
display_localities = artifacts['display_localities']
mapping_lookup = artifacts['mapping_lookup']
rate_lookup = artifacts['rate_lookup']

# --- DYNAMIC EXPORT REPORT MICROSERVICE (PDF GENERATION) ---
def generate_pdf_report(locality, area, bhk, bath, parking, furnish, status, trans, p_type, valuation, user_name, broker_info):
    pdf = FPDF()
    pdf.add_page()
    
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Header Section
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 12, "DELHI NCR PROPERTY VALUATION REPORT", ln=True, align="C")
    
    pdf.set_font("Arial", "I", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 8, "Statistical Real Estate Analysis & Valuation Sheet", ln=True, align="C")
    
    pdf.set_draw_color(226, 232, 240)
    pdf.line(10, 35, 200, 35)
    pdf.ln(8)
    
    # Metadata Framework (Client & Broker Verification Details)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(95, 6, f"Prepared For:  {user_name if user_name else 'N/A'}", ln=False)
   # pdf.cell(95, 6, f"Date:  {current_date}", ln=True, align="R")
    pdf.cell(95, 6, f"Broker / Agency:  {broker_info if broker_info else 'N/A'}", ln=False)
    #pdf.cell(95, 6, f"Time:  {current_time}", ln=True, align="R")
    
    pdf.line(10, 52, 200, 52)
    pdf.ln(10)
    
    # 1. Property Specification Metrics Layout
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Property Parameters Specification", ln=True)
    pdf.ln(3)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(51, 65, 85)
    
    details = [
        f"Target Locality: {locality}",
        f"Total Area: {area} Sq. Ft.",
        f"BHK Configuration: {bhk} BHK",
        f"Bathrooms: {bath}",
        f"Parking Spaces: {parking}",
        f"Furnishing Status: {furnish}",
        f"Construction Status: {status}",
        f"Transaction Type: {trans}",
        f"Property Structural Type: {p_type}"
    ]
    for item in details:
        pdf.cell(0, 6.5, f"   - {item}", ln=True)
        
    pdf.ln(6)
    pdf.line(10, 138, 200, 138)
    pdf.ln(6)
    
    # 2. Market Assessment Layout Block
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Market Valuation Assessment", ln=True)
    pdf.ln(3)
    
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 14, f" Estimated Market Value: Rs. {valuation:,.2f}", ln=True, fill=True)
    
    pdf.ln(4)
    pdf.set_font("Arial", "", 9)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 6, "Disclaimer: This estimation is computed based on historical regional data distributions and market parameters.", ln=True)
    
    # Premium Corporate Footer Box Alignment
    pdf.set_fill_color(248, 250, 252) 
    pdf.set_draw_color(226, 232, 240)  
    pdf.rect(10, 245, 190, 32, 'DF')   
    
    pdf.set_font("Arial", "B", 10.5)
    pdf.set_text_color(15, 23, 42)    
    pdf.set_y(248) 
    pdf.cell(0, 6, "   Platform Support & System Details", ln=True)
    pdf.ln(1)
    
    pdf.set_font("Arial", "", 9.5)
    pdf.set_text_color(71, 85, 105)   
    pdf.cell(0, 5, "      Platform Owner: Khushi (Lead Systems Architect)", ln=True)
    pdf.cell(0, 6, "      Corporate Email: support@delhirealestatepredictor.com", ln=True)
    pdf.cell(0, 5, "      Contact Support: +91 98765 43210", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

# --- MAIN DASHBOARD USER INTERFACE ---
st.title("🏢 Delhi NCR Property Valuation Engine")
st.write("An enterprise real estate valuation system utilizing verified data pipelines and statistical pricing models.")
st.write("---")

# Expandable Statistical Benchmarking Dashboard
with st.expander("📊 View Architecture Benchmarking Metrics"):
    st.write(f"**Random Forest Target Accuracy (R²):** `{rf_r2:.4f}`")
    st.write(f"**Baseline Linear Regression Accuracy (R²):** `{lr_r2:.4f}`")

st.info(f"💡 Therefore, the system automatically routes all valuation inputs through the **Random Forest Regressor** to guarantee optimal pattern match and minimize computational variance.")

# Feature Weights Resolution
feature_names = ['Area', 'BHK', 'Bathroom', 'Furnishing', 'Parking', 'Status', 'Transaction', 'Type', 'Per_Sqft', 'Locality_Code']
importances = rf_model.feature_importances_
importance_df = pd.Series(importances, index=feature_names).sort_values(ascending=True)

# Expandable Feature Importance Panel
with st.expander("📈 View Live Feature Variance Diagnostics"):
    st.write("Below are the relative structural metrics mapping how the system weighs distinct house configurations:")
    st.bar_chart(importance_df, height=220)

st.write("---")

# User Metadata Block Inputs
st.subheader("👤 Client & Broker Profile")
meta_c1, meta_c2 = st.columns(2)
with meta_c1:
    user_name = st.text_input("Client / User Name", placeholder="e.g. Mansi Sharma")
with meta_c2:
    broker_info = st.text_input("Broker Agency / Reference ID", placeholder="e.g. Bansal Properties")

st.write("---")

# Structural Layout Inputs
st.subheader("📍 Target Asset Parameters")
selected_locality = st.selectbox("Select Locality / Sector:", display_localities)

avg_sqft_rate = int(rate_lookup[selected_locality])
st.caption(f"ℹ️ Sector Baseline Matrix: Historical average rate in this region is ~₹{avg_sqft_rate:,} / Sq. Ft.")

col1, col2 = st.columns(2)
with col1:
    area = st.number_input("Total Area (in Sq. Ft.)", min_value=100, max_value=10000, value=1200, step=50)
    bhk = st.slider("BHK Configuration", min_value=1, max_value=6, value=3)
    bathroom = st.slider("Bathrooms", min_value=1, max_value=5, value=2)
    parking = st.slider("Allocated Parking", min_value=0, max_value=5, value=1)
    
with col2:
    furnishing = st.selectbox("Furnishing Specification", ["Unfurnished", "Semi-Furnished", "Furnished"])
    status = st.selectbox("Construction Status", ["Almost Ready", "Ready to Move"])
    transaction = st.selectbox("Transaction Type", ["New Property", "Resale"])
    prop_type = st.selectbox("Property Type", ["Apartment", "Builder Floor"])

# --- CORES SYSTEM DATA INTEGRITY CORE VALIDATION ---
validation_passed = True

if area < 300 and bhk >= 3:
    st.warning("⚠️ Operational Alert: The configuration ratios between total built-up Area and selected BHK count deviate from standard structural parameters.")
    validation_passed = False
elif area > 5000 and bhk <= 1:
    st.warning("⚠️ Operational Alert: Unusually large spatial footprint selected for a single BHK layout configuration.")
    validation_passed = False
    
if bathroom > (bhk + 1):
    st.warning("⚠️ Operational Alert: The count of bathrooms allocated exceeds proportional bedroom distribution ratios.")
    validation_passed = False

st.write("---")

# Dynamic Button Form Safeguard Coordination
if validation_passed:
    execute_inference = st.button("Calculate Property Valuation", type="primary", use_container_width=True)
else:
    st.button("Calculate Property Valuation", type="primary", use_container_width=True, disabled=True)
    st.caption("🔒 Execution disabled due to layout structural logic variance alerts above.")
    execute_inference = False

# --- COMPILATION & OUTPUT DISPLAY MATRIX ---
if execute_inference or st.session_state.get('calculated', False):
    if execute_inference:
        st.session_state['calculated'] = True
        
        furnishing_encoded = ["Unfurnished", "Semi-Furnished", "Furnished"].index(furnishing)
        status_encoded = ["Almost Ready", "Ready to Move"].index(status)
        transaction_encoded = ["New Property", "Resale"].index(transaction)
        type_encoded = ["Apartment", "Builder Floor"].index(prop_type)
        locality_encoded = mapping_lookup[selected_locality]
        
        input_data = pd.DataFrame([[
            area, bhk, bathroom, furnishing_encoded, parking, 
            status_encoded, transaction_encoded, type_encoded, avg_sqft_rate, locality_encoded
        ]], columns=['Area', 'BHK', 'Bathroom', 'Furnishing', 'Parking', 'Status', 'Transaction', 'Type', 'Per_Sqft', 'Locality_Code'])
        
        st.session_state['prediction'] = rf_model.predict(input_data)[0]
        if st.session_state['prediction'] < 0:
            st.session_state['prediction'] = area * avg_sqft_rate

    pred = st.session_state['prediction']
    
    # Premium Valuation HTML Render Block
    st.markdown(f"""
        <div class="premium-valuation-card">
            <p class="card-label">Evaluated Market Asset Value</p>
            <div class="card-value">₹{pred:,.2f}</div>
            <div class="premium-badge">✓ High-Precision Predictive System</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Compilation to local byte payload
    pdf_bytes = generate_pdf_report(
        selected_locality, area, bhk, bathroom, parking, 
        furnishing, status, transaction, prop_type, pred, user_name, broker_info
    )
    
    # Export File Downloader Action Item
    st.download_button(
        label="📥 Download Personalized Valuation Report (PDF)",
        data=pdf_bytes,
        file_name=f"Valuation_Report_{selected_locality}.pdf",
        mime="application/pdf",
        use_container_width=True
    )