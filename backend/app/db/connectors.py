from abc import ABC, abstractmethod
import pandas as pd
from sqlalchemy import create_engine, text
from app.db.database import SQLALCHEMY_DATABASE_URL

class BaseDatabaseConnector(ABC):
    """
    Abstract base class for all database connectors used by the Chatbot.
    Enables loose coupling and plug-and-play functionality.
    """

    @abstractmethod
    def get_schema(self) -> str:
        """
        Returns a string representation of the database schema (tables, columns)
        for the LLM to understand what data is available.
        """
        pass

    @abstractmethod
    def execute_query(self, query: str) -> str:
        """
        Executes a raw query against the database and returns the results.
        """
        pass


class NeonPostgresConnector(BaseDatabaseConnector):
    """
    Implementation for connecting to the Neon PostgreSQL database.
    """
    def __init__(self):
        # Ensure we are using the synchronous driver for Pandas/SQLAlchemy standard usage
        db_url = SQLALCHEMY_DATABASE_URL
        if db_url and db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        self.engine = create_engine(db_url)

    def get_schema(self) -> str:
        """
        Queries the information_schema to build a representation of all tables
        and their columns, specifically focusing on the chatbot data tables.
        """
        try:
            with self.engine.connect() as conn:
                # Get all tables in the public schema
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = conn.execute(tables_query).fetchall()
                
                schema_info = []
                for (table_name,) in tables:
                    columns_query = text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                    """)
                    columns = conn.execute(columns_query, {"table_name": table_name}).fetchall()
                    
                    cols_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
                    schema_info.append(f"Table: {table_name}\nColumns: {cols_str}\n")
                
                return "\n".join(schema_info)
        except Exception as e:
            return f"Error retrieving schema: {str(e)}"

    def execute_query(self, query: str) -> str:
        """
        Executes a readonly SQL query using pandas to easily format the output as a string/markdown.
        """
        try:
            # We explicitly prevent destructive operations for safety
            lower_query = query.lower()
            if any(forbidden in lower_query for forbidden in ['insert', 'update', 'delete', 'drop', 'truncate', 'alter']):
                return "Error: Only SELECT queries are allowed."
                
            with self.engine.connect() as conn:
                df = pd.read_sql_query(query, conn)
                if df.empty:
                    return "Query executed successfully, but returned 0 results."
                # Return the results as a markdown table or limited string
                # We limit the rows to prevent overwhelming the LLM context size
                return df.head(50).to_markdown(index=False)
        except Exception as e:
            return f"Query Error: {str(e)}"
