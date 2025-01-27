import sqlite3
import streamlit as st
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.process_query_output import QueryProcessingChain


class ShowReservationChain():
    """
    Class to show the reservations pending of the host

    Attributes:
    ----------
        db_path : str
            Function to the SQLite database

    Methods:
    --------
        __init__(db_path)
            Initialize the ShowReservationChain with a database path.
        ShowReservation()
            Show all the reservations pending of the host

    """

    def __init__(self,
                 db_path=get_sqlite_database_path()):
        """
        Initialize the ShowReservationChain with a database path.

        Parameters:
        ----------
            db_path : str
                Function to the SQLite database.
        """

        self.db_path = db_path

    def ShowReservation(self):
        """
        Show all the reservations pending of the host

        Returns:
        -------
                Prints the reservations pending of the host or
                a message if there are no reservations pending.
        """

        host_id = st.session_state.user_id
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """SELECT a.activity_name, u.username, u.cumulative_rating,
                              u.phone_number, u.email, r.message
                        FROM reservations r join activities a join users u
                            on r.activity_id = a.activity_id and
                            u.user_id = r.user_id
                        WHERE r.host_id = ? and a.activity_state = 'open' and
                              r.state = 'pending' """

            cursor.execute(query, (host_id,))
            reservations = cursor.fetchall()
            if len(reservations) == 0:
                return "You currently have no reservations pending to accept or reject"

        finally:
            cursor.close()
            conn.close()

        return QueryProcessingChain().invoke({
                "user_input": str(reservations),
                "sql_query": query
                })
