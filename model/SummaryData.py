import rpy2.robjects as r
from rpy2.robjects import pandas2ri


class SummaryData:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        pandas2ri.activate()  # Aktifkan konversi otomatis antara pandas dan R

    def get_column_names(self):
        return self.dataframe.columns.tolist()

    def get_summary(self, column_names):

        # Konversi DataFrame Pandas ke DataFrame R
        r_dataframe = pandas2ri.py2rpy(self.dataframe)

        # Inisialisasi hasil summary
        summary = {}

        # Load DataFrame ke environment R
        r.globalenv["df"] = r_dataframe

        for column in column_names:
            if column in self.dataframe.columns:
                # Evaluasi fungsi summary di R
                r_summary = r.r(f"summary(df${column})")
                r_summary_dict = dict(zip(r_summary.names, list(r_summary)))
                summary[column] = r_summary_dict
            else:
                summary[column] = {"Error": "Column not found in DataFrame"}

        return summary
