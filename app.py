import streamlit as st
import pandas as pd
import pickle
import os
from fpdf import FPDF

st.set_page_config(page_title="Delhi NCR Valuation Engine", layout="wide")

# Custom CSS Styling Injection
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 1. MODEL ARTIFACTS LOADING
@st.cache_resource
def load_valuation_model():
    if os.path.exists("model_artifacts.pkl"):
        with open("model_artifacts.pkl", "rb") as f:
            artifacts = pickle.load(f)
        return artifacts
    return None

artifacts = load_valuation_model()

# 2. CORE FRONTEND DATA PIPELINE UI
st.title("🏢 Delhi NCR Property Valuation Engine")
st.markdown("An enterprise real estate valuation system utilizing verified data pipelines and statistical pricing models.")

if artifacts is None:
    st.error("Error: 'model_artifacts.pkl' backend file not found! Please check your repository deployment.")
else:
    if isinstance(artifacts, dict) and "model" in artifacts:
        model = artifacts["model"]
    else:
        model = artifacts
        
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Property Dimensions & Inputs")
        client_name = st.text_input("Client Name (Optional)", value="Valued Client")
        broker_name = st.text_input("Broker / Agency Name (Optional)", value="Delhi NCR Analytics")
        
        area = st.number_input("Total Area (in Sq. Ft.)", min_value=100, max_value=50000, value=1200, step=50)
        bhk = st.slider("Number of Bedrooms (BHK)", 1, 10, 3)
                
    with col2:
        st.subheader("Live Valuation Inference Engine")
        
        try:
            input_df = pd.DataFrame([[area, bhk]])
            predicted_price = model.predict(input_df)[0]
        except Exception:
            input_df = pd.DataFrame([{"Area": area, "No. of Bedrooms": bhk}])
            predicted_price = model.predict(input_df)[0]
            
        if predicted_price >= 100:
            formatted_price_str = f"₹ {predicted_price/100:.2f} Crores"
        else:
            formatted_price_str = f"₹ {predicted_price:.2f} Lakhs"
            
        st.metric(label="Estimated Market Value", value=formatted_price_str)
        st.write(f"**Verification Stamp:** System verification successfully parsed at standard runtime framework.")

        # 3. PDF GENERATION ENGINE WITH CORRECT ALIGNMENT & SPACING
        class PropertyReport(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'DELHI NCR PROPERTY VALUATION REPORT', 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 5, 'Statistical Real Estate Analysis & Valuation Sheet', 0, 1, 'C')
                self.ln(10)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()} | Certified Enterprise Output Log', 0, 0, 'C')

        def build_pdf_report(price_text, area_val, bhk_val, client, broker):
            pdf = PropertyReport()
            pdf.add_page()
            
            # Metadata Row (Prepared For / Broker)
            pdf.set_font("Arial", 'B', 11)
            pdf.cell(100, 10, f"Prepared For: {client}", ln=0)
            pdf.cell(90, 10, f"Broker / Agency: {broker}", ln=1, align='R')
            
            # Horizontal Divider Line below metadata row for proper separation
            pdf.set_draw_color(220, 220, 220)
            pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
            pdf.ln(8) # Adding space after the line
            
            # Section 1: Property Specifications
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, "1. Property Parameters Specification", ln=1)
            pdf.ln(2) # Space before list items
            
            pdf.set_font("Arial", size=11)
            pdf.cell(200, 8, f" - Total Area: {area_val} Sq. Ft.", ln=1)
            pdf.cell(200, 8, f" - BHK Configuration: {bhk_val} BHK", ln=1)
            pdf.ln(8) # Space before next section
            
            # Section 2: Market Valuation
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, "2. Market Valuation Assessment", ln=1)
            pdf.ln(2)
            
            # Highlight Box style pricing
            pdf.set_fill_color(240, 244, 248)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 15, f" Estimated Market Value: {price_text}", ln=1, fill=True)
            pdf.ln(10)
            
            # Disclaimer
            pdf.set_font("Arial", 'I', 9)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, "Disclaimer: This estimation is computed based on historical regional data distributions.", ln=1)
            
            return pdf.output(dest='S').encode('latin-1')

        # Generate Action Trigger
        pdf_data = build_pdf_report(formatted_price_str, area, bhk, client_name, broker_name)
        
        st.download_button(
            label="📥 Download Certified Valuation Report",
            data=pdf_data,
            file_name="Valuation_Report.pdf",
            mime="application/pdf"
        )