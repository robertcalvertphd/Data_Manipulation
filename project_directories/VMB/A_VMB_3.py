from core.h_assumptions import h
from core.h_assumptions import hfh
import core.h_raw_processor as hr
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import (pairwise_tukeyhsd, MultiComparison)
import statsmodels.api as sm
from scipy.stats import chi2
import warnings
pd = hfh.pd
#   warnings.filterwarnings("error")

def process_sanja_paired_files(form_file, data_file):
    print(form_file)
    #   define parameters
    UCD = [3]
    FOREIGN = [0, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 99]
    US = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
    WESTERN = [39]
    ids = [UCD, US, FOREIGN, WESTERN]
    group_names = ['UCD', 'US', 'FOREIGN', 'WESTERN']
    d_df = hfh.get_df(data_file, header=0)
    d_df = combine_groups_for_df(d_df, group_names, ids, 'GROUP_NAME')
    f_df = hfh.convert_xlsx_to_csv(form_file, "delete_me.csv", get_df=True)
    #   n = d_df.groupby('GROUP_NAME').count()
    ret = handle_pretest_v_operational(d_df, f_df,hfh.get_stem(form_file))
    return ret


def handle_pretest_v_operational(d_df, f_df, file_name):
    a_df = d_df['Item Response String']
    try:
        times = d_df['Item Time (listed in seconds)']
    except:
        times = d_df['Item Time']

    times = times.dropna()
    ret = []
    for time in times:
        try:
            ret.append(list(map(int, time.split(','))))
        except:
            pass
    t_df = pd.DataFrame(ret)

    a_ret = []
    a_df = a_df.dropna()
    for item in a_df:
        line = []
        counter = -1
        for c in item:
            counter += 1
            if c == f_df['CorrectAnswer'][counter]:
                line.append(1)
            else:
                line.append(0)
        a_ret.append(line)
    a_df = pd.DataFrame(a_ret)

    #   operational
    operational_mask = 0
    operational_mask = get_mask_from_var_and_value(f_df, 'UseCode', 'Operational')
    operational_answers = a_df.T[operational_mask].T
    operational_answers['SCORE'] = operational_answers.sum(axis=1)
    operational_answers['id'] = d_df['Candidate ID']
    operational_answers['GROUP_NAME'] = d_df['GROUP_NAME']

    operational_answers.to_csv(file_name+"_op_ans.csv")
    operational_times = t_df.T[operational_mask].T
    operational_times['TIME'] = operational_times.sum(axis=1) / 60
    operational_times['id'] = d_df['Candidate ID']
    operational_times['GROUP_NAME'] = d_df['GROUP_NAME']

    #   pretest
    pretest_mask = get_mask_from_var_and_value(f_df, 'UseCode', 'Pretest')
    pretest_answers = a_df.T[pretest_mask].T
    pretest_answers['SCORE'] = pretest_answers.sum(axis=1)
    pretest_answers['id'] = d_df['Candidate ID']
    pretest_answers['GROUP_NAME'] = d_df['GROUP_NAME']
    pretest_answers.to_csv(file_name + "pre_ans.csv")
    pretest_times = t_df.T[pretest_mask].T
    pretest_times['TIME'] = pretest_times.sum(axis=1) / 60
    pretest_times['id'] = d_df['Candidate ID']
    pretest_times['GROUP_NAME'] = d_df['GROUP_NAME']

    a_df['GROUP_NAME'] = d_df['GROUP_NAME']

    items = item_level_analysis(a_df)
    explore(operational_answers, pretest_answers, d_df)
    check_work(operational_answers, pretest_answers, d_df)
    processed = process_dfs(operational_answers, operational_times, pretest_answers, pretest_times)
    return processed, items


