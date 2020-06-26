class R:
    #   todo: add errors as they are identified here.
    PATH_DNE = 90
    FILE_DNE = 91
    PRO_EXAM_FORM_NOT_RESET = 92
    PATH_INVALID = 93
    WRONG_FOLDER = 94
    CRASH_AVOIDED = 99
    NO_STATS_FILES = 96
    VALID = 1
    USER_ELECTED_TO_TERMINATE = 95

    def __init__(self, function_id, constant_message_tuples):
        self.function_id = function_id
        self.cm_tuples = constant_message_tuples

class ErrorHandler:

    def __init__(self):
        self.error_log = []
        self.history = []
        self.messages = []

    def process_response(self, R):
        valid = 1
        counter = -1

        for response in R.cm_tuples:
            counter +=1
            if not response == ErrorHandler.VALID:
                valid = 0
            if valid:
                '''
                m = "VALID CALL"
                if R.messages[counter]:
                    m = R.messages[counter]
                '''
                self.history.append("function_id:" +R.function_id+ " valid.")
            else:
                self.error_log.append("error" + R.function_id + ErrorHandler.translate_error_constant(response[0])+ "," + response[1])

    def create_error_log_entry(self, R):
        for i in range(len(R.constants)):
            log = "Function ID:" + R.function_id + ":" + ErrorHandler.translate_error_constant(R.cm_tuples[i][0])
            R.messages
            log += ":: " + R.cm_tuples[i][1]
            self.error_log.append(log)

    @staticmethod
    def translate_error_constant(constant):
        if constant == R.FILE_DNE: return "File does not exist."
        elif constant == R.PATH_DNE: return "Path does not exist."
        elif constant == R.PRO_EXAM_FORM_NOT_RESET: return "Pro Exam form was not reset. Please create again."
        elif constant == R.CRASH_AVOIDED: return "Crash Avoided. Please report."
        elif constant == R.PATH_INVALID: return "Path Invalid"
        elif constant == R.WRONG_FOLDER: return "Wrong Folder. Check instructions."
        elif constant == R.NO_STATS_FILES: return "xCalibreOutput reports not located in folder."

