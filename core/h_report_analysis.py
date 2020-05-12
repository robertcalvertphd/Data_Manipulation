from core.h_file_handling import get_lines_from_X_to_Y_from_file
from core.h_file_handling import get_next_blank_line_after_index
from core.h_file_handling import get_df
from core.h_file_handling import write_lines_to_text
from core.h_file_handling import get_stem
from core.h_file_handling import get_all_file_names_in_folder
from core.h_file_handling import get_lines
from core.h_file_handling import get_all_folders_in_folder
from numpy import unique

import pandas as pd


#   this file contains helper functions for extracting meaningful data from reports.
#   the extracted data should export as a .txt file and its target is the test specialist in
#   charge of the test. Functions here should quickly extract information to answer questions
#   from specialists without much additional coding.

def get_first_line_of_stats(path_to_stats):
    i = 0
    lines = get_lines(path_to_stats)
    for line in lines:
        i += 1
        line_split = line.split(',')
        if len(line_split) > 0:
            if line_split[0] == "Sequence":
                return i


def convert_stats_to_df(path_to_stats, destination_path):
    first_line = get_first_line_of_stats(path_to_stats)
    try:
        blankLine = get_next_blank_line_after_index(path_to_stats, first_line - 1)
        f = get_lines_from_X_to_Y_from_file(path_to_stats, first_line - 1, blankLine)
        name = destination_path + get_stem(path_to_stats) + "_cs.csv"
        write_lines_to_text(f, name)
        df = get_df(name, header=0, dtype="string")
    except:
        pass

    return df


def get_top_n_rpbis(df, n):
    ret = df.sort_values(by='T-Rpbis', ascending=False)
    ret = ret.head(n)
    ret = ret[["Item ID", 'T-Rpbis']]
    return ret


def get_parameters(df):
    ret = df[["Item ID", 'a', 'b', 'c']]
    return ret


def get_low_performing_items(df, n=10):
    ret = df.sort_values(by='T-Rpbis')
    ret = ret.head(n)
    ret = ret[["Item ID", 'T-Rpbis']]
    return ret


def get_aggregate_report_items(df):
    ret = df.sort_values(by='Item ID')
    ret = ret[['Item ID', 'b', 'T-Rpbis', 'S-Rpbis', 'Flags']]
    return ret


def get_flagged_items(df):
    ret = df.sort_values(by='Flags')
    ret = ret[['Item ID', 'Flags']]
    ret = ret[ret.Flags.notnull()]
    ret = ret.sort_values(by='Item ID')
    return ret


def create_reports(path_to_stats, destination_path, is_cs=False):
    # todo: make this smarter. Look through for any stats files in folder or subfolders and then munch on them.
    destination_path += '/'
    if is_cs:
        files = get_all_file_names_in_folder(path_to_stats, target_string="_cs")
    else:
        files = get_all_file_names_in_folder(path_to_stats, target_string="Stats")

    for file in files:
        if is_cs:
            df = get_df(file, header=0)
        else:
            df = convert_stats_to_df(file, destination_path)
        high = get_top_n_rpbis(df, 20)
        low = get_low_performing_items(df)
        flagged = get_flagged_items(df)
        agg = get_aggregate_report_items(df)
        # parameters = get_parameters(df)
        name = get_stem(file) + "_c"
        high.to_csv(destination_path + name + "_high_.csv", index=False)
        low.to_csv(destination_path + name + "_low_.csv", index=False)
        flagged.to_csv(destination_path + name + "_flagged_.csv", index=False)
        agg.to_csv(destination_path + name + "_agg.csv", index=False)
        # parameters.to_csv(name + "_parameters_.csv", index=False)


def create_aggregate_report(path, destination_path, target_string, header_txt, sort_by):
    files = get_all_file_names_in_folder(path, target_string=target_string)
    file_name = destination_path + "/_aggregate_" + target_string + ".csv"
    write_lines_to_text([header_txt + "\n"], file_name)
    for file in files:
        lines = get_lines(file)
        write_lines_to_text(lines[1:], file_name, 'a')
    df = pd.read_csv(file_name, header=0)
    df = df.sort_values(by=sort_by, ascending=False)
    df.to_csv(file_name, index=False)


