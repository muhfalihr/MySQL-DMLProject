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

class MySQLConnectorError(Error):
    pass