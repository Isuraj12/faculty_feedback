import streamlit as st
import pandas as pd
import os
import re
from io import BytesIO



def extract_faculty_feedback(file_obj):
    filename = file_obj.name.replace("feedback_", "").replace(".xlsx", "")

    # Flexible date extraction
    match = re.search(r"(.+?)\s*(?:\(|\s)(\d{2}\.\d{2}\.\d{4})(?:\)|\s|$)", filename)
    if match:
        faculty_name = match.group(1).strip()
        session_date = match.group(2)
    else:
        faculty_name = filename
        session_date = None

    df = pd.read_excel(file_obj, header=None)

    averages = []
    for row in df.values:
        if isinstance(row[-1], (float, int)) and not pd.isna(row[-1]):
            averages.append(row[-1])

    if averages:
        avg_out_of_5 = sum(averages) / len(averages)
        avg_out_of_10 = avg_out_of_5 * 2
    else:
        avg_out_of_10 = None

    return {
        "Faculty Name": faculty_name,
        "Session Date": session_date,
        "Average Rating (out of 10)": round(avg_out_of_10, 2) if avg_out_of_10 else None
    }

def process_feedback(files):
    results = [extract_faculty_feedback(file) for file in files]
    return pd.DataFrame(results)

def export_to_excel(df):
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output



st.set_page_config(page_title="Faculty Feedback", layout="centered")

st.title(" Faculty Feedback Summary")
st.write("Upload multiple feedback Excel files to get Faculty Name, Date, and Average Rating out of 10.")

uploaded_files = st.file_uploader("Upload Excel Files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    df = process_feedback(uploaded_files)

    if not df.empty:
        st.subheader("Summary Table")
        st.dataframe(df)

        
        excel_file = export_to_excel(df)
        st.download_button(
            label="Download Combined Feedback (Excel)",
            data=excel_file,
            file_name="faculty_feedback_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No valid ratings found in the uploaded files.")
else:
    st.info("Please upload one or more Excel files.")
