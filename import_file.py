import pandas as pd

class Import_File():
    def __init__(self, file):
        self.file = file

    def clean_file(self):
        #Read and open the master logistics file
        master_file = pd.read_excel(self.file, sheet_name="SMT LOAD LOG 2025")
        #Drop the duplicated Carrier column
        master_file = master_file.drop(columns=["Carrier"])  
        import_file_with_all_columns = master_file.rename(
            columns = {
                "Control #": "Control",                
                "Release": "Reference",
                "Pick/Ref #": "Trailer",
                " Rate": "Freight Rate", #Yes, there is supposed to be a space before 'Rate'
                "Carrier Code": "Carrier", 
                "Pick Date": "MR Date",
                "Del Date": "MS Appointment Date",
                "Del Time": "MS Appointment Earliest Time"
            }
        )
        column_list = [
            "MR Earliest Time",
            "Mr Latest Time",
            "MR Pickup Date",
            "MR Pickup Earliest Time",
            "MR Pickup Latest Time",
            "MS Requested",
            "MS Ordered",
            "MS Delivered",
            "MS Released",
            "MS Ready",
            "MS Scheduled Shipment",
            "MS Appointment Latest Time"
        ]
        
        #Makes Date = MR Date and cleans it of things like "ASAP" and deletes the time from the date
        time_pat = r"\b(\d{1,2}:\d{2}:\d{2})\b"
        import_file_with_all_columns["MR Date"] = pd.to_datetime(import_file_with_all_columns["MR Date"], errors="coerce")
        import_file_with_all_columns['MS Appointment Date'] = pd.to_datetime(import_file_with_all_columns["MS Appointment Date"], errors='coerce')
        import_file_with_all_columns["MS Appointment Earliest Time"] = import_file_with_all_columns["MS Appointment Earliest Time"].astype(str).str.extract(time_pat, expand=False)
        import_file_with_all_columns["MS Appointment Earliest Time"] = (
        pd.to_datetime(import_file_with_all_columns["MS Appointment Earliest Time"],
                   errors="coerce").dt.strftime("%I:%M %p"))
        
        #Copied MR Date's data to the "Date" column
        import_file_with_all_columns["Date"] = import_file_with_all_columns["MR Date"]

        #Narrows it down to which columns we want to keep and clears out the columns that are empty. For pd.to_numeric, it clears out anything that is not a number
        import_file = import_file_with_all_columns[["Control", "Date", "Trailer", "Freight Rate", "Carrier", "MR Date", "MS Appointment Date", "MS Appointment Earliest Time", "Reference"]]
        import_file = import_file[pd.to_numeric(import_file['Control'], errors='coerce').notna()]
        
        #Drop the empty rows for each of the listed columns
        cleaned_import_file = import_file.dropna(subset=["Control", "Date", "MR Date"], how='any')                                                       # -> datetime.time
        
        #Filled these columns with placeholder data
        cleaned_import_file["Mr Status"] = 'Status MR'
        cleaned_import_file["MS Status"] = 'Status MS'
        cleaned_import_file["MR Status"] = 'Status'
        #cleaned_import_file["Release"] = 'Release'

        for column in column_list:
            cleaned_import_file[column] = None

        desired_column_order = [
            "Control",
            "Date",
            "Trailer",
            "Freight Rate",
            "MR Status",
            "Reference",
            "Carrier",
            "MR Date",
            "MR Earliest Time",
            "Mr Latest Time",
            "Mr Status",
            "MR Pickup Date",
            "MR Pickup Earliest Time",
            "MR Pickup Latest Time",
            "MS Status",
            "MS Requested",
            "MS Ordered",
            "MS Delivered",
            "MS Released",
            "MS Ready",
            "MS Scheduled Shipment",
            "MS Appointment Date",
            "MS Appointment Earliest Time",
            "MS Appointment Latest Time"
        ]
        #Set the desired order
        cleaned_import_file = cleaned_import_file[desired_column_order]

        #Cleaned the Freight Rate column
        cleaned_import_file['Freight Rate'] = cleaned_import_file['Freight Rate'].astype(str)
        cleaned_import_file['Freight Rate'] = cleaned_import_file['Freight Rate'].str.extract(r'(\d+\.?\d*)') #Use .astype() to convert types
        cleaned_import_file['Freight Rate'] = cleaned_import_file['Freight Rate'].astype(float).round(2)

        #Only take the dates in the 'Dates' column from the previous 4 days and beyond.
        import_file_with_all_columns["Date"] = pd.to_datetime(import_file_with_all_columns["Date"], errors="coerce")
        cutoff_past = pd.Timestamp.today().normalize() - pd.Timedelta(days=4)
        cutoff_future = pd.Timedelta(days=21) + pd.Timestamp.today().normalize()
        correct_dates   = (cleaned_import_file['Date'] >= cutoff_past) & (cleaned_import_file['Date'] <= cutoff_future)
        cleaned_import_file = cleaned_import_file[correct_dates]

        #Converted all dates to datetime format
        pd.to_datetime(cleaned_import_file["Date"], errors='coerce')
        pd.to_datetime(cleaned_import_file["MR Date"], errors='coerce')
        cleaned_import_file["Date"] = cleaned_import_file['Date'].dt.strftime('%m/%d/%Y')
        cleaned_import_file["MR Date"] = cleaned_import_file['MR Date'].dt.strftime('%m/%d/%Y')
        cleaned_import_file["MS Appointment Date"] = cleaned_import_file['MS Appointment Date'].dt.strftime('%m/%d/%Y')

        return cleaned_import_file
