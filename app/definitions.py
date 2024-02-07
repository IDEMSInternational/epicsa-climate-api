from enum import Enum
from typing import Literal


country_name = Literal["zm", "mw"]

class Language(str, Enum):
    English ="English"
    Tonga="Tonga",
    Chewa="Chewa",
    Lozi="Lozi",
    Lunda="Lunda",
    Kaonde="Kaonde", 
    Bemba="Bemba",
    Luvale="Luvale",
   


language_code = {
    Language.English:"en", 
    Language.Tonga: "to",
    Language.Chewa:"ny",
    Language.Lozi: "lozi",
    Language.Lunda: "lunda",
    Language.Kaonde: "kaonde", 
    Language.Bemba: "bemba",
    Language.Luvale: "luvale",
    }
