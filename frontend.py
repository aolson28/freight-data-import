import streamlit as st
import pandas as pd
import io
from import_file import Import_File

class Frontend:
    def run(self):
        st.title("🧹 Rimas Data Cleaner")
        st.write("Upload a CSV or Excel file. This app will remove any rows with empty values.")

        uploaded_file = st.file_uploader("📁 Drag and drop your file here", type=["csv", "xlsx"])

        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1]

            # Read the file
            if file_type == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_type == "xlsx":
                df = pd.read_excel(uploaded_file, sheet_name="SMT Load Log 2025")
            else:
                st.error("Unsupported file format!")
                return

            st.subheader("🔍 Preview of Original Data")
            st.write(df)

            try:
                processor = Import_File(uploaded_file)
                cleaned_import_file = processor.clean_file()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return

            st.subheader("✅ Cleaned Data (Rows with empty cells removed)")
            st.write(cleaned_import_file)

            towrite = io.BytesIO()
            if file_type == "csv":
                cleaned_import_file.to_csv(towrite, index=False)
                file_extension = ".csv"
            else:
                cleaned_import_file.to_excel(towrite, index=False, engine='openpyxl')
                file_extension = ".xlsx"

            towrite.seek(0)
            st.download_button(
                label="📥 Download Cleaned File",
                data=towrite,
                file_name=f"cleaned_file{file_extension}",
                mime="application/octet-stream"
            )
