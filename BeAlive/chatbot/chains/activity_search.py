import sqlite3
from datetime import datetime
from pinecone import Pinecone
import streamlit as st
from langchain.schema.runnable.base import Runnable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from BeAlive.chatbot.chains.activity_search_info import GetDesiredActivityInfoChain
from BeAlive.chatbot.chains.process_query_output import QueryProcessingChain
from BeAlive.data.loader import get_sqlite_database_path


def format_request(age: int, interests: str, message: str) -> str:
    """
    A function to format the request for the chatbot.

    Parameters:
    -----------

    - age (int): The age of the user.
    - interests (str): The interests of the user.
    - message (str): The message from the user.

    Returns:
    -------
    - str: The formatted request.

    """
    return (
        f"""User Age: {age},
        User interests: {interests},
        User Message: {message}"""
    )


class ActivitySearchChain(Runnable):
    """
    A class to search for activities based on user input.

    Attributes:
    ----------
    db_path : function
        The function to get the path to the SQLite database.
    llm : ChatOpenAI
        The language model used to process user input and generate output.
    pc : Pinecone
        The Pinecone client.
    index : Pinecone.Index
        The Pinecone index.
    embedding : OpenAIEmbeddings
        The OpenAI embeddings model.
    vectorstore : PineconeVectorStore
        The vector store that holds and retrieves vectors from the Pinecone
        index.

    Methods:
    -------
    __init__(self, llm=ChatOpenAI(), db_path=func, index_name=str):
        Initializes the system with the specified language model, database
        path, and Pinecone index.

    invoke(self, inputs: dict, config=None, user_id: int):
        Processes the user's input, retrieves user data and activitys
        information, and returns recommended activities or an error message.

    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 db_path=get_sqlite_database_path(),
                 index_name='activities',
                 embeding='text-embedding-3-small'
                 ):

        """
        Initializes the ActivityRecommendationSystem with a language model,
        SQLite database path, and Pinecone index. Sets up the connection to
        Pinecone.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used to process user input and generate
            activity search information.
        db_path : function
            The function to get the path to the SQLite database.
        index_name : str
            The name of the Pinecone index used for vector-based activity
            search.
        embeding : str
             The name of the embedding used.

        """
        super().__init__()
        self.db_path = db_path
        self.llm = llm

        # Initialize Pinecone and set up the index
        self.pc = Pinecone()
        self.index = self.pc.Index(index_name)

        self.embedding = OpenAIEmbeddings(model=embeding)
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=self.embedding)

    def invoke(self, inputs: dict, config=None,
               user_id: int = st.session_state.user_id):

        """
        Retrieves user details from the database, checks for
        activity availability in the specified city and date range,
        performs similarity searches on relevant activities,
        and returns a set of recommended activities.

        Parameters:
        ----------
        inputs : dict
            A dictionary containing user input data.
        config : Optional
            Configuration settings for the execution.
        user_id : int
            The unique identifier of the user.

        Returns:
        -------
        str
            A string containing the recommended activities.
            Or an error message if any error occurs during execution.

        """
        user_input = inputs['user_input']
        today = datetime.today().date()
        activity_search_info = GetDesiredActivityInfoChain(self.llm).invoke({
            'user_input': user_input},
            config
            )

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""SELECT birthday, interests, location
                              FROM users
                              WHERE user_id = ?""",  (user_id,))
            user_info = cursor.fetchone()
            user_age = (today.year - datetime.strptime(user_info[0], '%Y-%m-%d').year)
            request_info = format_request(user_age, user_info[1], user_input)
        except:
            return "There was a database error while obtaining your information"

        finally:
            cursor.close()
            conn.close()

        if activity_search_info.city == 'None':
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""SELECT activity_id
                                FROM activities
                                WHERE city = ? and date_begin > ? and
                                date_finish < ? and activity_state = 'open'""",
                               (user_info[2],
                                activity_search_info.date_range_start,
                                activity_search_info.date_range_end))
                id_list = [str(res[0]) for res in cursor.fetchall()]
                if len(id_list) == 0:
                    return "No activity was found with those characteristics"
            except:
                return "There was a database error while obtaining activities"

            finally:
                cursor.close()
                conn.close()

        else:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("""SELECT activity_id
                                FROM activities
                                WHERE city = ? and date_begin > ? and
                               date_finish < ? and activity_state = 'open'""",
                               (activity_search_info.city,
                                activity_search_info.date_range_start,
                                activity_search_info.date_range_end))
                id_list = [str(res[0]) for res in cursor.fetchall()]
                if len(id_list) == 0:
                    return "No activity was found with those characteristics"
            except:
                return "There was a database error while obtaining activities"

            finally:
                cursor.close()
                conn.close()

        # Configure the retriever with similarity search and score threshold
        retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "filter": {"pinecone_id": {"$in": id_list}},
                "score_threshold": 0.5
                },
        )
        recommended_ids = [int(response.id) for response in retriever.invoke(request_info)]

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            aux = {1: '(?)', 2: '(?,?)', 3: '(?,?,?)'}
            query = """SELECT activity_name, activity_description, location,
                    number_participants, max_participants, city, date_begin,
                    date_finish
                    FROM activities
                    WHERE activity_id IN """ + aux[len(recommended_ids)]
            cursor.execute(query, (tuple(recommended_ids)))
            recommended_activities = cursor.fetchall()
        except:
            return f"There was a database error while obtaining recommened activities."

        finally:
            cursor.close()
            conn.close()

        return QueryProcessingChain().invoke({
                "user_input": str(recommended_activities),
                "sql_query": query
                })
