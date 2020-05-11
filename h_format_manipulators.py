import h_file_handling as hfh
pd = hfh.pd
np = hfh.np
def convert_iteman_format(file_name, destination_path ="", create_csv = True, pretest_cutoff = False):
    #   old format is of style
    #   gibberish first line
    #   correct answers
    #   number of options
    #   included
    #   start response entries


    old = hfh.get_lines(file_name)
    #   check if first line is omitted (it is sometimes in Karen data
    if old:
        adjust = 0
        if len(old[0]) < len(old[1]):
            # first line is junk
            adjust = 1
        correct = old[adjust]
        if len(correct) < 10:
            #todo: sloppy need better checking of file types
            return False
        number_of_possible_responses = old[1+adjust]
        included = old[2+adjust]
        control = []
        i = -1
        for answer in correct:
            if not answer == '\n' and not answer == ' ':
                i += 1
                if len(correct) == len(number_of_possible_responses) == len(included):
                    n = number_of_possible_responses[i]
                    inc = included[i]
                else:
                    n = 4
                    inc = included[i]

                #line = str(i + 1) + "," + answer + "," + str(n) + ",1," + inc + ",M \n"
                if pretest_cutoff:
                    if inc == 'Y' and pretest_cutoff:
                        line = [str(i+1), answer, str(n), '1', inc, 'M']
                        control.append(line)
                else:
                    line = [str(i + 1), answer, str(n), '1', inc, 'M']
                    control.append(line)
            #control = control[:-1]

        df = pd.DataFrame(control, index=None)

        if create_csv:
            control_file_path = destination_path + "/" + hfh.get_stem(file_name) + "_c.csv"
            df.to_csv(control_file_path, header = None, index=None)
            data_file_path = destination_path + "/" + hfh.get_stem(file_name)+"_f.txt"
            hfh.write_lines_to_text(old[4:], data_file_path)

        if is_valid_data(data_file_path):
            return True
        return False
    print("fed invalid file to convert to iteman", file_name)

def convert_folder_from_iteman_format(folder_path, destination_path ="", pretest_cutoff = False):
    files = hfh.get_all_file_names_in_folder(folder_path, extension='txt')
    for f in files:
        convert_iteman_format(f, destination_path, pretest_cutoff)


def convert_2016_format(file_name, destination_path = "", pretest_cutoff = False):
    #   of form:
    #   PT1   PT116MAR   BB... correct
    #   answers
    #   todo: rename this

    lines = hfh.get_lines(file_name)
    start_of_answers = lines[0].rfind(' ')
    answers = lines[0][start_of_answers+1:]

    ret = []

    for line in lines[2:]:
        # remove R or F at end
        last_entry = line[len(line)-2]
        if last_entry == 'R' or last_entry == 'F':
            line = line[:-5]+'\n'
        ret.append(line)
    name = hfh.get_stem(file_name)
    new = hfh.get_stem(destination_path + "/" + name)+"_f.txt"
    hfh.write_lines_to_text(ret, new)

    if is_valid_data(new):
        convert_answers_to_default_control(name, answers, destination_path, pretest_cutoff)
        return True
    return False


def convert_answers_to_default_control(file_name, answers, destination_path, cutoff_for_pretest = 175):
    new = []
    counter = 0
    for a in answers:
        counter += 1
        if not a == '\n':
            include = 'y'
            if counter > cutoff_for_pretest and cutoff_for_pretest:
                include = 'n'
            new.append(str(counter) + "," + a + ",4,1," + include + ",M\n")
    name = destination_path + "/" + hfh.get_stem(file_name)
    hfh.write_lines_to_text(new, name + "_c.csv")


def convert_first_line_answers_to_default_control_and_data(file_name, cutoff_for_not_included =175):
    #todo: handle cutoff for not included
    lines = hfh.get_lines(file_name)
    correct = lines[0]
    new = []
    counter = 0
    for a in correct:
        counter +=1
        if not a == '\n':
            include = 'y'
            if counter > cutoff_for_not_included:
                include ='n'
            new.append(str(counter)+","+a +",4,1,"+include+",M\n")

    name = hfh.get_stem(file_name)
    hfh.write_lines_to_text(new, name+"_c.csv")
    #   contains a random F at the end will test to see if it matters
    formatted = []
    for line in lines[2:]:
        formatted.append(line[:])
    hfh.write_lines_to_text(formatted, name + "_f.txt")


