from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable.base import Runnable


class ReasoningChain(Runnable):
    """
    A chain to extract specific fields from user input, chat history, and user
    intention for the BeAlive platform.

    Attributes:
    ----------
        llm : ChatOpenAI
            A language model for processing input and generating
        output.
        prompt : PromptTemplat
            A template defining input variables and
            extraction logic.
        output_parser : StrOutputParser
            Parses the output into a string
            format.
        chain : Chain
            The sequence combining the prompt, LLM, and parser.

    Methods:
    --------
        __init__(llm)
            Initializes the ReasoningChain with a language model.
        invoke(inputs, config=None, **kwargs)
            Processes inputs to extract and structure required information.
    """

    def __init__(self, llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')):
        """
        Initialize the ReasoningChain with a language model.

        Parameters:
        ----------
            llm : ChatOpenAI
                A language model for processing input and generating output.
        """
        super().__init__()

        self.llm = llm

        self.prompt = PromptTemplate(
                input_variables=["user_input",
                                 "chat_history",
                                 "intention"],
                template="""
            You are an expert data extractor assistant for the BeAlive activity
            recommendation platform.
            Your role is to accurately identify and structure in a specific
            output format the required fields needed based on 3 things:
            - The user's input ({user_input}).
            - The chat history/conversation history ({chat_history}).
            - The user's intention ({intention}).

            The user intention can be one of the following intents:
            "company_information", "delete_activities", "activity_search",
            "review_user", "review_activity", "make_reservation",
            "accept_reservation", "reject_reservation", "check_reservations",
            "check_reviews", "check_number_reservations".
            Focus on the specified user intention: {intention}.

            Based on the intention, follow the respective extraction and
            output format below.

            **Output Format:**

            1. **company_information:**
            Extract the question about the company, chatbot, or webpage.
            Return it in structured plain text.
            Example question about the company: 'What is your refund policy?'.

            2. **delete_activities:**
            Extract the activity name and return it in a structured format.
            Example: 'Activity name: Sunset Yoga Retreat'.

            3. **activity_search:**
            Extract the city (if mentioned) and the date constraint (if
            mentioned).
            Combine these with the user input and structure the output.
            Example: 'I want to do a fun activity in Lisbon on February 12th'.

            4. **review_user:**
            Extract the review, username, rating and activity name.
            Example: 'Review: The participant was punctual and very
            cooperative.
                      Username: JohnDoe.
                      Rating: 5.
                      Activity name: Culinary Masterclass, Italian Cuisine.'.

            5. **review_activity:** (review, activity_name and rating)
            Extract the review, activity name, and rating.
            Example: 'Review: The dance Workshop was and and not well
            organized.
                      Activity name: Dance Workshop.
                      Rating: 1'.

            6. **make_reservation:** (activity name, message)
            Extract the activity name and any associated message.
            Example: 'Activity name: Wine Tasting Experience.
                      Message: Please i am very funny and want to relax.'.

            7. **accept_reservation:** (username, activity_name)
            Extract the username and activity name.
            Example: 'Username: JohnDoe.
                      Activity name: Sunset Yoga Retreat'.

            8. **reject_reservation:** (username, activity_name)
            Extract the username and activity name.
            Example: 'Username: JaneSmith.
                      Activity name: Kayaking Adventure'.

            9. **check_reservations:** (activity_name)
            Extract the activity name.
            Example: 'Activity name: Creative Writing Workshop: Unleash Your
            Imagination'.

            10. **check_reviews:** (activity_name)
            Extract the activity name.
            Example: 'Activity name: Pottery Wheel Experience'.

            11. **check_number_reservations:** (activity_name)
            Extract the activity name.
            Example: 'Activity name: Meditation Retreat'.

            12. **chitchat:**
            Analyze the user input and chat history.
            Extract any question or statement made by the user and pair
            it with the answer (if found in the memory).

            Key Notes:
            - For all intentions also return the intention.
            (Example: "Intention: accept_reservation")
            - Extract and return only the fields mentioned in the relevant
            context. Do not extract irrelevant fields from random contexts.
            - Always infer the context and fields to extract from the given
            intention: {intention}.
            - Use only the following sources for your extraction:
                1) User Input: {user_input}
                2) Chat History: {chat_history}

            - Consider as first priority only the User input,
              if you cannot find something in the user input then,
              use the chat history.

            Your output must strictly follow the formats specified above and
            focus solely on extraction.
            Do not provide additional commentary or responses.
                          """)

        self.output_parser = StrOutputParser()
        self.chain = (self.prompt | self.llm | self.output_parser)

    def invoke(self, inputs, config=None, **kwargs):
        """
        Processes the input data using the defined chain.

        Parameters:
        ----------
            inputs : dict
                The input data to be processed.
            config : dict, optional
                Configuration settings for the chain.
        """

        return self.chain.invoke(inputs, config)
