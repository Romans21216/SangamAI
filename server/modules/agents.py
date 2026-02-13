"""Specialized agents for structured data analysis (CSV, Excel, etc.).

Unlike RAG workflows that embed+retrieve text, these agents use LangChain's
tool-calling capabilities to directly interact with Pandas DataFrames for
querying, plotting, and statistical analysis.
"""

import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent


def create_pandas_agent_chain(llm, dataframe: pd.DataFrame, verbose: bool = False):
    """Create a Pandas DataFrame agent that can query and plot data.
    
    The agent has access to the full DataFrame and can:
    - Answer natural language questions about the data
    - Generate plots (matplotlib)
    - Perform statistical analysis
    - Filter, group, aggregate data
    
    Parameters
    ----------
    llm : ChatOpenAI
        The language model (same instance used elsewhere in the app)
    dataframe : pd.DataFrame
        The CSV data loaded into memory
    verbose : bool
        Whether to print agent reasoning steps
        
    Returns
    -------
    Agent executor that can be called with natural language queries
    
    Example
    -------
    >>> agent = create_pandas_agent_chain(llm, df)
    >>> agent.run("What is the average sales by region?")
    'The average sales by region are: East: $45,234, West: $52,101...'
    """
    return create_pandas_dataframe_agent(
        llm=llm,
        df=dataframe,
        verbose=verbose,
        allow_dangerous_code=True,  # Required for code execution
        handle_parsing_errors=True,
    )


def ask_dataframe_question(agent, question: str) -> str:
    """Run a natural language question through the Pandas agent.
    
    Parameters
    ----------
    agent : Agent executor from create_pandas_agent_chain()
    question : str
        Natural language query about the data
        
    Returns
    -------
    str : Agent's answer (may include plot generation instructions)
    """
    try:
        result = agent.invoke({"input": question})
        return result.get("output", str(result))
    except Exception as e:
        return f"Error processing query: {str(e)}"
