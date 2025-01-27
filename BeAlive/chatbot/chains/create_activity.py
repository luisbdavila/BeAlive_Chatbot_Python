from BeAlive.data.loader import get_sqlite_database_path
from datetime import datetime
from pydantic import BaseModel
from langchain.schema.runnable.base import Runnable
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
import sqlite3
import streamlit as st
from pinecone import Index, Pinecone
from langchain_pinecone import PineconeVectorStore


class CreateActvityInput(BaseModel):
    """
    Represents the input model for creating an activity.
    Attributes:
    ----------
        activity_name : str
            The name of the activity.
        activity_description : str
            The description of the activity.
        location : str
            The location of the activity.
        max_participants : int
            The maximum number of participants in an activity.
        city : str
            The city where the activity will take place.
        date_begin : datetime
            The date when the activity begins.
        date_finish : datetime
            The date when the activity ends.
    """

    activity_name: str
    activity_description: str
    location: str
    max_participants: int
    city: str
    date_begin: datetime
    date_finish: datetime


def format_activity(activity: CreateActvityInput) -> str:
    """
    A function to format the request for the chatbot.

    Parameters:
    ----------
        activity : CreateActvityInput
            The activity details.

    Returns:
    -------
        str
            The formatted request.
    """
    return (
        f"""Activity Name: {activity.activity_name},
        Activity Description: {activity.activity_description}"""
    )


class CreateActivityChain(Runnable):
    """
    A chain for processing user inputs, validating activity details and
    saving them to a database and Pinecone vector store.

    Attributes:
    ----------
    llm : ChatOpenAI
        The language model used for natural language processing
        and generating responses.
    db_path : str
        The path to the SQLite database.
    input_prompt : PromptTemplate
        The template used for constructing the system and human prompts for
        the language model.
    output_parser : PydanticOutputParser
        A parser to validate and format the output and return the response
        as a string.
    input_chain : Runnable
        The chain combining the prompt, language model, and output parser to
        process inputs.

    Methods:
    -------
    __init__(self,
                 llm=ChatOpenAI(),
                 db_path=get_sqlite_database_path()):
        Initializes the CreateActivityChain with the language model and
        database path.

    invoke(self, content: str) -> str:
        Processes the input content, validates activity details, saves them to
        the database and integrates them into Pinecone.

    _store_activity_in_pinecone(self, parsed_output, act_id):
        Stores the activity in Pinecone.
    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 db_path=get_sqlite_database_path(),
                 ):

        """
        Initializes the CreateActivityChain with the language model and
        database path.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used for natural language processing and
            generating responses.
        db_path : str
        The path to the SQLite database.

        """

        self.llm = llm
        self.db_path = db_path

        # Define the prompt template for translation
        self.input_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    """Extract from the text into a JSON format "
                    the information that matches the following keys:
                    'activity_name', 'activity_description',
                    'location', 'max_participants', 'city', 'date_begin',
                    'date_finish'. Ensure the types are correct.
                    'max_participants' should be an integer number
                    and 'date_begin'/'date_finish' should be a date
                    in ISO 8601 format (YYYY-MM-DD hh:mm:ss).
                    """
                ),
                HumanMessagePromptTemplate.from_template("{content}"),
            ]
        )
        self.output_parser = PydanticOutputParser(
            pydantic_object=CreateActvityInput)
        self.input_chain = self.input_prompt | self.llm | self.output_parser

    def invoke(self, content: str) -> str:
        """
        Processes the input content and execute the activity creation logic.

        Parameters:
        ----------
        content : str
            The user's input describing the activity.

        Returns:
        -------
        str
            Either a success or error message, based on the outcome
            of the operation.
        """

        try:
            # Process the input through the chain
            parsed_output = self.input_chain.invoke({"content": content})

            # Validation checks
            if parsed_output.max_participants == 0:
                return """The maximum number of participants has been inserted
                incorrectly, please fill the form again and re-submit it."""
            if parsed_output.date_begin > parsed_output.date_finish:
                return """The end date for the activity is before the start
                date, please fill the form again and re-submit it."""
            if datetime.now() > parsed_output.date_begin or datetime.now() > parsed_output.date_finish:
                return """The start and/or end dates for the activity are set
                to a date that has already passed, please fill the form again
                and re-submit it."""
            if len(parsed_output.activity_description) > 400:
                return """The activity description exceeds the maximum limit of
                400 characters, please fill the form again and re-submit it."""

            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """INSERT INTO activities
                    (host_id, activity_name, activity_description, location,
                      city, max_participants, date_begin, date_finish)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (st.session_state.user_id, parsed_output.activity_name,
                     parsed_output.activity_description,
                     parsed_output.location,
                     parsed_output.city, parsed_output.max_participants,
                     parsed_output.date_begin, parsed_output.date_finish),
                )
                conn.commit()
                act_id = int(cursor.lastrowid)

                # Pinecone integration
                self._store_activity_in_pinecone(parsed_output, act_id)

                cursor.execute("""UPDATE activities SET pinecone_id = ?
                                WHERE activity_id = ?""", (act_id, act_id))
                conn.commit()

            except:
                return "An error occurred while saving the activity"

            finally:
                cursor.close()
                conn.close()

            return f"""Activity created successfully, with ID: {act_id}, please remove the file uploaded by clicling the X"""

        except:
            return "An error occurred, resubmit againg with correct format"

    def _store_activity_in_pinecone(self, parsed_output, act_id):
        """
        Store the activity details in Pinecone for vector search.

        Parameters:
        ----------
        parsed_output : CreateActvityInput
            The validated and parsed activity details.
        act_id : int
            The activity ID in the database.
        """
        pinecone_prompt_template = PromptTemplate(
            input_variables=["activity"],
            template="""Transform the following structured activity data into
            a human-readable text using less than 500 characters:

            Activity Data:
            {activity}

            Human-Readable Text:"""
        )
        pinecone_chain = (pinecone_prompt_template | self.llm | 
                          StrOutputParser())
        pc = Pinecone()
        index: Index = pc.Index("activities")
        vector_store = PineconeVectorStore(
            index=index, embedding=OpenAIEmbeddings(
                model="text-embedding-3-small")
        )

        doc_activity = Document(page_content=pinecone_chain.invoke(
            {"activity": format_activity(parsed_output)}),
            metadata={"pinecone_id": str(act_id)})

        vector_store.add_documents(documents=[doc_activity], ids=[str(act_id)])
