import core.h_file_handling as hfh
import core.h_user_input as ui
pd = hfh.pd
np = hfh.np

#   todo: ensure that all helpers throw errors when invalid arguments are passed to them
#   todo: institute a return True without error and a check for True


def convert_iteman_format(file_name, destination_path ="", create_csv = True, pretest_cutoff = False):
    if file_name == "LCLE_IRT/data/AB Forms by Admin/LCLE2018ABForms/Jan2018AB/LCLEJan2018BTest.txt":
        print("target")
    #   old format is of style
    #   gibberish first line
    #   correct answers
    #   number of options
    #   included
    #   start response entries
    old = hfh.get_lines(file_name)

    #   check if first line is omitted
    if old:
        adjust = 0
        if len(old[0]) < len(old[1]):
            # first line is junk
            adjust = 1
        correct = old[adjust]
        if len(correct) < 10:
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
                        if i > pretest_cutoff:
                            line = [str(i+1), answer, str(n), '1', 'N', 'M']
                        else: line = [str(i + 1), answer, str(n), '1', 'Y', 'M']
                        control.append(line)
                else:
                    line = [str(i + 1), answer, str(n), '1', inc, 'M']
                    control.append(line)

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


def convert_default_data_to_iteman(file_name, processed_data_path, new_name = False):
    if processed_data_path[-1] == '/':
        processed_data_path = processed_data_path[:-1]
    lines = hfh.get_lines(file_name)
    ret = []
    for line in lines[2:]:
        line = set_standard_id_length_for_line(line,8)
        ret.append(line)

    path = processed_data_path + "/" + hfh.get_stem(file_name) + "_f.txt"
    if new_name:
        path = processed_data_path + "/" + hfh.get_stem(new_name) + "_f.txt"

    hfh.write_lines_to_text(ret, path)


def convert_first_line_answers_to_default_control_and_data(file_name):
    #todo: handle cutoff for not included
    lines = hfh.get_lines(file_name)
    correct = lines[0]
    new = []
    counter = 0
    for a in correct:
        counter +=1
        if not a == '\n':
            include = 'y'
            new.append(str(counter)+","+a +",4,1,"+include+",M\n")

    name = hfh.get_stem(file_name)
    hfh.write_lines_to_text(new, name+"_c.csv")
    #   contains a random F at the end will test to see if it matters
    formatted = []
    for line in lines[2:]:
        formatted.append(line[:]) #no clue why : is here perhaps I will remove it.
    hfh.write_lines_to_text(formatted, name + "_f.txt")


def convert_response_string_to_csv_and_get_df(file, id_length, number_of_spaces, create_csv= False):
    df_rows = []
    lines = hfh.get_lines(file)
    for line in lines:
        df_row = []
        beginning = id_length + number_of_spaces
        FR_space = line.rfind('F')
        if FR_space == -1:
            FR_space = line.rfind('R')
        if FR_space > -1:
            stripped_line = line[beginning:FR_space]
        else:
            stripped_line = line[beginning:]
        for c in stripped_line:
            df_row.append(c)
        df_rows.append(df_row)

    df = pd.DataFrame(df_rows)
    if create_csv:
        name = hfh.create_name(file, modificaiton="_d_")
        df.to_csv(name)
    return df


def convert_csv_response_string_to_raw_with_bogus_header(file, id_spaces = 3):
    lines = hfh.get_lines(file)
    ret = ["BOGUS \n\n"]
    for line in lines:
        id_loc = line.find(',')
        id = line[:id_loc]
        spaces = ""
        for i in range(id_spaces):
            spaces += ' '
        ret_line = id + spaces
        ret_line += line[id_loc:].replace(',','')
        ret.append(ret_line)
    hfh.write_lines_to_text(ret,file+"_m")


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


