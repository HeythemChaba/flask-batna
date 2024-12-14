import pandas as pd
import numpy as np

class EDAtoJSON:
    def __init__(self, df):
        self.df = df
        self.results = {}

    def generate_countplot(self, x, hue=None):
        """
        Generates data for a countplot in JSON format.
        :param x: Column for x-axis.
        :param hue: Column for grouping by hue.
        """
        count_data = (
            self.df.groupby([x, hue]).size().reset_index(name='count') if hue
            else self.df[x].value_counts().reset_index(name='count')
        )
        count_data.columns = [x, hue, 'count'] if hue else [x, 'count']
        self.results[f"countplot_{x}_{hue}"] = count_data.to_dict(orient='records')

    def generate_crosstab(self, row, col, values=None):
        """
        Generates a crosstab in JSON format.
        :param row: Row index for crosstab.
        :param col: Column index for crosstab.
        :param values: Optional boolean Series for aggregation.
        """
        if values is not None:
            values_eval = values.astype(int)
            crosstab_result = pd.crosstab(
                self.df[row], self.df[col], values=values_eval, aggfunc='sum', dropna=False
            )
        else:
            crosstab_result = pd.crosstab(self.df[row], self.df[col], dropna=False)

        self.results[f"crosstab_{row}_{col}"] = crosstab_result.fillna(0).to_dict(orient='index')

    def value_counts_normalized(self, col):
        """
        Computes normalized value counts for a column in JSON format.
        :param col: Column to compute value counts for.
        """
        value_counts = self.df[col].value_counts(normalize=True).reset_index()
        value_counts.columns = [col, 'proportion']
        self.results[f"value_counts_normalized_{col}"] = value_counts.to_dict(orient='records')

    def add_age_bins(self, age_col, bins, labels):
        """
        Adds age bins and computes distribution in JSON format.
        :param age_col: Column with age values.
        :param bins: List of bin edges.
        :param labels: List of bin labels.
        """
        self.df['AgeRange'] = pd.cut(self.df[age_col], bins=bins, labels=labels)
        value_counts = self.df['AgeRange'].value_counts(normalize=True).reset_index()
        value_counts.columns = ['AgeRange', 'proportion']
        self.results['age_bins_distribution'] = value_counts.to_dict(orient='records')

    def generate_histogram_sales_by_category(self, category_cols, sales_col):
        """
        Generates histogram data for categorical columns and their corresponding sales.
        :param category_cols: List of categorical columns.
        :param sales_col: Column containing sales data.
        """
        for col in category_cols:
            if col in self.df.columns and sales_col in self.df.columns:
                histogram_data = self.df.groupby(col)[sales_col].sum().reset_index()
                histogram_data.columns = [col, 'total_sales']
                self.results[f"histogram_{col}_sales"] = histogram_data.to_dict(orient='records')

    def generate_histogram_sales_by_time(self, time_col, sales_col):
        """
        Generates histogram data for sales over time.
        :param time_col: Column containing time data.
        :param sales_col: Column containing sales data.
        """
        if time_col in self.df.columns and sales_col in self.df.columns:
            time_sales_data = self.df.groupby(time_col)[sales_col].sum().reset_index()
            time_sales_data.columns = [time_col, 'total_sales']
            self.results[f"histogram_{time_col}_sales"] = time_sales_data.to_dict(orient='records')

    def generate_line_graph_sales_over_time(self, time_col, sales_col):
        """
        Generates line graph data for sales over time.
        :param time_col: Column containing time data.
        :param sales_col: Column containing sales data.
        """
        if time_col in self.df.columns and sales_col in self.df.columns:
            line_graph_data = self.df.groupby(time_col)[sales_col].sum().reset_index()
            line_graph_data.columns = [time_col, 'total_sales']
            self.results[f"line_graph_{time_col}_sales"] = line_graph_data.to_dict(orient='records')


def get_results(self):
        """
        Returns all EDA results as a dictionary.
        """
        return self.results
