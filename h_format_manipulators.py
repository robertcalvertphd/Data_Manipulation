import os
import pandas as pd
import numpy as np


def get_lines(file_name):  # candidate for general helper file
    lines = []
    with open(file_name) as f:
        for line in f: lines.append(line)
    return lines


def write_lines_to_text(lines, file_path):  # candidate for general helper file
    with open(file_path, "w") as file:
        file.writelines(lines)


def get_stem(name_with_extension):  # candidate for general helper file
    i = name_with_extension.index('.')

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


def convertOldFormatToNew(file_name):
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
            inc = 'y'

        line = str(i + 1) + "," + answer + "," + str(n) + ",1," + inc + ",M \n"
        control.append(line)
    control = control[:-1]
    write_lines_to_text(control, get_stem(file_name)+"c.csv")
    write_lines_to_text(old[4:], file_name)

def convert_first_line_answers_to_default_control_and_data(file_name):
    lines = get_lines(file_name)
    correct = lines[0][14:62]
    new = []
    counter = 0
    for a in correct:
        counter +=1
        if not a == '\n':
            new.append(str(counter)+","+a +",4,1,y,M\n")

    name = get_stem(file_name)
    write_lines_to_text(new, name+"_control.csv")
    #   contains a random F at the end will test to see if it matters
    formatted = []
    for line in lines[2:]:
        formatted.append(line[:62]+'\n')
    write_lines_to_text(formatted, name + "_formatted.txt")

def get_all_files_names_in_folder(folder_path, extension = False):
    list = os.listdir(folder_path)
    ret = []
    if extension:
        for item in list:
            e = get_extension(item)
            if e == extension:
                ret.append(folder_path + "/" + item)
    else:
        for item in list:
            ret.append(folder_path + "/" + item)
    return ret


#convertOldFormatToNew("d.txt")
#convert_first_line_answers_to_default_control_and_data("d3.txt")
def create_control_files(file_path):
    data = get_all_files_names_in_folder(file_path, "txt")
    control = get_all_files_names_in_folder(file_path, "csv")
    for d in data:
        control_name = file_path + get_stem(d)+"c.csv"
        if not control.__contains__(control_name):
            convertOldFormatToNew(d)

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


def remove_first_line_of_csv(file_path):
    lines = get_lines(file_path)
    write_lines_to_text(lines[1:], file_path)


#path_to_files = "data_files"
#create_control_files(path_to_files)
update_control_files_with_item_bank_key("data_files/item_map.csv", "data_files")