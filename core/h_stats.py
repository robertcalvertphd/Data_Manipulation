from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import (pairwise_tukeyhsd)
import statsmodels.api as sm
from scipy.stats import chi2
import pandas as pd
from math import pow, e
from sklearn.decomposition import PCA as p
from sklearn.decomposition import FactorAnalysis
import factor_analyzer as f

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
    a = fa.fit(df)
    b = fa.get_eigenvalues()
    return b[0]
def get_p_for_item_given_theta_and_b(theta, B):
    y = theta - B
    top = pow(e, y)
    bottom = 1 + pow(e, theta-B)
    return top/bottom


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
