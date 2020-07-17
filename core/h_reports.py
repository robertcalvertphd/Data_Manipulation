import core.h_file_handling as hfh
import core.h_assumptions as ha
import core.h_reports as hr
import core.h_format_manipulators

pd = hfh.pd


#   This file is intended to generalize output of dataframes into csvs that may easily be formatted to APA in excel


def create_table(df, df_columns, column_names, column_spanners, title_name, note):
    data = df[df_columns]


class Table:

    def __init__(self, title, columnInfo, rows, notes):
        self.create_csv(title, columnInfo, rows, notes)

    def create_csv(self, title, columnInfo, rows, notes):
        lines = []
        lines.append(title+'\n')
        c = columnInfo.get_column_and_span_lines()
        lines.append(c[0]+'\n')
        lines.append(c[1]+'\n')
        for row in rows:
            lines.append(row+'\n')
        for note in notes:
            lines.append(","+note+'\n')
        hfh.write_lines_to_text(lines,title+".csv")

class ColumnInfo:

    def __init__(self, column_span_names, column_spans, column_names):
        self.column_spans = column_spans
        self.column_span_names = column_span_names
        self.columns = column_names
    def get_info(self):
        assert len(self.column_span_names) == len(self.column_spans)
        #spread the column span names according to column spans
        ret = []
        column_span_line = []
        for i in range(len(self.column_spans)):
            column_span_line.append(self.column_span_names[i])
            for j in range(self.column_spans[i]-1):
                column_span_line.append(',')
        ret.append(column_span_line)
        ret.append(self.columns)
        return ret

    def get_column_and_span_lines(self):
        assert len(self.column_span_names) == len(self.column_spans)
        ret = []
        column_span_line = ","
        counter = -1
        for i in self.column_span_names:
            counter+=1
            column_span_line+=i
            for j in range(self.column_spans[counter]):
                column_span_line+=','
        columns_line = ","
        for col in self.columns:
            columns_line+=col+','
        ret=[column_span_line,columns_line]
        return ret

def get_count_summary(df, group_var, target_var, target_var_full_name = None, group_var_full_name = None):
    #todo: implement table logic for APA
    d = df.groupby([group_var, target_var]).size().unstack(fill_value=0)
    d[group_var + "_count"] = d.sum(axis=1)
    return d


def create_item_level_analysis(stats_R_path, stats_2_path, tif_path, matrix_path, bank_path, passing_proportion):
    bank = hfh.get_df_from_xlsx(bank_path)
    stats_R_df = hfh.get_stats_df(stats_R_path, bank)
    stats_2_df = hfh.get_stats_df(stats_2_path, bank)
    tif_df = hfh.get_df(tif_path, header = 0)
    matrix_df = core.h_format_manipulators.convert_xCalibre_matrix_for_PCI(matrix_path)
    a = ha.get_residuals_by_domain(matrix_df, stats_R_df, tif_df)
    b = ha.evaluate_in_fit_out_fit(stats_R_df)
    c = ha.evaluate_item_discriminatsion(stats_2_df)
    d = hr.get_count_summary(b, 'Domain', 'IN_DEV_EVAL')
    e = hr.get_count_summary(b, 'Domain', 'OUT_DEV_EVAL')
    f = hr.get_count_summary(b, 'Domain', 'B_EVAL')
    g = hr.get_count_summary(c, 'Domain', 'A_DEV_EVAL')
    h = ha.get_residuals_by_difficulty(matrix_df, stats_R_df, tif_df, a[1])
    j = ha.evaluate_max_info(stats_R_df, tif_df, passing_proportion)

