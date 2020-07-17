import core.h_file_handling as hfh
import core.h_format_manipulators as h
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import (pairwise_tukeyhsd)
import statsmodels.api as sm
from scipy.stats import chi2
import pandas as pd
import os
from math import pow, e
from sklearn.decomposition import PCA as p
from sklearn.decomposition import FactorAnalysis
import factor_analyzer as f



def grade_responses(data_file, control_file):
    # todo: this has been back burnered so assumption item assessment can be finished.
    # this assumes that data has been processed
    a = os.path.isfile(data_file)
    b = os.path.isfile(control_file)
    data_df = h.get_data_df(data_file)
    control_df = hfh.get_df(control_file)
    ret_df = data_df
    answers = control_df.iloc[:,1]
    ids = data_df.iloc[:,0]
    data_df = data_df.drop(columns = 0)
    data_df.index = data_df.index+1
    for col in range(data_df.shape[0]-1):
        for row in range(data_df.shape[1]):
            individuals_answers = data_df.loc[row+1]
            #   data_df[data_df.loc[row+1]==individuals_answers,'q'+str(row+1)] = 1
            #   b = control_df.iloc[row,1]
            print(a,b)
            #ret_df.loc[row][data_df[col] == control_df.iloc[row,1], "q"+str(col)] = 1
    print("hello")



def get_group_stats(df):
    group_var = "GROUP"
    target_var = 'TARGET'
    mean = df.groupby(group_var).mean()
    std = df.groupby(group_var).std()
    n = df.groupby(group_var).count()
    ret = mean
    ret['STD'] = std[target_var]
    ret['n'] = n[target_var]
    return ret


def get_group_df(df, target_index = None, target_name = None, group_index = None, group_name = None):
    work_df = pd.DataFrame()
    target = False
    group = False
    if target_index is not None:
        target = True
        work_df['TARGET'] = df.iloc[:,target_index]
    if group_index is not None:
        group = True
        work_df['GROUP'] = df.iloc[:,group_index]
    if target_name:
        if target:
            print("error: two targets assigned in get_group_df")
        else:
            target = True
            work_df['TARGET'] = df[target_name]
    if group_name:
        if group:
            print("error: two groups assigned in get_group_df")
        else:
            group = True
            work_df['GROUP'] = df[group_name]
    if target and group:
        return work_df
    else:
        print("error: did not identify target and group in get_group_df")
        return False
        return False


def ANOVA(df):
    target = df.columns[0]
    group_var_name = df.columns[1]
    cmd = target + "~" + group_var_name
    work_df = pd.DataFrame()
    work_df[group_var_name] = df[group_var_name]
    work_df = work_df.dropna(axis=0)
    mod = ols(cmd, data=work_df).fit()
    aov_table = sm.stats.anova_lm(mod, typ=2)
    print(aov_table)
    res2 = pairwise_tukeyhsd(work_df[target], work_df[group_var_name])
    print(res2)


def ANOVA_output(res2, df_of_means):
    pass


def run_pca(df):
    pca = p()
    pca.fit(df)
    ratios = pca.explained_variance_ratio_
    return ratios


def run_factor_analysis(df):
    '''
    transformer = FactorAnalysis(n_components=7, random_state=0)
    X_transformed = transformer.fit_transform(df)
    a = transformer.get_params()
    b = transformer.get_covariance()
    c = transformer.get_precision()
    print("hello")
    '''

    fa = f.FactorAnalyzer(rotation=None)
    fa.use_smc = False
    a = fa.fit(df)
    b = fa.get_eigenvalues()
    return b[0]

def set_person_theta(matrix_df = None, tif_df = None):
    if matrix_df is None or tif_df is None:
        print("get_theta must be fed a matrix_df and tif_df")
        return False
    score = matrix_df.sum(axis = 1)
    n = matrix_df.shape[1]
    averages = score/n
    #inefficient I would like to get apply working
    ret = []
    for a in averages:
        x = tif_df.iloc[(tif_df['TRF'].astype(float) - a).abs().argsort()[:1]]['Theta'].values[0]
        x = float(x)
        ret.append(x)
    s = pd.Series(ret)
    matrix_df['PERSON_THETA'] = s
    return matrix_df


