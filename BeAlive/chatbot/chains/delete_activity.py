import sqlite3
from pydantic import BaseModel
from langchain.schema.runnable.base import Runnable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import streamlit as st
from pinecone import Index, Pinecone
from langchain_pinecone import PineconeVectorStore
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain


class DeleteActvityInput(BaseModel):
    """
    Input schema for the DeleteActivityChain.
    """
    activity_name: str


class DeleteActivityChain(Runnable):
    """

    A chain to handle the deletion of activities associated with a host user.

    Attributes:
    ----------
        llm : ChatOpenAI
            A language model used for processing user input and
            extracting relevant information.
        db_path : function
            Function with the path to the SQLite database where activity
            information is stored.
        index : str
            The name of the Pinecone index that will be used to
            retrieve information.
        embedding : str
            The name of the embedding used.

    Methods:
    -------
        __init__(llm, db_path):
            Initializes the DeleteActivityChain with the provided language
            model and database path.

        invoke(inputs, config=None, **kwargs):
            Processes the input content, fetches the activity details, and
            executes the deletion logic.

        _remove_activity_in_pinecone(act_id):
            Deletes the specified activity's data from the Pinecone vector
            database.
    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 db_path=get_sqlite_database_path(),
                 index_name='activities',
                 embeding='text-embedding-3-small'):
        """
        Initializes the DeleteActivityChain with the provided language
        model and database path.

        Parameters:
        ----------
            llm : ChatOpenAI
                A language model used for processing user input and
                extracting relevant information.
            db_path : function
                Function with the path to the SQLite database where activity
                information is stored.
            index_name : str
                The name of the Pinecone index that will be used to
                retrieve information.
            embeding : str
                The name of the embedding used.
        """

        super().__init__()
        self.llm = llm
        self.db_path = db_path
        self.index = index_name
        self.embedding = embeding

    def invoke(self, inputs, config=None, **kwargs):
        """
        Process the input content and execute the activity removal logic.

        Parameters:
        ----------
            inputs : dict
                A dictionary containing the user input.
            config : optional
                Configuration settings for the chain.
            **kwargs : dict
                Additional keyword arguments.

        Returns:
        -------
            str
                A message indicating the result of the activity removal.
        """

        try:
            host_id = st.session_state.user_id
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""SELECT activity_id, activity_name
                              FROM activities
                              WHERE host_id = ? and activity_state != 'finished'""",  (host_id,))
            activity_list = cursor.fetchall()
            activity_id = GetActivityIDChain().invoke({"user_input": inputs['user_input'],
                                                       'activity_list': str(activity_list)
                                                       })
            if activity_id.activity_id == -1:
                return "You have no activity with that name"

            conn.close()

        except:
            return "Error: Failed to retrieve activity list."

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""SELECT activity_state
                              FROM activities
                              WHERE activity_id = ?""",  (activity_id.activity_id,))
            activity_state = cursor.fetchone()

            if not activity_state[0] == 'finished':

                self._remove_activity_in_pinecone(activity_id.activity_id)

                cursor.execute("""DELETE FROM activities
                                WHERE activity_id = ?""",
                               (activity_id.activity_id,))
                conn.commit()
                cursor.execute("""DELETE FROM reservations
                               WHERE activity_id = ?""",
                               (activity_id.activity_id,))
                conn.commit()

            else:
                return "The activity already finished"

        except:
            return "An error occurred while deleting the activity."

        finally:
            cursor.close()
            conn.close()

        return "Activity removed successfully"

    def _remove_activity_in_pinecone(self, act_id):
        """
        Delete the activity from Pinecone.
        """

        pc = Pinecone()
        index: Index = pc.Index(self.index)
        vector_store = PineconeVectorStore(
            index=index, embedding=OpenAIEmbeddings(model=self.embedding)
        )

        vector_store.delete(ids=[str(act_id)])
