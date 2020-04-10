def getInt(prompt, _max, _min=1):
    while 1:
        try:
            ret = int(input(prompt))
            if _max >= ret >= _min:
                return ret
            print('invalid response: out of range')
        except (ValueError, Exception):
            print('invalid syntax: integer only')


def select_from_list(prompt, options):
    print(prompt)
    for i in range(len(options)):
        print(i + 1, ":", options[i])
    selectionID = getInt(prompt, len(options)) - 1
    return selectionID
