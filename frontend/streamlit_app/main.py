"""
AI Prescription Analyzer - Streamlit Frontend
Main application for prescription analysis and drug interaction detection.
"""

import streamlit as st
import requests
import pandas as pd
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List

# Configure page
st.set_page_config(
    page_title="AI Prescription Analyzer",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PrescriptionAnalyzerApp:
    def __init__(self):
        """Initialize the Streamlit application."""
        if 'user_token' not in st.session_state:
            st.session_state.user_token = None
        if 'user_email' not in st.session_state:
            st.session_state.user_email = None
        if 'prescriptions' not in st.session_state:
            st.session_state.prescriptions = []
    
    def authenticate_user(self, email: str, password: str) -> bool:
        """Authenticate user with backend API."""
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.user_token = data["access_token"]
                st.session_state.user_email = email
                return True
            return False
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict:
        """Get authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {st.session_state.user_token}",
            "Content-Type": "application/json"
        }
    
    def show_login_page(self):
        """Display login/registration page."""
        st.markdown('<h1 class="main-header">🏥 AI Prescription Analyzer</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Welcome to your healthcare guardian")
            st.write("Analyze prescriptions, detect drug interactions, and get personalized medication insights.")
            
            tab1, tab2 = st.tabs(["Login", "Register"])
            
            with tab1:
                with st.form("login_form"):
                    email = st.text_input("Email")
                    password = st.text_input("Password", type="password")
                    login_button = st.form_submit_button("Login")
                    
                    if login_button:
                        if self.authenticate_user(email, password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
            
            with tab2:
                with st.form("register_form"):
                    reg_email = st.text_input("Email", key="reg_email")
                    reg_password = st.text_input("Password", type="password", key="reg_password")
                    full_name = st.text_input("Full Name")
                    age = st.number_input("Age", min_value=1, max_value=120, value=30)
                    role = st.selectbox("Role", ["patient", "doctor", "pharmacist"])
                    
                    register_button = st.form_submit_button("Register")
                    
                    if register_button:
                        try:
                            response = requests.post(
                                f"{API_BASE_URL}/api/v1/auth/register",
                                json={
                                    "email": reg_email,
                                    "password": reg_password,
                                    "full_name": full_name,
                                    "age": age,
                                    "role": role
                                }
                            )
                            
                            if response.status_code == 200:
                                st.success("Registration successful! Please login.")
                            else:
                                st.error("Registration failed")
                        except Exception as e:
                            st.error(f"Registration error: {str(e)}")
    
    def show_dashboard(self):
        """Display main dashboard."""
        st.sidebar.markdown(f"### Welcome, {st.session_state.user_email}")
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Dashboard", "Upload Prescription", "My Prescriptions", "Drug Interactions", "AI Chatbot", "Pharmacy Finder", "Profile"]
        )
        
        if st.sidebar.button("Logout"):
            st.session_state.user_token = None
            st.session_state.user_email = None
            st.rerun()
        
        # Main content
        if page == "Dashboard":
            self.show_dashboard_content()
        elif page == "Upload Prescription":
            self.show_upload_page()
        elif page == "My Prescriptions":
            self.show_prescriptions_page()
        elif page == "Drug Interactions":
            self.show_interactions_page()
        elif page == "AI Chatbot":
            self.show_chatbot_page()
        elif page == "Pharmacy Finder":
            self.show_pharmacy_page()
        elif page == "Profile":
            self.show_profile_page()
    
    def show_dashboard_content(self):
        """Display dashboard overview."""
        st.markdown('<h1 class="main-header">📊 Dashboard</h1>', unsafe_allow_html=True)
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Active Prescriptions", "3", "1")
        
        with col2:
            st.metric("Safety Score", "85%", "5%")
        
        with col3:
            st.metric("Interactions Detected", "1", "0")
        
        with col4:
            st.metric("Next Refill", "5 days", "-1")
        
        st.markdown("---")
        
        # Recent activity
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📋 Recent Prescriptions")
            recent_data = {
                "Medication": ["Amoxicillin", "Ibuprofen", "Lisinopril"],
                "Dosage": ["500mg", "200mg", "10mg"],
                "Status": ["Active", "Active", "Active"],
                "Next Dose": ["2 hours", "6 hours", "Tomorrow"]
            }
            df = pd.DataFrame(recent_data)
            st.dataframe(df, use_container_width=True)
        
        with col2:
            st.markdown("### ⚠️ Safety Alerts")
            st.markdown("""
            <div class="warning-box">
                <strong>Moderate Interaction:</strong> Amoxicillin may interact with alcohol.
                Avoid alcohol during treatment.
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="success-box">
                <strong>All Clear:</strong> No severe interactions detected in current medications.
            </div>
            """, unsafe_allow_html=True)
        
        # Medication timeline
        st.markdown("### 📈 Medication Timeline")
        
        # Create sample timeline data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        timeline_data = pd.DataFrame({
            'Date': dates,
            'Amoxicillin': [3] * 7 + [0] * 23,
            'Ibuprofen': [2] * 30,
            'Lisinopril': [1] * 30
        })
        
        fig = px.line(timeline_data, x='Date', y=['Amoxicillin', 'Ibuprofen', 'Lisinopril'],
                      title='Daily Medication Intake')
        st.plotly_chart(fig, use_container_width=True)
    
    def show_upload_page(self):
        """Display prescription upload page."""
        st.markdown('<h1 class="main-header">📤 Upload Prescription</h1>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📷 Upload Image", "✍️ Manual Entry"])
        
        with tab1:
            st.markdown("### Upload prescription image or PDF")
            
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['jpg', 'jpeg', 'png', 'pdf'],
                help="Upload a clear image of your prescription"
            )
            
            if uploaded_file:
                # Display uploaded image
                if uploaded_file.type.startswith('image'):
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Prescription", use_column_width=True)
                
                if st.button("Process Prescription", type="primary"):
                    with st.spinner("Processing prescription with AI..."):
                        # Simulate OCR processing
                        st.success("✅ Prescription processed successfully!")
                        
                        # Mock OCR results
                        st.markdown("### 🔍 Extracted Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Raw Text:**")
                            st.text_area("", "Amoxicillin 500mg\n3 times daily\nfor 7 days\nDr. Smith", height=100)
                        
                        with col2:
                            st.markdown("**Structured Data:**")
                            extracted_data = {
                                "Medication": "Amoxicillin",
                                "Dosage": "500mg",
                                "Frequency": "3 times daily",
                                "Duration": "7 days",
                                "Doctor": "Dr. Smith"
                            }
                            for key, value in extracted_data.items():
                                st.write(f"**{key}:** {value}")
                        
                        # Safety analysis
                        st.markdown("### 🛡️ Safety Analysis")
                        safety_col1, safety_col2 = st.columns(2)
                        
                        with safety_col1:
                            st.metric("Safety Score", "85%", "Good")
                        
                        with safety_col2:
                            st.metric("Confidence", "92%", "High")
                        
                        # Interactions
                        st.markdown("**Interactions Found:**")
                        st.warning("⚠️ Moderate: May increase drowsiness with alcohol")
                        
                        # Save button
                        if st.button("💾 Save to My Prescriptions"):
                            st.success("Prescription saved successfully!")
        
        with tab2:
            st.markdown("### Enter prescription details manually")
            
            with st.form("manual_prescription"):
                col1, col2 = st.columns(2)
                
                with col1:
                    medication_name = st.text_input("Medication Name*")
                    dosage = st.text_input("Dosage (e.g., 500mg)*")
                    frequency = st.text_input("Frequency (e.g., 3 times daily)*")
                
                with col2:
                    duration = st.text_input("Duration (e.g., 7 days)")
                    doctor_name = st.text_input("Doctor Name")
                    notes = st.text_area("Additional Notes")
                
                submitted = st.form_submit_button("💊 Add Prescription", type="primary")
                
                if submitted and medication_name and dosage and frequency:
                    # Simulate API call
                    st.success("✅ Prescription added successfully!")
                    
                    # Show safety analysis
                    st.markdown("### 🛡️ Quick Safety Check")
                    st.info("✅ No critical interactions detected")
                    st.warning("ℹ️ Recommended to take with food")
    
    def show_prescriptions_page(self):
        """Display user's prescriptions."""
        st.markdown('<h1 class="main-header">💊 My Prescriptions</h1>', unsafe_allow_html=True)
        
        # Mock prescription data
        prescriptions = [
            {
                "id": "rx_001",
                "medication": "Amoxicillin",
                "dosage": "500mg",
                "frequency": "3x daily",
                "duration": "7 days",
                "doctor": "Dr. Smith",
                "date": "2024-01-01",
                "status": "Active"
            },
            {
                "id": "rx_002", 
                "medication": "Ibuprofen",
                "dosage": "200mg",
                "frequency": "As needed",
                "duration": "14 days",
                "doctor": "Dr. Johnson",
                "date": "2024-01-05",
                "status": "Active"
            }
        ]
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Active", "Completed", "Expired"])
        with col2:
            doctor_filter = st.selectbox("Doctor", ["All", "Dr. Smith", "Dr. Johnson"])
        with col3:
            date_range = st.date_input("Date Range", value=[])
        
        # Prescription cards
        for prescription in prescriptions:
            with st.expander(f"💊 {prescription['medication']} - {prescription['dosage']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Frequency:** {prescription['frequency']}")
                    st.write(f"**Duration:** {prescription['duration']}")
                
                with col2:
                    st.write(f"**Doctor:** {prescription['doctor']}")
                    st.write(f"**Date:** {prescription['date']}")
                
                with col3:
                    st.write(f"**Status:** {prescription['status']}")
                    if st.button(f"🔍 Analyze", key=f"analyze_{prescription['id']}"):
                        st.info("Analysis feature will be implemented")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button(f"✏️ Edit", key=f"edit_{prescription['id']}"):
                        st.info("Edit functionality coming soon")
                with btn_col2:
                    if st.button(f"📋 Refill", key=f"refill_{prescription['id']}"):
                        st.info("Refill request sent")
                with btn_col3:
                    if st.button(f"🗑️ Delete", key=f"delete_{prescription['id']}"):
                        st.warning("Delete confirmation required")
    
    def show_interactions_page(self):
        """Display drug interactions checker."""
        st.markdown('<h1 class="main-header">⚠️ Drug Interactions</h1>', unsafe_allow_html=True)
        
        st.markdown("### Check for drug interactions in your medications")
        
        # Current medications
        st.markdown("#### Current Medications")
        current_meds = ["Amoxicillin 500mg", "Ibuprofen 200mg", "Lisinopril 10mg"]
        
        for i, med in enumerate(current_meds):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {med}")
            with col2:
                if st.button(f"Remove", key=f"remove_{i}"):
                    st.info("Medication removed")
        
        # Add new medication
        st.markdown("#### Add Medication for Checking")
        new_med = st.text_input("Enter medication name")
        if st.button("Check Interactions"):
            if new_med:
                st.success(f"Checking interactions for {new_med}")
                
                # Mock interaction results
                st.markdown("### 🔍 Interaction Analysis")
                
                # Severity levels
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Severe", "0", "🟢")
                with col2:
                    st.metric("Moderate", "1", "🟡")
                with col3:
                    st.metric("Minor", "2", "🟠")
                
                # Detailed interactions
                st.markdown("#### Detailed Analysis")
                
                st.warning("""
                **Moderate Interaction:** Ibuprofen + New Medication
                - **Effect:** May increase risk of gastrointestinal bleeding
                - **Recommendation:** Monitor for symptoms, take with food
                - **Action:** Consult your doctor if experiencing stomach pain
                """)
                
                st.info("""
                **Minor Interaction:** Amoxicillin + New Medication  
                - **Effect:** May reduce effectiveness slightly
                - **Recommendation:** Take medications 2 hours apart
                - **Action:** Follow dosing schedule carefully
                """)
        
        # Safety recommendations
        st.markdown("### 💡 General Safety Tips")
        st.markdown("""
        - Always inform healthcare providers about all medications
        - Keep an updated medication list
        - Don't stop medications without consulting your doctor
        - Report any unusual side effects immediately
        """)
    
    def show_chatbot_page(self):
        """Display AI chatbot interface."""
        st.markdown('<h1 class="main-header">🤖 AI Health Assistant</h1>', unsafe_allow_html=True)
        
        st.markdown("Ask questions about your medications, side effects, and general health advice.")
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! I'm your AI health assistant. How can I help you with your medications today?"}
            ]
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI Assistant:** {message['content']}")
        
        # Chat input
        user_input = st.text_input("Ask your question:", key="chat_input")
        
        if st.button("Send") and user_input:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Generate AI response (mock)
            ai_response = self.generate_ai_response(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            st.rerun()
        
        # Quick questions
        st.markdown("### Quick Questions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("What are the side effects of Amoxicillin?"):
                self.ask_quick_question("What are the side effects of Amoxicillin?")
        
        with col2:
            if st.button("How should I take Ibuprofen?"):
                self.ask_quick_question("How should I take Ibuprofen?")
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Drug interaction between medications"):
                self.ask_quick_question("Can you check interactions between my medications?")
        
        with col4:
            if st.button("Dosage recommendations"):
                self.ask_quick_question("Are my current dosages appropriate for my age?")
    
    def generate_ai_response(self, question: str) -> str:
        """Generate AI response (mock implementation)."""
        responses = {
            "side effects": "Common side effects of Amoxicillin include nausea, vomiting, diarrhea, and stomach pain. Contact your doctor if you experience severe symptoms.",
            "take ibuprofen": "Take Ibuprofen with food or milk to reduce stomach irritation. Don't exceed 800mg per dose or 3200mg per day unless directed by your doctor.",
            "interactions": "Based on your current medications, I found one moderate interaction. Ibuprofen may increase the risk of stomach issues when combined with certain medications.",
            "dosage": "Your current dosages appear appropriate for adults. However, always consult your healthcare provider for personalized recommendations."
        }
        
        question_lower = question.lower()
        for key, response in responses.items():
            if key in question_lower:
                return response
        
        return "I understand your question about medications. For specific medical advice, please consult with your healthcare provider. I can help with general information about drug interactions and medication schedules."
    
    def ask_quick_question(self, question: str):
        """Handle quick questions."""
        st.session_state.chat_history.append({"role": "user", "content": question})
        response = self.generate_ai_response(question)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    def show_pharmacy_page(self):
        """Display pharmacy finder."""
        st.markdown('<h1 class="main-header">🏪 Find Nearby Pharmacies</h1>', unsafe_allow_html=True)
        
        # Search input
        location = st.text_input("Enter your location (address, zip code, or 'use my location')")
        search_radius = st.slider("Search radius (miles)", 1, 25, 5)
        
        if st.button("🔍 Find Pharmacies"):
            if location:
                st.success(f"Searching for pharmacies within {search_radius} miles of {location}")
                
                # Mock pharmacy data
                pharmacies = [
                    {
                        "name": "CVS Pharmacy",
                        "address": "123 Main St, Your City",
                        "distance": "0.5 miles",
                        "phone": "(555) 123-4567",
                        "hours": "8 AM - 10 PM",
                        "rating": 4.2,
                        "in_stock": ["Amoxicillin", "Ibuprofen"]
                    },
                    {
                        "name": "Walgreens",
                        "address": "456 Oak Ave, Your City", 
                        "distance": "1.2 miles",
                        "phone": "(555) 234-5678",
                        "hours": "7 AM - 11 PM",
                        "rating": 4.0,
                        "in_stock": ["Lisinopril", "Ibuprofen"]
                    },
                    {
                        "name": "Local Pharmacy",
                        "address": "789 Pine St, Your City",
                        "distance": "2.1 miles", 
                        "phone": "(555) 345-6789",
                        "hours": "9 AM - 8 PM",
                        "rating": 4.8,
                        "in_stock": ["Amoxicillin", "Lisinopril", "Ibuprofen"]
                    }
                ]
                
                for pharmacy in pharmacies:
                    with st.expander(f"🏪 {pharmacy['name']} - {pharmacy['distance']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"📍 **Address:** {pharmacy['address']}")
                            st.write(f"📞 **Phone:** {pharmacy['phone']}")
                            st.write(f"⏰ **Hours:** {pharmacy['hours']}")
                        
                        with col2:
                            st.write(f"⭐ **Rating:** {pharmacy['rating']}/5")
                            st.write(f"💊 **Your meds in stock:** {', '.join(pharmacy['in_stock'])}")
                        
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        with col_btn1:
                            if st.button(f"📞 Call", key=f"call_{pharmacy['name']}"):
                                st.info(f"Calling {pharmacy['phone']}")
                        with col_btn2:
                            if st.button(f"🗺️ Directions", key=f"directions_{pharmacy['name']}"):
                                st.info("Opening directions...")
                        with col_btn3:
                            if st.button(f"💊 Check Stock", key=f"stock_{pharmacy['name']}"):
                                st.info("Checking medication availability...")
    
    def show_profile_page(self):
        """Display user profile."""
        st.markdown('<h1 class="main-header">👤 Profile</h1>', unsafe_allow_html=True)
        
        # Profile information
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://via.placeholder.com/150", caption="Profile Picture")
            if st.button("Upload New Photo"):
                st.info("Photo upload feature coming soon")
        
        with col2:
            st.markdown("### Personal Information")
            with st.form("profile_form"):
                full_name = st.text_input("Full Name", value="John Doe")
                email = st.text_input("Email", value=st.session_state.user_email, disabled=True)
                age = st.number_input("Age", value=35, min_value=1, max_value=120)
                phone = st.text_input("Phone", value="+1 (555) 123-4567")
                
                # Emergency contact
                st.markdown("#### Emergency Contact")
                emergency_name = st.text_input("Emergency Contact Name", value="Jane Doe")
                emergency_phone = st.text_input("Emergency Contact Phone", value="+1 (555) 987-6543")
                
                if st.form_submit_button("Update Profile"):
                    st.success("Profile updated successfully!")
        
        # Medical information
        st.markdown("### Medical Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Allergies")
            allergies = st.text_area("Known allergies", value="Penicillin, Peanuts")
            
        with col2:
            st.markdown("#### Chronic Conditions")
            conditions = st.text_area("Chronic conditions", value="Hypertension")
        
        # Preferences
        st.markdown("### Notification Preferences")
        col1, col2 = st.columns(2)
        
        with col1:
            email_reminders = st.checkbox("Email reminders", value=True)
            sms_reminders = st.checkbox("SMS reminders", value=True)
        
        with col2:
            interaction_alerts = st.checkbox("Interaction alerts", value=True)
            refill_reminders = st.checkbox("Refill reminders", value=True)
        
        if st.button("Save Preferences"):
            st.success("Preferences saved!")

def main():
    """Main application entry point."""
    app = PrescriptionAnalyzerApp()
    
    if st.session_state.user_token:
        app.show_dashboard()
    else:
        app.show_login_page()

if __name__ == "__main__":
    main()