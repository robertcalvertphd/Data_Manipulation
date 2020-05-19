import core.h_format_manipulators as h
import core.h_report_analysis as r
import core.h_passing_score as p
hfh = h.hfh

def get_control_files(path_to_data, processed_data_path, control_target_string):
    files = hfh.get_all_files(path_to_data= path_to_data, target_string=control_target_string)
    for file in files:
        if hfh.is_delimited(file,'\t'):
            h.convert_delimited_control(file,processed_data_path, remove_version=True)
        if hfh.is_delimited(file, ','):
            h.convert_delimited_control(file, processed_data_path, delimiter=',', remove_version=True)
        converted_file_name = processed_data_path + "/"+hfh.get_stem(file)
        hfh.abbreviate_name(converted_file_name,target_string='LLE', new_extension='_c.csv', characters_kept_after_target=5, AB = "Form")
    return files

def get_data_files(path_to_data, processed_data_path, data_target_string = False, control_files = False):
    if data_target_string:
        files = hfh.get_all_files(path_to_data=path_to_data, target_string=data_target_string)
    else:
        files = hfh.get_all_files(path_to_data=path_to_data)
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
        if h.check_for_header(file, True):
            print("removed header in " + file)
        if hfh.get_extension(file) == 'csv':
            h.convert_delimited_to_iteman(file, processed_data_path, ',')
        elif hfh.is_delimited(file,'\t'):
            h.convert_delimited_to_iteman(file, processed_data_path, '\t')
        else:
            hfh.copy_file_and_write_to_destination(file,processed_data_path,new_extension='_f.txt')

def convertIteman(path_to_data, processed_data_path):
    files = hfh.get_all_files(path_to_data, target_string="LLE16")
    for file in files:
        h.convert_iteman_format(file, processed_data_path)
    h.set_standard_id_length_in_data_files(path_to_data,8)


def process_amy_data(path_to_data, processed_data_path):
    control_files = get_control_files(path_to_data,processed_data_path,"Control")
    get_data_files(path_to_data, processed_data_path, control_files=control_files)
    convertIteman(path_to_data, processed_data_path)
    h.set_standard_id_length_in_data_files(processed_data_path,8)
    c_files = hfh.get_all_file_names_in_folder(processed_data_path,target_string="_c.csv")
    for file in c_files:
        h.convert_control_to_include_pretest(file)
    files = hfh.get_all_files("LPCC_IRT/processed_data")
    hfh.rename_all_files_to_lower(files)

def create_amy_reports(report_path, xCalibre_path, key_path):
    valid = h.has_acceptable_correct_percentage(xCalibre_path)
    if valid:
        r.create_all(xCalibre_path,report_path,"_LPCC_")
    p.evaluate_past_tests(report_path,key_path, Amy_data=True, passing_theta=1)

path_to_data = "LPCC_IRT/data/AB_test"
processed_data_path = "LPCC_IRT/processed_data"
xCalibre_path = "LPCC_IRT/xCalibreOutput"
reports_path = "LPCC_IRT/reports"
key_path = "LPCC_IRT/keys"
#process_amy_data(path_to_data, processed_data_path)
create_amy_reports(reports_path, xCalibre_path, key_path)
