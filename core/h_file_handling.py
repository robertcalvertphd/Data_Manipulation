#   this file contains functions that modify files and retrieve information
#from core.import_handler import os
import os
#from core.import_handler import copyfile
from shutil import copyfile
import pandas as pd
import numpy as np
#from core.import_handler import pd




def file_is_readable(file_path):
    try:
        with open(file_path, mode='r') as file:
            return file.readable()
    except IOError as e:
        return 0


def file_is_writable(file_path):
    try:
        with open(file_path, mode='a') as file:
            return file.writable()
    except IOError as e:
        return 0


def copy_file_and_write_to_destination(file, destination, modified_name = False, new_extension = False, upper = True):

    if new_extension:
        extension = new_extension
    else:
        extension = "." + get_extension(file)

    name = destination +"/" + get_stem(file) + extension

    if modified_name:
        name = destination + "/" + modified_name
    try:
        copyfile(file, name)
        return True
    except:
        print("problem copying file:" + file)
        return False


def purge_invalid_extensions(files, list_of_valid_extensions):
    ret = []
    for file in files:
        extension = get_extension(file)
        if extension in list_of_valid_extensions:
            ret.append(file)
    return ret


def get_all_folders_in_folder(folder_path):
    if os.path.isdir(folder_path):
        list = os.listdir(folder_path)
        ret = []
        for item in list:
            if os.path.isdir(folder_path + '/'+item):
                ret.append(folder_path + '/'+item)
        return ret
    else:
        print("get all folders fed path that DNE.")
        return False

def get_all_file_names_in_folder(folder_path, extension = False, target_string = False, can_be_empty = True):
    ret = []
    if os.path.isdir(folder_path):
        list = os.listdir(folder_path)

        if extension:
            for item in list:
                e = get_extension(item)
                if e == extension:
                    ret.append(folder_path + "/" + item)
        elif target_string:
            for item in list:
                f = item.find(target_string)
                if f>-1 :
                    ret.append(folder_path + "/" + item)
        else:
            for item in list:
                ret.append(folder_path + "/" + item)
        return ret
    else:
        print(folder_path + " is not a folder.")
        if can_be_empty:
            return ret
        return False


def get_all_files(path_to_data, target_string = False, extension = False):
    #todo: verify that this works with many layers of folders
    folders = get_all_folders_in_folder(path_to_data)
    data_files = []
    for folder in folders:
        if os.path.isdir(folder):
            sub_folders = get_all_folders_in_folder(folder)
            for s in sub_folders:
                folders.append(s)
    folders.append(path_to_data)
    for folder in folders:
        if os.path.isdir(folder):
            files = get_all_file_names_in_folder(folder,target_string=target_string, extension = extension)
            for file in files:
                    if os.path.isfile(file):
                        data_files.append(file)
    return data_files


def find_and_replace_string_in_file(file, find, replace):
    lines = get_lines(file)
    ret = []
    for line in lines:
        line = line.replace(find,replace)
        ret.append(line)
    write_lines_to_text(ret,file)


def create_name(path, extension = False, name = False, modificaiton = ""):
    #modified
    print("changed on 6_2_20 if problems")
    if not name:
        name = get_stem(path)
    if extension:
        if extension.rfind('.') == -1:
            extension = '.' + extension
    else:
        extension = get_extension(path)
    ret = get_parent_folder(path) + "/" + name + modificaiton + extension
    return ret


def get_index_of_line_that_starts_with_word_based_on_delimiter(lines, word, delimiter = ','):
    index = -1
    looking = True
    while looking:
        index += 1
        split_line = lines[index].split(delimiter)
        if split_line[0] == word:
            looking = False
    return index


def get_next_blank_line_after_index_from_lines(lines, index):
    count = 0
    for line in lines[index:]:
        if line == "\n":
            return count
        count += 1
    return False


def get_next_blank_line_after_index(file_path, index):
    ### should deprecate the file_path option
    with open(file_path) as file:
        lines = file.readlines()
        count = 0
        for line in lines[index:]:
            if line == "\n":
                return count
            count += 1
        return False


def rename_all_files_to_lower(files):
    for file in files:
        if os.path.isfile(file):
            os.rename(file,file.lower())


def get_lines_from_X_to_Y_from_file(file_path, x, y):
    with open(file_path) as file:
        lines = file.readlines()
    if y > len(lines):
        print("Y in get lines from X to Y from File is greater than length of file.")
    ret = []
    work = lines[x:y]
    for line in work:
        ret.append(line)
    return ret


def get_lines(file_name):  # candidate for general helper file
    lines = []
    try:
        with open(file_name) as f:
            for line in f: lines.append(line)
        return lines
    except:
        print("invalid file type call in get_lines")
        return False


def get_df(path_to_csv, header = None, index = None, dtype = object):
    return pd.DataFrame(pd.read_csv(path_to_csv, header = header, dtype=dtype), index = index)


def write_lines_to_text(lines, file_path, mode = 'w'):  # candidate for general helper file
    double_forward = '//'
    if file_path.find(double_forward)>-1:
        print("double forward slash found and removed")
        file_path.replace(double_forward,'/')
    with open(file_path, mode) as file:
        for line in lines:
            if line is not None:
                file.write(line)
    return 1
    '''
    try:
        with open(file_path, mode) as file:
            file.writelines(lines)
        return 1
    except:
        print("could not open file:" + file_path)
        return 0
    '''


