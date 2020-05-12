import core.h_format_manipulators as h
hfh = h.hfh

#todo: problem with this code... the matching seems off.

def process_PT_data(processed_data_folder):

    h.create_L_files_from_item_bank_master("PT_IRT/item_map.csv", "PT_IRT/PT_processed_data", "testFORM", "testSeq","AccNum")
    h.add_header_to_csvs(processed_data_folder, 'sequence,form,bank_id,subject,number\n', '_L.csv')
    h.convert_folder_from_iteman_format("PT_IRT/PT_data/PT 12 Forms", destination_path=processed_data_folder, pretest_cutoff=175)
    h.convert_folder_from_iteman_format("PT_IRT/PT_data/PT 13 Forms", destination_path=processed_data_folder, pretest_cutoff=175)
    h.convert_folder_from_iteman_format("PT_IRT/PT_data/PT 14 Forms", destination_path=processed_data_folder, pretest_cutoff=175)
    h.convert_folder_from_iteman_format("PT_IRT/PT_data/PT 15 Forms", destination_path=processed_data_folder, pretest_cutoff=175)
    convert_2016_data(hfh.get_all_file_names_in_folder("PT_IRT/PT_data/PT 16 Forms", extension='txt'), processed_data_folder)
    move_valid_and_rename("PT_IRT/PT_data/PT 17 Forms", processed_data_folder)
    move_valid_and_rename("PT_IRT/PT_data/PT 18 Forms", processed_data_folder)
    h.add_header_to_csvs(processed_data_folder, 'sequence,key,number_of_options,group,include,scoring_option\n','_c.csv')
    h.update_c_from_L_in_matched_folder(processed_data_folder)
    h.set_standard_id_length_in_data_files(processed_data_folder, 8)
    rename_files(processed_data_folder)
def rename_files(processed_data_path):
    data = hfh.get_all_file_names_in_folder(processed_data_path, target_string='_f.txt')
    control = hfh.get_all_file_names_in_folder(processed_data_path, target_string='_c.csv')
    for file in data:
        hfh.abbreviate_name(file, target_string="_", characters_kept_after_target=2)
    for file in control:
        hfh.abbreviate_name(file, target_string= "_", characters_kept_after_target=2)


def convert_2016_data(files, destination_path):
    for file in files:
        h.convert_2016_format(file, destination_path = destination_path)


def move_valid_and_rename(original_data, processed_data_folder):
    valid_data = hfh.get_all_file_names_in_folder(original_data, extension='txt')
    valid_control = hfh.get_all_file_names_in_folder(original_data, extension='csv')
    for file in valid_data:
        name = hfh.get_stem(file) + "_f.txt"
        hfh.copy_file_and_write_to_destination(file, processed_data_folder, modified_name=name)
    for file in valid_control:
        name = hfh.get_stem(file) + "_c.csv"
        hfh.copy_file_and_write_to_destination(file, processed_data_folder, modified_name=name)


process_PT_data("PT_IRT/PT_processed_data")

