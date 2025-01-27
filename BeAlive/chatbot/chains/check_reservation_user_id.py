from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable.base import Runnable
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from BeAlive.chatbot.chains.base import PromptTemplate, generate_prompt_templates


class UserID(BaseModel):
    """
    UserID is a Pydantic model that represents the user ID
    as an integer. It is used to parse the output of the LLM.
    Attributes:
    ----------
        user_id : int
            The user ID.
    """
    user_id: int


class GetReservationUserIDChain(Runnable):
    """
    A chain for identifying and extracting the most similar user ID from
    a user input by matching it to a list of available reservations.

    Attributes:
    ----------
    llm : ChatOpenAI
        The language model used for natural language processing and user ID
        matching.
    prompt : PromptTemplate
        The template used for constructing the system and human prompts for
        the language model.
    output_parser : PydanticOutputParser
        A parser to validate and format the output into a predefined Pydantic
        object.
    chain : Runnable
        The chain combining the prompt, language model, and output parser to
        process inputs.

    Methods:
    -------
    __init__(self, llm=ChatOpenAI(), memory=False):
        Initializes the GetReservationUserIDChain with the language model and
        memory settings.

    invoke(self, inputs: dict):
        Processes the user's input and reservation list to find the most
        similar user ID and returns it.
    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False):

        """
        Initializes the GetReservationUserIDChain with a language model and
        memory settings.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used for natural language processing and
            user ID matching.
        memory : bool
            Whether or not to use memory for the language model.
        """

        super().__init__()

        self.llm = llm
        prompt_template = PromptTemplate(
            system_template="""
            You are part of the customer support team.
            Your task is to identify the most similar 'user_id' from
            the user input in a list of tuples of usernames
            [(user_id, username),...], and return the
            'user_id' (only 1, in integer form) of the most similar
            activit name. If you are sure that no activity in the list
            has a similar name return -1. Please try to always return an
            actual user_id, only return -1 as a last resort.

            Here is the user input:
            {user_input}

            Here is the list of user reservations [(user_id, username),...]:
            {reservation_list}

            Here is are the format instructions:
            {format_instructions}
            """,
            human_template="User Query: {user_input}",
        )

        self.prompt = generate_prompt_templates(prompt_template, memory=memory)
        self.output_parser = PydanticOutputParser(pydantic_object=UserID)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inputs):

        """
        Processes the user's input and reservation list to find the most
        similar user ID and return it.

        Parameters:
        ----------
        inputs : dict
            A dictionary containing the user's input and the list of
            activities.

        Returns:
        -------
        str
            The extracted user ID or an error message stating that
            something went wrong.
        """

        try:
            return self.chain.invoke(
               {
                    "user_input": inputs["user_input"],
                    "reservation_list": inputs["reservation_list"],
                    "format_instructions": self.format_instructions
                }
            )
        except:
            return "Error during execution."