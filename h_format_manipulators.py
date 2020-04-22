import os
import pandas as pd
import numpy as np


def get_all_files_in_directory_and_sub_directories_starting_with_stem(directory_path, stem):
    pass
    #   todo: this may be necessary for clean implementation without relying on users...


def get_lines(file_name):  # candidate for general helper file
    lines = []
    with open(file_name) as f:
        for line in f: lines.append(line)
    return lines

def get_df(path_to_csv, header = None, index = None):
    return pd.DataFrame(pd.read_csv(path_to_csv, header = header), index = index)
def write_lines_to_text(lines, file_path):  # candidate for general helper file
    with open(file_path, "w") as file:
        file.writelines(lines)


def remove_first_line_of_csv(file_path):
    lines = get_lines(file_path)
    write_lines_to_text(lines[1:], file_path)


def get_stem(name_with_extension):  # candidate for general helper file
    try:
        i = name_with_extension.index('.')
    except:
        print("er")
    s = name_with_extension.rfind('/')
    if s == -1: s = 0
    ret = name_with_extension[s+1:i]
    return ret


def get_extension(name_with_extension):
    i = name_with_extension.find('.')
    if i > -1:
        return name_with_extension[i+1:]


def process_old_format(file_name, correctDataLine=1, firstDataLine=4, removeIncompleteSets=False):
    lines = []
    with open(file_name) as f:
        for line in f: lines.append(line)
    correct = lines[correctDataLine]
    data = []
    for line in lines[firstDataLine:]:
        currentLine = line
        #   find first space in line
        firstSpace = currentLine.find(" ")
        id = currentLine[:firstSpace]
        responseString = currentLine[firstSpace + 3:]
        if responseString.find(" ") and removeIncompleteSets:
            print("RESPONSE REMOVED DUE TO MISSINGNESS", id)
        else:
            listOfGradedResponses = []
            for i in range(len(correct) - 1):
                if responseString[i] == correct[i]:
                    listOfGradedResponses.append(1)
                else:
                    listOfGradedResponses.append(0)
            data.append([id, listOfGradedResponses])


def processNewFileFormat(controlFile, dataFile):
    correct = pd.read_csv(controlFile, delimiter=',', header=None)[1].tolist()
    ids = []
    correctLists = []
    with open(dataFile) as f:
        for line in f:
            correctList = []
            firstSpace = line.find(" ")
            responseString = line[firstSpace + 3:]
            id = line[:firstSpace]

            for i in range(len(correct)):
                if correct[i] == responseString[i]:
                    correctList.append(1)
                else:
                    correctList.append(0)
            ids.append(id)
            correctLists.append(correctList)

    df = pd.DataFrame(correctLists, index=None).T
    df.to_csv('list2.csv', index=False)
    return [ids, correctList]


def convertOldFormatToNew(file_name, destination_path = "", create_csv = True, exclude_pre_test = True):
    #   old format is of style
    #   gibberish first line
    #   correct answers
    #   number of options
    #   included
    #   start response entries

    old = get_lines(file_name)
    correct = old[1]
    number_of_possible_responses = old[2]
    included = old[3]
    control = []


    i = -1
    for answer in correct:
        if len(correct) == len(number_of_possible_responses) == len(included):
            i += 1
            n = number_of_possible_responses[i]
            inc = included[i]
        else:
            n = 4
            inc = included[i]

        #line = str(i + 1) + "," + answer + "," + str(n) + ",1," + inc + ",M \n"
        if exclude_pre_test:
            if inc == 'Y' and exclude_pre_test:
                line = [str(i+1), answer, str(n), '1', inc, 'M']
                control.append(line)
        else:
            line = [str(i + 1), answer, str(n), '1', inc, 'M']
            control.append(line)
    #control = control[:-1]
    df = pd.DataFrame(control, index=None)

    if create_csv:
        control_file_path = destination_path + get_stem(file_name) + "_c.csv"
        df.to_csv(control_file_path, header = False, index=None)
        #write_lines_to_text(control, destination_path + get_stem(file_name)+"_c.csv")
        data_file_path = destination_path + get_stem(file_name)+"_f.txt"
        write_lines_to_text(old[4:], data_file_path)
    return df

def convert_2016_format(file_name, destination_path = ""):
    #   of form:
    #   PT1   PT116MAR   BB... correct
    #   answers
    #   todo: rename this

    lines = get_lines(file_name)
    start_of_answers = lines[0].rfind(' ')
    answers = lines[0][start_of_answers+1:]

    ret = [answers]

    for line in lines[2:]:
        # remove R or F at end
        line = line[:-5]+'\n'
        ret.append(line)
    new = get_stem(destination_path + file_name)+"_n.txt"
    write_lines_to_text(ret, new)


