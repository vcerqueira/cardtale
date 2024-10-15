import pandas as pd

from rpy2.robjects import pandas2ri
import rpy2.robjects as r_objects

r_objects.r(
    """
    bc_r_port <-
      function(x) {
        library(forecast)

        xt = BoxCox(x, 'auto')
        lambda_ = attr(xt, 'lambda')

        return(list(xt=xt,lambda_=lambda_))
      }
    """
)

r_objects.r(
    """
    bc_with_l_r_port <-
      function(x, lambda_) {
        library(forecast)

        xt = BoxCox(x, lambda_)

        return(xt)
      }
    """
)

r_objects.r(
    """
    inv_bc_r_port <-
      function(x, lambda_) {
        library(forecast)

        return(InvBoxCox(x, lambda=lambda_))
      }
    """
)


class BoxCox:
    box_cox = r_objects.globalenv['bc_r_port']
    box_cox_lmd = r_objects.globalenv['bc_with_l_r_port']
    inv_box_cox = r_objects.globalenv['inv_bc_r_port']

    def __init__(self):
        self.lambda_ = -1

    def transform(self, series: pd.Series):
        pandas2ri.activate()

        y = pandas2ri.py2rpy_pandasseries(series)

        y_bc = self.box_cox(y)

        yt = pd.Series(y_bc[0], index=series.index)
        self.lambda_ = y_bc[1][0]

        pandas2ri.deactivate()

        return yt

    def transform_lambda(self, series: pd.Series):
        pandas2ri.activate()

        y = pandas2ri.py2rpy_pandasseries(series)

        y_bc = self.box_cox_lmd(y, self.lambda_)

        yt = pd.Series(y_bc, index=series.index)

        pandas2ri.deactivate()

        return yt

    def transform_df_lambda(self, data: pd.DataFrame):
        pandas2ri.activate()

        df = pandas2ri.py2rpy_pandasdataframe(data)

        y_bc = self.box_cox_lmd(df, self.lambda_)

        y_bc = pandas2ri.rpy2py_dataframe(y_bc)

        pandas2ri.deactivate()

        return y_bc

    def inverse_transform(self, series: pd.Series):
        pandas2ri.activate()

        y = pandas2ri.py2rpy_pandasseries(series)

        y_ibc = self.inv_box_cox(y, self.lambda_)
        yt = pd.Series(y_ibc, index=series.index)

        pandas2ri.deactivate()

        return yt

    def inverse_transform_df(self, data: pd.DataFrame):
        pandas2ri.activate()

        df = pandas2ri.py2rpy_pandasdataframe(data)

        df_ibc = self.inv_box_cox(df, self.lambda_)
        df_ibc = pandas2ri.rpy2py_dataframe(df_ibc)
        # df_ibc = pd.DataFrame(df_ibc, index=data.index, columns=data.columns)

        pandas2ri.deactivate()

        df_ibc.index = data.index

        return df_ibc
