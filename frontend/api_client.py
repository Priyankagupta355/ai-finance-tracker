
import os
import requests

API_BASE_URL = os.getenv(
    "FINANCE_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


def api_request(
    method: str,
    endpoint: str,
    token: str | None = None,
    json_data: dict | None = None,
):
    """Send a request to the FastAPI backend."""

    # Use a dictionary for HTTP headers
    headers = {}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method=method,
            url=f"{API_BASE_URL}{endpoint}",
            headers=headers,
            json=json_data,
            timeout=20,
        )
    except requests.RequestException as error:
        raise RuntimeError(
            "Cannot connect to FastAPI. Check that the backend is running."
        ) from error

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text

        raise RuntimeError(
            f"API request failed ({response.status_code}): {detail}"
        )

    if response.status_code == 204 or not response.content:
        return None

    return response.json()


def api_get(endpoint: str, token: str | None = None):
    return api_request("GET", endpoint, token=token)


def api_post(
    endpoint: str,
    json_data: dict,
    token: str | None = None,
):
    return api_request(
        "POST",
        endpoint,
        token=token,
        json_data=json_data,
    )


def api_put(
    endpoint: str,
    json_data: dict,
    token: str | None = None,
):
    return api_request(
        "PUT",
        endpoint,
        token=token,
        json_data=json_data,
    )


def api_delete(endpoint: str, token: str | None = None):
    return api_request("DELETE", endpoint, token=token)
