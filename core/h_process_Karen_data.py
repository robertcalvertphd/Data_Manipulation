import core.h_format_manipulators as h
hfh = h.hfh
pd = h.pd
import core.h_passing_score as p
from core.h_Rasch_report_analysis import create_all
#   this file processes data formatted as test and data
#   test files follow the form number. Subject ID e.g 1. Law 102
#   admin files follow the standard iteman format row 2 = key, row row 3 = response options, row 4 = include

def procees_karen_data(data_path, processed_data_path, report_path, test_bank_string, data_string, report_name, xCalibre_path):

    #1  gather all test files
    test_bank_files = hfh.get_all_files(data_path, target_string=test_bank_string)
    #2  create _L files
    for file in test_bank_files:
        create_L_from_test(file, destination_path = processed_data_path, create_csv = True)
    #3  gather all data files
    data_files = hfh.get_all_files(data_path, target_string=data_string)
    #4  create control files from _L and data
    for file in data_files:
        h.convert_iteman_format(file, destination_path=processed_data_path)
    h.add_header_to_csvs(processed_data_path, 'sequence,key,number_of_options,group,include,scoring_option', '_c.csv')
    processed = 0
    for file in data_files:
        matching_control_name = processed_data_path  + "/" + hfh.get_stem(file) + "_c.csv"
        matching_item_bank_name = processed_data_path + "/"+ hfh.get_stem(file)[:-len(data_string)]+ test_bank_string + "_L.csv"
        processed+=merge_control_and_bank_info(matching_control_name, matching_item_bank_name)

    #5  process xCalibreOutput files and create Stats_c files
    #6  create aggregate reports from _Stats_c files



def create_L_from_test(file_path, destination_path = "", create_csv = True):

    lines = hfh.get_lines(file_path)
    ret = [['form', 'sequence', 'subject', 'bank_id_number', 'bank_id']]
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
        df.to_csv(destination_path + "/" + name, index = False, header = False)

    return df


def merge_control_and_bank_info(control_path, bank_path):
    control_df = hfh.get_df(control_path, header=0)
    bank_df = hfh.get_df(bank_path, header = 0)
    try:
        new = pd.merge(control_df, bank_df, on='sequence', how='left')
        new = new[['bank_id', 'key','number_of_options','group','include','scoring_option']]
        new.to_csv(control_path, header=0, index = False)
    except:
        print("error in merge_control")
        return 0
    return 1


