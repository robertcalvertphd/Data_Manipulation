import pandas as pd
import h_user_input as h


def get_stem(name_with_extension):
    i = name_with_extension.index('.')
    return name_with_extension[:i]


def drop_first_item_from_csv(fileName):
    lines = []
    ret = []
    with open(fileName) as f:
        for line in f: lines.append(line)
    for line in lines:
        index_of_first_comma = line.index(',')
        line = line[index_of_first_comma + 1:]
        ret.append(line)
    with open(fileName, 'w') as f:
        f.writelines(ret)


def restore_id_integrity(file_name, id_length):
    #   open file
    ret = []
    with open(file_name) as f:
        first = True
        for line in f:
            if first:
                first = False
            else:
                newLine = ""
                #   find first comma
                i = line.index(',')
                #   calculate number of zeroes needed
                zeroes = id_length - i
                #   add zeroes
                for z in range(zeroes):
                    newLine += '0'
                newLine += line
                ret.append(newLine)
    write_lines_to_text(ret, file_name)





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
                    correctList.append(0)
                else:
                    correctList.append(1)
            ids.append(id)
            correctLists.append(correctList)

    df = pd.DataFrame(correctLists, index=None).T
    df.to_csv('list.csv', index=False)
    return [ids, correctList]


def convert_new_format_to_csv(file_path, id_length=8, index_for_start_of_responses=11):
    stem = get_stem(file_path)
    with open(file_path) as file:
        lines = file.readlines()

    ret = "id,"
    number_of_questions = len(lines[0]) - index_for_start_of_responses - 1
    for i in range(number_of_questions):
        ret += 'q' + str(i + 1) + ","
    ret = ret[:-1]
    ret += '\n'
    for line in lines:

        newLine = line[:id_length] + ','
        for i in range(len(line) - index_for_start_of_responses):
            entry = line[i + index_for_start_of_responses]
            if not entry == '\n':
                newLine += entry + ','

        ret += newLine[:-1] + '\n'

    with open(stem + ".csv", "w") as file:
        file.write(ret)


def convert_csv_to_new_format(file_path, id_length=8, index_for_start_of_responses=11):
    with open(file_path) as f:
        first = True
        ret = []
        for line in f.readlines():
            if first:
                first = False
            else:
                first_comma = line.index(',')
                id = line[:first_comma]
                new_line = id + "   "

                remainder = line[first_comma:]
                for i in remainder:
                    if not i == ',':
                        new_line += i
                ret.append(new_line)
        name = get_stem(file_path)
        write_lines_to_text(ret, name + ".txt")


def convert_new_format_to_df(filepath, id_length=8, index_for_start_of_responses=11):
    #   create csv
    convert_new_format_to_csv(filepath, id_length, index_for_start_of_responses)
    #   create data frame from csv
    name = get_stem(filepath)
    df = pd.DataFrame(pd.read_csv(name + ".csv"), index=None)
    #   return data frame
    return df


def write_lines_to_text(lines, file_path):
    #   todo: consider removal or consistent implementation
    with open(file_path, "w") as file:
        file.writelines(lines)


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


def getNextBlankLineAfterIndex(file_path, index):
    with open(file_path) as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            if line == "\n":
                if count > index:
                    return count
            count += 1
        return False


def get_rows_of_data_frame_from_list_of_ids(df, list_of_ids, id_column_name="Item ID"):
    criterion = lambda row: row[id_column_name] in list_of_ids
    ret = df[df.apply(criterion, axis=1)]
    return ret


def get_top_n_as_csv(csv_file_path, n, column_name, first_line=34):
    #   chop up csv to isolate table

    file_pathToTopCSV = get_stem(csv_file_path) + "_top_" + str(n) + "_" + column_name + ".csv"
    blankLine = getNextBlankLineAfterIndex(csv_file_path, first_line - 1)
    choppedLines = get_lines_from_X_to_Y_from_file(csv_file_path, first_line - 1, blankLine)
    #   convert data to csv file
    write_lines_to_text(choppedLines, file_pathToTopCSV)
    #   convert data to pandas df
    df = pd.DataFrame(pd.read_csv(file_pathToTopCSV), index=None)
    #   sort dataFrame
    df = df.sort_values(by=column_name, ascending=False)
    #   select top n
    topN = df.head(n)
    #   create csv
    topN.to_csv(file_pathToTopCSV)
    return topN


def create_test_from_highly_discriminatory_questions(p_data, p_control, p_score_file, n=20, target_var='S-Rpbis'):

    original_data = convert_new_format_to_df(p_data)
    #   establish the high scoring items
    df = get_top_n_as_csv(p_score_file, n, target_var)
    #   get the relevant question ids
    a = df['Sequence']
    a_list = ["id"]
    for item in a.to_list():
        a_list.append('q' + str(item))

    #   get data frame of all answers
    all_answers = convert_new_format_to_df(p_data)
    #   select responses to just those questions from test taker data
    selected_data = all_answers[a_list]
    #   read lines from control file and write those that were selected
    #   create control file for top 20
    control_lines = []
    with open(p_control) as f:
        lines = []
        for line in f.readlines():
            lines.append(line)
    for item in a:
        control_lines.append(lines[item-1])
    name_of_control_file = get_stem(p_control) + "_" + "select_top_" + str(n) + "_for_" + target_var + ".csv"
    write_lines_to_text(control_lines,name_of_control_file)

    '''
    for line in f.readlines():
        count += 1
        if a_list.__contains__('q' + str(count)):
            control_strings.append(line)
    '''

    #   create relevant files for IRT testing
    name = get_stem(p_data)
    selected_data_file_name = name + "_top_" + str(n) + ".csv"
    selected_data.to_csv(selected_data_file_name)
    drop_first_item_from_csv(selected_data_file_name)
    restore_id_integrity(selected_data_file_name, 8)
    convert_csv_to_new_format(selected_data_file_name)


def subset():
    print("subset selected")
    filePath = input("read file?")
    #   read the file and spit out the columns as options...
    #   will pause on this pursuit for the time being.

    column = input("what column would you like to select?")
    n = h.getInt("how many rows would you like", 1000)


class DataManipulator:
    def __init__(self):
        self._cont = True

    def receive_direction(self):
        self._cont = True
        possibleChoices = ["Create Subset for Top n for column"]
        functions_for_choices = [subset]
        choice = h.select_from_list("What would you like to do?", possibleChoices)
        function = functions_for_choices[choice]
        function()

        # eventually there will be more choices


d = DataManipulator()
create_test_from_highly_discriminatory_questions("d2.txt", "c2.csv", "pt_s.csv", n = 50)

# need to make control for selected questions
