import time
import json
import mysql.connector

from typing import Optional
from MySQL.exception import *
from MySQL.utility import Utility


class MySQLDDefinition:
    def __init__(self, **kwargs) -> None:
        self.__kwargs = kwargs

        self.__connector = mysql.connector.connect(**kwargs)
        self.__cursor = self.__connector.cursor()
        self.__maxlength = lambda data_list: max(map(len, data_list))

    def __execute(self, **kwargs):
        try:
            start = time.time()
            self.__cursor.execute(**kwargs)
            end = time.time()
            elapsed = end-start
            return elapsed

        except MySQLConnectorError as error:
            ErrorHandling(error)

    def create_database(self, name: str) -> None:
        try:
            query = f"CREATE DATABASE {name}"

            elapsed = self.__execute(operation=query)

            message = f"Query OK, 1 row affected ({elapsed: .2f} sec )"
            print(message)

        except MySQLConnectorError as error:
            ErrorHandling(error)

    def drop_database(self, name: str) -> None:
        try:
            query = f"DROP DATABASE {name}"

            elapsed = self.__execute(operation=query)

            message = f"Query OK, 0 row affected ({elapsed: .2f} sec )"
            print(message)

        except MySQLConnectorError as error:
            ErrorHandling(error)

    def create_table(self, name: str, detail: str, engine: str = "InnoDB"):
        try:
            query = (
                f"CREATE TABLE {name}("
                f"{detail}"
                f") ENGINE = {engine}"
            )
            elapsed = self.__execute(operation=query)

            message = f"Query OK, 0 row affected ({elapsed: .2f} sec )"
            print(message)

        except MySQLConnectorError as error:
            ErrorHandling(error, name)

    def recreate_table(self, name: str):
        try:
            table = f'{self.__kwargs["database"]}.{name}'

            query = f"TRUNCATE {name}"

            elapsed = self.__execute(operation=query)

            message = f"Query OK, 0 row affected ({elapsed: .2f} sec )"
            print(message)

        except MySQLConnectorError as error:
            ErrorHandling(error, table)