def create_aggregate_reports(path, destination_path):
    create_aggregate_report(path, destination_path, "high", "Item ID,T-Rpbis", "T-Rpbis")
    create_aggregate_report(path, destination_path, "low", "Item ID,T-Rpbis", "T-Rpbis")
    create_aggregate_report(path, destination_path, "flagged", "Item ID, Flags", "Item ID")
    create_aggregate_report(path, destination_path, "c_agg", "Item ID,b,T-Rpbis,S-Rpbis,Flags", "Item ID")


def create_all_reports(path_to_stats, destination_path):
    f = get_all_folders_in_folder(path_to_stats)
    f.append(path_to_stats)
    for p in f:
        create_reports(p, destination_path)


def get_descriptives(series):

    try:
        _mean = round(series.astype(float).mean(), 3)
        _min = round(series.astype(float).min(), 3)
        _max = round(series.astype(float).max(), 3)
        _range = round(_max - _min, 2)
        return _mean, _min, _max, _range
    except:
        return 0, 0, 0, 0

def get_flag_count(series):
    flags = ['La', 'Lb', 'K', 'Ha', 'Hb']
    ret = [0, 0, 0, 0, 0]
    for i in series:
        if i == i:
            for f in flags:
                try:
                    if isinstance(f, str):
                        if i.find(f) > -1:
                            ret[flags.index(f)] += 1
                except:
                    print("flag exception")
    return ret


def create_general_report_table(aggregate_cs_path, name, destination_path):
    flags = ['La', 'Lb', 'K', 'Ha', 'Hb']  # todo: sloppy
    suggestions = ["caution", "low_biserial", "negative_biserial", "high_B_range", "keyed_error", "good_irt"]
    df = get_df(aggregate_cs_path, header=0)
    unique_df = unique(df['Item ID']).tolist()

    lines = [["Item ID", "TR mean", "TR min", "TR max", "TR range", "SR mean", "SR min", "SR max", "SR range", "B mean",
              "B min", "B max", "B range", "count"]]
    for item in flags:
        lines[0].append(item)
    for s in suggestions:
        lines[0].append(s)
    good_irt = 0
    cautions = 0
    for id in unique_df:
        subset = df[df['Item ID'] == id]
        s = subset.copy()
        TR = get_descriptives(s['T-Rpbis'])
        SR = get_descriptives(s['S-Rpbis'])
        B = get_descriptives(s['b'])
        flags = subset["Flags"]
        flag_count = get_flag_count(flags)
        suggestion = get_suggestions(SR, TR, B, flag_count)
        if suggestion[1]: good_irt += 1
        if suggestion[2]: cautions += 1
        suggestion = suggestion[0]
        line = [id, TR[0], TR[1], TR[2], TR[3], SR[0], SR[1], SR[2], SR[3], B[0], B[1], B[2], B[3], len(subset)]
        for flag in flag_count:
            line.append(flag)
        for s in suggestion:
            line.append(s)
        lines.append(line)

    print("IRT:", good_irt, "of", len(lines), "=", str(round(good_irt * 100 / (len(lines) - 1), 2)) + "%")
    print("Cautions:", cautions, "of", len(lines), "=", str(round(cautions * 100 / (len(lines) - 1), 2)) + "%")
    report_df = pd.DataFrame(lines)
    final_report_name = destination_path+"/"+name+"_complete_.csv"
    report_df.to_csv( final_report_name , index=False, header=0)
    _df = pd.read_csv(final_report_name)
    for i in _df:
        print(i)
    caution = _df.where(_df['caution'] == True)
    irt = _df.where(_df['good_irt'] == True)
    caution = caution.dropna()
    irt = irt.dropna()
    caution.to_csv(destination_path + "/" + name +"_caution_.csv")
    irt.to_csv(destination_path + "/" + name +"_high_performers_for_irt_.csv")


# create_general_report_table("LCLE_IRT/aggregate__cs.csv")

# create_reports("PT_data/pt1_17")

def get_suggestions(SR, TR, B, flags):
    #   flags = ['La', 'Lb', 'K', 'Ha', 'Hb'] # todo: sloppy

    caution = False
    low_biserial = False
    negative_biserial = False
    high_difficulty_range = False
    keyed_error = False
    good_irt = False

    if SR[0] < .1 or TR[0] < .1:
        caution = True
        low_biserial = True
    elif SR[1] < 0 or TR[1] < 0:
        caution = True
        negative_biserial = True
    if abs(B[3]) > 1:
        caution = True
        high_difficulty_range = True
    if flags[2] > 0:
        caution = True
        keyed_error = True
    if TR[0] > .3 and B[3] < .5:
        caution = False
        good_irt = True
    ret = [caution, low_biserial, negative_biserial, high_difficulty_range, keyed_error, good_irt]
    return ret, good_irt, caution


