import core.h_format_manipulators as h
hfh = h.hfh

def remove_duplicates(path_to_csv, column1, column2, column3):
    df = hfh.get_df(path_to_csv,header=0)
    df = df.drop_duplicates(subset = [column1,column2,column3])
    df = df.sort_values([column1,column2,column3], ascending=False)
    return df


def get_pass_fail_by_exam(df, exam_name):
    exam_subset = df[df['Exam'] == exam_name]
    OJT_subset_of_exam = exam_subset[exam_subset["Path"] == "OJT"]
    EDU_subset_of_exam = exam_subset[exam_subset["Path"] == "EDU"]
    OJT_pass = OJT_subset_of_exam[OJT_subset_of_exam["Passing"] == "Pass"].count()["Passing"]
    EDU_pass = EDU_subset_of_exam[EDU_subset_of_exam["Passing"] == "Pass"].count()["Passing"]
    OJT_attempts = OJT_subset_of_exam.count()["Passing"]
    EDU_attempts = EDU_subset_of_exam.count()["Passing"]
    return OJT_pass, OJT_attempts, OJT_pass/OJT_attempts,EDU_pass, EDU_attempts,EDU_pass/EDU_attempts, OJT_subset_of_exam, EDU_subset_of_exam
    # 13 people passed without a recorded score


def get_passed_both(written, law_ethics):
    #merged data
    p = written.merge(law_ethics, how = "outer", on = "Name") #contains multiple entries per person
    #p.loc[p[(p.Passing_x =="Pass") & (p.Passing_y == "Pass")], 'Passed_Flag'] = 1

    #unique test_takers
    up = p.drop_duplicates(subset = ["Name"])
    up = up.sort_values("Exam_Date_x", ascending=False)
    #passed both
    pb = p[(p.Passing_x =="Pass") & (p.Passing_y == "Pass")]
    #pb["Passed_Flag"] = 1

    #unique passed both
    upb = pb.drop_duplicates(subset = ["Name"])
    n = up.count()["Name"]
    p = upb.count()["Name"]
    return p, n, p/n

def passed_combined(combined):
    p = combined
    up = p.drop_duplicates(subset=["Name"])
    pb = up[up.Passing == "Pass"]
    upb = pb.drop_duplicates(subset=["Name"])
    n = up.count()["Passing"]
    p = upb.count()["Passing"]
    return p, n, p / n

def process(data_file):
    OJT_PASS = 0
    OJT_ATTEMPTS = 1
    OJT_PERCENT = 2
    EDU_PASS = 3
    EDU_ATTEMPTS = 4
    EDU_PERCENT = 5
    OJT_DF = 6
    EDU_DF = 7

    df = remove_duplicates(data_file, "Name", "Exam", "Exam_Date")
    rda_LE = get_pass_fail_by_exam(df,"RDA L&E - RDA Law and Ethics")
    rda_W = get_pass_fail_by_exam(df,"RDA WRIT - RDA Written")
    rda_C = get_pass_fail_by_exam(df,"RDAC - RDA Combine")
    OJT_both = get_passed_both(rda_LE[OJT_DF], rda_W[OJT_DF])
    EDU_both = get_passed_both(rda_LE[EDU_DF], rda_W[EDU_DF])
    OJT_combined = passed_combined(rda_C[OJT_DF])
    EDU_combined = passed_combined(rda_C[EDU_DF])

    print(rda_C[:6])
    print(rda_W[:6])
    print(rda_LE[:6])
    print(OJT_both[:2])
    print(EDU_both[:2])
    print(OJT_combined[:2])
    print(EDU_combined[:2])

process("RDA_16_20_all.csv")