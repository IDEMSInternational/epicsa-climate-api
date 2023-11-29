from typing import OrderedDict

from fastapi import HTTPException, status

from app.utils.response import get_dataframe_response

def run_epicsa_function_and_get_dataframe(endpoint_function, **kwargs):
    try:
        result: OrderedDict = endpoint_function(**kwargs)
        
        # `get_dataframe_response()` function cannot cope with categorical data.
        # So convert categorical columns to strings
        data_frame = result["data"]
        for col in data_frame.columns:
            if data_frame[col].dtype.name == "category":
                data_frame[col] = data_frame[col].astype(str)

        # ensure that the data frame can be serialized
        result["data"] = get_dataframe_response(data_frame)

        return result

    except Exception as e:
        # Return a meaningful error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}",
        )

