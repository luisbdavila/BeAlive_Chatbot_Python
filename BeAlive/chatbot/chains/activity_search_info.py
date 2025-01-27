from datetime import datetime
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable.base import Runnable
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from BeAlive.chatbot.chains.base import PromptTemplate, generate_prompt_templates


class ActivitySearchInfo(BaseModel):
    """
    A data model representing information about a user's desired activity
    search.

    Attributes:
    ----------
    city : str
        The city where the user is searching for an activity.
    date_range_start : datetime
        The start date and time of the activity search period.
    date_range_end : datetime
        The end date and time of the activity search period.
    """

    city: str
    date_range_start: datetime
    date_range_end: datetime


class GetDesiredActivityInfoChain(Runnable):

    """
    A class that processes user queries to extract specific activity search
    information.

    Attributes:
    ----------
    llm : ChatOpenAI
        The language model used to process user input and generate the
        response.
    prompt_template : PromptTemplate
        The prompt template that defines the system and human inputs for the
        interaction.
    prompt : str
        The formatted system prompt that is passed to the language model.
    output_parser : PydanticOutputParser
        The output parser that converts the raw response from the language
        model into a structured object.
    format_instructions : str
        Instructions that specify the format of the response.
    chain : Chain
        The chain of operations (prompt, language model, and output parser).

    Methods:
    -------
    __init__(self, llm=ChatOpenAI(), memory=False):
        Initializes the chain by setting up the language model, prompt
        template, output parser, and format instructions.

    invoke(self, inputs: dict, config=None, **kwargs):
        Executes the chain with the provided inputs, processes the user query,
        and returns the parsed activity search information.

    """
    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False):

        """
        Initializes the GetDesiredActivityInfo with a language model.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used to process user input and generate the
            response.
        memory : bool
            Whether to use memory for the language model.
        """
        super().__init__()

        self.llm = llm
        prompt_template = PromptTemplate(
            system_template="""You are part of the customer support team.
                Your task is to identify if in the user has mentioned
                any specific date period or city where he is searching for an
                actvity. If you can't find a city just return 'None'
                and if you can't find any dates return the start date as day 1,
                month 1, year 1 at midnight and the end date as day 1, month 1,
                year 9999 at midnight. Never return an end date that's before
                the start date, obviously. Ensure that the start and end dates
                for the interval are after the current date, except in the case
                where no date range is specified.
                The current date is {today}.
                Values for city, start date and end date must always be
                returned, if you can't find the information return the
                default values specified above. Always ensure that the
                dates returned are in ISO 8601 format.

                Here is the user input:
                {user_input}

                Please follow these format instructions:
                {format_instructions}
                """,
            human_template="User Query: {user_input}",
        )

        self.prompt = generate_prompt_templates(prompt_template, memory)
        self.output_parser = PydanticOutputParser(pydantic_object=ActivitySearchInfo)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inputs, config=None, **kwargs):

        """

        Retrieves the desired activity search information from the user's
        input.

        Parameters:
        ----------
        inputs : dict
            A dictionary containing the user's input.
        config : optional
            Configuration settings for the chain.
        **kwargs :
            Additional keyword arguments.

        Returns:
        -------
        ActivitySearchInfo
            The parsed activity search information.

        """

        try:
            return self.chain.invoke(
                {
                    "user_input": inputs["user_input"],
                    "today": datetime.now(),
                    "format_instructions": self.format_instructions
                }, config
            )
        except:
            return "Error during execution:"
