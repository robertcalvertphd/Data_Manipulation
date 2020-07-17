import os
import math
import core.h_format_manipulators as h
import core.h_reports as hr
import core.h_file_handling as hfh
import core.h_stats as s
import core.h_2p_report_analysis as two_p
from numpy import nan

pd = h.pd
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo, FactorAnalyzer
from sklearn.decomposition import PCA as p


def can_use_factor_analysis(df):
    #   ignore bartlett for the time being but is there in case I want it.
    # chi_square_value, p_value = calculate_bartlett_sphericity(df)
    # print(chi_square_value, p_value)

    a = calculate_kmo(df)
    if a[1] < .6:
        return False
    print("kmo = " + str(a))
    return True


def get_residuals_from_item_person(irt_folder, report_name):
    '''
    #   get df for factor analysis

    #   irt_folder has reports, xCalibreOutput and processed_data
    #   get theta from matrix
    #   get items from Stats    *not really needed for this analysis* only relevant if looking up aggregate
    #   get difficulties from Stats
    #       a different analysis would get difficulty from aggregate

    #   general process thoughts:
    #       I think I just check the raw score and then associate.
    #       residual = observed - expected (0-1)
    #       observed is 1 or 0 and comes from matrix file
    #       expected is calculated from difficulty and theta
    #       results in list of residuals which will be a row

    #  steps
        #   get matrix
        #   for person
        #       calculate person score
        #       get theta for person
        #       check each item for residual needs item difficulty
        #       write results to row
    '''

    matrix_file = irt_folder + "/xCalibreOutput/" + report_name + ' Matrix.txt'
    if os.path.isfile(matrix_file):
        matrix_df = h.convert_xCalibre_matrix_for_PCI(matrix_file, include_id=True)
        matrix_df = matrix_df.apply(pd.to_numeric, errors='ignore')
        print("hello")

    else:
        print("matrix file does not exist")
        return 0

    test_df = matrix_df
    test_df = test_df.drop(columns=0)
    test_df.to_csv("fa_test.csv")
    r = s.run_factor_analysis(test_df)
    test_df['ID'] = matrix_df[0]
    matrix_df = matrix_df.drop(columns=0)
    matrix_df['SCORE'] = matrix_df.sum(axis=1)
    matrix_df['ID'] = test_df['ID']

    cleaned_stats = irt_folder + "/xCalibreOutput/" + report_name + ".cleaned_stats"
    if os.path.isfile(cleaned_stats):
        stats_df = hfh.get_df(cleaned_stats, header=0)
    else:
        unclean_path = irt_folder + '/' + "xCalibreOutput/" + report_name + " Stats.csv"
        stats_df = h.clean_stats_csv(unclean_path, get_df=True)

    stats_df = stats_df.apply(pd.to_numeric, errors='ignore')
    tif_path = irt_folder + "/xCalibreOutput/" + report_name + " TIF.csv"
    tif_df = hfh.get_df(tif_path, header=0)
    tif_df = tif_df.apply(pd.to_numeric, errors='ignore')
    matrix_df = set_theta_from_score_in_matrix_df(tif_df, matrix_df)

    residuals_df = s.get_residuals(matrix_df, stats_df)
    residuals_df = residuals_df.apply(pd.to_numeric, errors='ignore')
    residuals_df = residuals_df.reset_index()
    residuals_df = residuals_df.drop(columns='index')
    residuals_df.to_csv("resid_test.csv", index=True)
    residuals_df.to_excel("resid_test.xlsx", index=True)
    print(can_use_factor_analysis(residuals_df))
    again = s.run_factor_analysis(residuals_df)
    again_df = pd.DataFrame(again).head(5)


def set_theta_from_score_in_matrix_df(tif_df, matrix_df):
    scores = matrix_df.sum(axis=1)
    ret = []

    for score in scores:
        #   get row with closest value
        theta = tif_df.iloc[(tif_df['TRF as Number Correct'].astype(float) - score).abs().argsort()[:1]]
        #   select TRF
        theta = theta['Theta'].values[0]
        ret.append(theta)

    matrix_df['PERSON_THETA'] = ret

    return matrix_df


# todo create residuals once and then pass them around...
def get_residuals_by_difficulty(matrix_df, stats_df, tif_df, _residuals = None):
    if _residuals is None:
        r = s.get_residuals(matrix_df, stats_df, tif_df)
    r = _residuals
    residuals = r[0]
    standardized_residuals = r[1]
    difficulty_factor_analysis_results = []
    difficulty_ranges = []
    partitions = 10

    for i in range(partitions):
        max = partitions/2-i
        min = partitions/2 - (i + 1)
        difficulty_ranges.append([min, max])

    for r in difficulty_ranges:
        d_mask = (stats_df['b'].astype(float) > r[0]) & (stats_df['b'].astype(float) <= r[1])
        a = d_mask.index[d_mask]
        a = [float(item) for item in a]
        d_df = residuals.iloc[:, a]
        d_df = d_df.dropna(axis=1)
        if d_df.shape[1] > 1:
            b = s.run_factor_analysis(d_df)
            difficulty_factor_analysis_results.append([b,r])

    return difficulty_factor_analysis_results


