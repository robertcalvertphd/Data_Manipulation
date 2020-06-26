import os
import math
import core.h_format_manipulators as h
import core.h_file_handling as hfh
import core.h_stats as s

pd = h.pd
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo, FactorAnalyzer
from sklearn.decomposition import PCA as p


def can_use_factor_analysis(df):
    #   ignore bartlett for the time being but is there in case I want it.
    #chi_square_value, p_value = calculate_bartlett_sphericity(df)
    #print(chi_square_value, p_value)

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

    matrix_file = irt_folder +"/xCalibreOutput/"+ report_name + ' Matrix.txt'
    if os.path.isfile(matrix_file):
        matrix_df = h.convert_xCalibre_matrix_for_PCI(matrix_file, include_id=True)
        matrix_df = matrix_df.apply(pd.to_numeric, errors = 'ignore')
        print("hello")

    else:
        print("matrix file does not exist")
        return 0

    test_df = matrix_df
    test_df = test_df.drop(columns = 0)
    test_df.to_csv("fa_test.csv")
    r = s.run_factor_analysis(test_df)
    test_df['ID'] = matrix_df[0]
    matrix_df = matrix_df.drop(columns = 0)
    matrix_df['SCORE'] = matrix_df.sum(axis = 1)
    matrix_df['ID'] = test_df['ID']


    cleaned_stats = irt_folder + "/xCalibreOutput/"+report_name+".cleaned_stats"
    if os.path.isfile(cleaned_stats):
        stats_df = hfh.get_df(cleaned_stats, header = 0)
    else:
        unclean_path = irt_folder+'/'+"xCalibreOutput/"+report_name + " Stats.csv"
        stats_df = h.clean_stats_csv(unclean_path, get_df=True)

    stats_df = stats_df.apply(pd.to_numeric, errors = 'ignore')
    tif_path = irt_folder + "/xCalibreOutput/"+report_name+" TIF.csv"
    tif_df = hfh.get_df(tif_path, header = 0)
    tif_df = tif_df.apply(pd.to_numeric, errors = 'ignore')
    matrix_df = set_theta_from_score_in_matrix_df(tif_df, matrix_df)

    residuals_df = get_residuals(matrix_df, stats_df)
    residuals_df = residuals_df.apply(pd.to_numeric, errors = 'ignore')
    residuals_df = residuals_df.reset_index()
    residuals_df = residuals_df.drop(columns = 'index')
    residuals_df.to_csv("resid_test.csv", index = True)
    residuals_df.to_excel("resid_test.xlsx", index=True)
    print(can_use_factor_analysis(residuals_df))
    again = s.run_factor_analysis(residuals_df)
    again_df = pd.DataFrame(again).head(5)
    again_df.to_csv("python_variance_explained.csv")
    print("hello")

def set_theta_from_score_in_matrix_df(tif_df, matrix_df):
    scores = matrix_df['SCORE']
    ret = []

    for score in scores:
        try:
            #   get row with closest value
            theta = tif_df.iloc[(tif_df['TRF as Number Correct'] - score).abs().argsort()[:1]]
            #   select TRF
            theta = theta['Theta'].values[0]
            ret.append(theta)
        except:
            pass
    matrix_df['PERSON_THETA']=ret

    return matrix_df


def get_residuals(matrix_df, stats_df):
    #   loop through columns of matrix_df calculating residuals for each row.
    person_level_residuals = pd.DataFrame()
    person_level_standardized = pd.DataFrame()
    for i, row in matrix_df.iterrows():
        standardized_residuals = []
        residuals = []
        for j, col in matrix_df.iteritems():
            person_theta = row['PERSON_THETA']
            id = row['ID']
            if str(j).isnumeric() and j > 0:
                actual = row[j]
                b = stats_df['b'].iloc[j-1]
                if b == 'Removed' or pd.isna(b) or b == 'Pretest':
                    print('omitted removed item.')
                else:
                    b = float(b)
                    expected = s.get_p_for_item_given_theta_and_b(theta=person_theta, B=b)
                    p = expected
                    q = 1-expected
                    var = p*q
                    std = math.pow(var,.5)
                    residual = actual - expected
                    residuals.append(residual)
                    standardized_residual = residual/std
                    standardized_residuals.append(standardized_residual)

            if j == 'SCORE':    #sloppy revise later
                name = str(id)+"_res"
                person_level_residuals[name] = residuals
                person_level_standardized[name] = standardized_residuals

    residuals_df = person_level_residuals.T
    standardized_df = person_level_standardized.T
    return residuals_df, standardized_df