# Import necessary classes and modules for chatbot functionality
from typing import Callable, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.memory import CombinedMemory, ConversationBufferWindowMemory, ConversationSummaryMemory
from BeAlive.chatbot.agents.check_agent import CheckAgent
from BeAlive.chatbot.agents.reservation_agent import ReservationAgent
from BeAlive.chatbot.agents.Reviews_agent import ReviewsAgent
from BeAlive.chatbot.chains.company_info import CompanyInfoChain
from BeAlive.chatbot.chains.delete_activity import DeleteActivityChain
from BeAlive.chatbot.chains.chit_chat import ChitChatChain
from BeAlive.chatbot.chains.activity_search import ActivitySearchChain
from BeAlive.chatbot.chains.router_chain import RouterChain
from BeAlive.chatbot.chains.reasoning_chain import ReasoningChain

# Falta mudar a memoria, o o unknown handler


class MainChatbot:
    """A bot that handles customer service interactions by processing user
    inputs and routing them through configured reasoning and response chains.

    Attributes:
    -----------

    llm : ChatOpenAI
        The language model used for generating responses.
    chat_memory : ConversationBufferWindowMemory
        The memory object that stores the conversation history.
    summary_memory : ConversationSummaryMemory
        The memory object that stores the summary of the conversation history.
    memory : CombinedMemory
        The combined memory object that combines the chat and summary memories.
    chain_map : Dict[str, Callable[[Dict[str, str]], str]]
        A dictionary mapping intent names to their corresponding reasoning and
        response chains.
    agent_map : Dict[str, Callable[[Dict[str, str]], str]]
        A dictionary mapping agent names to their corresponding agents.
    intent_handler : Callable[[Dict[str, str]], str]
        A dictionary mapping intent names to their corresponding handlers.

    Methods:
    --------
    __init__()
        Initializes the bot with session and language model configurations.
    clear_memory()
        Clears the memory of the bot.
    add_messages_memory(message: str, respond: str)
        Adds messages to the memory of the bot.
    user_login(user_id: str)
        Logs in the user with the given user ID and conversation ID.
    get_chain(intent: str)
        Retrieves the reasoning and response chains based on the given intent.
    get_agent(intent: str)
        Retrieves the agent based on the given intent.
    handle_company_information(user_input: Dict)
        Handles the company information intent by processing user input and
        providing a response.
    handle_delete_activities(user_input: Dict)
        Handles the delete activity intent by processing user input and
        providing a response.
    handle_activity_search(user_input: Dict)
        Handles the activity search intent by processing user input and
        providing a response.
    handle_review_user((user_input: Dict)
        Handles the review user intent by processing user input and providing
        a response.
    handle_review_activity(user_input: Dict)
        Handles the review activity intent by processing user input and
        providing a response.
    handle_make_reservation(user_input: Dict)
        Handles the make reservation intent by processing user input and
        providing a response.
    handle_accept_reservation(user_input: Dict)
        Handles the accept reservation intent by processing user input and
        providing a response.
    handle_reject_reservation(user_input: Dict)
        Handles the reject reservation intent by processing user input and
        providing a response.
    handle_check_reservation(user_input: Dict)
        Handles the check reservation intent by processing user input and
        providing a response.
    handle_check_reviews(user_input: Dict)
        Handles the check reviews intent by processing user input and providing
        a response.
    handle_check_number_reservations(user_input: Dict)
        Handles the check number reservations intent by processing user input
        and providing a response.
    handle_chit_chat_intent(user_input: Dict)
        Handles the chit chat intent by processing user input and provides
        response.
    process_user_input(user_input: Dict)
        Processes the user input and provides a response based on the intent.
    """

    def __init__(self):
        """
        Initialize the bot with session and language model configurations.
        """

        # Configure the language model with specific parameters for response generation
        self.llm = ChatOpenAI(temperature=0.0, model="gpt-4o")

        # Initialize the memory to manage session history
        self.chat_memory = ConversationBufferWindowMemory(return_messages=True, memory_key="buffer_history", k=4)
        self.summary_memory = ConversationSummaryMemory(llm=self.llm,
                                                        memory_key="summary")

        self.memory = CombinedMemory(memories=[self.chat_memory,
                                               self.summary_memory])

        # Map intent names to their corresponding reasoning and response chains

        self.chain_map = {

            "Reasoning": ReasoningChain(llm=self.llm),

            "chitchat":  ChitChatChain(llm=self.llm),

            "company_information": CompanyInfoChain(llm=self.llm, index_name = 'company-info-rag', embeding = 'text-embedding-3-small'),

            "delete_activities":  DeleteActivityChain(llm=self.llm, index_name='activities', embeding = 'text-embedding-3-small'),

            "activity_search":  ActivitySearchChain(llm=self.llm, index_name='activities', embeding = 'text-embedding-3-small'),

            "router": RouterChain(llm=self.llm)}

        self.agent_map = {
            "review_user": ReviewsAgent(llm=self.llm),
            "review_activity": ReviewsAgent(llm=self.llm),
            "accept_reservation": ReservationAgent(llm=self.llm),
            "reject_reservation": ReservationAgent(llm=self.llm),
            "make_reservation": ReservationAgent(llm=self.llm),
            "check_reservations":  CheckAgent(llm=self.llm),
            "check_reviews": CheckAgent(llm=self.llm),
            "check_number_reservations": CheckAgent(llm=self.llm),
        }

        # Map of intentions to their corresponding handlers
        self.intent_handlers: Dict[Optional[str], Callable[[Dict[str, str]], str]] = {
            "company_information": self.handle_company_information,
            "delete_activities": self.handle_delete_activities,
            "activity_search": self.handle_activity_search,
            "review_user": self.handle_review_user,
            "review_activity": self.handle_review_actvity,
            "make_reservation": self.handle_make_reservation,
            "accept_reservation": self.handle_accept_reservation,
            "reject_reservation": self.handle_reject_reservation,
            "check_reservations": self.handle_check_reservations,
            "check_reviews": self.handle_check_reviews,
            "check_number_reservations": self.handle_check_number_reservations,
            "chitchat": self.handle_chitchat_intent}

    def clear_memory(self):
        """
            Deletes the memory history of the chatbot.
        """
        for memory in self.memory.memories:
            memory.clear()

    def add_messages_memory(self, message: str, respond: str):
        """
            Add the messages to the memory history of the chatbot.

        Parameters:
        -----------
        message: str
            The message to be added to the memory history.
        respond: str
            The response to the message to be added to the memory history.
        """
        for memory in self.memory.memories:
            memory.save_context(
                {"input": message},
                {"output": respond}
                )

    def user_login(self, user_id: str) -> None:
        """
        Log in a user by setting the user identifier.

        Parameters:
        ----------
            user_id:  str
                Identifier for the user.
        """
        self.user_id = user_id

    def get_chain(self, intent: str):
        """
        Retrieve the reasoning and response chains based on user intent.

        Parameters:
        ----------
            intent: str
                The identified intent of the user input.

        Returns:
        --------
            A tuple response chain instances for the intent.
        """
        return self.chain_map[intent]

    def get_agent(self, intent: str):
        """
        Retrieve the agent based on user intent.

        Parameters:
        ----------
            intent: str
                The identified intent of the user input.

        Returns:
        --------
            The agent instance for the intent.
        """
        return self.agent_map[intent]

    def handle_company_information(self, user_input: Dict):
        """
        Handle the product information intent by processing user input and
        providing a response.

        Parameters:
        ----------
            user_input: Dict
                The input text from the user.

        Returns:
        -------
            The content of the response after processing through the chains.
        """
        # Retrieve reasoning and response chains for the product information intent
        response_chain = self.get_chain("company_information")

        response = response_chain.invoke(user_input)

        return response

    def handle_delete_activities(self, user_input: Dict):
        """
        Handle the delete activities intent by processing user input and
        providing a response.

        Parameters:
        ----------
            user_input: str
                The input text from the user.

        Returns:
        -------
            The content of the response after processing through the chains.
        """
        # Retrieve reasoning and response chains for the product information intent
        response_chain = self.get_chain("delete_activities")

        response = response_chain.invoke(user_input)

        return response

    def handle_activity_search(self, user_input: Dict):
        """
        Handle the activity search intent by processing user input and
        providing a response.

        Parameters:
        ----------
            user_input: dict
                The input text from the user.

        Returns:
        -------
            The content of the response after processing through the chains.
        """

        response_chain = self.get_chain("activity_search")

        response = response_chain.invoke(user_input)

        return response

    def handle_review_user(self, user_input: Dict):
        """Handle the review user intent by processing user input and
        providing a response.

        Parameters:
        ----------
            user_input: Dict
            The input text from the user.

        Returns:
        -------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("review_user")

        response = agent.invoke(user_input)

        return response

    def handle_review_actvity(self, user_input: Dict):
        """
        Handle the review activity intent by processing user input and
        providing a response.

        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        -------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("review_activity")

        response = agent.invoke(user_input)

        return response

    def handle_make_reservation(self, user_input: Dict):
        """
        Handle the make reservation intent by processing user input and
        providing a response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        -------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("make_reservation")

        response = agent.invoke(user_input)

        return response

    def handle_accept_reservation(self, user_input: Dict):
        """
        Handle the accept reservation intent by processing user input and
        providing a response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        --------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("accept_reservation")

        response = agent.invoke(user_input)

        return response

    def handle_reject_reservation(self, user_input: Dict):
        """
        Handle the reject reservation intent by processing user input and
        providing a response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        --------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("reject_reservation")

        response = agent.invoke(user_input)

        return response

    def handle_check_reservations(self, user_input: Dict):
        """
        Handle the check reservations intent by processing user input and
        providing a response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        --------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("check_reservations")

        response = agent.invoke(user_input)

        return response

    def handle_check_reviews(self, user_input: Dict):
        """
        Handle the check reviews intent by processing user input and
        providing a response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        --------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("check_reviews")

        response = agent.invoke(user_input)

        return response

    def handle_check_number_reservations(self, user_input: Dict):
        """
        Handle the check number of reservations intent by processing user
        input and providing a response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.
        Returns:
        --------
            The content of the response after processing through the chains.
        """

        agent = self.get_agent("check_number_reservations")

        response = agent.invoke(user_input)

        return response

    def handle_chitchat_intent(self, user_input: Dict):
        """Handle the chitchat intent by processing user input and providing a
        response.
        Parameters:
        ----------
            user_input: Dict
                The input text from the user.

        Returns:
        -------
            The content of the response after processing through the chains.
        """

        response_chain = self.get_chain("chitchat")

        response = response_chain.invoke(user_input)

        return response

    def process_user_input(self, user_input: Dict[str, str]) -> str:
        """
        Process user input by routing through the appropriate
        intention pipeline.

        Parameters:
        ----------
            user_input: Dict[str, str]
                The input text from the user.

        Returns:
        -------
            The content of the response after processing through the chains.
        """
        # Collect the information based on chat_history and current input.

        inputs = {"user_input": user_input["user_input"],
                  "chat_history": [self.memory.memories[1].load_memory_variables({}),
                                   self.memory.memories[0].load_memory_variables({}),
                                   ]}

        # Classify the user's intent based on their input
        user_intention = self.get_chain("router").invoke(inputs)

        print("Intent:", user_intention.intent)

        inputs["intention"] = user_intention.intent

        input_processed = self.get_chain("Reasoning").invoke(inputs)

        inputs["user_input"] = input_processed

        # Route the input based on the identified intention
        handler = self.intent_handlers.get(user_intention.intent)

        return handler(inputs)