def create_mapping_from_Karen_test_data(file_path, destination_path = "", create_csv = False, add_underscore = False):
    lines = hfh.get_lines(file_path)
    #   assumes files are of format
    #   number. Name NN
    #   ....  where no lines will start with a number and then a dot other than my target lines
    #   number. Name NN
    #   name of file is stem(file_path)+_L.csv
    ret = []
    if lines:
        for line in lines:
            if line[0].isnumeric():
                entry = line.split()
                test_name = hfh.get_stem(file_path)
                test_id = line[:line.index('.')]
                subject = entry[1]
                bank_id = entry[2]
                underscore = ""
                if add_underscore:
                    underscore = "_"
                record = [test_name, test_id, subject, bank_id, subject+underscore+str(bank_id)]
                ret.append(record)

        df = pd.DataFrame(ret)
        df.columns = ['form', 'test_id', 'subject', 'bank_id_number', 'bank_id']

    else:
        print(file_path + "does not contain lines.")
    if create_csv:
        name = hfh.get_stem(file_path)[:8]
        #df.sort_values(df[1])
        file_name = destination_path+ "/" + name + "_L.csv"
        df.to_csv(file_name, index = False, header = 0)

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
    # check that id is not already merged
    sequence_value = control_df['sequence'][1]
    if not sequence_value == str(2):
        print(control_path, "expected sequence = 2 got", sequence_value+", file was not merged. Check for repairs.")
        valid = is_valid_control(control_path)
        if valid: print(control_path + " is a valid control file.")

    else:
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


def remove_header_and_blank_lines(control_path):
    lines = hfh.get_lines(control_path)
    ret = []
    for line in lines:
        remove = False
        if line == '\n':
            remove = True
        split_line = line.split(',')
        if len(split_line)>2:
            a = split_line[2]
            if not split_line[2].isnumeric():
                remove = True
        if not remove:
            ret.append(line)
    hfh.write_lines_to_text(ret, control_path)


def convert_control_to_include_pretest(control_file):
    lines = hfh.get_lines(control_file)
    ret = []
    for line in lines:
        split_line = line.split(',')
        ret_line = split_line[0]+"," +split_line[1]+"," +split_line[2]+"," +split_line[3]+ ",Y,"+split_line[5]
        ret.append(ret_line)
    dot = control_file.rfind(".")
    name = control_file[:dot]+"_cf.csv"
    hfh.write_lines_to_text(ret, name)


def convert_delimited_control(control_file, destination_path, delimiter = '\t', remove_version = False,remove_header = True):
    lines = hfh.get_lines(control_file)
    ret = []
    changed = False
    csv_detected = False
    if len(lines)>1:
        if remove_header:
            check_for_header(control_file, True)
        for line in lines:
            # check for delimiter
            split_line = line.split(delimiter)
            if len(split_line)> 1:
                changed = True
                ret_line = split_line[0] + ","
                if remove_version:
                    version_location = ret_line.rfind('V')
                    if version_location > 0:
                        ret_line = ret_line[:version_location]+','

                for i in split_line[1:]:
                    ret_line += i + ','
                ret_line=ret_line[:-1]
                ret.append(ret_line)
            else:
                # check to see if file is comma delimited
                split_line = line.split(',')
                # if comma delimited and removing version get bank id and remove version
                if len(split_line)>1 and remove_version:
                    csv_detected = True
                    ret_line = split_line[0]
                    version_location = ret_line.rfind('V')
                    if version_location > 0:
                        ret_line = ret_line[:version_location] + ','
                        for i in split_line[1:]:
                            ret_line += i + ','
                        ret_line = ret_line[:-1]
                        ret.append(ret_line)

                else:
                    ret.append(line)

        if csv_detected:
            print("Comma delimited identified. ID_BANK version identifier removed" )
        if not changed:
            print(control_file + " asked to be delimiter converted but did not contain target delimiter")

        hfh.write_lines_to_text(ret, destination_path+'/'+hfh.get_stem(control_file))
        return True
    else:
        print(control_file, " is an empty file and asked to be converted")
        return False


def is_valid_control(file):
    lines = hfh.get_lines(file)
    valid = True
    for line in lines:
        valid = False
        # check for header line and remove
        split_line = line.split(',')
        if not len(split_line) == 4:
            valid = False
        else:
            if len(split_line)>2:
                if not split_line[2].isnumeric():
                    valid = False
            # check for empty line and remove
            if len(split_line) == 0:
                valid = False
            # check for bank id
            if len(split_line[0])<4:
                valid = True
            # check for entries in four points

    if not valid: print("invalid control file attempting repair", file)
    remove_header_and_blank_lines(file)
    return valid


