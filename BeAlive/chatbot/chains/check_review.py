from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable.base import Runnable
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from BeAlive.chatbot.chains.base import PromptTemplate, generate_prompt_templates


class Review(BaseModel):
    """
    Represents the review extracted from user input.
    Attributes:
    ----------
        review : str
            The review.
    """
    review: str


class GetReviewChain(Runnable):
    """
    A chain for identifying and extracting a review from a
    user input.

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
        Initializes the GetReviewChain with the language model and memory
        settings.

    invoke(self, inputs: dict):
        Processes the user's input to extract the review from it and
        returns the parsed review.

    """
    def __init__(self, llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                  memory=False):
        """
        Initializes the GetReviewChain with a language model and memory
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
            Your task is to directly extract a review from the user input,
            and return it as a string.
            An example of a review:
            "The dance Workshop was and and not well-organized" for an activity
            "The participant was punctual and very cooperative." for a user

            Here is the user input:
            {user_input}

            Please follow these format instructions:
            {format_instructions}
            """,
            human_template="User Query: {user_input}",)

        self.prompt = generate_prompt_templates(prompt_template,
                                                 memory=memory)
        self.output_parser = PydanticOutputParser(pydantic_object=Review)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inputs):
        """
        Processes the user's input to extract the review and
        returns it.

        Parameters:
        ----------
        inputs : dict
            A dictionary containing the user's input.

        Returns:
        ----------
        str
            The extracted review or an error message stating that
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
