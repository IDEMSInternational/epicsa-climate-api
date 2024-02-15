from typing import Literal

def with_fallback(value:str, expected:Literal[None], fallback:str | None):
    """Provide a fallback value when assigning a str value to a literal type
    Args:
        value (str): String value to check
        expected (Literal): Literal model to check for valid string
        fallback (str | None): Value to return when input value does not satisfy literal type
    """
    if(value in expected.__args__):
        return value
    else:
        return fallback