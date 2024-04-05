
import numpy as np
from pandas import DataFrame

def get_dataframe_response(
    dataframe: DataFrame,
):
    # JSON cannot represent NaN values, so change to None
    dataframe = dataframe.replace({np.nan:None})
    return dataframe.to_dict(orient="records")
