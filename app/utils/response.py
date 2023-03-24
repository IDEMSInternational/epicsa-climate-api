from pandas import DataFrame

def get_dataframe_response(
    dataframe: DataFrame,
):
    # JSON cannot represent NaN values, so change to space
    dataframe = dataframe.fillna("")
    return dataframe.to_dict(orient="records")