def convert_control_to_include_pretest(file_path):
    df = pd.read_csv(file_path)
    df.iloc[:,4] = 'Y'
    name = hfh.get_parent_folder(file_path) +"/"+ hfh.get_stem(file_path) + "_full.csv"
    df.to_csv(name, header = False, index = None)


def update_control_files_with_item_bank_key(path_to_item_bank_csv, path_to_control):
    #   todo: this is only good for the pt format... general application should be more robust.
    control_file_paths = hfh.get_all_file_names_in_foler(path_to_control, "csv")
    item_bank_df = pd.DataFrame(pd.read_csv(path_to_item_bank_csv))
    for file_path in control_file_paths:
        if not file_path == path_to_item_bank_csv:
            control_df = pd.DataFrame(pd.read_csv(file_path, header = None))
            name = hfh.get_stem(file_path)
            n = name[2]
            y = name[4:6]
            test_form = "20" + y + "_" + n
            form_relevant = item_bank_df.loc[item_bank_df['testFORM'] == test_form]
            testSeq = form_relevant["testSeq"]
            testSeq_c = control_df[0]
            for i in testSeq:
                if control_df[0].__contains__(i):
                  value = form_relevant[form_relevant["testSeq"] == i]["AccNum"]

            control_df[0] = np.where(control_df[0] == i, value, control_df[0])
            control_df.to_csv(file_path, index = False, header = 0)
            #remove_first_line_of_csv(file_path)


def create_mapping_from_Karen_test_data(file_path, destination_path = "", create_csv = False):
    lines = hfh.get_lines(file_path)
    #   assumes files are of format
    #   number. Name NN
    #   ....  where no lines will start with a number and then a dot other than my target lines
    #   number. Name NN
    #   name of file is stem(file_path)+_L.csv
    ret = [['form', 'test_id', 'subject', 'bank_id_number', 'bank_id']]
    for line in lines:
        if line[0].isnumeric():
            entry = line.split()
            test_name = hfh.get_stem(file_path)
            test_id = line[:line.index('.')]
            subject = entry[1]
            bank_id = entry[2]
            record = [test_name, test_id, subject, bank_id, subject+"_"+str(bank_id)]
            ret.append(record)
    df = pd.DataFrame(ret)

    if create_csv:
        name = hfh.get_stem(file_path) + "_L.csv"
        #df.sort_values(df[1])
        df.to_csv(destination_path + name, index = False, header = 0)

    return df


def process_karen_data(path_to_data_files, path_to_test_bank_files, destination_path, removed_suffix = "FullAmdin", suffix = "Test"):
    #   todo: this relies on the name Test for the bank information. It is assumed that the data file is the same
    #   todo: as the test file with the exception of the suffix. i.e. XXX12Data and XXX12Test
    data_files = hfh.get_all_file_names_in_folder(path_to_data_files,target_string='FullAdmin')
    test_bank_files = hfh.get_all_file_names_in_folder(path_to_test_bank_files,target_string='Test')
    for file in test_bank_files:
        create_mapping_from_Karen_test_data(file, True)

    test_bank_lists = []
    for file in test_bank_files:
        a = create_mapping_from_Karen_test_data(file, destination_path=destination_path, create_csv=True)
        test_bank_lists.append(a)

    for file in data_files:
        convert_iteman_format(file, destination_path=destination_path)

    for file in data_files:
        matching_control_name = destination_path + hfh.get_stem(file) + "_c.csv"
        matching_item_bank_name = destination_path + hfh.get_stem(file)[:-len(removed_suffix)]+ suffix + "_L.csv"
        merge_control_and_bank_info(matching_control_name, matching_item_bank_name)


def update_c_from_L_in_matched_folder(combined_folder):
    c_files = hfh.get_all_file_names_in_folder(combined_folder, target_string= "_c.csv")
    L_files = hfh.get_all_file_names_in_folder(combined_folder, target_string="_L.csv")
    #assert len(c_files) == len(L_files)
    for i in range(len(c_files)):
        c = c_files[i]
        L = L_files[i]
        merge_control_and_bank_info(c,L)


def create_L_files_from_item_bank_master(file, destination_path, test_form_col_name, test_sequence_col_name, bank_id_col_name, subject_separator = '_' ):
    df = pd.read_csv(file)
    forms = np.unique(df[test_form_col_name]).tolist()
    df["subject"] = 'NA'
    df["test_id"] = 'NA'

    for form in forms:
        form_df = df[df[test_form_col_name] == form]
        name = hfh.create_name(form,destination_path,'.csv', '_L')
        form_df.to_csv(name, index = False, header = 0)

