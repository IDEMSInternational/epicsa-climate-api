import io
import logging
from typing import Any, Callable, Dict, OrderedDict

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ValidationError

from app.utils.response import get_dataframe_response

from rpy2.rinterface_lib.callbacks import logger as rpy2_logger

RunEpicsaFunctionType = Callable[..., Dict[str, Any]]

def run_epicsa_function_and_get_dataframe(endpoint_function,has_dataframe = True, **kwargs):
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    rpy2_logger.addHandler(stream_handler)

    try:
        result: OrderedDict = endpoint_function(**kwargs)
        if not has_dataframe:
            return result
        
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
        log_stream.seek(0)
        log_content = log_stream.read()   
        combined_message = f"Error occurred: {e}R message:\n {log_content}"
        raise RuntimeError(combined_message) from e
    finally:
        rpy2_logger.removeHandler(stream_handler)
        stream_handler.close()

#used for dependecy injection
def get_run_epicsa_function() -> RunEpicsaFunctionType:
   return run_epicsa_function_and_get_dataframe

def handle_epicsa_request(
    epicsa_function: Callable,
    response_model: BaseModel,
    run_epicsa_function: RunEpicsaFunctionType,
    has_dataframe: bool = True,
    **kwargs: Any
) -> BaseModel:
    try:
        result = run_epicsa_function(epicsa_function,has_dataframe, **kwargs)
        return response_model.parse_obj(result)
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=f"Response model validation error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

