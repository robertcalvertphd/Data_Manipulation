import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import core.h_format_manipulators as hf

def getInt(prompt, _max, _min=1):
    while 1:
        try:
            ret = int(input(prompt))
            if _max >= ret >= _min:
                return ret
            print('invalid response: out of range')
        except (ValueError, Exception):
            print('invalid syntax: integer only')


def select_from_list(prompt, options):
    print(prompt)
    for i in range(len(options)):
        print(i + 1, ":", options[i])
    selectionID = getInt(prompt, len(options)) - 1
    return selectionID

def get_all_data_files(prompt, string_prompt = "what is a common naming component in your data files?"):
    files = get_data_files(prompt, string_prompt)
    verified = get_yes_no_response("Data Files", "Those parameters returned " + str(len(files)) + " files. Is this correct?")
    while not verified:
        add_more = get_yes_no_response("Add files with different naming component", "Would you like to add other files?")
        if add_more:
            new_files = get_data_files(prompt)
            for file in new_files:
                if not files.__contains__(file):
                    files.append(file)
            verified = get_yes_no_response("Data Files", "We found " + str(len(files)) + " files. Is this correct?")
        else:
            exit = get_yes_no_response("Exit", "Would you like to exit?")
            if exit:
                return 0
    return files

def get_data_files(prompt = "Where are your data files located?", string_prompt = "what is a common naming component in your data files?"):
    print("select folder where data files are located.")
    root = tk.Tk()
    root.withdraw()
    file_path = ""
    target_string = simpledialog.askstring("Input", string_prompt,parent=root)
    if target_string == None:
        target_string = False
    while file_path == "":
        file_path = filedialog.askdirectory(title = prompt)
    folders =  hf.get_all_sub_folders(file_path)
    file_names = []
    for f in folders:
        files = hf.get_all_file_names_in_folder(f, target_string= target_string)
        for file in files:
            file_names.append(file)

    return file_names


def get_yes_no_response(title, message):
    root = tk.Tk()
    root.withdraw()
    MsgBox = tk.messagebox.askquestion(title, message,icon='warning')
    if MsgBox == 'yes':
        return 1
    else:
        return 0


def get_folder(title = "Select folder where data or folders of data are located.", required = True):
    root = tk.Tk()
    root.withdraw()
    if required:
        file_path = ""
        while file_path == "":
            file_path = filedialog.askdirectory(title=title)
    else:
        file_path = filedialog.askdirectory(title=title)
    return file_path

def get_file(title = "Select file."):
    root = tk.Tk()
    root.withdraw()
    file_path = ""
    while file_path == "":
        file_path = filedialog.askopenfilename(title=title)
    return file_path

def get_string(message, title = "Input"):
    root = tk.Tk()
    root.withdraw()
    ret = simpledialog.askstring(title, message, parent=root)
    return ret