def get_theta_from_percent_correct(percent, path_to_tif = None, tif_df = None, return_stem = True,):
    if tif_df is None:
        df = pd.read_csv(path_to_tif)
    else:
        df=tif_df
    SCORE_COL = "TRF"
    THETA_COL = "Theta"
    a = df.iloc[(df[SCORE_COL].astype(float) - percent).abs().argsort()[:1]]
    a = a[THETA_COL].values[0].astype(float)
    if return_stem:
        return hfh.get_stem(path_to_tif), int(a * 100) / 100
    return int(a * 100) / 100


def process_response_string_for_classical_upload(data_file, control_file):
    data_df = hfh.get_df(data_file)
    control_df = hfh.get_df(control_file)



def get_percent_from_theta(theta, path_to_tif = None, tif_df = None, return_values = True, return_df = False):
    if path_to_tif is None and tif_df is None:
        print("get_percent_from_theta was not passed a tif path or df.")
    else:
        if tif_df is None:
            df = pd.read_csv(path_to_tif)
        else:
            df=tif_df
        SCORE_COL = "TRF"
        THETA_COL = "Theta"
        a = df.iloc[(df[THETA_COL].astype(float) - theta).abs().argsort()[:1]]
        a = a[SCORE_COL].values[0]
        if return_values:
            return hfh.get_stem(path_to_tif), int(a * 100) / 100

def get_p_for_item_given_theta_and_b(theta, B):
    theta = float(theta)
    B = float(B)
    y = theta - B
    top = pow(e, y)
    bottom = 1 + pow(e, theta-B)
    return top/bottom


def get_residuals(matrix_df = None, stats_df = None, tif_df = None):
    if matrix_df is None or stats_df is None or tif_df is None:
        print("get residuals requires matrix_df, stats_df, and tif_df.")
    difficulties = stats_df['b'].astype(float)

    thetas = matrix_df['PERSON_THETA'].astype(float)

    ret = []
    ret_resid = []
    ret_std_resid = []
    for i in difficulties.index:
        expecteds = []
        actuals = []
        residuals = []
        standardized_residuals = []

        b = difficulties[i]
        for j in thetas.index:
            theta = thetas[j]
            expected = get_p_for_item_given_theta_and_b(theta,b)
            expecteds.append(expected)
            actual = matrix_df.iloc[j,i]
            actuals.append(actual)
            residual = actual - expected
            residuals.append(residual)
            std_residual = residual/(expected*(1-expected))
            standardized_residuals.append(std_residual)
        ret_resid.append(residuals)
        ret_std_resid.append(standardized_residuals)
        df = hfh.pd.DataFrame([expecteds,actuals,residuals,standardized_residuals]).T
        #   note: df is just for validation it is not in itself useful.
        ret.append([df])
    resid_df = hfh.pd.DataFrame(ret_resid)
    std_resid_df = hfh.pd.DataFrame(ret_std_resid)
    return [ret,resid_df,std_resid_df]
def resid_chisq(o, expected):
    a = 0
    if expected > 0:
        a = (o - expected) * (o - expected) / expected
    return a


def chisq_2_2(g1p, g1n, g2p, g2n):
    row1 = g1p + g1n
    row2 = g2p + g2n
    col1 = g1p + g2p
    col2 = g1n + g2n

    n = row1 + row2

    ea = col1 * row1 / n
    eb = col2 * row1 / n
    ec = col1 * row2 / n
    ed = col2 * row2 / n

    a = resid_chisq(g1p, ea)
    b = resid_chisq(g1n, eb)
    c = resid_chisq(g2p, ec)
    d = resid_chisq(g2n, ed)

    chisq = a + b + c + d
    a = chi2.pdf(chisq, 1)
    if a > 1:
        a = 1
    return chisq, a
