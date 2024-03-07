# =================================================================
#
# Authors: IDEMS International, Stephen Lloyd
#
# Copyright (c) 2023, E-PICSA Project
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================
"""Provides a set of wrapper functions for the `epicsawrap` R package.

This module provides access to the `epicsawrap` R package
(https://github.com/IDEMSInternational/epicsawrap).
It communicates with the R environment using the `rpy2` package.
Access is provided through a set of wrapper functions. 
Each wrapper function:
  - Allows the equivalent R function to be called from Python, using Python 
    data types.
  - Has a parameter list that is as close as possible to the equivalent R 
    function's parameter list.
  - Returns its result as a platform independent object, typically a Python 
    pandas data frame.
  - Has a similar structure. First it converts the Python parameters (as 
    needed) into R equivalent data types used by `rpy2`. It calls the R 
    function. If needed, it converts the returned result into a Python data 
    type.
"""
import os
from collections import OrderedDict
from typing import Dict, List

import numpy
from pandas import DataFrame
from rpy2.robjects import NULL as r_NULL
from rpy2.robjects import (
    conversion,
    default_converter,
    packages,
    pandas2ri,
)
from rpy2.robjects.vectors import DataFrame as RDataFrame
from rpy2.robjects.vectors import (
    BoolVector,
    FloatVector,
    IntVector,
    ListVector,
    StrVector,
)

r_epicsawrap = packages.importr("epicsawrap")
r_epicsadata = packages.importr("epicsadata")

def extremes_summaries(
    country: str,
    station_id: str,
    summaries: List[str] = None,  
) -> OrderedDict:
    if summaries is None:
        summaries = [
            "extremes_rain",
            "extremes_tmin",
            "extremes_tmax",
        ]

    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.overall_extremes_summaries(
        country=r_params["country"],
        station_id=r_params["station_id"],
        summaries=r_params["summaries"],
    )
    return __get_list_vector_as_ordered_dict(r_list_vector)

def annual_rainfall_summaries(
    country: str,
    station_id: str,
    summaries: List[str] = None,
) -> OrderedDict:
    """TODO"""
    if summaries is None:
        summaries = [
            "annual_rain",
            "start_rains",
            "end_rains",
        ]

    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.annual_rainfall_summaries(
        country=r_params["country"],
        station_id=r_params["station_id"],
        summaries=r_params["summaries"],
    )
    return __get_list_vector_as_ordered_dict(r_list_vector)


def annual_temperature_summaries(
    country: str,
    station_id: str,
    summaries: List[str] = None,
) -> OrderedDict:
    """TODO"""
    if summaries is None:
        summaries = ["mean_tmin", "mean_tmax", "min_tmin", "min_tmax", "max_tmin", "max_tmax"]

    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.annual_temperature_summaries(
        country=r_params["country"],
        station_id=r_params["station_id"],
        summaries=r_params["summaries"],
    )
    return __get_list_vector_as_ordered_dict(r_list_vector)


def crop_success_probabilities(
    country: str,
    station_id: str,
    water_requirements: List[int] = None,
    planting_length: List[int] = None,
    planting_dates: List[int] = None,
    start_before_season: bool = None,
) -> OrderedDict:
    """TODO"""
    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.crop_success_probabilities(
        country=r_params["country"],
        station_id=r_params["station_id"],
        water_requirements=r_params["water_requirements"],
        planting_length=r_params["planting_length"],
        planting_dates=r_params["planting_dates"],
        start_before_season=r_params["start_before_season"],
    )
    return __get_list_vector_as_ordered_dict(r_list_vector)


def monthly_temperature_summaries(
    country: str,
    station_id: str,
    summaries: List[str] = None,
) -> OrderedDict:
    """TODO"""
    if summaries is None:
        summaries = ["mean_tmin", "mean_tmax", "min_tmin", "min_tmax", "max_tmin", "max_tmax"]

    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.monthly_temperature_summaries(
        country=r_params["country"],
        station_id=r_params["station_id"],
        summaries=r_params["summaries"],
    )
    return __get_list_vector_as_ordered_dict(r_list_vector)


def season_start_probabilities(
    country: str, station_id: str, start_dates: List[int] = None
) -> OrderedDict:
    """TODO"""
    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    r_list_vector: ListVector = r_epicsawrap.season_start_probabilities(
        country=r_params["country"],
        station_id=r_params["station_id"],
        start_dates=r_params["start_dates"],
    )
    return __get_list_vector_as_ordered_dict(r_list_vector)

def station_metadata(
    country: str,
    station_id: str,
    include_definitions : bool,
) -> OrderedDict:
    __init_data_env()
    r_params: Dict = __get_r_params(locals())
    if country == "":
        r_list_vector: RDataFrame = r_epicsawrap.station_metadata(
            include_definitions=r_params["include_definitions"],  
        )
    elif station_id =="":
         r_list_vector: RDataFrame = r_epicsawrap.station_metadata(
            country=r_params["country"],   
            include_definitions=r_params["include_definitions"],  
        )   
    else:
        r_list_vector: RDataFrame = r_epicsawrap.station_metadata(
            country=r_params["country"],   
            station_id=r_params["station_id"],
            include_definitions=r_params["include_definitions"],  
        )
    return OrderedDict([("data", __get_data_frame(r_list_vector))])



