import core.h_file_handling as hfh
import core.h_format_manipulators as h
from core.e_handler import R
import core.h_user_input as u
from numpy import nan

from core.h_Rasch_report_analysis import create_aggregate_report
pd = hfh.pd
os = hfh.os

def create_master_file(report_name = False, xCalibre_output_path = False, reports_path = False, master_folder = False):
    function_id = "h_2p_report_analysis|create_master_file"
    r_entries = [] # list of tuples constant, message
    if master_folder:
        #confirm master folder does not end in /
        if master_folder[-1] == '/':
            master_folder = master_folder[:-1]
        reports_path = master_folder + "/reports"
        xCalibre_output_path = master_folder + "/xCalibreOutput"
        search_name = master_folder[:-1]
        report_name = master_folder[search_name.rfind('/')+1:]
    if not report_name:
        u.get_string("What would you like to title the report?")

    path = xCalibre_output_path
    if not xCalibre_output_path:
        path = u.get_folder("Locate the xCalibreOutput reports folder", required=False)
        if not path:
            r_entries.append([R.PATH_INVALID,"Invalid xCalibrePath:" + path])
            f = hfh.get_parent_folder(path)
            if not f == 'xCalibreOutput':
                r_entries.append([R.WRONG_FOLDER," must select xCalibreOutput folder"])

    if not reports_path:
        reports_path  = u.get_folder("Choose a folder for generated reports.", required=False)
        if not reports_path:
            r_entries.append([R.PATH_INVALID, "Invalid report path:" + path])
        if hfh.get_parent_folder(reports_path) != "xCalibreOutput":
            r_entries.append([R.WRONG_FOLDER,"Not xCalibreOutput"])

    if os.path.isdir(reports_path):
        stats_files = hfh.get_all_files(xCalibre_output_path, "Stats")
        if len(stats_files) == 0:
            r_entries.append([R.NO_STATS_FILES, "xCalibreOutput reports:" + path])
        else:
            process_stats_files(stats_files, reports_path, report_name)
        if len(r_entries) == 0:
            r_entries.append([R.VALID,"create_master_file executed"])
    return R(function_id,r_entries)

def process_stats_files(stats_files, reports_path, report_name):
    r_entries = []  # list of tuples constant, message
    header = False
    ret = []
    header_index = 0
    for file in stats_files:
        lines = hfh.get_lines(file)
        header_index = hfh.get_index_of_line_that_starts_with_word_based_on_delimiter(lines,'Sequence')
        blank_index = hfh.get_next_blank_line_after_index_from_lines(lines, header_index)
        if not header:
            ret_lines = lines[header_index:blank_index+header_index]
            header = True
        else:
            ret_lines = lines[header_index+1:blank_index+header_index]
        for line in ret_lines:
            ret.append(line)
        # use ret to make master df
    aggregate_report_path = reports_path+"/"+report_name+"_aggregate_.csv"
    hfh.write_lines_to_text(ret, aggregate_report_path)
    df = pd.read_csv(aggregate_report_path)
    df = df[['Item ID', 'S-Rpbis', 'T-Rpbis','P','a','b','Flags']]
    df['K'] = 0
    df['La'] = 0
    df['Lb'] = 0

    mask_K = df['Flags'].str.contains(r'K', na=False)
    mask_Lb = df['Flags'].str.contains(r'Lb', na=False)
    mask_La = df['Flags'].str.contains(r'La', na=False)

    df.loc[mask_K, 'K'] = 1
    df.loc[mask_La, 'La'] = 1
    df.loc[mask_Lb, 'Lb'] = 1

    df['count'] = df['Item ID'].map(df['Item ID'].value_counts())
    df = add_descriptives_to_df_by_group(df, 'Item ID', 'a')
    df = add_descriptives_to_df_by_group(df, 'Item ID', 'b')
    df = add_descriptives_to_df_by_group(df, 'Item ID', 'T-Rpbis')
    df = add_descriptives_to_df_by_group(df, 'Item ID', 'S-Rpbis')
    df = add_descriptives_to_df_by_group(df, 'Item ID', 'P')

    df = df.sort_values('Item ID')
    df.to_csv(aggregate_report_path)
    df_new = df['Item ID'].apply(get_id_from_item_id)
    df = pd.concat([df, df_new], axis=1)
    df = df.sort_values('Item ID').groupby(['Item ID']).first()

    df['Caution'] = 0
    df['Good'] = 0

    mask1 = (df['K'] == 2) | (df['Lb'] == 1)
    df.loc[mask1, 'Caution'] = 1

    mask2 = (df['Caution'] == 0) & (df['a_mean'] > 1) & (df['T-Rpbis_mean'] > .3)
    df.loc[mask2, 'Good'] = 1

    df = df.drop(['S-Rpbis','T-Rpbis','P','a','b','Flags'], axis = 1)
    df.to_csv(reports_path + "/" + report_name + "_complete_.csv")


def get_id_from_item_id(item_id):
    i = [x.isdigit() for x in item_id].index(True)

    return pd.Series({
        'area': item_id[:i],
        'number': item_id[i:]
    })


def add_descriptives_to_df_by_group(df, group, column_name):
    #change removed value to nan
    df = df.replace('Removed', nan)
    df[column_name] = pd.to_numeric(df[column_name])
    df[column_name+"_mean"] = df.groupby(group)[column_name].transform('mean')
    df[column_name+"_min"] = df.groupby('Item ID')[column_name].transform('min')
    df[column_name+"_max"] = df.groupby('Item ID')[column_name].transform('max')
    df[column_name+"_range"] = df[column_name+"_max"] - df[column_name + '_min']
    return df
#   creates unique entries per item


'''
xCal = "G:/LICENSING EXAMINATION/Robert/data/LEX/xCalibreOutpuxt"
rep = "G:/LICENSING EXAMINATION/Robert/data/LEX/reports"
create_master_file("LEX",xCal, rep)
'''