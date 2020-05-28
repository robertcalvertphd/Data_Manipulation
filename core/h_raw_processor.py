import core.h_file_handling as hfh
import core.h_format_manipulators as h
import core.h_user_input as u
pd = hfh.pd
os = hfh.os


def make_folders(name, parent_folder):
    try:
        #a = os.path.abspath("")
        #b = a[:a.rfind("\\")]
        project_folder = parent_folder+"/"+name
        os.mkdir(project_folder)
        os.mkdir(project_folder + "/data")
        os.mkdir(project_folder + "/processed_data")
        os.mkdir(project_folder + "/reports")
        os.mkdir(project_folder + "/xCalibreOutput")
        os.mkdir(project_folder + "/keys")
    except:
        return 1
        print("Error creating folders. Confirm that they already exist.\n Folder: " + project_folder)


def ui_process_raw_data():
        name = u.get_string("What is the name of this data set? e.g. LEX", "Name data set")
        parent_folder = u.get_folder("Where would you like the data stored?")
        raw_data = u.get_folder("Where is the raw data?")
        process_raw_data(name, parent_folder, raw_data)


def process_raw_data(name, parent_folder, raw_data):
    a = make_folders(name, parent_folder)
    project_folder = parent_folder+"/"+name
    b = pair_data_and_pro_exam(raw_data, project_folder)
    return a,b

def process_paired_files(pe_file, data_file, project_folder, select_Domain = False):
    #   todo: add in domain processing here so that sets without domain names are still separated
    pe_df = hfh.get_df(pe_file,header=0)
    pe_df.Position = pe_df.Position.astype(float)
    pe_df = pe_df.sort_values("Position", ascending=True, )
    try:
        pe_df = pe_df[["AccNum",'CorrectAnswer','Domain']]
    except:
        return 0, "csv file is missing AccNum or CorrectAnswer or Domain."
        pe_df = pe_df[["AccNum", 'CorrectAnswer']]
#    pe_df["AccNum"] = pe_df["AccNum"] + "_" + pe_df["Domain"]

    pe_df['number_of_options'] = 4
    pe_df['group'] = 1
    pe_df["include"] = 'Y'

    if select_Domain:
        pe_df.loc[pe_df.Domain != select_Domain, 'include'] = 'N'

    pe_df['type'] = 'M'
    processed_path = project_folder+"/processed_data/"
    c_path = processed_path+hfh.get_stem(pe_file)+"_c.csv"
    pe_df.to_csv(c_path, header=False, index = False)
    h.convert_default_data_to_iteman(data_file, processed_path, new_name=hfh.get_stem(pe_file))
    return 1

def pair_files_by_month_and_year(pe_files, data_files, project_folder):
    for pe_file in pe_files:
        target = hfh.get_stem(pe_file)
        for data_file in data_files:
            if data_file.find(target)>-1:
                print(pe_file,"matches",data_file)
                #consider creating a log
                process_paired_files(pe_file,data_file,project_folder, select_Domain='01')

def pair_data_and_pro_exam(raw_data, project_folder, try_again_option=False):
    pe_files = hfh.get_all_file_names_in_folder(raw_data, extension='csv')
    data_files = hfh.get_all_file_names_in_folder(raw_data, extension='txt')
    confirm_message = "We found " +str(len(pe_files)) + " pro exam files and " + str(len(data_files)) + " data files.\n"
    confirm_message += "Is this the correct number for each?"
    confirm = u.get_yes_no_response("Matching", confirm_message)
    if confirm:
        pair_files_by_month_and_year(pe_files,data_files, project_folder)
        return 1
    else:
        try_again = u.get_yes_no_response("Error","No files found. Would you like to try again?")
        if try_again and try_again_option:
            ui_process_raw_data()
        else:
            return 0

        #print("suggest they change their stuff and exit.")

#ui_process_raw_data()