def __get_data_frame(r_data_frame: RDataFrame) -> DataFrame:
    """Converts an R format data frame into a Python format data frame.

    Converts 'r_data_frame' into a Python data frame and returns it.

    Args:
        r_data_frame: A data frame in rpy2 R format.

    Returns:
        The data frame converted into Python format.
    """
    # convert R data frame to pandas data frame
    with conversion.localconverter(default_converter + pandas2ri.converter):
        data_frame: DataFrame = conversion.get_conversion().rpy2py(r_data_frame)

    # The converter above converts missing integers to the smallest possible signed 32-bit
    #   integer (-2147483648). Convert these values to `None` instead
    for col in data_frame.columns:
        # If this column has a category type, then the next if statement will raise an exception.
        #    So in this case, continue to next column.
        if data_frame[col].dtype.name == "category":
            continue
        if numpy.issubdtype(data_frame[col].dtype, numpy.integer):
            data_frame[col] = data_frame[col].replace(
                numpy.iinfo(numpy.int32).min, None
            )
    return data_frame


def __get_list_vector_as_ordered_dict(r_list_vector: ListVector) -> OrderedDict:
    """TODO"""
    data_frame = __get_data_frame(r_list_vector[1])
    r_list_as_dict = OrderedDict(
        [
            ("metadata", __get_python_types(r_list_vector[0])),
            ("data", data_frame),
        ]
    )
    return r_list_as_dict


def __get_python_types(data):
    """Converts a collection of rpy2 R objects into Python objects.

    Recursively converts each rpy2 R object in 'data'. Each R object will be converted to its
    Python equivalent (integer, string, list, dictionary etc.). If 'data' is a hierarchy
    (e.g. lists of lists), then the returned Python objects will follow the same hierarchy.

    This function is based on a function from
    https://stackoverflow.com/questions/24152160/converting-an-rpy2-listvector-to-a-python-dictionary

    Args:
        data: A collection of rpy2 R objects.

    Returns:
        'data' represented as a collection of Python types.
    """
    r_array_types = [BoolVector, FloatVector, IntVector]
    r_list_types = [StrVector]
    r_list_vector_types = [ListVector]
    r_data_frame_types = [RDataFrame]

    if type(data) in r_data_frame_types:
        return __get_data_frame(data)
    elif type(data) in r_list_vector_types:
        converted_values = [__get_python_types(elt) for elt in data]
        if data.names is r_NULL:
            return converted_values
        else:
            return OrderedDict(zip(data.names, converted_values))
    elif type(data) in r_list_types:
        return [__get_python_types(elt) for elt in data][0]
    elif type(data) in r_array_types:
        return numpy.array(data).tolist()[0]
    else:
        if hasattr(data, "rclass"):  # An unsupported r class
            raise KeyError(
                "Could not proceed, type {} is not defined"
                "to add support for this type, just add it to the imports "
                "and to the appropriate type list above".format(type(data))
            )
        else:
            return data  # We reached the end of recursion


def __get_r_params(params: Dict) -> Dict:
    """Returns a dictionary of parameters in R format.

    Converts each Python parameter in 'params' and converts it into an R
    parameter suitable for passing to rpy2. Returns the R parameters as a
    dictionary.

    Args:
        params: A dictionary of Python parameters, normally populated by
          calling `locals()`.

    Returns:
        A dictionary of parameters. Each parameter is in an R format suitable
        for passing to rpy2.
    """
    r_params: Dict = params.copy()

    for key in r_params:
        if r_params[key] is None:
            r_params[key] = r_NULL
        elif isinstance(r_params[key], List):
            if len(r_params[key]) > 0:
                if isinstance(r_params[key][0], str):
                    r_params[key] = StrVector(r_params[key])
                elif isinstance(r_params[key][0], float):
                    r_params[key] = FloatVector(r_params[key])
        elif isinstance(r_params[key], DataFrame):
            with default_converter + pandas2ri.converter:
                r_params[key] = conversion.get_conversion().py2rpy(r_params[key])

    return r_params


def __init_data_env():
    """TODO"""
    # ensure that this function is only called once per session
    # (because it relies on the current working folder when session started)
    if not hasattr(__init_data_env, "called"):
        __init_data_env.called = True
    else:
        return

    working_folder = os.getcwd()

    service_file: str = os.path.join(working_folder, "service-account.json")
    service_file = os.path.normpath(service_file).replace("\\", "/")
    r_epicsadata.gcs_auth_file(service_file)

    data_folder: str = os.path.join(working_folder, "working_data")
    data_folder = os.path.normpath(data_folder).replace("\\", "/")
    r_epicsawrap.setup(data_folder)
