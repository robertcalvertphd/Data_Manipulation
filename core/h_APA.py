from core.h_file_handling import pd
import core.h_file_handling as hfh

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