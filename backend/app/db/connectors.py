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
                    AND table_name IN ('sql', 'ba_sql', 'sql_ba', 'sql_dm', 'dm', 'pm', 'apm', 'qc', 'cf')
                """)
                tables = conn.execute(tables_query).fetchall()
                
                schema_info = [
                    "--- [DB] POSTGRES DATA-TRANSFORMATION HINTS ---\n"
                    "1. Dates in columns like 'resource_onboarded_date_if_selected_' may contain strings like 'Offer Drop' or '... - 12-May-25'.\n"
                    "2. ALWAYS use a regex filter like `~ '^\\d{4}-\\d{2}-\\d{2}'` OR search for specific sub-strings BEFORE casting to timestamp.\n"
                    "3. For analytics, use `NULLIF(column, '')` or `NULLIF(column, 'Offer Drop')` when performing math.\n\n"
                ]
                for (table_name,) in tables:
                    columns_query = text("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = :table_name
                    """)
                    columns = conn.execute(columns_query, {"table_name": table_name}).fetchall()
                    
                    cols_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
                    
                    try:
                        # Pull 10 rows for better variety visibility
                        sample_query = text(f'SELECT * FROM "{table_name}" LIMIT 10')
                        sample_df = pd.read_sql_query(sample_query, conn)
                        sample_data = sample_df.to_csv(index=False).strip()
                    except Exception:
                        sample_data = "No sample data available."
                        
                    schema_info.append(f"Table: {table_name}\nColumns: {cols_str}\nSample Data:\n{sample_data}\n")
                
                return "\n".join(schema_info)
        except Exception as e:
            return f"Error retrieving schema: {str(e)}"

    def execute_query(self, query: str) -> str:
        """
        Executes a readonly SQL query using pandas to easily format the output as a string/markdown.
        """
        try:
            # We explicitly prevent destructive operations for safety
            import re
            # Remove all string literals ('...') and ("...") to prevent false positives like '%offer drop%'
            clean_query = re.sub(r"'.*?'", "", query, flags=re.DOTALL)
            clean_query = re.sub(r'".*?"', "", clean_query, flags=re.DOTALL)
            lower_query = clean_query.lower()
            if re.search(r'\b(insert|update|delete|drop|truncate|alter)\b', lower_query):
                return "Error: Only SELECT queries are allowed."
                
            with self.engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
                if df.empty:
                    return "Query executed successfully, but returned 0 results."
                # Return the results as a CSV string
                # We limit the rows to prevent overwhelming the LLM context size
                return df.head(50).to_csv(index=False)
        except Exception as e:
            return f"Query Error: {str(e)}"
