import chainlit as cl
import httpx

from auth import get_oauth_token


@cl.step(type="tool", show_input=True)
async def get_bugs_by_keyword(keyword: str, page_index: int = 1) -> dict:
    """
    Fetches bugs based on a keyword from the Cisco API.

    Args:
        keyword (str): Keyword(s) to return details on associated bugs. Maximum length of 50 characters.
        page_index (int, optional): Index number of the page to return. Defaults to 1.

    Returns:
        dict: The response from the API as a dictionary.
    """
    # Validate input
    if not isinstance(keyword, str) or len(keyword) > 50:
        raise ValueError("`keyword` must be a string with a maximum length of 50 characters.")
    if not isinstance(page_index, int) or page_index < 1:
        raise ValueError("`page_index` must be a positive integer.")

    # Endpoint
    base_url = "https://apix.cisco.com/bug/v3.0/bugs/keyword/"
    url = f"{base_url}{keyword}"

    # Parameters
    params = {"page_index": page_index}
    token = await get_oauth_token()  # Get OAuth token
    auth_header = {"Authorization": f"Bearer {token}"}
    try:
        # Make the request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=auth_header)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.text  # LLM tool call requires string response
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")
        return f"An error occurred while fetching defect details: {e}"
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred while fetching defect details: {e.response.status_code} - {e.response.text}")
        return f"HTTP error occurred while fetching defect details: {e.response.status_code} - {e.response.text}"


@cl.step(type="tool", show_input=True)
async def get_security_advisories(start_date: str, end_date: str, page_index: int = 1) -> dict:
    """
    Fetches security advisories published within a specified date range.
    Args:
        start_date (str): Start date in the format YYYY-MM-DD (e.g., "2024-05-12").
        end_date (str): End date in the format YYYY-MM-DD (e.g., "2024-05-12").
        page_index (int, optional): The current page index. Defaults to 1. Must be between 1 and 100.
    Returns:
        dict: The response from the API as a dictionary.
    """
    # Validate input
    if not isinstance(start_date, str) or not isinstance(end_date, str):
        raise ValueError("`startDate` and `endDate` must be strings in the format YYYY-MM-DD.")
    if not (1 <= page_index <= 100):
        raise ValueError("`pageIndex` must be an integer between 1 and 100.")
    # Endpoint
    url = "https://apix.cisco.com/security/advisories/v2/all/lastpublished"
    # Parameters
    params = {"startDate": start_date, "endDate": end_date, "pageIndex": page_index, "pageSize": 5}
    token = await get_oauth_token()  # Get OAuth token
    auth_header = {"Authorization": f"Bearer {token}"}
    try:
        # Make the request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, headers=auth_header)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.text  # LLM tool call requires string response
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")
        return f"An error occurred while fetching security advisories: {e}"
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred while fetching security advisories: {e.response.status_code} - {e.response.text}")
        return f"HTTP error occurred while fetching security advisories: {e.response.status_code} - {e.response.text}"


cisco_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_security_advisories",
            "description": "Fetch security advisories published within a specified date range.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in the format YYYY-MM-DD (e.g., '2024-05-12').",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in the format YYYY-MM-DD (e.g., '2024-05-12').",
                    },
                    "page_index": {
                        "type": "integer",
                        "description": "The current page index. Must be between 1 and 100.",
                    },
                },
                "required": ["start_date", "end_date", "page_index"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bugs_by_keyword",
            "description": "Fetches bugs based on a keyword from the Cisco API.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword(s) to return details on associated bugs. Maximum length of 50 characters.",
                    },
                    "page_index": {
                        "type": "number",
                        "description": "Index number of the page to return. Defaults to 1.",
                    },
                },
                "required": ["keyword", "page_index"],
                "additionalProperties": False,
            },
        },
    },
]