def item_level_analysis(df, group_var='GROUP_NAME'):
    FOREIGN = 0
    DAVIS = 1
    US = 2
    WESTERN = 3

    davis_better_items = []
    davis_worse_items = []
    western_better_items = []
    western_worse_items = []

    davis_better_than = 0
    western_better_than = 0
    davis_worse_than = 0
    western_worse_than = 0

    for i in range(df.shape[1] - 3):
        test = df.iloc[:, i]
        # test[group_var] = df[group_var]
        test.loc[group_var] = df.loc[:, (group_var)]
        correct = test.groupby(group_var).sum()
        total = test.groupby(group_var).count()
        incorrect = total - correct
        ##  DAVIS:
        #   vs US
        a = chisq_2_2(correct[DAVIS], incorrect[DAVIS], correct[US], incorrect[US])
        # vs US+WESTERN
        b = chisq_2_2(correct[DAVIS], incorrect[DAVIS], correct[US] + correct[WESTERN],
                      incorrect[US] + incorrect[WESTERN])
        # vs ALL
        c = chisq_2_2(correct[DAVIS], incorrect[DAVIS], correct[US] + correct[WESTERN] + correct[FOREIGN],
                      incorrect[US] + incorrect[WESTERN] + incorrect[FOREIGN])

        ##WESTERN:
        d = chisq_2_2(correct[WESTERN], incorrect[WESTERN], correct[US], incorrect[US])
        # vs US+WESTERN
        e = chisq_2_2(correct[WESTERN], incorrect[WESTERN], correct[US] + correct[DAVIS],
                      incorrect[US] + incorrect[WESTERN])
        # vs ALL
        f = chisq_2_2(correct[WESTERN], incorrect[WESTERN], correct[US] + correct[DAVIS] + correct[FOREIGN],
                      incorrect[US] + incorrect[DAVIS] + incorrect[FOREIGN])
        if a[1] < .05:
            if correct[DAVIS] / total[DAVIS] > correct[US] / total[US]:
                davis_better_than += 1
                davis_better_items.append(i)

            else:
                davis_worse_than += 1
                davis_worse_items.append(i)
        if d[1] < .05:
            if correct[WESTERN] / total[WESTERN] > correct[US] / total[US]:
                western_better_than += 1
                western_better_items.append(i)
            else:
                western_worse_than += 1
                western_worse_items.append(i)

    return davis_better_items, davis_worse_items, western_better_items, western_worse_items


def resid_chisq(o, e):
    a = 0
    if e > 0:
        a = (o - e) * (o - e) / e
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


def process_dfs(op_ans, op_time, pre_ans, pre_time):
    opa_r = get_stats(op_ans, 'SCORE', 'GROUP_NAME')
    opt_r = get_stats(op_time, 'TIME', 'GROUP_NAME')
    pra_r = get_stats(pre_ans, 'SCORE', 'GROUP_NAME')
    prt_r = get_stats(pre_time, 'TIME', 'GROUP_NAME')
    ret = pd.concat([opa_r, pra_r, opt_r, prt_r], axis=1)

    return ret


def get_subset_from_var_and_values(df, target_var, values):
    mask = get_mask_from_var_and_value(df, target_var, values)
    subset = df[mask]
    return subset


def get_mask_from_var_and_value(df, target_var, value):
    mask = df[target_var] == value
    return mask


def combine_groups_for_df(df, list_of_group_names, list_of_lists_of_ids, name='GROUP_NAME'):
    for i in range(len(list_of_group_names)):
        df.loc[df['School Code'].astype(float).isin(list_of_lists_of_ids[i]), name] = list_of_group_names[i]
        df.loc[df['School Code'].astype(float).isin(list_of_lists_of_ids[i]), "GROUP_ID"] = float(i)
    return df


def get_stats(df, target_var, group_var):
    work_df = pd.DataFrame()
    work_df[group_var] = df[group_var]
    work_df[target_var] = df[target_var].astype(float)

    mean = work_df.groupby(group_var).mean()
    std = work_df.groupby(group_var).std()
    n = work_df.groupby(group_var).count()

    ret = mean
    ret['STD'] = std[target_var]
    ret['n'] = n[target_var]

    #ANOVA(df, target_var, group_var)
    return ret

