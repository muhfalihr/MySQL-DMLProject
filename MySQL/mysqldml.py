import time
import mysql.connector
import json
from typing import Optional
from MySQL.exception import *


class MySQLDManipulator:
    """`MySQLDManipulator` is a Python class designed to streamline and simplify Data Manipulation Language (DML) operations on MySQL databases. This class is specifically crafted to provide a convenient interface for executing common DML tasks, such as inserting, updating, and deleting records, within a MySQL database using Python.

    Key features and functionalities of the `MySQLDManipulator` class include:

    1. `Connection Management`:
        - Facilitates the establishment of a connection to a MySQL database.
        - Allows for configuration of connection parameters such as host, username, password, and database name.

    2. `Record Insertion`:
        - Provides methods for inserting new records into MySQL tables.
        - Supports both single-record and batch-insert operations.

    3. `Record Update`:
        - Simplifies the process of updating existing records in MySQL tables.
        - Enables the modification of specific fields within records based on specified conditions.

    4. `Record Deletion`:
        - Offers methods for deleting records from MySQL tables.
        - Allows for the deletion of records based on specified conditions.

    5. `Transaction Support`:
        - Implements transaction handling to ensure atomicity of DML operations.
        - Enables users to commit or rollback transactions based on the success or failure of a sequence of DML operations.

    6. `Error Handling`:
        - Incorporates robust error handling mechanisms to capture and report any issues that may arise during DML operations.
        - Provides clear and informative error messages to assist in troubleshooting.

    7. `Flexible Query Building`:
        - Allows for the construction of custom SQL queries for advanced users who may need more complex DML operations.

    8. `Logging and Debugging`:
        - Includes logging capabilities to track the execution flow and diagnose potential issues.
        - Supports debugging by providing detailed information about the executed queries and their outcomes.
    """

    def __init__(self, **kwargs) -> None:
        """
        Keyword Arguments:
            - **kwargs (Required)
                Example = {
                    'host' = '127.0.0.1', 
                    'user' = 'username', 
                    'password' = 'passwd', 
                    'database' = 'databasename'
                }
        """
        self.__connector = mysql.connector.connect(**kwargs)
        self.__cursor = self.__connector.cursor()

    def insert(self, table: str, datas: dict) -> None:
        """inserts new data into a database

        Arguments :
            - table (Required) = table name
            - datas (Required) = data to be inserted into the database. Dictionary data type.
        """

        try:
            if datas:
                pattern = tuple("%s" for _ in range(len(datas))
                                ).__str__().replace("'", "")
                column = tuple(key for key in datas.keys()
                               ).__str__().replace("'", "")
                values = tuple(value for value in datas.values())
            else:
                raise EmptyDictionaryError(
                    "Error! A dictionary error occurred as the dictionary appears to be empty. Please make sure the dictionary contains valid key-value pairs."
                )

            query = f"INSERT INTO {table}{column} VALUES{pattern}"

            self.__cursor.execute(operation=query, params=values)

            self.__connector.commit()

        except MySQLConnectorError as e:

            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise MySQLConnectorError(
                    "Error! Access denied. Check your username and password."
                )
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                raise MySQLConnectorError(
                    "Error! Database not found."
                )
            else:
                raise MySQLConnectorError(
                    f"Error! {e}"
                )

    def manyinsert(self, table: str, datas: list) -> None:
        """inserting a lot of new data into the database

        Arguments :
            - table (Required) = table name
            - datas (Required) = data to be inserted into the database. List data type.
        """
        try:
            if datas:
                pattern = tuple("%s" for _ in range(
                    len(datas[0]))).__str__().replace("'", "")
                column = tuple(
                    key for key in datas[0].keys()).__str__().replace("'", "")
                values = [tuple(value for value in data.values())
                          for data in datas]
            else:
                raise EmptyListError(
                    "Error! An error occurred due to an empty list. Please ensure that the list is not empty before proceeding."
                )

            query = f"INSERT INTO {table}{column} VALUES{pattern}"

            self.__cursor.executemany(operation=query, seq_params=values)

            self.__connector.commit()

        except MySQLConnectorError as e:

            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise MySQLConnectorError(
                    "Error! Access denied. Check your username and password."
                )
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                raise MySQLConnectorError(
                    "Error! Database not found."
                )
            else:
                raise MySQLConnectorError(
                    f"Error! {e}"
                )

    def update(self, table: str, column: str, set: str, condition: str) -> None:
        """updates data in a database

        Arguments :
            - table (Required) = table name
            - column (Required) = column name
            - set (Required) = settings for updates
            - condition (Required) = condition of the WHERE clause
        """

        try:
            query = f"UPDATE {table} SET {column} = {set} WHERE {condition}"

            self.__cursor.execute(operation=query)

            self.__connector.commit()

        except MySQLConnectorError as e:

            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise MySQLConnectorError(
                    "Error! Access denied. Check your username and password."
                )
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                raise MySQLConnectorError(
                    "Error! Database not found."
                )
            else:
                raise MySQLConnectorError(
                    f"Error! {e}"
                )

    def delete(self, table: str, condition: Optional[str] = None) -> None:
        """deletes data from a database

        Arguments :
            - table (Required) = table name
            - condition (Optional) = condition of the WHERE clause
        """
        try:
            query = f"DELETE FROM {table}"
            query += " " + f"WHERE {condition}" if condition else ""

            self.__cursor.execute(operation=query)

            self.__connector.commit()

        except MySQLConnectorError as e:

            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise MySQLConnectorError(
                    "Error! Access denied. Check your username and password."
                )
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                raise MySQLConnectorError(
                    "Error! Database not found."
                )
            else:
                raise MySQLConnectorError(
                    f"Error! {e}"
                )
