from math import pow, e
import core.h_format_manipulators as h
hfh = h.hfh

#   this file is used to interact with known items to calculate a passing score from a test.


def get_p_for_item_given_theta_and_b(theta, B):
    y = theta - B
    top = pow(e, y)
    bottom = 1 + pow(e, theta-B)
    return top/bottom


def get_difficulties_of_items(df_of_items, path_aggregate_data, column_index_of_item_ids = 4, path_to_items = False):
    handled = []
    if path_to_items:
        ids = hfh.get_df(path_to_items)
    else:
        ids = df_of_items
    agg = hfh.get_df(path_aggregate_data, header = 0)
    ids_sequence = ids['bank_id'] # need to confirm that always has this name.
    sequence_list = ids_sequence.tolist()
    #ids_sequence = ids[column_index_of_item_ids].to_list()
    a = agg['Item ID'].isin(ids_sequence)
    b = agg[a]['B mean']

    #c = agg['Item ID'].tolist()
    #d = a.tolist()

    b_list = b.to_list()
    b_list = h.pd.to_numeric(b_list)
    m = b_list.mean()
    return b, m, len(b_list), a


def get_items_not_in_aggregate_data(path_to_items, path_to_aggregate_data, Karen_data = False, Amy_data = False):
    if Karen_data:
        df = h.create_mapping_from_Karen_test_data(path_to_items)
    elif Amy_data:
        df = h.create_key_df_from_csv(path_to_items)
    else:
        print("no data type selected in get_items_not_in_aggregate_data")
        return False
    agg = hfh.get_df(path_to_aggregate_data, header=0)
    df.columns = ['form', 'test_id', 'subject', 'bank_id_number', 'bank_id']
    df = df.drop([0])
    #todo learn to use merge better and pandas in general
    a = agg['Item ID'].tolist()
    b = df['bank_id'].tolist()
    ret = []
    for key_id in b:
        if not key_id in a:
            ret.append(key_id)
    return ret


def evaluate_test_items(path_to_items, path_to_aggregate_data, passing_theta, Karen_data = False, Amy_data = False):
    ret = 0
    if Karen_data:
        df = h.create_mapping_from_Karen_test_data(path_to_items)
    elif Amy_data:
        df = h.create_key_df_from_csv(path_to_items)
    else:
        print("evaluate test items did not know what type of data it was dealing with")
        return False
    diff = get_difficulties_of_items(df, path_to_aggregate_data)
    bs = diff[0]
    for b in bs:
        x = get_p_for_item_given_theta_and_b(passing_theta, float(b))
        ret += x

    know = ret
    guess = len(bs)-know
    guess = guess*0
    #   consider modification but it seems that there is a better than odds chance on guessing (eliminate 1)
    predicted_correct = know + guess
    #print (hfh.get_stem(path_to_items), predicted_correct/len(bs), diff[1], diff[2])
    return [hfh.get_stem(path_to_items), predicted_correct/len(bs), diff[1], diff[2]]

def create_key_from_control_file(control_path, path_to_keys):
    #assumes control does not have header
    df = hfh.get_df(control_path)
    df.columns = ["ID","b","c","d","e","f"]
    ids = df['ID'].to_list()
    ret = ["Position,AccNum\n"]
    counter = 0
    for id in ids:
        counter+=1
        line = str(counter)+","+id+"\n"
        ret.append(line)
    name = path_to_keys +"/"+ hfh.get_stem(control_path)+"_KEY.csv"
    hfh.write_lines_to_text(ret,name)

def create_key_from_L_file(L_file, path_to_keys):
    lines = hfh.get_lines(L_file)[1:]
    counter = 0
    ret = ["Position,AccNum\n"]
    for line in lines:
        counter += 1
        split_line = line.split(",")
        ret.append(str(counter)+"," + split_line[4])
    file_path = path_to_keys + "/" + hfh.get_stem(L_file)[:-2] + "_KEY.txt"
    hfh.write_lines_to_text(ret, file_path)

def evaluate_past_tests(report_path, test_path, passing_theta, key_strings = ['Key','KEY','Test'], Karen_data = False, Amy_data = False, ):
    #LMLE_report = "LMLE_IRT/reports/_LMLE__complete_.csv"

    keys = []
    for k in key_strings:
        files = hfh.get_all_file_names_in_folder(test_path, target_string=k)
        for f in files:
            keys.append(f)

    report = hfh.get_all_file_names_in_folder(report_path, target_string="complete" )
    if len(report)>1:
        print("there is more than 1 file with complete in the name in reports folder... this is a problem")
    report = report[0]

    records = []
    for key in keys:
        record = []
        a = evaluate_test_items(key, report, passing_theta, Amy_data = Amy_data, Karen_data= Karen_data)
        for item in a:
            record.append(item)
        missing_items = get_items_not_in_aggregate_data(key,report, Amy_data=Amy_data, Karen_data = Karen_data)
        missing_items.sort()
        for item in missing_items:
            record.append(item)
        records.append(record)
    df = hfh.pd.DataFrame(records)
    df.to_csv(report_path+"/"+"_passing.csv", header = None, index = 0)


def make_key_of_n_top_B_from_complete(complete_file, key_path, n):
    df = hfh.get_df(complete_file, header = 0)
    df = df.sort_values(by = "B mean", ascending=False)
    ids = df.head(n)['Item ID'].tolist()
    counter = 0
    ret = []
    for i in ids:
        counter+=1
        ret.append([counter,i])
    ret_df = hfh.pd.DataFrame(ret)
    ret_df.columns = ["Position","AccNum"]
    ret_df.to_csv(key_path+"/"+"topDiff_KEY.csv", index = False)
    print("hello")

#report_path = "LMLE_IRT/reports/"
#test_path = "LMLE_IRT/keys/"
#evaluate_past_tests(report_path, test_path,1)
#score = get_test_score(-.2, "LCLE_IRT/processed_data/LCLEApr2018Test_L.csv", "final_LCLE_aggregate_report.csv")
#print(score)