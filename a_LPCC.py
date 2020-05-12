import core.h_format_manipulators as h
hfh = h.hfh

def get_control_files(path_to_data, processed_data_path, control_target_string):
    files = hfh.get_all_files(path_to_data= path_to_data, target_string=control_target_string)
    for file in files:
        h.convert_delimited_control(file,processed_data_path, remove_version=True)
        converted_file_name = processed_data_path + "/"+hfh.get_stem(file)
        hfh.abbreviate_name(converted_file_name,target_string='LLE', new_extension='_c.csv', characters_kept_after_target=5)
    return files

def get_data_files(path_to_data, processed_data_path, data_target_string = False, control_files = False):
    if data_target_string:
        files = hfh.get_all_files(path_to_data=path_to_data, target_string=data_target_string)
    else:
        files = hfh.get_all_files(path_to_data=path_to_data, )
    data_files = []
    #   naming has no identifying characteristic so filtering by control
    if control_files:
        for file in files:
            if not file in control_files:
                data_files.append(file)
    else:
        for file in files:
            data_files.append(file)
    for file in data_files:
        hfh.copy_file_and_write_to_destination(file,processed_data_path,new_extension='_f.txt')

def convertIteman(path_to_data, processed_data_path):
    files = hfh.get_all_files(path_to_data, target_string="LLE16")
    for file in files:
        h.convert_iteman_format(file, processed_data_path)

path_to_data = "LPCC_IRT/data"
processed_data_path = "LPCC_IRT/processed_data"
control_files = get_control_files(path_to_data,processed_data_path,"Control")
get_data_files(path_to_data, processed_data_path, control_files=control_files)
#convertIteman(path_to_data, processed_data_path)