def convert_delimited_to_iteman(file, destination_path, delimiter = ','):
    #verify is CSV
    ret = []
    lines = hfh.get_lines(file)
    if len(lines)>0:
        if len(lines[0].split(delimiter)) >1:
            #is CSV
            for line in lines:
                new_line = ""
                line = line.split(delimiter)
                id_handled = False
                non_answer_characters = False
                for i in line:
                    if not id_handled:
                        i+='   '
                        id_handled = True
                    if not i == 'Y' and not i == 'M':
                        new_line+=i
                ret.append(new_line)
        if not non_answer_characters:
            print(file, "non answer character in data response string. It was removed.")

        name = hfh.create_name(hfh.get_stem(file),destination_path,'txt','_f')
        hfh.write_lines_to_text(ret, name)
        return True
    else:
        print(file, "is empty")
        return False


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


def add_header_to_csvs(path_to_files, header, target_string = ".", single_file = False):
    files = []
    if single_file:
        files.append(path_to_files)
    else:
        files = hfh.get_all_file_names_in_folder(path_to_files, target_string=target_string)
    for file in files:
        with open(file, 'r') as original:
            data = original.read()
        if not data[0] == header:
            with open(file, 'w') as modified: modified.write(header+'\n' + data)


def has_acceptable_correct_percentage(xCalibre_report_path, id_length = 8, debug = True):
    files = hfh.get_all_files(xCalibre_report_path,"Matrix")
    for file in files:
        total = 0
        correct = 0
        lines = hfh.get_lines(file)
        for line in lines:
            scores = line[id_length:-1]
            for x in scores:
                total += 1
                try:
                    correct += int(x)
                except:
                    pass
        percent_correct = round(correct/total*100,4)
        if debug: print(file, percent_correct)
        if percent_correct < 50:
            print(file, "has low correct rate.")
            return False
    return True


def create_key_df_from_csv(file_path):
    #   assumes format
    #   Position,Domain,AccNum,UseCode,CorrectAnswer,Content Area,...
    #   1,02,LLE669,Operational,C,0202,44,,56,0.18,,,Bank,InUse,1,,,101,AUG19(P),,,0,1,0,No,,1, ,5/13/2019,

    df = hfh.get_df(file_path, header = 0)
    ret = []
    test_ids = df['Position'].tolist()
    bank_ids = df['AccNum'].tolist()
    for i in range(len(test_ids)):
        form = hfh.get_stem(file_path)
        test_id = test_ids[i]
        bank_id = bank_ids[i]
        subject = bank_id[:3]
        bank_id_number = bank_id[3:]
        ret.append([form, test_id, subject, bank_id_number, bank_id])
    df = pd.DataFrame(ret)
    df.columns = ['form', 'test_id', 'subject', 'bank_id_number', 'bank_id']
    name = hfh.create_name(hfh.get_stem(file_path),"LPCC_IRT/keys/L_files","csv",'_L')
    df.to_csv(name, index=None)
    return df


def check_for_header(file, remove_if_present, interactive = True):
    lines = hfh.get_lines(file)
    has_header = False
    if len (lines)>1:
        #   assumes that a header line has a different length than data
        #   assumes delimited by comma
        line0 = len(lines[0])
        line1 = len(lines[1])
        if not line0 == line1:
            if interactive:
                has_header = ui.get_yes_no_response("Remove Header?\n",str("Is this a header?" + lines[0] + "?"))
            else:
                has_header = True
                print(file,line0,'\n', "header automatically removed. Confirm that it had a header")
        #   todo: when this fails fix it
    if remove_if_present and has_header:
        lines = lines[1:]
        hfh.write_lines_to_text(lines, file)
    if has_header:
        return True
    return False


def set_standard_id_length_for_line(line, target_length, spaces_between_id_and_data = 3):
    first_space = line.find(' ')
    if first_space == -1:
        pass
    else:
        end_of_space = first_space + spaces_between_id_and_data
        remainder = line[end_of_space:]
        id_length = first_space
        _id = line[:first_space]
        new = line
        if id_length < target_length:
            new = ""
            spacers_needed = target_length - id_length
            for spacer in range(spacers_needed):
                new += '_'
            new += _id
            for space in range(spaces_between_id_and_data):
                new += ' '
            new += remainder
        return new


def set_standard_id_length_in_data_files(path_to_files,target_length, spaces_between_id_and_data = 3):
    #assumes data has spaces
    files = hfh.get_all_file_names_in_folder(path_to_files, target_string='_f.txt')
    for file in files:
        new_lines = []
        lines = hfh.get_lines(file)
        for line in lines:
           new_lines.append(set_standard_id_length_for_line(line, target_length))
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