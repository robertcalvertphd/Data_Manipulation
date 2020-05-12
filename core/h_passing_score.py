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
    if path_to_items:
        ids = h.get_df(path_to_items)
    else:
        ids = df_of_items
    agg = hfh.get_df(path_aggregate_data, header = 0)
    ids_sequence = ids[column_index_of_item_ids]
    a = agg['Item ID'].isin(ids_sequence)
    b = agg[a]['B mean']
    b_list = b.to_list()
    b_list = h.pd.to_numeric(b_list)
    m = b_list.mean()
    return b, m, len(b_list)


def evaluate_test_items(path_to_items, path_to_aggregate_data, passing_theta):
    ret = 0
    df = h.create_mapping_from_Karen_test_data(path_to_items)
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

def evaluate_past_tests(report_path, test_path, passing_theta):
    #LMLE_report = "LMLE_IRT/reports/_LMLE__complete_.csv"

    keys = hfh.get_all_file_names_in_folder(test_path, target_string="Test")
    keys2 = hfh.get_all_file_names_in_folder(test_path, target_string="Key")
    report = hfh.get_all_file_names_in_folder(report_path, target_string="complete" )
    if len(report)>1:
        print("there is more than 1 file with complete in the name in reports folder... this is a problem")
    report = report[0]
    for key in keys2:
        keys.append(key)

    results = []
    for key in keys:
        a = evaluate_test_items(key, report, passing_theta)
        results.append(a)
    df = hfh.pd.DataFrame(results)
    df.to_csv(report_path+"/"+"_passing.csv", header = None, index = 0)
report_path = "LMLE_IRT/reports/"
test_path = "LMLE_IRT/keys/"
evaluate_past_tests(report_path, test_path,-.2)

#score = get_test_score(-.2, "LCLE_IRT/processed_data/LCLEApr2018Test_L.csv", "final_LCLE_aggregate_report.csv")
#print(score)