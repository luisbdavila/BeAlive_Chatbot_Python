from pydantic import Field, BaseModel
from typing import Literal
from langchain_openai import ChatOpenAI
from langchain.schema.runnable.base import Runnable
from langchain.output_parsers import PydanticOutputParser
from BeAlive.chatbot.chains.base import PromptTemplate, generate_prompt_templates


class IntentClassification(BaseModel):
    """
    Represents the input model for intent classification os user queries.
    Attributes:
    ----------
        intent : Literal
            The classified intent of the user query,
              chosen from predefined options.
    """

    intent: Literal["company_information",
                    "delete_activities",
                    "activity_search",
                    "review_user",
                    "review_activity",
                    "make_reservation",
                    "accept_reservation",
                    "reject_reservation",
                    "check_reservations",
                    "check_reviews",
                    "check_number_reservations",
                    "chitchat"] = Field(
        ...,
        description="The classified intent of the user query",
    )


class RouterChain(Runnable):
    """
    A chain for processing user inputs and classifying intents using an LLM.

    Attributes:
    ----------
    llm : ChatOpenAI
        The language model used for natural language processing
        and generating responses.
    prompt : PromptTemplate
        The template used for constructing the system and human prompts for
        the language model.
    output_parser : PydanticOutputParser
        A parser to validate and format the output and return the response
        as a string.
    chain : Runnable
        The chain combining the prompt, language model, and output parser to
        process inputs.

    Methods:
    -------
    __init__(self,
                    llm=ChatOpenAI(),
                    memory = False):
        Initializes the RouterChain with a language model and memory
        settings.

    invoke(self, inputs, config=None, **kwargs):
        Processes the user query, classifies the intent and resturns it in
        a structures way.
    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False):
        """
        Initializes the RouterChain with a language model and memory
        settings.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used for natural language processing and
            generating responses.
        memory : bool
            Whether or not to use memory for the language model.

        """
        super().__init__()

        self.llm = llm
        prompt_template = PromptTemplate(
            system_template="""
            You are an expert classifier of user intentions for the BeAlive
            activity recommendation platform.
            Your role is to accurately identify the user's
            intent based on their query and the context provided by
            the conversation history.
            Analyze the user's query in the conversation history
            context and classify it into one of the intents:
            "company_information", "delete_activities", "activity_search",
            "review_user", "review_activity", "make_reservation",
            "accept_reservation", "reject_reservation", "check_reservations",
            "check_reviews", "check_number_reservations".
            You'll use the following detailed descriptions to
            classify the user's intent:

            1. **company_information:**
            The user wants to obtain information about the company
            or its chatbot and webpage.
            Terms like "How", "What" and "Where" or similar may be present.


            2. **delete_activities:**
           The user wants to delete a specific activity.
           Generally will include terms like 'delete' or
           'remove' or similar, and must specify an activity name.

            3. **activity_search:**
            The user wants to find an activity that best matches their
            interests and the preferences he is asking for.
            Generally, will have a description of what the user is
            looking for in an activity, additionally it may also include
            specific cities or time periods.

            4. **review_user:**
            The host of the activity wants to leave reviews about
            a participant of a specific activity.
            It must specify an activity name and a username, and will likely
            contain a review describing user behavior and potentially
            a 1 to 5 rating.

            5. **review_activity:**
            The user wants to review a specific activity they took part in
            and maybe leave feedback.
            It must specify an activity name, and will likely contain a review
            describing good or bad elements about that activity
            and potentially a 1 to 5 rating.

            6. **make_reservation:**
            The user wants to make a reservation for a specific activity.
            Must contain an activity name and may contain terms like
            "I want to reserve..." or "Book me a spot for..." or similar.

            7. **accept_reservation:**
            The host of the activity wants to accept a reservation from a
            specific user for a specific activity.
            An activity name and a username must be specified and terms like
            "I want to accept..." or simply "Accept" or similar should be
            present.

            8. **reject_reservation:**
            The host of the activity wants to reject a reservation from a
            specific user for a specific activity.
            An activity name and a username must be specified and terms like
            "I want to reject..." or simply "Reject", "decline" or similar
            should be present.

            9. **check_reservations:**
            The host of the activity wants to check the reservations to a
            specific activity.
            Must contain an activity name and will specify a request to
            check reservations or participants of that activity

            10. **check_reviews:**
            The host of the activity wants to check the reviews to a
            specific activity.
            Must contain an activity name and will specify a request to
            check reviews or opinions about that activity

            11. **check_number_reservations:**
            The host of the activity wants to check the number of reservations
            to a specific activity.
            Must contain an activity name and will specify a request to
            check the number of reservations of that activity.
            Terms like "How full...", "Is activity_name full?" or simply
            "How many reservations..." or "How many spots left in..." or
            similiar may be present.


            12. **chitchat:**
            The user is simply making small talk, not asking any questions or
            making any requests relevant to the activity recommendation system.
            The user could be asking about random topics or simply rambling
            about meaningless (in this context) topics.
            Use it when you feel that any other option is incorrect.


            **Input:**

            - User Input: {user_input}
            - Conversation History: {chat_history}

            **Output Format:**

            - Follow the specified output format and use these
            detailed descriptions:
            {format_instructions}
            """,
            human_template="User Query: {user_input}",
        )

        self.prompt = generate_prompt_templates(prompt_template, memory=memory)

        self.output_parser = PydanticOutputParser(
            pydantic_object=IntentClassification)
        self.format_instructions = self.output_parser.get_format_instructions()
        self.chain = (self.prompt | self.llm | self.output_parser)

    def invoke(self, inputs, config=None, **kwargs):
        """
        Processes the user query, classifies the intent and returns it in
        a structures way.

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
        IntentClassification
            The classified intent as a structured object.
        """

        return self.chain.invoke(
                {
                    "user_input": inputs["user_input"],
                    "chat_history": inputs["chat_history"],
                    "format_instructions": self.format_instructions,
                }, config
            )