def get_residuals_by_domain(matrix_df, stats_df, tif_df):
    domains = stats_df['Domain'].unique()
    r = s.get_residuals(matrix_df, stats_df, tif_df)
    residuals = r[1]
    standardized_residuals = r[2]
    domain_factor_analysis_results = []

    for domain in domains:
        # items are denoted by numbers should be able to make a list of each domain and then mask from list.
        d_mask = stats_df['Domain'] == domain
        a = d_mask.index[d_mask]
        a = [float(item) for item in a]
        d_df = residuals.iloc[:, a]
        d_df = d_df.dropna(axis=1)
        b = s.run_factor_analysis(d_df)
        domain_factor_analysis_results.append(b)
        print("hello")
    residuals = residuals.dropna(axis=1)
    c = s.run_factor_analysis(residuals)
    domain_factor_analysis_results.append(c)
    print("hello")
    return domain_factor_analysis_results, r

def lamda_practice(difficulties, thetas):
    return difficulties.astype(float)*thetas.astype(float)

    '''
def get_residuals(matrix_df, stats_df, tif_df):
    # get_residuals_by_domain(matrix_df, stats_df, tif_df)
    #   loop through columns of matrix_df calculating residuals for each row.
    person_level_residuals = pd.DataFrame()
    person_level_standardized = pd.DataFrame()
    matrix_df = set_theta_from_score_in_matrix_df(tif_df, matrix_df)

    #todo: matrix df is wrong in rows 1 and 2

    difficulties = stats_df['b']
#   matrix_df['test'] = matrix_df.apply(lambda x: lamda_practice(difficulties, matrix_df['PERSON_THETA']))
    for i, person in matrix_df.iterrows():
        standardized_residuals = []
        residuals = []
        person_theta = person['PERSON_THETA']
        pass
    '''
    '''
    #todo: make matrix_df match stats_df (remove na rows)
    for i, row in matrix_df.iterrows():
        standardized_residuals = []
        residuals = []
        for j, col in matrix_df.iteritems():
            person_theta = row['PERSON_THETA']
            # id = row['ID']
            if str(j).isnumeric() and j > -1:
                actual = row[j]
                try:
                    b = stats_df['b'].iloc[i - 1]
                except:
                    pass
                if b == 'Removed' or pd.isna(b) or b == 'Pretest':
                    residuals.append(nan)
                else:
                    b = float(b)
                    expected = s.get_p_for_item_given_theta_and_b(theta=person_theta, B=b)
                    p = expected
                    q = 1 - expected
                    var = p * q
                    std = math.pow(var, .5)
                    residual = actual - expected
                    residuals.append(residual)
                    standardized_residual = residual / std
                    standardized_residuals.append(standardized_residual)

  
        name = str(i) + "_res"
        person_level_residuals[name] = residuals
        person_level_standardized[name] = standardized_residuals
        '''
    residuals_df = person_level_residuals.T
    standardized_df = person_level_standardized.T
    return residuals_df, standardized_df


def evaluate_in_fit_out_fit(stats_df):
    df = stats_df

    #   check that file is 2 parameter IIF
    eval = pd.DataFrame()
    if "In-MSQ" in df.columns and "Out-MSQ" in df.columns:
        df = stats_df[['In-MSQ', 'Out-MSQ', 'b', 'z Resid']]
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna(axis=0)

        df['B_EVAL'] = 0
        df['IN_DEV'] = abs(1 - df['In-MSQ'])
        df['OUT_DEV'] = abs(1 - df['Out-MSQ'])
        df.loc[df['IN_DEV'] > .5, 'IN_DEV_EVAL'] = -2
        df.loc[df['IN_DEV'] < .5, 'IN_DEV_EVAL'] = -1
        df.loc[df['IN_DEV'] < .2, 'IN_DEV_EVAL'] = 1

        df.loc[df['OUT_DEV'] > .5, 'OUT_DEV_EVAL'] = -2
        df.loc[df['OUT_DEV'] < .5, 'OUT_DEV_EVAL'] = -1
        df.loc[df['OUT_DEV'] < .2, 'OUT_DEV_EVAL'] = 1

        df['B_EVAL'] = 1
        df.loc[abs(df['b']) > 3, 'B_EVAL'] = -2

        df['AccNUM'] = stats_df["Item ID"]
        df['Domain'] = stats_df['Domain']

        return df
    else:
        print("It appears you asked for a Rasch analysis of fit for a non Rasch model")


def evaluate_item_discrimination(stats_df):
    # df = stats_df
    df = pd.DataFrame()
    if "In-MSQ" in df.columns and "Out-MSQ" in df.columns:
        print("It appears you asked for a 2 parameter analysis discrimination but fed it Rasch data.")
    else:
        df['Domain'] = stats_df['Domain']
        df['A'] = stats_df['a']
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.dropna(axis=0)
        df['A_DEV'] = abs(1 - df['A'])

        df.loc[df['A_DEV'] > .5, 'A_DEV_EVAL'] = -2
        df.loc[df['A_DEV'] < .5, 'A_DEV_EVAL'] = -1
        df.loc[df['A_DEV'] < .2, 'A_DEV_EVAL'] = 1

    return df


def evaluate_max_info(stats_df, tif, passing_proportion):
    # get theta for passing
    theta = float(tif.iloc[(tif['TRF'].astype(float) - passing_proportion).abs().argsort()[:1]]['Theta'].values[0])
    #   returns distance between max and passing as series
    work_df = stats_df
    work_df = stats_df.apply(pd.to_numeric, errors='coerce')
    work_df = work_df[work_df['Theta at Max'].notna()]
    stats_df['Theta_delta'] = work_df['Theta at Max'].astype(float)-theta
    #stats_df['Theta_percent'] = s.get_percent_from_theta(stats_df['Theta at Max'].astype(float),"no path", tif_df=tif)
    return stats_df['Theta_delta']




