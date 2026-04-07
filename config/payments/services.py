import requests
from requests import RequestException

ORDER_SERVICE_URL = "http://localhost:8003/api/orders"
HTTP_TIMEOUT_SECONDS = 5


def get_order(order_id):
    try:
        response = requests.get(
            f"{ORDER_SERVICE_URL}/{order_id}/",
            timeout=HTTP_TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            return {
                "success": True,
                "data": response.json(),
                "error": None,
                "status_code": 200,
            }

        if response.status_code == 404:
            return {
                "success": False,
                "data": None,
                "error": "not_found",
                "status_code": 404,
            }

        return {
            "success": False,
            "data": None,
            "error": "service_error",
            "status_code": response.status_code,
        }

    except RequestException:
        return {
            "success": False,
            "data": None,
            "error": "connection_error",
            "status_code": 503,
        }


def update_order_status(order_id, status):
    try:
        response = requests.patch(
            f"{ORDER_SERVICE_URL}/{order_id}/status/",
            json={"status": status},
            timeout=HTTP_TIMEOUT_SECONDS,
        )

        if response.status_code in (200, 204):
            return {
                "success": True,
                "error": None,
                "status_code": response.status_code,
            }

        if response.status_code == 404:
            return {
                "success": False,
                "error": "not_found",
                "status_code": 404,
            }

        return {
            "success": False,
            "error": "service_error",
            "status_code": response.status_code,
        }

    except RequestException:
        return {
            "success": False,
            "error": "connection_error",
            "status_code": 503,
        }