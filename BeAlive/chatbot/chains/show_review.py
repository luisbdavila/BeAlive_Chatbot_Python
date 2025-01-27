import sqlite3
import streamlit as st
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.process_query_output import QueryProcessingChain


class ShowReviewChain():
    """
    Show all the reviews that users can give and hosts can give

    Attributes:
    ----------
        db_path : str
            Function to the SQLite database

    Methods:
    --------
        __init__(db_path)
            Initialize the ShowReviewChain with a database path.
        ShowReview()
            Show all the reviews that users can give and hosts can give
    """
    def __init__(self,
                 db_path=get_sqlite_database_path()):

        """
        Initializes the ShowReviewChain with a database path.

        Parameters:
        ----------
            db_path : str
                Function to the SQLite database.

        """

        self.db_path = db_path

    def ShowReview(self):
        """
        Show all the reviews that users can give and hosts can give

        Returns:
        -------
            Shows the reviews that users can give and hosts can give.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Review for users (they review activities)
        try:
            query_ac_re = """SELECT a.activity_name
                            FROM activities a JOIN reservations r
                                ON a.activity_id = r.activity_id
                                LEFT JOIN  review_activity re
                                    ON r.activity_id = re.activity_id
                            WHERE a.activity_state = 'finished' AND
                                  re.activity_id IS NULL and
                                  r.state = 'confirmed'
                                  and r.user_id = ?
                           """
            cursor.execute(query_ac_re, (st.session_state.user_id,))

            list_activitys_reviews = cursor.fetchall()
            list_activitys_reviews_names = [row[0] for row in list_activitys_reviews]

            # Join the list of strings with commas
            result_string = ", ".join(list_activitys_reviews_names)

            if len(list_activitys_reviews) == 0:
                text_ac_re = "NO PENDING REVIEWS OF ACTIVITIES"

            else:
                text_ac_re = "PENDING REVIEWS OF ACTIVITIES: " + result_string
        except:
            return "Error: Failed to retrieve the activity."

        finally:
            cursor.close()
            conn.close()

        # Review for hosts (they review users)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            query_u_re = """SELECT a.activity_name, u.username
                            FROM activities a JOIN reservations r
                                ON a.activity_id = r.activity_id
                                JOIN users u ON r.user_id = u.user_id
                                LEFT JOIN review_user re
                                    ON (r.user_id = re.user_id and
                                    r.activity_id = re.activity_id)
                            WHERE a.activity_state = 'finished' and
                            r.state = 'confirmed'
                                 and re.user_id IS NULL and a.host_id = ? """
            cursor.execute(query_u_re, (st.session_state.user_id,))
            list_users_reviews = cursor.fetchall()

            if len(list_users_reviews) == 0:
                text_u_re = "NO PENDING REVIEWS OF USERS"

            else:
                text_u_re = "PENDING REVIEWS OF USERS: " + \
                                    QueryProcessingChain().invoke({
                                        "user_input": str(list_users_reviews),
                                        "sql_query": query_u_re
                                        })

        except:
            return "Error: Failed to retrieve the informations."

        finally:
            cursor.close()
            conn.close()

        return text_ac_re + "\n\n" + text_u_re
