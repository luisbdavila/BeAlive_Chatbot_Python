from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable.base import Runnable, RunnableLambda
from langchain_core.runnables import RunnablePassthrough
from pinecone import Pinecone
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from BeAlive.chatbot.chains.base import (PromptTemplate,
                                         generate_prompt_templates)


class CompanyInfoChain(Runnable):
    """
    A chain for answering user inputs by retrieving relevant
    company information and generating a response.

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
    pc : Pinecone
        An instance for interacting with the Pinecone vector database.
    index : PineconeIndex
        The Pinecone index used for retrieving company documents.
    embedding : OpenAIEmbeddings
        Embedding model used for generating document embeddings.
    vectorstore : PineconeVectorStore
        A store for indexing and retrieving documents based on embeddings.
    retriever : Retriever
        A component that searches similarity between documents.
    company_info : Runnable
        A sequence of actions to retrieve and format company information.

    Methods:
    -------
    __init__(self,
                 llm=ChatOpenAI(),
                 memory=False,
                 index_name='company-info-rag'):
        Initializes the ChitChatChain with the language model, memory
        settings and Pinecone index configurations.

    invoke(self, inputs: dict, config=None, **kwargs):
        Processes the user's input, retrieves relevant company information
        and generates a response.
    """

    def __init__(self,
                 llm=ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo'),
                 memory=False,
                 index_name='company-info-rag',
                 embeding='text-embedding-3-small'):

        """
        Initializes the ChitChatChain with the language model, memory
        settings and Pinecone index configurations.

        Parameters:
        ----------
        llm : ChatOpenAI
            The language model used for natural language processing and
            generating responses.
        memory : bool
            Whether or not to use memory for the language model.
        index_name : str
             The name of the Pinecone index that will be used to
             retrieve information.
        embeding : str
             The name of the embedding used.
        """

        super().__init__()

        # Initialize Pinecone and set up the index
        self.pc = Pinecone()
        self.index = self.pc.Index(index_name)

        self.llm = llm

        self.embedding = OpenAIEmbeddings(model=embeding)
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=self.embedding)

        # Configure the retriever with similarity search and score threshold
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.5},
        )

        self.prompt_template = PromptTemplate(
            system_template="""
            You are an assistant that helps users by providing them
            information about the company.
            Use three sentences maximum.
            Your responses should be relevant to the query and focused on the
            company, using relevant company information.
            If you don't know the answer, just say that you don't know, don't
            try to make up an answer.

            Here is the user input:
            {user_input}

            Here is the relevant company information:
            {company_info}
            """,
            human_template="User Input: {user_input}",
        )

        self.company_info = (
                RunnablePassthrough()  # Passes user input
                | RunnableLambda(lambda inputs: self.retriever.get_relevant_documents(inputs["user_input"]))
                | RunnableLambda(lambda documents: (
                 "No relevant company information found." if not documents else "\n".join(doc.page_content for doc in documents)))
        )

        self.prompt = generate_prompt_templates(self.prompt_template, memory=memory)

        # Create the main chain
        self.chain = (
            RunnablePassthrough()  # Passes the user input
            .assign(company_info=self.company_info)  # Adds formatted company info
            | self.prompt  # Generates a prompt
            | self.llm  # Calls the language model
            | StrOutputParser()  # Parses the output
        )

    def invoke(self, inputs: dict, config=None, **kwargs) -> str:

        """
        Processes the user's input, retrieves relevant company information
        and generates a response.

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
            The response generated from the language model or an error message
            stating that something went wrong.
        """

        try:
            return self.chain.invoke(inputs, config)
        except:
            return "Error during execution:"
