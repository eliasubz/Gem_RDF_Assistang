import requests


def get_snomed_term(code, language="en"):
    """
    Fetch the SNOMED CT term for a given concept ID.

    Parameters:
        code (str or int): SNOMED CT concept code (e.g. 84114007)
        language (str): Language code (default = 'en')

    Returns:
        str: The preferred term or None if not found
    """
    url = f"https://snowstorm.ihtsdotools.org/fhir/CodeSystem/$lookup"
    params = {
        "system": "http://snomed.info/sct",
        "code": str(code),
        "language": language,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        for prop in data.get("parameter", []):
            if prop.get("name") == "display":
                return prop.get("valueString")
        return None
    else:
        print(f"Error fetching term for {code}: {response.status_code}")
        return None


print(get_snomed_term(84114007))
