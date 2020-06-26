import core.h_file_handling as hfh
import core.h_format_manipulators as h
import core.h_user_input as u

pd = hfh.pd
os = hfh.os


def make_folders(name, parent_folder):
    try:
        project_folder = parent_folder + "/" + name
        os.mkdir(project_folder)
        os.mkdir(project_folder + "/data")
        os.mkdir(project_folder + "/processed_data")
        os.mkdir(project_folder + "/reports")
        os.mkdir(project_folder + "/xCalibreOutput")
        os.mkdir(project_folder + "/keys")
        return 1
    except:
        return 0
        print("Error creating folders. Confirm that they already exist.\n Folder: " + project_folder)


def ui_process_raw_data():
    name = u.get_string("What is the name of this data set? e.g. LEX", "Name data set")
    parent_folder = u.get_folder("Where would you like the data stored?")
    raw_data = u.get_folder("Where is the raw data?")
    process_raw_data(name, parent_folder, raw_data)


def process_raw_data(master_folder, raw_data):
    form_files = hfh.get_all_files(raw_data, extension="csv")
    data_files = hfh.get_all_files(raw_data, extension='txt')
    if not len(form_files) == len(data_files):
        #   assume that we are using xlsx files
        form_files = hfh.get_all_file_names_in_folder(raw_data, extension="xlsx")

    for file in form_files:
        name = hfh.get_stem(file) + '_raw_backup_form.' + hfh.get_extension(file)
        hfh.copy_file_and_write_to_destination(file, master_folder + "/data", modified_name=name)

    for file in data_files:
        name = hfh.get_stem(file) + '_raw_backup_data.' + hfh.get_extension(file)
        hfh.copy_file_and_write_to_destination(file, master_folder + "/data", modified_name=name)

    paired_files = pair_files(form_files, data_files)
    if paired_files:
        for pair in paired_files:
            pe_file = pair[0]
            data_file = pair[1]
            process_paired_files(pe_file, data_file, master_folder)


def find_month(file_name):
    months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]
    ret = []
    file_name = hfh.get_stem(file_name).upper()
    for month in months:
        full = file_name.find(month)
        if full > -1:
            ret.append(month)
        mon = month[:3]
        three = file_name.find(mon)
        if len(ret) == 0 and three > -1:
            ret.append(mon)
    if len(ret) > 1:
        return False
    else:
        return ret[0]


def find_year(file_name):
    #   check if month present
    m = find_month(file_name)
    mi = file_name.find(m)
    if mi > 2:
        #   check if month is preceded by two numbers
        possible_year = file_name[mi-2:mi]
        if possible_year.isdigit():
            return possible_year
    else:
        print("no month present in file" + file_name)
    #   returns the first two consecutive numbers
    number_index = []
    for i in range(len(file_name)):
        if file_name[i].isdigit():
            number_index.append(i)
    if int(number_index[0]+1) == int(number_index[1]):
        print("bad number finding")
        return file_name[number_index[0]] + file_name[number_index[1]]

    return False


def pair_files(pe_files, data_files, check = False):
    ret = []
    unhandled = []
    for pe_file in pe_files:
        pe_mon = find_month(pe_file)
        pe_year = find_year(pe_file)
        handled = 0
        for data_file in data_files:
            data_mon = find_month(data_file)
            data_year = find_year(data_file)
            if pe_mon == data_mon and pe_year == data_year:
                ret.append([pe_file, data_file])
                handled = 1
        if handled == 0:
            unhandled.append(pe_file)
    if len(pe_files) == len(data_files):
        if len(ret) == len(pe_files):
            return ret
        else:
            if not check:
                print("unhandled items in process data")
                return ret
            else:
                return False
    else:
        print("length of pe_files and data_files are unequal. Should not happen.")
        return False


def check_p_for_processed_data(master_path):
    pe_files = hfh.get_all_file_names_in_folder(master_path+'/processed_data', extension='csv')
    dt_files = hfh.get_all_file_names_in_folder(master_path+'/processed_data', extension='txt')
    pairs = pair_files(pe_files, dt_files)
    ret = True
    mismatched = []
    for pair in pairs:
        pe_file = pair[0]
        dt_file = pair[1]
        if not check_p(pe_file, dt_file):
            ret = False
            mismatched.append([pe_file, dt_file])
            print("Very low p value in " + pe_file)
            print("when matched with " + dt_file)
    return ret, mismatched


def check_p(pe_file, data_file, threshold = .4):
    pe_df = hfh.get_df(pe_file)
    d_df = h.convert_response_string_to_csv_and_get_df(data_file, id_length=8, number_of_spaces=3).T
    pe_df_t = pe_df.T.iloc[1]
    combined = d_df
    combined['correct'] = pe_df_t
    attempted = 0
    correctAnswers = 0

    for test_taker_id in range(d_df.shape[1]):
        #for item_id in range(pe_df_t):
        count = -1
        d = pe_df_t.size
        attempted += pe_df_t.size
        for item in pe_df_t:
            count += 1
            print(test_taker_id, item, count)
            test_response = d_df.iloc[count,test_taker_id]
            correct_answer = pe_df_t.iloc[count]
            if test_response == correct_answer:
                correctAnswers += 1
    p = correctAnswers/attempted
    if p < threshold:
        return False
    return True


def process_paired_files(pe_file, data_file, project_folder, select_Domain=False):
    #   todo: add in domain processing here so that sets without domain names are still separated
    if hfh.get_extension(pe_file) == 'xlsx':
        pe_df = hfh.get_df_from_xlsx(pe_file)
    else:
        pe_df = hfh.get_df(pe_file, header=0)

    pe_df.Position = pe_df.Position.astype(float)
    pe_df = pe_df.sort_values("Position", ascending=True, )

    pe_df = pe_df[["AccNum", 'CorrectAnswer', 'Domain']]
    #pe_df.Domain = pe_df.Domain.apply(str)
    #pe_df["AccNum"] = str(pe_df["AccNum"]) + "_" + pe_df["Domain"]

    if select_Domain:
        pe_df.loc[pe_df.Domain != select_Domain, 'include'] = 'N'

    pe_df = pe_df.drop(['Domain'], axis=1)

    pe_df['number_of_options'] = 4
    pe_df['group'] = 1
    pe_df["include"] = 'Y'
    pe_df['type'] = 'M'
    pe_df = pe_df[['AccNum', 'CorrectAnswer', 'number_of_options', 'group', 'include', 'type']]
    processed_path = project_folder + "/processed_data/"
    c_path = processed_path + hfh.get_stem(pe_file) + "_c.csv"
    pe_df.to_csv(c_path, header=False, index=False)
    h.convert_default_data_to_iteman(data_file, processed_path, new_name=hfh.get_stem(pe_file))
    return 1


def get_confirm_on_pairing(raw_data, ui = True):
    pe_files = hfh.get_all_files(raw_data, extension='csv')
    data_files = hfh.get_all_files(raw_data, extension='txt')
    xlsx_files = hfh.get_all_files(raw_data, extension='xlsx')
    confirm = True
    if ui:
        confirm_message = "We found " + str(len(pe_files)) + " csv pro exam files, " + str(len(xlsx_files)) + \
                          " +  excel pro exam files, and " + str(len(data_files)) + " data files.\n"
        confirm_message += "Is this the correct number for each?"
        confirm = u.get_yes_no_response("Matching", confirm_message)
    if confirm:
        return 1
    return 0

# ui_process_raw_data()
