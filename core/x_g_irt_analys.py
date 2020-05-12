import core.h_format_manipulators as hf
import core.h_user_input as hu



#   1)  check data file and control files. convert if necessary
#   2)  match item_id with control file
#           could be an item bank or a series of test forms (Karen data)
#   3)  run Rasch models in xCalibre
#   4)  item analysis
#           aggregate reports
#           recommendations

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ #

#   1)  check data file and control files. convert if necessary
def step1():
    destination_folder = hu.get_folder("Where would you like formatted files stored?")+"/"
    files = hu.get_all_data_files()
    files = hf.purge_invalid_extensions(files, ["csv","txt"])
    validation_results = verify_files(files)
    valid = validation_results[0]
    invalid = validation_results[1]
    ignored = format_files(invalid, destination_folder, control_string = False)
    control_files = hu.get_yes_no_response("Control Files", "Does your data already have control files?")
    control_string = False
    if control_files:
        control_string = hu.get_string("What is a common naming component of your control files?")
    format_files(valid, destination_folder, control_string)


#   2)  match item_id with control file
def step2():
    # ask if data is stored in a single bank or in individual files
    q_item_bank = hu.get_yes_no_response("Item Bank Type", "Is the item to form pairing stored in a single item bank?")
    if q_item_bank:
        item_bank_file = hu.get_file("Select item bank file.")
        control_path = hu.get_folder("Select folder with control files in it.")
        hf.update_control_files_with_item_bank_key(item_bank_file, control_path)
    else:
        path_to_data = hu.get_folder("Where is data located?")
        destination_path = hu.get_folder("Where would like the data to be placed?")
        hf.process_karen_data(path_to_data, destination_path)


def process_karen_data():
    data_files = hu.get_all_data_files("Select data files", "Common component in data")
    test_bank_files = hu.get_all_data_files("Select test files", "Common component in test_bank")
    destination_path = hu.get_folder("Select destination folder") +"/"
    hf.process_karen_data(data_files,test_bank_files,destination_path)


def format_files(files, destination, control_string):
    handled = []
    for file in files:
        if hf.fix_format_of_data_file(file, destination, control_string):
            handled.append(file)
    for file in handled:
         files.remove(file)
    return files


def verify_files(files):
    verified = []
    invalid = []
    for file in files:
        if hf.is_valid_data(file):
            verified.append(file)
        else:
            invalid.append(file)

    return verified, invalid


#step1()
#step2()
process_karen_data()