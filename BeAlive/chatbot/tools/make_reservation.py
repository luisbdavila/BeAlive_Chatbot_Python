import sqlite3
import streamlit as st
from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain
from BeAlive.chatbot.chains.get_activity_message import GetActivityMessageChain

class MakeReservationInfo(BaseModel):
    """
    Represents the input model for making a
    reservation.

    Attributes:
    ----------
        message : str
            The message left by the user.
        activity_name : str
            The name of the activity.
    """
    message: str
    activity_name: str


class MakeActivityReservationTool(BaseTool):
    """
    Tool for making a reservation for an activity.

    Attributes:
    ----------

        name : str
            The name of the tool.
        description : str
            The description of the tool.
        args_schema : Type[BaseModel]
            The schema for the input arguments of the tool.
        return_direct: bool
            Whether to return the result directly or not.

    Methods:
    -------
        _run(self, user_id: int = st.session_state.user_id, **kwargs) -> str:
            Makes a reservation for an activity.

    """
    name: str = "MakeActivityReservationTool"
    description: str = "Make a reservations for an activity."
    args_schema: Type[BaseModel] = MakeReservationInfo
    return_direct: bool = True

    def _run(self,
             user_id: int = st.session_state.user_id,
             **kwargs) -> str:

        """
        Makes a reservation for an activity.

        Parameters:
        ----------
            user_id : int
                The user ID.
            **kwargs : dict
                Dictionary containing the user input arguments.

        Returns:
        -------
            str
                The result of the reservation.

        """
        db_path = get_sqlite_database_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT activity_id, activity_name
                                FROM activities
                                WHERE activity_state = 'open'""")
            activity_list = cursor.fetchall()

        except:
            return "An error occurred while obtaining the list of available activities."

        finally:
            cursor.close()
            connection.close()

        try:
            activity_id = GetActivityIDChain().invoke({'user_input': kwargs.get("activity_name", "No activity"),
                                                      'activity_list': str(activity_list)})

            if activity_id.activity_id == -1:
                return "An error occurred. There are no available activities with that name."

        except:
            return f"An error occurred."

        try:
            message = GetActivityMessageChain().invoke(
                                                {'user_input': kwargs.get("message", "No message")})

        except:
            return "An error occurred."

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            # Obtaining the host id
            cursor.execute("""SELECT host_id
                            FROM activities
                            WHERE activity_id = ?""", 
                           (activity_id.activity_id,))

            activity_info = cursor.fetchone()
            activity_host = activity_info[0]
        except:
            return "An error occurred."

        try:
            cursor.execute("""INSERT INTO reservations (activity_id, host_id,
                            user_id, message) VALUES (?,?,?,?)""",
                           (activity_id.activity_id, activity_host,
                            user_id, message.message,))
            connection.commit()

        except:
            return """An error occurred while inserting the reservations
            (you may already have one reservation for that activity)."""

        finally:
            cursor.close()
            connection.close()

        return "Your reservation has been made"
