import sqlite3
import streamlit as st
from langchain.tools import BaseTool
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.process_query_output import QueryProcessingChain
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain


class CheckActivityReviewsTool(BaseTool):
    """
    Tool for checking activity reviews.

    Attributes:
    --------
        name : str
            The name of the tool.
        description : str
            The description of the tool.
        return_direct : bool
            Whether to return the result directly.

    Methods:
    --------
        _run(user_input: str, host_id: int = st.session_state.user_id) -> str:
            Retrieve reviews for an activity.
    
    """
    name: str = "CheckActivityReviewsTool"
    description: str = "Retrieve reviews for an activity."
    return_direct: bool = True

    def _run(
        self,
        user_input: str,
        host_id: int= st.session_state.user_id
    ) -> str:
        """
        Retrieve reviews for an activity.

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
                              WHERE host_id = ? and activity_state = 'finished'""",
                              (host_id,))
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
            query = """SELECT review, rating
                        FROM review_activity
                        WHERE activity_id = ?"""
            cursor.execute(query, (activity_id.activity_id,))
            reviews = cursor.fetchall()
            if len(reviews) == 0:
                return "You currently have no reviews for that activity"

        except:
            return "An error occurred while obtaining the reviews."

        finally:
            cursor.close()
            connection.close()

        return QueryProcessingChain().invoke({
                "user_input": str(reviews),
                "sql_query": query
                })
