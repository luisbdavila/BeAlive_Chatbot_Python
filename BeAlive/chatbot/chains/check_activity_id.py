from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable.base import Runnable
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from BeAlive.chatbot.chains.base import PromptTemplate, generate_prompt_templates


class ActivityID(BaseModel):
    """
    ActivityID is a Pydantic model that represents the activity ID
    as an integer. It is used to parse the output of the LLM.
    Attributes:
    ----------
        activity_id : int
            The activity ID.
    """
    activity_id: int


class GetActivityIDChain(Runnable):
    """
    A chain for identifying the most similar activity name from a
    user provided input within a list of available activities.

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
        Initializes the GetActivityIDChain with the language model and memory
        settings.

    invoke(self, inputs: dict):
        Processes the user's input and activity list to find the most similar
        activity name
        and return its ID.

    """
    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False):

        """
        Initializes the GetActivityIDChain with a language model and memory
        settings.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used for natural language processing and
            activity matching.
        memory : bool
            Whether to use memory for the language model.
        """

        super().__init__()

        self.llm = llm
        prompt_template = PromptTemplate(
            system_template="""You are part of the customer support team.
                Your task is to identify the most similar 'activity_name' from
                the user input in a list of tuples of activities
                [(activity_id, activity_name),...], and return the
                'activity_id' (only 1, in integer form) of the most similar
                activit name. If there is a perfect match between the input and
                one activity_name, return the corresponding activity_id,
                otherwise return the activity_id of the most similar
                activity_name.
                If you are sure that no activity in the list
                has a similar name return -1. Please try to always return an
                actual activity_id, only return -1 as a last resort.

                Here is the user input:
                {user_input}

                Here is the list of activities [(activity_id, activity_name),...]:
                {activity_list}

                Please follow these format instructions:
                {format_instructions}
                """,
            human_template="User Query: {user_input}",
        )

        self.prompt = generate_prompt_templates(prompt_template, memory=memory)
        self.output_parser = PydanticOutputParser(pydantic_object=ActivityID)
        self.format_instructions = self.output_parser.get_format_instructions()

        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inputs):
        """
        Processes the user's input and activity list to find the most similar
        activity name and return its ID.

        Parameters:
        ----------
        inputs : dict
            A dictionary containing the user's input and the list of
            activities.

        Returns:
        --------
                The activity ID of the most similar activity name.
        """

        try:
            return self.chain.invoke(
                {
                    "user_input": inputs["user_input"],
                    "activity_list": inputs["activity_list"],
                    "format_instructions": self.format_instructions
                }
            )
        except:
            return "Error during execution:"