def check_work(operational_df, pretest_df, recorded_df):
    #   remove items 12 and 72 from operational
    work_df = operational_df
    work_df = work_df.drop(columns = ["SCORE", "id", "GROUP_NAME", "DELTA", "REC_SCORE"])
    work_pre = pretest_df.drop(columns = ["SCORE", "id", "GROUP_NAME"])
    for i in range(100):
        mod_df = work_df.drop(columns = i)
        mod_df['MOD_SCORE'] = mod_df.sum(axis = 1)
        difference = mod_df['MOD_SCORE']-operational_df['REC_SCORE']
        difference = abs(difference)
        if min(difference)<3:
            print("remove", i)
        #   assume two items were made credit no matter what.

    #identifies 12 and 72
    dropA = work_df.iloc[:,12]
    dropB = work_df.iloc[:, 72]
    work_df = work_df.drop(columns = [12,72])
    #   confirms only negative error present
    current_error = work_df.sum(axis = 1)-operational_df['REC_SCORE']
    #   remaining error is 128
    zeroes = work_df[work_df.sum(axis = 1)-operational_df['REC_SCORE'] == 0]
    negatives = work_df[work_df.sum(axis=1) - operational_df['REC_SCORE'] == 0]
    negatives77 = negatives[operational_df['REC_SCORE']==77]
    print("hello")
    values = []
    # the pretest items are not the correct answer to this isssue.
    for i in range(22):
        for j  in range(23):
            item = work_pre.iloc[:,i]
            itemb = work_pre.iloc[:,j]
            score = work_df.sum(axis = 1) + item + itemb
            current_delta = abs(operational_df['REC_SCORE']-score)
            d = abs(current_delta.sum())
            values.append([i,j,d, item.sum(), itemb.sum()])
    v_df = pd.DataFrame(values)
    print("hello")

    '''
    operational_df = operational_df.drop(columns = [12,72])
    #   add items 3 and 9 from pretest
    operational_df["added1"] = pretest_df.iloc[:,3]
    operational_df["added2"] = pretest_df.iloc[:,9]
    operational_df = operational_df.drop(columns = ["SCORE", "id", "GROUP_NAME", "DELTA", "REC_SCORE"])
    operational_df['regraded'] = operational_df.sum(axis = 1)
    operational_df['DELTA'] = operational_df['regraded']-recorded_df['Score'].astype(float)
    print("hello")
    '''

    #   grade

def pair_files(file_path):
    form_files = hfh.get_all_files(file_path, extension='xlsx')
    data_files = hfh.get_all_files(file_path, extension='csv')
    pairs = hr.pair_files(pe_files=form_files, data_files=data_files)
    rep = []
    items = []
    for pair in pairs:
        f_df = hfh.convert_xlsx_to_csv(pair[0], "delete_me.csv", get_df=True)
        d_path = pair[0]
        f_path = pair[1]

        p = process_sanja_paired_files(pair[0], pair[1])
        rep.append(p[0])
        items.append(get_bank_ids_from_sequence(p[1], f_df))
    item_analysis = pd.concat(items, axis=0)
    process_items(item_analysis)

    f = pd.concat(rep, axis=0)

    print("hello")
    f.to_csv("final_report.csv")


def process_items(item_analysis):
    db = item_analysis[pd.notna(item_analysis.UCD_BETTER)].shape[0]
    dw = item_analysis[pd.notna(item_analysis.UCD_WORSE)].shape[0]
    wb = item_analysis[pd.notna(item_analysis.WESTERN_BETTER)].shape[0]
    ww = item_analysis[pd.notna(item_analysis.WESTERN_WORSE)].shape[0]

    dbo = item_analysis[(item_analysis.USE == 'Operational') & pd.notna(item_analysis.UCD_BETTER)].shape[0]
    dwo = item_analysis[(item_analysis.USE == 'Operational') & pd.notna(item_analysis.UCD_WORSE)].shape[0]
    dbp = item_analysis[(item_analysis.USE == 'Pretest') & pd.notna(item_analysis.UCD_BETTER)].shape[0]
    dwp = item_analysis[(item_analysis.USE == 'Pretest') & pd.notna(item_analysis.UCD_WORSE)].shape[0]

    wbo = item_analysis[(item_analysis.USE == 'Operational') & pd.notna(item_analysis.WESTERN_BETTER)].shape[0]
    wwo = item_analysis[(item_analysis.USE == 'Operational') & pd.notna(item_analysis.WESTERN_WORSE)].shape[0]
    wbp = item_analysis[(item_analysis.USE == 'Pretest') & pd.notna(item_analysis.WESTERN_BETTER)].shape[0]
    wwp = item_analysis[(item_analysis.USE == 'Pretest') & pd.notna(item_analysis.WESTERN_WORSE)].shape[0]

    print("DAVIS: bo, wo, bp, wp", dbo, dwo, dbp, dwp)
    print("WESTERN: bo, wo, bp, wp", wbo, wwo, wbp, wwp)
    print("hello")
    #   df[(df.a > 1) & (df.a < 3)].sum()
    #   davis aggregate
    count_ucd_df = item_analysis.groupby('UCD_BETTER').count()
    count_ucd_w_df = item_analysis.groupby('UCD_WORSE').count()
    count_ucd_df = count_ucd_df.drop(columns='UCD_WORSE')
    count_ucd_w_df = count_ucd_w_df.drop(columns='UCD_BETTER')
    count_ucd_df.columns = ['W+', 'W-', 'D+']
    count_ucd_df = count_ucd_df[['D+', 'W+', 'W-']]
    count_ucd_w_df.columns = ['W+', 'W-', 'D-']
    count_ucd_w_df = count_ucd_w_df[['D-', 'W+', 'W-']]
    count_ucd_df.to_csv("Davis_high_performers.csv")
    count_ucd_w_df.to_csv("Davis_low_performers.csv")

    #   western aggregate
    count_WESTERN_df = item_analysis.groupby('WESTERN_BETTER').count()
    count_WESTERN_w_df = item_analysis.groupby('WESTERN_WORSE').count()
    count_WESTERN_df = count_WESTERN_df.drop(columns='WESTERN_WORSE')
    count_WESTERN_w_df = count_WESTERN_w_df.drop(columns='WESTERN_BETTER')

    count_WESTERN_df.columns = ['D+', 'D-', 'W+']
    count_WESTERN_df = count_WESTERN_df[['W+', 'D+', 'D-']]
    count_WESTERN_w_df.columns = ['D+', 'D-', 'W-']
    count_WESTERN_w_df = count_WESTERN_w_df[['W-', 'D+', 'D-']]
    count_WESTERN_df.to_csv("Western_hp.csv")
    count_WESTERN_w_df.to_csv("Western_low_performers.csv")
    item_analysis.to_csv("item_level_analysis.csv")

