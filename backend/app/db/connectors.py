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


class ProductionSqlConnector(BaseDatabaseConnector):
    """
    Implementation for connecting to the Production SQL database (PostgreSQL or MySQL).
    """
    def __init__(self):
        # Ensure we are using the synchronous driver for Pandas/SQLAlchemy standard usage
        db_url = SQLALCHEMY_DATABASE_URL
        if db_url and db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        self.engine = create_engine(db_url)
        self.dialect = self.engine.dialect.name # 'postgresql' or 'mysql'

    def get_schema(self) -> str:
        """
        Queries the information_schema to build a representation of CORE recruitment tables.
        Uses a WHITELIST to reduce noise and context size for the LLM.
        """
        # Define the whitelist of essential and secondary tables
        WHITELIST = [
            # Essential
            'candidate', 'joborder', 'company', 'candidate_joborder', 
            'candidate_joborder_status', 'activity', 'contact',
            # Secondary
            'user', 'tag', 'candidate_tag', 'candidate_source', 'extra_field'
        ]
        
        try:
            with self.engine.connect() as conn:
                if self.dialect == 'postgresql':
                    # PostgreSQL filtering (though we are focused on MySQL right now)
                    tables_query = text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name IN :whitelist
                    """)
                    params = {"whitelist": tuple(WHITELIST)}
                else: # MySQL
                    db_name = self.engine.url.database
                    tables_query = text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = :db_name AND table_name IN :whitelist
                    """)
                    params = {"db_name": db_name, "whitelist": tuple(WHITELIST)}

                tables_result = conn.execute(tables_query, params).fetchall()
                tables = [t[0] for t in tables_result]
                
                schema_info = []
                if self.dialect == 'postgresql':
                    schema_info.append("--- [DB] POSTGRES DATA-TRANSFORMATION HINTS ---\n")
                else: # MySQL
                    schema_info.append("--- [DB] MYSQL DATA-TRANSFORMATION HINTS & DATA DICTIONARY ---\n")
                    schema_info.append("1. JOINING RULES:\n")
                    schema_info.append("   - `candidate` table primary key is `candidate_id`.\n")
                    schema_info.append("   - `joborder` table primary key is `joborder_id`.\n")
                    schema_info.append("   - `candidate_joborder` is the bridge table. Use `candidate_joborder.candidate_id` and `candidate_joborder.joborder_id` to join.\n")
                    schema_info.append("   - `candidate_joborder.status` joins with `candidate_joborder_status.candidate_joborder_status_id`.\n\n")
                    
                    schema_info.append("2. CANDIDATE NAMES:\n")
                    schema_info.append("   - Candidates have `first_name` and `last_name`. Always use `CONCAT(first_name, ' ', last_name)` or `LIKE` for full-name searches.\n\n")
                    
                    schema_info.append("3. RECRUITMENT STATUS CODES (candidate_joborder.status):\n")
                    schema_info.append("   - 300: Qualifying / Sourced\n")
                    schema_info.append("   - 400: Submitted to Client\n")
                    schema_info.append("   - 500: Interviewing\n")
                    schema_info.append("   - 600: Offered\n")
                    schema_info.append("   - 800/900: Joined / Placed / Hired (Goal status)\n\n")
                    
                    schema_info.append("4. Use `STR_TO_DATE()` for dates. Use `LIMIT` for pagination. Handling nulls with `IFNULL()`.\n\n")

                for table_name in tables:
                    if self.dialect == 'postgresql':
                        columns_query = text("""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = :table_name
                        """)
                    else: # MySQL
                        columns_query = text("""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE TABLE_NAME = :table_name AND TABLE_SCHEMA = :db_name
                        """)
                    
                    col_params = {"table_name": table_name}
                    if self.dialect == 'mysql':
                        col_params["db_name"] = self.engine.url.database

                    columns = conn.execute(columns_query, col_params).fetchall()
                    cols_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
                    
                    try:
                        # Pull 5 rows for context variety
                        quote_char = '"' if self.dialect == 'postgresql' else '`'
                        sample_query = text(f'SELECT * FROM {quote_char}{table_name}{quote_char} LIMIT 5')
                        sample_df = pd.read_sql_query(sample_query, conn)
                        
                        # TRUNCATE strings for the LLM context to save tokens and prevent noise
                        def truncate_llm_val(val):
                            if isinstance(val, str) and len(val) > 100:
                                return val[:97].replace('\n', ' ').replace('\r', ' ') + "..."
                            if val is None:
                                return "NULL"
                            return str(val).replace('\n', ' ').replace('\r', ' ')

                        if hasattr(sample_df, 'map'):
                            sample_df_clean = sample_df.map(truncate_llm_val)
                        else:
                            sample_df_clean = sample_df.applymap(truncate_llm_val)
                            
                        sample_data = sample_df_clean.to_csv(index=False).strip()
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