def remove_first_line_of_csv(file_path):
    lines = get_lines(file_path)
    write_lines_to_text(lines[1:], file_path)


def get_stem(name_with_extension):  # candidate for general helper file
    try:
        i = name_with_extension.index('.')
        s = name_with_extension.rfind('/')
        if s == -1: s = 0
        ret = name_with_extension[s + 1:i]
        return ret
    except:
        return name_with_extension


def get_parent_folder(file_path):
    if get_extension(file_path):
        last_slash = file_path.rfind('/')
        return file_path[:last_slash]


def get_extension(name_with_extension):
    i = name_with_extension.find('.')
    if i > -1:
        return name_with_extension[i+1:]
    return False


def abbreviate_name(file_path, new_extension = False, target_string = False, static_length = False, characters_kept_after_target = 0, AB = False):
    # AB assumes there will be a target string that preceeds the form
    # e.g Form A

    name = get_stem(file_path)
    old = file_path
    new = ""
    if name == file_path:
        if os.path.isfile(file_path):
            if new_extension:
                new = file_path + new_extension
            else:
                print("file without extension passed to abbreviate name and no new extension specfied. Default x extension given.")
                new = new + '.X'
    extension = get_extension(file_path)
    form = False
    if AB:
        form_loc = file_path.find(AB)
        if form_loc > -1:
            form = file_path[form_loc+5]

    if new_extension:
        extension = new_extension
    parent_folder = get_parent_folder(new)
    if static_length and len(name) > static_length:
        ret = name[:static_length]
    if target_string:
        loc = name.find(target_string)
        ret = name[:loc+len(target_string) + characters_kept_after_target]
        if form:
            ret+=form
        ret = get_stem(ret)
    if extension.rfind("."):
        ret = ret + extension
    else:
        ret = parent_folder + "/" + ret +"."+ extension
    # automatically writes over previous file.
    if os.path.exists(ret):
        os.remove(ret)
    os.rename(file_path, ret)


def is_delimited(file, delimiter, minimum_columns = 4):
    lines = get_lines(file)
    split_line = lines[0].split(delimiter)
    if len(split_line) < minimum_columns:
        return False
    return True


def find_month(file_name):
    months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"]
    ret = []
    file_name = get_stem(file_name).upper()
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
    if len(ret) == 1:
        return ret[0]
    else:
        return False

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


def pair_files(filesA, filesB, check = False, get_unhandled_items = False):
    if get_unhandled_items and check:
        print("can not simultaneously get unhandled and check that match")
    ret = []
    unhandled = []
    for fa in filesA:
        pe_mon = find_month(fa)
        pe_year = find_year(fa)
        handled = 0
        for fb in filesB:
            data_mon = find_month(fb)
            data_year = find_year(fb)
            if pe_mon == data_mon and pe_year == data_year:
                ret.append([fa, fb])
                handled = 1
        if handled == 0:
            unhandled.append(fa)
    if len(filesA) == len(filesB):
        if len(ret) == len(filesA):
            return ret
        else:
            if not check:
                print("unhandled items in process data")
                if get_unhandled_items:
                    return ret, unhandled
                else:
                    return ret
            else:
                return False
    elif check:
        print("length of files are unequal. Should not happen.")
        return False
    else:
        return ret


def convert_xlsx_to_csv(file_path, destination_path, get_df = False):
    read_file = pd.read_excel(file_path)
    read_file.to_csv(destination_path, index=None, header=True)
    if get_df:
        return read_file


def get_df_from_xlsx(file_path):
    return pd.read_excel(file_path)


def get_stats_df(stats_path, bank = None, remove_na = True):
    ret = []
    lines = get_lines(stats_path)
    header_index = get_index_of_line_that_starts_with_word_based_on_delimiter(lines,'Sequence')
    blank_index = get_next_blank_line_after_index_from_lines(lines, header_index)
    data = lines[header_index+1:blank_index+header_index]
    for line in data:
        ret.append(line.split(','))
    df = pd.DataFrame(ret)

    header = lines[header_index].split(',')
    df.columns = header[:-1]
    #   note the last entry has \n
    if remove_na:
        df = df.apply(pd.to_numeric, errors='coerce')
        #df = df.dropna['b'](axis=1, how='any')
        df = df[df['b'].notna()]
    if bank is not None:
        df['Domain'] = bank['Domain']
    return df


def get_matched_files(path = None, possible_X = ['R','2'], possible_Y = ['TIF','IIF','STATS'], only_return_complete_sets = True):
    #   this is intended to work with files following TESYRMON_X_Y
    if os.path.isdir(path):
        files = get_all_files(path)

        for file in files:
            name = file[file.rfind('/'):file.rfind('.')]
            year = find_year(file)
            mon = find_month(file)
            x_i = name.find('_')
            y_i = name.rfind('_')
            x = file[x_i:y_i]
            y = file[y_i:]
    else:
        print("invalid path")
        return False
