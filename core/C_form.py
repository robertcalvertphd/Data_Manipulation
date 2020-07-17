import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import core.h_raw_processor as hr
import core.h_2p_report_analysis as h2p
import core.e_handler as e
import core.h_file_handling as hfh

import os


class GUI:
    def __init__(self):
        browse_col = 1
        button_col = 5
        button_width = 20
        text_col = 2
        text_col_span = 3
        text_width = 70
        label_width = 10
        #   todo:   add scroll bar
        #   todo:   log errors
        #   todo:   validate all steps and confirm action
        self.log = []

        self.EH = e.ErrorHandler()
        self.gui = tk.Tk()
        self.gui.geometry("800x400")
        self.gui.title("OPES IRT xCalibreOutput Summary Program")

        self.MessageBox = tk.Text(self.gui, wrap=tk.WORD)
        self.MessageBox.grid(row=6, rowspan=50, columnspan=5)
        self.d_procedure()

        self.raw_data_path = tk.StringVar()
        self.L_raw_data = tk.Label(self.gui, text="Raw Data Path", width = label_width)
        self.L_raw_data.grid(row=0, column=0 )
        self.E_raw_data_path = tk.Entry(self.gui, textvariable=self.raw_data_path, width = text_width)
        self.E_raw_data_path.grid(row=0, column=text_col, columnspan = text_col_span)

        self.b_raw_data = ttk.Button(self.gui, text="Browse Folder", command=self.get_raw_data, width = button_width)
        self.b_raw_data.grid(row=0, column=browse_col)

        self.report_path = tk.StringVar()
        self.a2 = tk.Label(self.gui, text="Report Location")
        self.a2.grid(row=1, column=0)
        self.btnFind2 = ttk.Button(self.gui, text="Browse Folder", command=self.get_report, width = button_width)
        self.btnFind2.grid(row=1, column=browse_col)
        self.E_report_location = tk.Entry(self.gui, textvariable=self.report_path, width = text_width)
        self.E_report_location.grid(row=1, column=text_col, columnspan = text_col_span)

        self.report_name = tk.StringVar()
        self.a3 = tk.Label(self.gui, text="Report Name")
        self.a3.grid(row=3, column=0)
        self.E_report_name = tk.Entry(self.gui, textvariable=self.report_name, width = text_width)
        self.E_report_name.grid(row=3, column=text_col, columnspan = text_col_span)

        self.c2 = tk.Button(self.gui, text="Process Data", command=self.process_data, width = 20)
        self.c2.grid(row=3, column=button_col)

        self.b_report = tk.Button(self.gui, text="Create Reports", command=self.create_reports, width = 20)
        self.b_report.grid(row=6, column=5)

        self.c3 = tk.Button(self.gui, text="Example Data File", command=self.d_data_file_format, width = button_width)
        self.c3.grid(row=18, column=button_col)

        self.c4 = tk.Button(self.gui, text="Example Data form file", command=self.d_form_file_format, width = button_width)
        self.c4.grid(row=19, column=button_col)

        self.c5 = tk.Button(self.gui, text="Procedure", command=self.d_procedure, width = button_width)
        self.c5.grid(row=20, column = button_col)

        self.error_log = tk.Button(self.gui, text="Log", command=self.d_log, width = button_width)
        self.error_log.grid(row=21, column=button_col)

        self.parent_path = ""
        self.master_folder = ""
        self.master_name = ""
        self.raw_path = ""
        self.report_destination_path = ""

        #self.d_general_instructions()
        default = True
        if default:

            raw = r"G:/LICENSING EXAMINATION/Robert/data/PSY/"
            report_location = r"C:/Users/ERRCALV/Desktop"
            name = "PSY2"
            #hfh.os.remove(report_location + '/' + name)
            self.raw_data_path.set(raw)
            self.report_path.set(report_location)
            self.report_name.set(name)
        self.gui.mainloop()

    def reset_paths(self):
        self.parent_path = ""
        self.master_folder = ""
        self.master_name = ""
        self.raw_path = ""
        self.report_destination_path = ""

    def d_error_log(self):
        self.MessageBox.configure(state='normal')
        self.clear_text()
        quote = ""
        for i in self.EH.error_log:
            quote += i+"\n"
        self.MessageBox.insert(tk.END, quote)
        self.MessageBox.configure(state='disabled')

    def d_data_file_format(self):
        self.MessageBox.configure(state='normal')
        self.clear_text()
        quote = """XYZYYMON   ABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDAB
12345   ABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDAB   F
12346   ABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDAB   F
12347   ABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDABCDAB   R
"""
        self.MessageBox.insert(tk.END, quote)
        self.MessageBox.configure(state='disabled')

    def d_form_file_format(self):
        print("form format call")
        self.MessageBox.configure(state='normal')
        self.clear_text()
        quote = "Position,Domain,AccNum,UseCode,CorrectAnswer,Rubric1,Rubric2,CognitiveLevel,.\n4,01,LEX05,Operational,A,01,T119,2019-09,98,0.05,,,Bank,InUse,2,2019-09,,K316,..5,01,LEX06,Operational,A,01,T119,,63,0.01,,,Bank,InUse,4,,,K316,ETHICS 6,,,0,1..\n6,01,LEX08,Operational,A,01,T119,,49,0.09,,,Bank,OldVersion,0,,,K316,ETHICS 8,..\n7,01,LEX10,Operational,A,01,T120,2019-09,85,-0.03,,,Bank,InUse,4,2019-09,,K317.."
        self.MessageBox.insert(tk.END, quote)
        self.MessageBox.configure(state='disabled')

    def d_procedure(self):
        print("form format call")
        self.MessageBox.configure(state='normal')
        self.clear_text()
        quote = "1: Setup Raw Data file with .txt data and .csv forms. Use examples if needed.\n"
        quote = "To create the csv open proexam, select the form, right click on the form, "
        quote += "2: Browse folders for raw data and report location and name report.\n"
        quote += "3: Click process data. This creates a folder with processed data for xCalibreOutput.\n"
        quote += "4: Run xCalibreOutput reports and put results in xCalibreOutput created in step 3.\n"
        quote += "5: Ensure New Report Location is still the correct folder and name is correct.\n"
        quote += "6: Click create reports."
        self.MessageBox.insert(tk.END, quote)
        self.MessageBox.configure(state='disabled')

    def d_log(self, reverse = False):
        print("dlog called")
        #log is a list and will read from most recent down. Currently no scroll is implemented
        self.MessageBox.configure(state='normal')
        self.clear_text()

        quote = ""
        if reverse:
            log_len = len(self.log)
            i = log_len - 1
            for j in range(log_len):
                quote += self.log[i] + "\n"
                i -= 1
        else:
            for entry in self.log:
                quote+= entry + '\n'

        self.MessageBox.insert(tk.END, quote)
        self.MessageBox.configure(state='disabled')

    def d_general_instructions(self):
        self.MessageBox.configure(state='normal')
        self.clear_text()
        quote = "RAW DATA PATH is a folder that contains .txt files for data, .csv files from proexam.\n\n"
        quote += "The NEW REPORT LOCATION is simply where the report will be stored on your computer. You may make a new folder"
        quote += " or choose a folder that already exists.A new set of folders will be created in that location and will "
        quote += "have the name you chose for the NEW REPORT NAME.\n\n"
        quote += "NEW REPORT NAME is a folder name. Follow standard naming conventions.\n\n"
        self.MessageBox.insert(tk.END, quote)
        self.MessageBox.configure(state='disabled')

    def clear_text(self):
        self.MessageBox.delete('1.0', tk.END)

    def get_raw_data(self):
        folder_selected = filedialog.askdirectory()
        self.raw_data_path.set(folder_selected)

    def get_report(self):
        folder_selected = filedialog.askdirectory()
        self.report_path.set(folder_selected)

    def create_reports(self, remove_rtf = True):
        print("report call")
        self.log.clear()
        self.b_report.config(state=tk.DISABLED)
        self.gui.after(200, lambda: self.b_report.config(state=tk.NORMAL))

        valid = self.pd_validate_inputs(xCalibre_required=True)
        parent_path = self.report_path.get()
        master_name = self.report_name.get()
        master_path = parent_path + "/" + master_name
        xCalibre_path = master_path + "/xCalibreOutput"
        if valid:
            report_log = str("report creation successful \nreports:" + master_path+"/reports" )
            self.log.append(report_log)
            results = h2p.create_master_file(master_folder= master_path)
            files = hfh.get_all_files(xCalibre_path, extension='rtf')
            for file in files:
                os.remove(file)
            self.d_log()
            self.log.clear()
            return results
        else:
            self.log.append("Invalid function call.")
            self.d_log()
            self.log.clear()
            return 0

    def process_data(self):
        self.log.clear()
        self.log.append("PROCESS DATA\n _______________")
        # check for xlsx instead of csvs
        valid = self.pd_validate_paths()
        if valid:
            self.pd_validate_year_mon()
            self.log.append("VALIDATED DATES")
            self.d_log()
            self.l
        if valid:
            valid = self.pd_validate_inputs(raw_required=True)
            self.log.append("VALIDATED INPUTS")
            self.d_log()

        if valid:
            self.log.append("BEGININNING PROCESS OF RAW DATA")
            self.d_log()

            hr.process_raw_data(self.master_folder,self.raw_path)
            check = hr.check_p_for_processed_data(self.master_folder)
            if not check[0]:
                self.log.append("Mismatched or inaccurate control files")
                for mismatch in check[1]:
                    self.log.append("Mismatch with " + mismatch[0])
                    self.log.append("and " + mismatch[1])

            self.log.append("FINISHED\n____________")
            self.d_log()
            self.log.clear()

        else:
            self.log.append("Error in process_data")
            self.d_log()
            self.log.clear()

    def pd_validate_inputs(self, raw_required = False, xCalibre_required = False):
        parent_path = self.report_path.get()
        raw_path = self.raw_data_path.get()
        valid = 1
        master_folder = parent_path
        if not os.path.isdir(parent_path):
            self.log.append("Path invalid:" + master_folder)
            valid = 0

        #   assume that parent path is a project folder e.g. ...Desktop/LEX
        if self.report_name.get == "":
            report_path = parent_path + "/reports"
            xCalibre_path = parent_path + "/xCalibreOutput"
            master_name = master_folder[master_folder.rfind('/')+1:]

        else:
            master_name = self.report_name.get()
            master_folder = parent_path + "/" + master_name
            report_path = master_folder + "/reports"
            xCalibre_path = master_folder + "/xCalibreOutput"
            #self.report_name.set(hfh.get_parent_folder(master_folder))
        if raw_required and raw_path == "":
            self.log.append("raw path required")
            valid = 0

        if raw_required and valid:
            data_files = hfh.get_all_files(raw_path, extension='txt')
            form_files = hfh.get_all_files(raw_path, extension='csv')
            if len(form_files) == 0:
                #   assume just xlsx files
                form_files = hfh.get_all_file_names_in_folder(raw_path, extension='xlsx')

            if data_files is None or form_files is None:
                valid = 0
                if data_files is None:
                    self.log.append("data files are missing")
                if form_files is None:
                    self.log.append("form files are missing")
            if valid:
                if len(data_files) == 0 or len(form_files) == 0:
                    valid = 0
                    self.log.append("Raw data does not contain both txt and csv files.")
                    self.log.append("Raw Path:" + raw_path)
                if not len(data_files) == len(form_files):
                    valid = 0
                    self.log.append("There are unequal data and form files in raw data.")
                    self.log.append("Found " + str(len(data_files)) + " data files and " + str(len(form_files)) + " form files.")
                    d = "data:\n"
                    fm = "form:\n"
                    for f in data_files:
                        d+= f+'\n'
                    for f in form_files:
                        fm+=f+'\n'
                    self.log.append(d)
                    self.log.append(fm)
                    self.log.append("Raw Path:" + raw_path)

                for file in data_files:
                    can_read = hfh.file_is_readable(file)
                    if not can_read:
                        valid = 0
                        self.log.append("read access denied for data file:" + file)

                for file in form_files:
                    can_read = hfh.file_is_readable(file)
                    if not can_read:
                        valid = 0
                        self.log.append("read access denied for form file:" + file)
                    if valid:
                        if hfh.get_extension(file) == 'csv':
                            test_df = hfh.get_df(file,header=0)
                        else:
                            test_df = hfh.get_df_from_xlsx(file)
                        required_columns = ["Domain", "AccNum", "CorrectAnswer"]
                        for column in required_columns:
                            if column not in test_df.columns:
                                self.log.append("______")
                                self.log.append(file)
                                self.log.append("pro exam file does not contain " + column + ".\nReset form and then download from Proexam.")
                                self.log.append("______")
                                valid = 0

        if valid:
            master_report_path = master_folder + "/" + 'reports'
            if not os.path.isdir(master_report_path):
                self.log.append("Path does not contain reports folder. \nPath:" + master_folder)
                valid = 0

        if valid:
            if not os.path.isdir(xCalibre_path) and xCalibre_required:
                self.log.append("Path does not contain xCalibreOutput folder. \nPath:" + master_folder)
                valid = 0

        if valid:
            if os.path.isfile(master_name):
                self.log.append("Folder name is a file. It should be a directory, i.e. no extension.")
                valid = 0

        if valid and raw_required:
            if not hr.get_confirm_on_pairing(raw_path):
                valid = 0
                self.log.append("User said pairing was wrong.")

        if valid and xCalibre_required:
            stats_files = hfh.get_all_file_names_in_folder(xCalibre_path, target_string="Stats")
            if len(stats_files) == 0:
                self.log.append("Report path does not contain xCalibreOutput reports")
                valid = 0

            #   check that can write reports
            aggregate_name = report_path + "/" + master_name + "_aggregate_.csv"
            complete_name = report_path + "/" + master_name + "_complete_.csv"

            if os.path.isfile(aggregate_name):
                if not hfh.file_is_writable(aggregate_name):
                    valid = 0
                    self.log.append("No access to " + aggregate_name)
            if os.path.isfile(complete_name):
                if not hfh.file_is_writable(complete_name):
                    valid = 0
                    self.log.append("No access to " + complete_name)

        if valid:
            self.log.append("validated call")
            self.d_log()
        return valid

    def pd_validate_paths(self):
        parent_path = self.report_path.get()
        master_name = self.report_name.get()
        raw_path = self.raw_data_path.get()
        master_folder = parent_path + "/" + master_name
        valid = 1
        if not os.path.isdir(parent_path):
            self.log.append("Path invalid:" + master_folder)
            valid = 0
        else:
            if os.path.isdir(master_folder):
                self.log.append("Folders already exist")
            else:
                f = hr.make_folders(master_name, parent_path)
                if f:
                    self.log.append("Folders created: " + master_folder)
                else:
                    self.log.append("ERROR: Folders not created. Confirm location and permission.")
        self.parent_path = parent_path
        self.master_name = master_name
        self.raw_path = raw_path
        self.master_folder = master_folder
        return valid

    def pd_validate_year_mon(self):
        pe_files = hfh.get_all_file_names_in_folder(self.raw_path, extension='csv')
        data_files = hfh.get_all_file_names_in_folder(self.raw_path, extension='txt')
        xlsx_files = hfh.get_all_file_names_in_folder(self.raw_path, extension='xlsx')
        valid = 1
        for file in xlsx_files:
            month = hr.find_month(file)
            year = hr.find_year(file)
            if not month:
                valid = 0
                self.log.append("No month identifier in " + file)
            if not year:
                valid = 0
                self.log.append("No year identifier in " + file)

        for file in pe_files:
            month = hr.find_month(file)
            year = hr.find_year(file)
            if not month:
                valid = 0
                self.log.append("No month identifier in " + file)
            if not year:
                valid = 0
                self.log.append("No year identifier in " + file)

        for file in data_files:
            month = hr.find_month(file)
            year = hr.find_year(file)
            if not month:
                valid = 0
                self.log.append("No month identifier in " + file)
            if not year:
                valid = 0
                self.log.append("No year identifier in " + file)
        
        return valid

def main():
    GUI()

if __name__ == "__main__":
    main()
