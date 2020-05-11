#   this file contains functions that modify files and retrieve information
import os
import pandas as pd
import numpy as np


def copy_file_and_write_to_destination(file, destination, modified_name = False):
    lines = get_lines(file)
    extension = "." + get_extension(file)
    name = destination + get_stem(file) + extension
    if modified_name:
        name = destination + "/" + modified_name
    write_lines_to_text(lines, name)


def purge_invalid_extensions(files, list_of_valid_extensions):
    ret = []
    for file in files:
        extension = get_extension(file)
        if extension in list_of_valid_extensions:
            ret.append(file)
    return ret


def get_all_folders_in_folder(folder_path):
    list = os.listdir(folder_path)
    ret = []
    for item in list:
        if get_stem(item) == item:
            ret.append(folder_path + "/"+item)
    return ret


def get_all_file_names_in_folder(folder_path, extension = False, target_string = False):
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
            if f>0 :
                ret.append(folder_path + "/" + item)
    else:
        for item in list:
            ret.append(folder_path + "/" + item)
    return ret


def get_all_files(path_to_data, target_string):
    folders = get_all_folders_in_folder(path_to_data)
    folders.append(path_to_data)
    data_files = []
    for folder in folders:
        sub_folders = get_all_folders_in_folder(folder)
        for s in sub_folders:
            folders.append(s)
    for folder in folders:
        files = get_all_file_names_in_folder(folder,target_string=target_string)
        for file in files:
            data_files.append(file)
    return data_files

'''
def get_all_sub_folders(folder_path):
    #todo: candidate for deletion
    processed_folders = []
    to_be_processed_folders = [folder_path]
    while len(to_be_processed_folders)>0:
        for folder in to_be_processed_folders:
            subfolders = get_all_folders_in_folder(folder)
            to_be_processed_folders.remove(folder)
            processed_folders.append(folder)
            for s in subfolders:
                to_be_processed_folders.append(s)
    return processed_folders
'''

def create_name(name, path, extension, modificaiton = ""):
    ret = path + "/" + name + modificaiton + extension
    return ret


def get_next_blank_line_after_index(file_path, index):
    with open(file_path) as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            if line == "\n":
                if count > index:
                    return count
            count += 1
        return False


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
        return False
        print("invalid file type call in get_lines")


def get_df(path_to_csv, header = None, index = None, dtype = object):
    return pd.DataFrame(pd.read_csv(path_to_csv, header = header, dtype=dtype), index = index)


def write_lines_to_text(lines, file_path, mode = 'w'):  # candidate for general helper file
    with open(file_path, mode) as file:
        file.writelines(lines)


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


def abbreviate_name(file_path, new_extension = False, target_string = False, static_length = False, characters_kept_after_target = 0):
    name = get_stem(file_path)
    extension = get_extension(file_path)
    if new_extension:
        extension = new_extension
    parent_folder = get_parent_folder(file_path)
    if static_length and len(name) > static_length:
        ret = name[:static_length]
    if target_string:
        loc = name.find(target_string)
        ret = name[:loc+1 + characters_kept_after_target]
    ret = parent_folder +"/"+ret + "." + extension
    os.rename(file_path, ret)
