from langchain_core.output_parsers.string import StrOutputParser
from langchain.schema.runnable.base import Runnable
from langchain_openai import ChatOpenAI
from BeAlive.chatbot.chains.base import (PromptTemplate,
                                         generate_prompt_templates)


class ChitChatChain(Runnable):
    """
    A chain for answering user inputs with a polite tone,
    simulating a customer assistant.

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
    __init__(self, llm=ChatOpenAI(), memory=False):
        Initializes the ChitChatChain with the language model and memory
        settings.

    invoke(self, inputs, config=None, **kwargs):
        Processes the user's input and generates a polite
        response based on it.
    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False):

        """
        Initializes the ChitChatChain with a language model and memory
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
            You are a chill customer assistant called AIventure
            that works for a compant called BeAlive.
            Your task is to respond politely
            to user input.

            Here is the user input:
            {user_input}
            """,
            human_template="User Query: {user_input}",
        )

        self.prompt = generate_prompt_templates(prompt_template, memory=memory)
        self.output_parser = StrOutputParser()

        self.chain = self.prompt | self.llm | self.output_parser

    def invoke(self, inputs, config=None, **kwargs):

        """
        Processes the user's input and generates a polite response to it.

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
        str
            The response generated from the language model or an error message
            stating that something went wrong.
        """

        try:
            return self.chain.invoke(
                inputs,
                config
            )
        except:
            return "Error during execution:"
