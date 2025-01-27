import sqlite3
from typing import Type
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.process_query_output import QueryProcessingChain
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain


class CheckActivityReservationInput(BaseModel):
    """
    Model for the input of the CheckActivityReservationTool.

    Attributes:
    --------
        host_id : int
            The ID of the host.
        user_input : str
            The user input.

    """

    host_id: int
    user_input: str


class CheckActivityReservationTool(BaseTool):
    """

    Tool to retrieve reservations for an activity.

    Attributes:
    --------
        name : str
            The name of the tool.
        description : str
            The description of the tool.
        args_schema : Type[BaseModel]
            The schema of the input arguments.
        return_direct : bool
            Whether to return the result directly.

    Methods:
    --------
        _run(user_input: str, host_id: int = st.session_state.user_id) -> str:
            Retrieve reservations for an activity.
    """

    name: str = "CheckActivityReservationTool"
    description: str = "Retrieve reservations for an activity."
    args_schema: Type[BaseModel] = CheckActivityReservationInput
    return_direct: bool = True

    def _run(
        self,
        user_input: str,
        host_id: int = st.session_state.user_id
    ) -> str:
        """
        Retrieve reservations for an activity.

        Parameters:
        --------
            user_input : str
                The user input.
            host_id : int
                The ID of the host.
        Returns:
        --------
            str
                The result of the tool.
        """
        db_path = get_sqlite_database_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT activity_id, activity_name
                              FROM activities
                              WHERE host_id = ?""",  (host_id,))
            activity_list = cursor.fetchall()

        except:
            return "An error occurred while obtaining your activities."

        finally:
            cursor.close()
            connection.close()

        try:
            activity_id = GetActivityIDChain().invoke({'user_input': user_input,
                                                       'activity_list': str(activity_list)})
            if activity_id.activity_id == -1:
                return "An error occurred. You don't have any activities with that name."

        except:
            return "An error occurred."

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            query = """SELECT a.activity_name, a.activity_state, u.username,
                              u.cumulative_rating,
                              u.phone_number, u.email, r.message, r.state
                        FROM reservations r join activities a join users u
                            on r.activity_id = a.activity_id and
                            u.user_id = r.user_id
                        WHERE r.host_id = ? and a.activity_id = ?"""
            cursor.execute(query, (host_id, activity_id.activity_id))
            reservations = cursor.fetchall()
            if len(reservations) == 0:
                return "You currently have no reservations for that activity."

        except:
            return "An error occurred while obtaining the reservations."

        finally:
            cursor.close()
            connection.close()

        return QueryProcessingChain().invoke({
                "user_input": str(reservations),
                "sql_query": query
                })
