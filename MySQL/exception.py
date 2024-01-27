from requests import RequestException
from mysql.connector import errorcode, Error


class MySQLProjectException(Exception):
    """Base exception for this script.

    :note: Pengecualian ini tidak boleh diajukan secara langsung.
    """
    pass


class EmptyListError(Exception):
    pass


class EmptyDictionaryError(Exception):
    pass


class HTTPErrorException(Exception):
    pass


class RequestProcessingError(RequestException):
    pass


class CSRFTokenMissingError(Exception):
    pass


class URLValidationError(Exception):
    pass


class FunctionNotFoundError(Exception):
    pass


class CookieFileNotFoundError(Exception):
    pass


class CookieCreationError(Exception):
    pass


class MySQLConnectorError(Error, Exception):
    pass


def ErrorHandling(error: MySQLConnectorError, name: str = None) -> None:
    if error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        raise MySQLConnectorError(
            "Error! Access denied. Check your username and password."
        )
    elif error.errno == errorcode.ER_BAD_DB_ERROR:
        raise MySQLConnectorError(
            "Error! Database not found."
        )
    elif error.errno == errorcode.ER_TABLE_EXISTS_ERROR:
        raise MySQLConnectorError(
            f"Error! Table '{name}' already exists"
        )
    elif error.errno == errorcode.ER_NO_SUCH_TABLE:
        raise MySQLConnectorError(
            f"Error! Table '{name}' doesn't exist"
        )
    else:
        raise MySQLConnectorError(
            f"Error! {error}"
        )
