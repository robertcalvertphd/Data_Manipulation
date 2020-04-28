from h_format_manipulators import get_lines_from_X_to_Y_from_file
from h_format_manipulators import get_next_blank_line_after_index
from h_format_manipulators import get_df
from h_format_manipulators import write_lines_to_text
from h_format_manipulators import get_stem
from h_format_manipulators import get_all_files_names_in_folder
from h_format_manipulators import get_lines
from h_format_manipulators import get_all_folders_in_folder
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
        i+=1
        line_split = line.split(',')
        if len(line_split)>0:
            if line_split[0] == "Sequence":
                return i


def convert_stats_to_df(path_to_stats, destination_path):
    first_line = get_first_line_of_stats(path_to_stats)
    blankLine = get_next_blank_line_after_index(path_to_stats, first_line - 1)
    f = get_lines_from_X_to_Y_from_file(path_to_stats, first_line - 1, blankLine)
    name = destination_path + get_stem(path_to_stats) + "_cs.csv"
    write_lines_to_text(f, name)
    df = get_df(name, header=0, dtype="string")
    return df


def get_top_n_rpbis(df, n):
    ret = df.sort_values(by='T-Rpbis', ascending=False)
    ret = ret.head(n)
    ret = ret[["Item ID", 'T-Rpbis']]
    return ret


def get_parameters(df):
    ret =df[["Item ID", 'a', 'b', 'c']]
    return ret


def get_low_performing_items(df, n = 10):
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


def create_reports(path_to_stats, destination_path, is_cs = False):
    #todo: make this smarter. Look through for any stats files in folder or subfolders and then munch on them.

    if is_cs:
        files = get_all_files_names_in_folder(path_to_stats,target_string="_cs")
    else:
        files = get_all_files_names_in_folder(path_to_stats, target_string="Stats")

    for file in files:
        if is_cs:
            df = get_df(file, header=0)
        else: df = convert_stats_to_df(file, destination_path)
        high = get_top_n_rpbis(df, 20)
        low = get_low_performing_items(df)
        flagged = get_flagged_items(df)
        agg = get_aggregate_report_items(df)
        #parameters = get_parameters(df)
        name = get_stem(file) + "_c"
        high.to_csv(destination_path + name+"_high_.csv", index=False)
        low.to_csv(destination_path + name + "_low_.csv", index=False)
        flagged.to_csv(destination_path + name+ "_flagged_.csv", index=False)
        agg.to_csv(destination_path + name + "_agg.csv", index = False)
        #parameters.to_csv(name + "_parameters_.csv", index=False)
        print("e")


def create_aggregate_report(path, destination_path, target_string, header_txt, sort_by):
    files = get_all_files_names_in_folder(path, target_string=target_string)
    file_name = destination_path + "_aggregate_"+target_string+".csv"
    write_lines_to_text([header_txt+"\n"], file_name)
    for file in files:
        lines = get_lines(file)
        write_lines_to_text(lines[1:], file_name, 'a')
    df = pd.read_csv(file_name, header=0)
    df = df.sort_values(by=sort_by, ascending=False)
    df.to_csv(file_name, index=False)


def create_aggregate_reports(path, destination_path):
    create_aggregate_report(path, destination_path,"high","Item ID,T-Rpbis","T-Rpbis")
    create_aggregate_report(path, destination_path, "low", "Item ID,T-Rpbis", "T-Rpbis")
    create_aggregate_report(path, destination_path, "flagged", "Item ID, Flags", "Item ID")
#    create_aggregate_report(path, "parameters", "Item ID, a,b,c", "Item ID")
    create_aggregate_report(path, destination_path,  "c_agg", "Item ID,b,T-Rpbis,S-Rpbis,Flags", "Item ID")


def create_all_reports(path_to_stats, destination_path):
    f = get_all_folders_in_folder(path_to_stats)
    f.append(path_to_stats)
    for p in f:
        create_reports(p, destination_path)
#p = "LCEE_data"


def get_descriptives(series):
    _mean = round(series.astype(float).mean(),3)
    _min = round(series.astype(float).min(),3)
    _max = round(series.astype(float).max(),3)
    return _mean, _min, _max

def get_flag_count(series):
    flags = ['La','Lb','K', 'Ha', 'Hb']
    ret = [0,0,0,0,0]
    for i in series:
        if i == i:
            for f in flags:
                try:
                    if isinstance(f, str):
                        if i.find(f)>-1:
                            ret[flags.index(f)]+=1
                except:
                    print("hu")
    return ret
def create_general_report_table(aggregate_cs_path):
    flags = ['La', 'Lb', 'K', 'Ha', 'Hb'] # todo: sloppy
    df = get_df(aggregate_cs_path, header=0)
    unique_df = unique(df['Item ID']).tolist()

    lines = [["Item ID", "TR mean", "TR min", "TR max", "SR mean", "SR min", "SR max", "B mean", "B min", "B max", "count"]]
    for item in flags:
        lines[0].append(item)

    print("hello")

    for id in unique_df:
        subset = df[df['Item ID']==id]
        s = subset.copy()
        for i in s:
            print(i)
        TR = get_descriptives(s['T-Rpbis'])
        SR = get_descriptives(s['S-Rpbis'])
        B = get_descriptives(s['b'])
        flags = subset["Flags"]
        flag_count = get_flag_count(flags)
        line = [id, TR[0], TR[1], TR[2], SR[0],SR[1], SR[2], B[0], B[1], B[2], len(subset)]
        for flag in flag_count:
            line.append(flag)
        lines.append(line)

    report_df = pd.DataFrame(lines)
    report_df.to_csv("final_LCLE_aggregate_report.csv",index=False, header=0)


        #   pull aggregate data
        #   setup entry by item_bank_id
        #   generate positive item report
        #       item id
        #       average T-Rpbis
        #       average P-Rpbis
        #       number of times high - performing
        #       number of times on a form
        #       difficulty range
        #       flags
        #   generate negative item report
        #       item id
        #       average T-Rpbis
        #       average P-Rpbis
        #       number of times low - performing
        #       number of times on a form
        #       flags


#create_general_report_table("LCEE_data/aggregate__cs.csv")

#create_reports("PT_data/pt1_17")

def get_theta_for_item(path_to_scores, item_id):
    theta = None

    return theta


def get_theta_from_passing_score(passing_score, path_to_tif):
    theta = None
    return theta

#todo: remove items that have no item_id (old items) currently I just manually deleted them.

#create_all_reports("LCEE_data/xCalibreOutput", "LCEE_data/processed_data/")
#create_aggregate_reports("LCEE_data/processed_data", "LCEE_data/processed_data/")
create_general_report_table("LCEE_data/processed_data/_aggregate_c_agg.csv")