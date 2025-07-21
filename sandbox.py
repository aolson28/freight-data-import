import pandas as pd
import datetime as dt

#TODO Add.strip() if necessary, and add empty columns

master_file = pd.read_excel(r'C:\Users\jacob.mazelin\Documents\All_Code\Freight_Data_Import\2025 SMT Logistics Master.xlsx', sheet_name="SMT Load Log 2025")
master_file = master_file.drop(columns=["Carrier"])  
import_file_with_all_columns = master_file.rename(
    columns = {
        "Control #": "Control",
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
time_pat = r"\b(\d{1,2}:\d{2}:\d{2})\b"
#Makes Date = MR Date and cleans it of things like "ASAP" and deletes the time from the date
import_file_with_all_columns["MR Date"] = pd.to_datetime(import_file_with_all_columns["MR Date"], errors="coerce")
import_file_with_all_columns["MS Appointment Earliest Time"] = import_file_with_all_columns["MS Appointment Earliest Time"].astype(str).str.extract(time_pat, expand=False)
import_file_with_all_columns["MS Appointment Earliest Time"] = (
pd.to_datetime(import_file_with_all_columns["MS Appointment Earliest Time"],
            format="%H:%M:%S",
            errors="coerce")
.dt.time
)
import_file_with_all_columns["Date"] = import_file_with_all_columns["MR Date"]
#Narrows it down to which columns we want to keep and clears out the columns that are empty. For pd.to_numeric, it clears out anything that is not a number
import_file = import_file_with_all_columns[["Control", "Date", "Trailer", "Freight Rate", "Carrier", "MR Date", "MS Appointment Date", "MS Appointment Earliest Time"]]
import_file = import_file[pd.to_numeric(import_file['Control'], errors='coerce').notna()]

cleaned_import_file = import_file.dropna(subset=["Control", "Date", "MR Date"], how='any')                                                       # -> datetime.time

cleaned_import_file["MR Freight Status"] = 'Status MR'

cleaned_import_file["MS Status"] = 'Status MS'

cleaned_import_file["MR Status"] = 'Status'

for column in column_list:
    cleaned_import_file[column] = None

desired_column_order = [
    "Control",
    "Date",
    "Trailer",
    "Freight Rate",
    "MR Status",
    "Carrier",
    "MR Date",
    "MR Earliest Time",
    "Mr Latest Time",
    "MR Freight Status",
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

cleaned_import_file = cleaned_import_file[desired_column_order]
cleaned_import_file['Freight Rate'] = cleaned_import_file['Freight Rate'].astype(str)
cleaned_import_file['Freight Rate'] = cleaned_import_file['Freight Rate'].str.extract(r'(\d+\.?\d*)') #Use .astype() to convert types
cleaned_import_file['Freight Rate'] = cleaned_import_file['Freight Rate'].astype(float).round(2)
#print(cleaned_import_file['Date'])
import_file_with_all_columns["Date"] = pd.to_datetime(import_file_with_all_columns["Date"], errors="coerce")
cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=4)
correct_dates   = cleaned_import_file['Date'] >= cutoff
cleaned_import_file = cleaned_import_file[correct_dates]

