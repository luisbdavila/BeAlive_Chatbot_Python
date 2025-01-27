from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable.base import Runnable
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from BeAlive.chatbot.chains.base import PromptTemplate, generate_prompt_templates


class Rating(BaseModel):
    """
    Rating is a Pydantic model that represents the rating
    as an integer. It is used to parse the output of the LLM.
    Attributes:
    ----------
        rating : int
            The rating.
    """
    rating: int


class GetRatingChain(Runnable):
    """
    A chain for identifying and extracting a rating from a
    user input within a list of available activities.

    Attributes:
    ----------
    llm : ChatOpenAI
        The language model used for natural language processing and activity
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
        Initializes the GetRatingChain with the language model and memory
        settings.

    invoke(self, inputs: dict):
        Processes the user's input to extract the rating from it and
        returns the parsed rating.

    """
    def __init__(self, llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False):

        """
        Initializes the GetRatingChain with a language model and memory
        settings.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used for natural language processing and
            activity matching.
        memory : bool
            Whether to use or not memory for the language model.
        """

        super().__init__()

        self.llm = llm
        prompt_template = PromptTemplate(
            system_template="""
            You are a part of the customer support team.
            Your task is to identify a rating (a number)
            in the user inut, an integer from 1 to 5 . 
            If you are sure that there is no rating return -1, Please try to always return a
            rating, only return -1 as a last resort.

            Here is the user input:
            {user_input}

            Please follow these format instructions:
            {format_instructions}
            """,
            human_template="User Query: {user_input}",)

        self.prompt = generate_prompt_templates(prompt_template, memory=memory)
        self.output_parser = PydanticOutputParser(pydantic_object=Rating)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inputs):
        """
        Processes the user's input to extract the rating and
        returns it.

        Parameters:
        ----------
        inputs : dict
            A dictionary containing the user's input and the list of
            activities.

        Returns:
        ----------
        str
            The extracted rating or an error message stating that
            something went wrong.
        """

        try:
            return self.chain.invoke(
                {
                    "user_input": inputs["user_input"],
                    "format_instructions": self.format_instructions
                }
            )
        except:
            return "Error during execution:"