def merge_control_and_bank_info(control_path, bank_path):
    control_df = hfh.get_df( control_path, header=0)
    bank_df = hfh.get_df(bank_path, header = 0)
    new = pd.merge(control_df, bank_df, on='sequence', how='right')
    new = new[['bank_id', 'key','number_of_options','group','include','scoring_option']]
    new.to_csv(control_path, header=None, index = False)

def convert_xCalibre_matrix_for_PCI(matrix_file, corresponding_control_file = False, id_length = 8):
    ret = []
    first_row = ""
    if corresponding_control_file:
        df = pd.read_csv(corresponding_control_file, header = None)
        item_ids = df.loc[:,0]
        for id in item_ids:
            first_row += id + ","
        first_row = first_row[:-1]
        ret = [first_row]
    lines = hfh.get_lines(matrix_file)
    for line in lines:
        ret_line = ""
        answer_string = line[id_length:]
        for c in answer_string:
            ret_line += c+','
        ret_line = ret_line[:-3]
        ret_line += '\n'
        ret.append(ret_line)
    name = hfh.get_stem(matrix_file)+"__c.csv"
    hfh.write_lines_to_text(ret, name)
    translated_name = hfh.get_stem(matrix_file)+"_T_c.csv"
    df = pd.read_csv(name, header = 0)
    df = df.T
    df.to_csv(translated_name, index = False)


def is_valid_data(file):
    #   id  responses
    lines = hfh.get_lines(file)
    if not lines:
        return 0
    length = len(lines[1])
    end_of_id = lines[1].find(" ")

    for line in lines[1:]:
        if not line.find(" ") == end_of_id:
            print(file + " is invalid because of spacing issues")
            return False
    return 1


def fix_format_of_data_file(file, destination):
    valid = is_valid_data(file)
    if valid:
        name = hfh.get_stem(file) + "_f.txt"
        hfh.copy_file_and_write_to_destination(file, destination, modified_name=name)
    if not valid:
        valid = convert_iteman_format(file, destination)
    if not valid:
        valid = convert_2016_format(file, destination)
    if not valid:
        print("could not convert " + file)
    return valid


def add_header_to_csvs(path_to_files, header, target_string):
    files = hfh.get_all_file_names_in_folder(path_to_files, target_string=target_string)
    for file in files:
        with open(file, 'r') as original:
            data = original.read()
        if not data[0] == header:
            with open(file, 'w') as modified: modified.write(header+'\n' + data)

def set_standard_id_length_in_data_files(path_to_files,target_length, spaces_between_id_and_data = 3):
    #assumes data has spaces
    files = hfh.get_all_file_names_in_folder(path_to_files, target_string='_f.txt')
    for file in files:
        new_lines = []
        lines = hfh.get_lines(file)
        for line in lines:
            first_space = line.find(' ')
            if first_space == -1:
                pass
            else:
                end_of_space = first_space+spaces_between_id_and_data
                remainder = line[end_of_space:]
                id_length = first_space+1
                _id = line[:first_space]
                new = line
                if  id_length < target_length:
                    new = ""
                    spacers_needed = target_length-id_length
                    for spacer in range(spacers_needed):
                        new += '_'
                    new += _id
                    for space in range(spaces_between_id_and_data):
                        new += ' '
                    new += remainder
                new_lines.append(new)
            #name = hfh.create_name(file,hfh.get_parent_folder(file)+"/formatted_data")
            hfh.write_lines_to_text(new_lines, file)


#set_standard_id_length_in_data_files("PT_IRT/PT_processed_data", 8)
#convert_xCalibre_matrix_for_PCI("PT_data/score_matrices/PT1_18_m.txt")
#process_karen_data("LCLE_IRT","LCLE_IRT","LCLE_IRT/processed_data/")
#merge_control_and_bank_info(a,b)
#path_to_files = "data_files"
#convertOldFormatToNew("LCLE_IRT/LCLEApr2019FullAdmin.txt")
#processNewFileFormat("LCLE_IRT/lcea1_18c.csv","LCLE_IRT/lcea1_18.txt")
#convert_first_line_answers_to_default_control_and_data(path_to_files+"/pt1_16_n.txt")
#create_control_files(path_to_files)
#update_control_files_with_item_bank_key("data_files/item_map.csv", "data_files")
#convert_2016_format("data_files/pt3_16.txt")

