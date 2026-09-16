import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="Life Insurance CRM", layout="wide")
st.title("🛡️ Life Insurance CRM & Client Advisor")

# Initialize session state for data including Location
if "client_data" not in st.session_state:
    st.session_state.client_data = pd.DataFrame(columns=[
        "Client ID", "Name", "Location", "Age", "Annual Income", "Sum Assured",
        "Annual Premium", "Policy Type", "Liabilities"
    ])

# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["📋 Client Records & Filters", "➕ Add & Manage Client", "💾 Export Data"])

# ----------------------------------------------------
# TAB 1: VIEW & FILTER CLIENTS (BY LOCATION & POLICY TYPE)
# ----------------------------------------------------
with tab1:
    st.subheader("Client Database & Smart Filters")
    
    # Excel / CSV Upload option
    uploaded_file = st.file_uploader("Upload Excel / CSV Data (Must include a 'Location' column)", type=["xlsx", "csv"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                st.session_state.client_data = pd.read_csv(uploaded_file)
            else:
                st.session_state.client_data = pd.read_excel(uploaded_file)
            st.success("File uploaded and loaded successfully!")
        except Exception as e:
            st.error(f"Error loading file: {e}")

    df = st.session_state.client_data

    if not df.empty:
        # Filter Layout Columns
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            if "Location" in df.columns and not df["Location"].dropna().empty:
                loc_options = list(df["Location"].dropna().unique())
                selected_loc = st.multiselect("Filter by Location", options=loc_options, default=loc_options)
            else:
                selected_loc = []

        with col_f2:
            if "Policy Type" in df.columns and not df["Policy Type"].dropna().empty:
                ptype_options = list(df["Policy Type"].dropna().unique())
                selected_ptype = st.multiselect("Filter by Policy Type", options=ptype_options, default=ptype_options)
            else:
                selected_ptype = []

        with col_f3:
            search_name = st.text_input("Search Client Name")

        # Apply Filters
        filtered_df = df.copy()
        if "Location" in filtered_df.columns and selected_loc:
            filtered_df = filtered_df[filtered_df["Location"].isin(selected_loc)]
        if "Policy Type" in filtered_df.columns and selected_ptype:
            filtered_df = filtered_df[filtered_df["Policy Type"].isin(selected_ptype)]
        if search_name:
            filtered_df = filtered_df[filtered_df["Name"].str.contains(search_name, case=False, na=False)]

        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No client records found. Upload an Excel file or add clients manually in Tab 2.")

# ----------------------------------------------------
# TAB 2: ADD, MANAGE & DELETE CLIENTS
# ----------------------------------------------------
with tab2:
    st.subheader("Add New Client & Policy Details")
    with st.form("add_client", clear_on_submit=True):
        cid = st.text_input("Client ID / Policy No.")
        name = st.text_input("Client Name")
        location = st.text_input("Location / Area / City")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=18, max_value=85, value=30)
            income = st.number_input("Annual Income", min_value=0, value=500000)
            sum_assured = st.number_input("Sum Assured", min_value=0, value=1000000)
        with col2:
            premium = st.number_input("Annual Premium", min_value=0, value=25000)
            ptype = st.selectbox("Policy Type", ["Term", "Endowment", "ULIP", "Pension"])
            liabilities = st.number_input("Liabilities", min_value=0, value=0)

        submitted = st.form_submit_button("Save Client Record")
        if submitted and cid and name:
            new_client = pd.DataFrame([{
                "Client ID": cid, "Name": name, "Location": location, "Age": age,
                "Annual Income": income, "Sum Assured": sum_assured, "Annual Premium": premium,
                "Policy Type": ptype, "Liabilities": liabilities
            }])
            st.session_state.client_data = pd.concat(
                [st.session_state.client_data, new_client], ignore_index=True
            ).drop_duplicates(subset=["Client ID"], keep="last")
            st.success(f"Added client record for {name} successfully!")

    st.divider()
    st.subheader("Delete Client Record")
    if not df.empty:
        to_delete = st.selectbox("Select Client ID to Delete", ["-- None --"] + list(df["Client ID"].astype(str).unique()))
        if st.button("Delete Record", type="primary"):
            if to_delete != "-- None --":
                st.session_state.client_data = df[df["Client ID"].astype(str) != to_delete]
                st.warning(f"Deleted record: {to_delete}")
                st.rerun()

# ----------------------------------------------------
# TAB 3: EXPORT DATA
# ----------------------------------------------------
with tab3:
    st.subheader("💾 Export & Backup CRM Data")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Updated CRM Data (CSV)", 
            csv, 
            "insurance_crm_data.csv", 
            "text/csv",
            type="primary"
        )
    else:
        st.info("No data available to download.")
      