def get_theta_for_item(path_to_scores, item_id):
    theta = None

    return theta


def get_theta_from_passing_percent_correct(percent_to_pass, path_to_tif):
    df = pd.read_csv(path_to_tif)
    SCORE_COL = "TRF"
    THETA_COL = "Theta"
    a = df.iloc[(df[SCORE_COL] - percent_to_pass).abs().argsort()[:1]]
    a = a[THETA_COL].values[0].astype(float)
    return get_stem(path_to_tif), int(a * 100) / 100


def get_theta_from_passing_score(passing_score, path_to_tif):
    df = pd.read_csv(path_to_tif)
    SCORE_COL = "TRF as Number Correct"
    THETA_COL = "Theta"
    a = df.iloc[(df[SCORE_COL] - passing_score).abs().argsort()[:1]]
    a = a[THETA_COL].values[0].astype(float)
    return get_stem(path_to_tif), int(a * 100) / 100

def get_passing_thetas_by_percentage(report_title, path_to_TIFs, aggregate_report_path, score = .7):
    passing_thetas = []
    files = get_all_file_names_in_folder(path_to_TIFs+"/", target_string="TIF")
    for file in files:
        a = get_theta_from_passing_percent_correct(score, file)
        passing_thetas.append(a)

    df = pd.DataFrame(passing_thetas)
    df.to_csv(aggregate_report_path + "/" + report_title + "_passing_thetas.csv", index=False, header=["FORM", "THETA"])


def get_passing_thetas_with_given_score(report_title, path_to_TIFs, aggregate_report_path, score = 34):
    passing_thetas = []
    files = get_all_file_names_in_folder(path_to_TIFs+"/", target_string="TIF")
    for file in files:
        a = get_theta_from_passing_score(score, file)
        passing_thetas.append(a)

    df = pd.DataFrame(passing_thetas)
    df.to_csv(aggregate_report_path + "/" + report_title + "_passing_thetas.csv", index=False, header=["FORM", "THETA"])


def get_passing_thetas(report_title):
    passing_thetas = []
    passing_thetas.append(get_theta_from_passing_score(34, "LMLE_IRT/LME_1_19A TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LMLE_IRT/LME_1_19A TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LMLE_IRT/LME_1_19A TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(34, "LMLE_IRT/LME_1_19A TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LCLE_IRT/xCalibreOutput/LCEE_4_17 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(36, "LCLE_IRT/xCalibreOutput/LCEE_4_19 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LCLE_IRT/xCalibreOutput/LCEE_7_16 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(36, "LCLE_IRT/xCalibreOutput/LCEE_7_19 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LCLE_IRT/xCalibreOutput/LCEE_7_17 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LCLE_IRT/xCalibreOutput/LCEE_7_18 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LCLE_IRT/xCalibreOutput/LCEE_10_17 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(35, "LCLE_IRT/xCalibreOutput/LCEE_10_18 TIF.csv"))
    passing_thetas.append(get_theta_from_passing_score(36, "LCLE_IRT/xCalibreOutput/LCEE_10_19 TIF.csv"))

    df = pd.DataFrame(passing_thetas)
    df.to_csv(report_title + "_passing_thetas.csv", index=False, header=["FORM", "THETA"])


#get_passing_thetas("LCLE")
# todo: remove items that have no item_id (old items) currently I just manually deleted them.

def create_all(xCalibre_report, aggregate_report_path, report_name):
    create_all_reports(xCalibre_report, aggregate_report_path)
    create_aggregate_reports(aggregate_report_path, aggregate_report_path)
    aggregate_file = aggregate_report_path + "/" + "_aggregate_c_agg.csv"
    create_general_report_table(aggregate_file, report_name, aggregate_report_path)
    get_passing_thetas_by_percentage(report_name, xCalibre_report, aggregate_report_path)


#create_all(xCalibre_report="LCLE_IRT/xCalibreOutput", aggregate_report_path="LCLE_IRT/reports", report_name="_LCEE_")

