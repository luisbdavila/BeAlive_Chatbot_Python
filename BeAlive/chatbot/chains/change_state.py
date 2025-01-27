from datetime import datetime
import sqlite3
from pinecone import Pinecone
from BeAlive.data.loader import get_sqlite_database_path


class UpdateActivitiesChain():
    """
    Update the state of activities in the database.

    Attributes:
    ----------
    db_path : func
        A function that returns the path to the SQLite database.

    Methods:
    -------

    __init__(self, db_path = funct):
        Initializes the UpdateActivitiesChain with the path to the SQLite
        database.

    UpdateActivities(self):
        Process the date and change the state of the activity to "finished" if
        the date is in the past.

    """

    def __init__(self,
                 db_path=get_sqlite_database_path()):

        """
        Initializes the UpdateActivitiesChain with the path to the SQLite
        database.

        Parameters:
        ----------
        db_path : func
            A function that returns the path to the SQLite database.

        """

        self.db_path = db_path

    def UpdateActivities(self):
        """
        Process the date and change the state of the activity to "finished" if
        the date is in the past.

        Returns:
        -------
            A string indicating the result of the update process.

        """

        today = datetime.now()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""SELECT activity_id
                              FROM activities
                              WHERE (activity_state = 'open'
                              or activity_state = 'full')
                              AND date_finish < ?""", (today,))
            finished_activities = [str(row[0]) for row in cursor.fetchall()]

        except:
            return "Error: Failed to retrieve finished activities."

        finally:
            cursor.close()
            conn.close()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(""" UPDATE activities
                           SET activity_state = 'finished', pinecone_id = NULL
                           WHERE (activity_state = 'open'
                           or activity_state = 'full')
                           AND date_finish < ?""", (today,))
            conn.commit()

        except:
            return "Error: Failed to update the activity state."

        finally:
            cursor.close()
            conn.close()

        try:
            pinecone = Pinecone()
            pinecone_index = pinecone.Index("activities")
            if finished_activities:
                pinecone_index.delete(ids=finished_activities)

        except:
            return "Error: Failed to remove finished activities."

        return "Activity state updated successfully."