def convert_first_line_answers_to_default_control_and_data(file_name, cutoff_for_not_included =175):
    lines = get_lines(file_name)
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

    name = get_stem(file_name)
    write_lines_to_text(new, name+"_control.csv")
    #   contains a random F at the end will test to see if it matters
    formatted = []
    for line in lines[2:]:
        formatted.append(line[:])
    write_lines_to_text(formatted, name + "_formatted.txt")


def get_all_files_names_in_folder(folder_path, extension = False, target_string = False):
    list = os.listdir(folder_path)
    ret = []
    if extension:
        for item in list:
            e = get_extension(item)
            if e == extension:
                ret.append(folder_path + "/" + item)
    elif target_string:
        for item in list:
            f = item.find(target_string)
            if f>0:
                ret.append(folder_path + "/" + item)
    else:
        for item in list:
            ret.append(folder_path + "/" + item)
    return ret


def create_control_files(file_path, destination_path = ""):
    ### todo: sloppy. Assumes that all .txt are data. This is not always the case. Phase out or replace.
    data = get_all_files_names_in_folder(file_path, "txt")
    control = get_all_files_names_in_folder(file_path, "csv")
    for d in data:
        control_name = file_path + get_stem(d)+"__c.csv"
        if not control.__contains__(control_name):
            convertOldFormatToNew(d, destination_path)
            #todo: add logic here to determine what type of original file we have and al


def update_control_files_with_item_bank_key(path_to_item_bank_csv, path_to_control):
    #   todo: this is only good for the pt format... general application should be more robust.
    control_file_paths = get_all_files_names_in_folder(path_to_control, "csv")
    item_bank_df = pd.DataFrame(pd.read_csv(path_to_item_bank_csv))
    for file_path in control_file_paths:
        if not file_path == path_to_item_bank_csv:
            control_df = pd.DataFrame(pd.read_csv(file_path, header = None))
            name = get_stem(file_path)
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
            control_df.to_csv(file_path, index = False)
            remove_first_line_of_csv(file_path)


def create_mapping_from_Karen_test_data(file_path, destination_path = "", create_csv = False):
    lines = get_lines(file_path)
    #   assumes files are of format
    #   number. Name NN
    #   ....  where no lines will start with a number and then a dot other than my target lines
    #   number. Name NN
    ret = []
    for line in lines:
        if line[0].isnumeric():
            entry = line.split()
            test_name = get_stem(file_path)
            test_id = line[:line.index('.')]
            subject = entry[1]
            bank_id = entry[2]
            record = [test_name, test_id, subject, bank_id, subject+"_"+str(bank_id)]
            ret.append(record)
    if create_csv:
        name = get_stem(file_path) + "_L.csv"
        df = pd.DataFrame(ret)
        df.to_csv(destination_path + name, index = False, header = None)

    return ret


def process_karen_data(path_to_data, destination_path):
    #   process test information files to create item bank map ID files
    test_bank_files = get_all_files_names_in_folder(path_to_data, target_string="Test")
    test_bank_lists = []
    for file in test_bank_files:
        a = create_mapping_from_Karen_test_data(file, destination_path = destination_path, create_csv= True)
        test_bank_lists.append(a)
    #   create control files
    #   create formatted data files
    data_files = get_all_files_names_in_folder(path_to_data, target_string="FullAdmin")
    for file in data_files:
        convertOldFormatToNew(file, destination_path = destination_path)

    #   replace control file ids with item bank ids
    item_bank_ids = get_all_files_names_in_folder(destination_path, target_string="_L")
    # todo: sloppy solution
    for item_bank in item_bank_ids:
        for file in data_files:
            name = get_stem(file)[:11]
            control_name = name + "FullAdmin_c.csv"
            control_path = destination_path + control_name
            merge_control_and_bank_info(control_path, item_bank)
        # create df from control file
        # create df from item_bank
        # set control_file_id to item_bank id.

    #   ?? delete the bank ID files ?? not sure they are needed after this step
def merge_control_and_bank_info(control_path, bank_path, control_id_col = 0, bank_control_col = 4):
    control_df = get_df(control_path)
    bank_df = get_df(bank_path)
    control_df[control_id_col] = bank_df[bank_control_col].values
    control_df.to_csv(control_path, header = None, index = False)


process_karen_data("LCEA_data/", "LCEA_data/processing/")

#merge_control_and_bank_info(a,b)
#path_to_files = "data_files"
#convertOldFormatToNew("LCEA_data/lcea1_18.txt")
#processNewFileFormat("LCEA_data/lcea1_18c.csv","LCEA_data/lcea1_18.txt")
#convert_first_line_answers_to_default_control_and_data(path_to_files+"/pt1_16_n.txt")
#create_control_files(path_to_files)
#update_control_files_with_item_bank_key("data_files/item_map.csv", "data_files")
#convert_2016_format("data_files/pt3_16.txt")
#create_mapping_from_Karen_test_data("LCEA_data/LCLE_Q.txt", True)

