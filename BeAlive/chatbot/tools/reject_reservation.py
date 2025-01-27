import sqlite3
import streamlit as st
from typing import Type
from langchain.tools import BaseTool
from pydantic import BaseModel
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.check_reservation_user_id import GetReservationUserIDChain
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain


class ReservationInfo(BaseModel):
    """
    Represents the input model for managing a
    reservation.

    Attributes:
    ----------
        user : str
            The name of the user who made the
            reservation.
        activity_name : str
            The name of the activity.
    """
    user: str
    activity_name: str


class RejectActivityReservationTool(BaseTool):
    """
    Tool to reject a reservation for an activity.

    Attributes:
    -----------
        name : str
            The name of the tool.
        description : str
            The description of the tool.
        args_schema : Type[BaseModel]
            The schema for the input arguments of the tool.
        return_direct : bool
            Whether to return the result directly or not.

    Methods:
    --------
        _run(self, user_input: str, host_id: int = st.session_state.user_id) ->str:
            Rejects a reservation for an activity based on user input and host ID.

    """
    name: str = "RejectActivityReservationTool"
    description: str = "Reject a reservation for an activity."
    args_schema: Type[BaseModel] = ReservationInfo
    return_direct: bool = True

    def _run(
            self,
            host_id: int = st.session_state.user_id,
            **kwargs
        ) -> str:
        """
        Rejects a reservation for an activity.

        Parameters:
        -----------
            user_input : str
                The user input.
            host_id : int
                The host ID.
            **kwargs : dict
                Dictionary containing the user input arguments.

        Returns:
        --------
            str
                A message indicating the result of the operation (success, error
                or a status).

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
            return "An error occurred while obtaining the list of your activities."

        finally:
            cursor.close()
            connection.close()

        try:
            activity_id = GetActivityIDChain().invoke({
                'user_input': kwargs.get("activity_name", "No activity"),
                'activity_list': str(activity_list)})

            if activity_id.activity_id == -1:
                return "An error occurred. You don't have any activities with that name."
        except:
            return "An error occurred. Be more clear"

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT r.user_id, u.username
                                FROM reservations r join users u 
                                    on r.user_id = u.user_id
                                WHERE r.activity_id = ? and r.state = 'pending'
                           """, (activity_id.activity_id,))
            reservation_user_list = cursor.fetchall()

            if len(reservation_user_list) == 0:
                return "There are currently no pending reservations for that activity"

        except:
            return "An error occurred while obtaining the list of reservations."

        finally:
            cursor.close()
            connection.close()

        try:
            user_id = GetReservationUserIDChain().invoke({
                'user_input': kwargs.get("user", "No user"),
                'reservation_list': str(reservation_user_list)})

            if user_id.user_id == -1:
                return "An error occurred. You don't have any reservations with that username for that activity."

        except:
            return "An error occurred."

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.execute(
                            """DELETE FROM reservations
                                WHERE activity_id = ? AND user_id = ? AND
                                state = 'pending' AND host_id = ?""",
                                (activity_id.activity_id, 
                                 user_id.user_id, host_id),
                            )
            connection.commit()

        except:
            return "An error occurred while rejecting the reservations."

        finally:
            cursor.close()
            connection.close()

        return "The reservation has been successfully rejected"
