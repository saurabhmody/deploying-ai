import os
from typing import Literal

import requests
from langchain.tools import tool
from pydantic import BaseModel, TypeAdapter

COUNTRYLAYER_URL = "https://api.apilayer.net/countrylayer/v2/all"

CountryField = Literal["capital", "region", "alpha2Code", "alpha3Code", "callingCodes"]
FIELD_LABELS: dict[CountryField, str] = {
    "capital": "Capital",
    "region": "Region",
    "alpha2Code": "Alpha2 Code",
    "alpha3Code": "Alpha3 Code",
    "callingCodes": "Calling Codes",
}


class CountryInfo(BaseModel):
    name: str
    capital: str | None = None
    region: str | None = None
    alpha2Code: str | None = None
    alpha3Code: str | None = None
    callingCodes: list[str | None] | None = None

    def to_line(self, fields: list[CountryField] | None) -> str:
        columns = [f"Country Name: {' '.join(self.name.split())}"]
        for field, label in FIELD_LABELS.items():
            if fields is not None and field not in fields:
                continue
            value = getattr(self, field)
            if isinstance(value, list):
                value = ", ".join(code.strip() for code in value if code and code.strip())
            text = " ".join(value.split()) if value else ""
            columns.append(f"{label}: {text or 'Not available'}")
        return ", ".join(columns)


COUNTRIES = TypeAdapter(list[CountryInfo])


@tool
def get_country_info(fields: list[CountryField] | None = None) -> str:
    """Return all countries with the selected optional fields."""
    api_key = os.getenv("APILAYER_API_KEY")
    if not api_key:
        return "UNAVAILABLE"

    try:
        response = requests.get(
            COUNTRYLAYER_URL,
            headers={"apikey": api_key},
            allow_redirects=False,
            timeout=20,
        )
        response.raise_for_status()
        countries = COUNTRIES.validate_python(response.json())
    except (requests.RequestException, ValueError):
        return "UNAVAILABLE"

    if not countries:
        return "EMPTY"
    return "\n".join(country.to_line(fields) for country in countries)
