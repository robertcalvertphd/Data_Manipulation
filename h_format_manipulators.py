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
    return name_with_extension[:i]


def process_old_format(fileName, correctDataLine=1, firstDataLine=4, removeIncompleteSets=False):
    lines = []
    with open(fileName) as f:
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


def convertOldFormatToNew(fileName):
    #   old format is of style
    #   gibberish first line
    #   correct answers
    #   number of options
    #   included
    #   start response entries

    old = get_lines(fileName)
    correct = old[1]
    number_of_possible_responses = old[2]
    included = old[3]
    new = []
    assert len(correct) == len(number_of_possible_responses) == len(included)
    i = -1
    for answer in correct:
        i += 1
        line = str(i + 1) + "," + answer + "," + number_of_possible_responses[i] + ",1," + included[i] + ",M \n"
        new.append(line)
    new = new[:-1]
    write_lines_to_text(new, "control_" + get_stem(fileName) + "_converted.txt")
    write_lines_to_text(old[4:], get_stem(fileName)+"_converted.txt")


convertOldFormatToNew("d.txt")