def get_bank_ids_from_sequence(items, f_df):
    # create mask from items
    ret = f_df.iloc[:, 0]
    i = -1
    for list in items:
        i += 1
        mask = f_df['Position'].isin(list)
        a = f_df[mask]['AccNum']
        ret = pd.concat([ret, a], axis=1)
    ret.columns = ['Sequence', 'UCD_BETTER', 'UCD_WORSE', 'WESTERN_BETTER', 'WESTERN_WORSE']
    ret = ret.drop(columns='Sequence')
    ret = ret.dropna(how='all')
    ret['USE'] = f_df['UseCode']

    return ret

def explore(correct_df, pretest_df, f_df):
    work_df = correct_df
    work_df['REC_SCORE'] = f_df['Score'].astype(float)
    work_df['DELTA'] = work_df['REC_SCORE']-work_df['SCORE']
    if work_df['DELTA'].sum() == 0:
        print("scores match")
    else:
        print("looking for reason")

        #   remove the column and check that delta moves appropriately...
        check_df = work_df
        corrected_score = work_df["SCORE"]
        corrected_delta = work_df['DELTA']
        check_df = check_df.drop(columns = ["SCORE", "id", "GROUP_NAME", "REC_SCORE", "DELTA"])
        #   by removing an item that was defined as operational but is not the scores will remain the same.
        for i in range(check_df.shape[1]):
            item = check_df.iloc[:,i]
            removed = work_df['SCORE']-item
            delta_removed = abs(work_df['REC_SCORE']-removed).sum()
            delta_original = abs(work_df['DELTA']).sum()
            change = delta_original-delta_removed
            if change > 0:
                print("hello")
                work_df['SCORE'] = work_df['SCORE']-item
                print("remove item", i)


        pretest_check_df = pretest_df.drop(columns = ["SCORE", "id", "GROUP_NAME"])
        positive_df = work_df[work_df['DELTA'] == 2]
        adjusted_delta = abs((positive_df['SCORE'] - positive_df['REC_SCORE']).sum())

        for i in range(pretest_check_df.shape[1]):
            #compare effect on negative_df to total_df
            item = pretest_check_df.iloc[:,i]
            positive = abs(((positive_df['SCORE']+item)-positive_df['REC_SCORE']).sum())

            change = adjusted_delta-positive
            if change > 0:
                #corrected_score = corrected_score+item
                print("add item",i, "brings about",change,"change in delta.")


def ANOVA(df, target_var_name, group_var_name):
    cmd = target_var_name + "~" + group_var_name
    work_df = pd.DataFrame()
    work_df[group_var_name] = df[group_var_name]
    work_df[target_var_name] = df[target_var_name].astype(float)
    work_df = work_df.dropna(axis=0)
    mod = ols(cmd, data=work_df).fit()
    aov_table = sm.stats.anova_lm(mod, typ=2)
    print(aov_table)
    res2 = pairwise_tukeyhsd(work_df[target_var_name], work_df[group_var_name])
    print(res2)


pair_files(r"C:\Users\ERRCALV\PycharmProjects\IRT_Data_Manipulation\VMB")
