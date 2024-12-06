import os
import re
import json
import asyncio
import requests
from typing import Dict, Any, List, Generator
import sqlite3

# Cerebras SDK
from cerebras.cloud.sdk import Cerebras

class CebrasCitationExtractor:
    def __init__(self, cerebras_client, model_name="llama3.1-8b"):
        """
        Initialize Cerebras-powered citation and paper details extractor
        
        Args:
            cerebras_client (Cerebras): Initialized Cerebras client
            model_name (str): Name of the Cerebras model to use
        """
        self.client = cerebras_client
        self.model_name = model_name

    def extract_paper_details(self, raw_content: str) -> Dict[str, Any]:
        """
        Use Cerebras to extract structured paper details from raw content
        
        Args:
            raw_content (str): Raw text content to analyze
        
        Returns:
            Dict with extracted paper details
        """
        try:
            # Detailed prompt for paper detail extraction
            extraction_prompt = f"""
            Analyze the following research text and extract structured information:
            
            Text: {raw_content}
            
            Please provide a detailed response in JSON format with the following fields:
            {{
                "title": "Extracted Paper Title",
                "authors": ["Author 1", "Author 2"],
                "abstract": "Concise research summary",
                "key_contributions": ["Contribution 1", "Contribution 2"],
                "research_domains": ["Domain 1", "Domain 2"],
                "potential_citations": ["Citation DOI 1", "Citation DOI 2"]
            }}
            
            Focus on extracting clear, precise information. If unsure about any field, 
            provide the best possible interpretation or leave as an empty list/string.
            """
            
            # Generate response using Cerebras
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"Error extracting paper details: {e}")
            return {}

class CebrasPaperFetcher:
    def __init__(self, explorer, model_name="llama3.1-8b"):
        """
        Initialize Cerebras-powered Paper Fetcher
        
        Args:
            explorer (ScientificLiteratureExplorer): The literature explorer instance
            model_name (str): Cerebras model for inference
        """
        # Secure API key handling (consider using environment variable)
        self.api_key = os.getenv('CEREBRAS_API_KEY', 'csk-3m4tcyxyvp9hwy9x4h3k38hpv8fkemy5mv3pdwhket5m4nxv')
        self.client = Cerebras(api_key=self.api_key)
        self.model_name = model_name
        self.explorer = explorer
        self.citation_extractor = CebrasCitationExtractor(self.client, model_name)

    def web_search_papers(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Use Cerebras to perform an intelligent web search for research papers
        
        Args:
            query (str): Search query for research papers
            num_results (int): Number of papers to fetch
        
        Returns:
            List of paper search results
        """
        try:
            # Prompt for intelligent paper search
            search_prompt = f"""
            Perform an academic web search for the most relevant research papers on:
            "{query}"
            
            Provide {num_results} most academically significant papers.
            Strictly return a JSON array with these keys: title, url, description
            
            Example format:
            [
                {{
                    "title": "Example Paper Title",
                    "url": "https://example.com/paper",
                    "description": "Brief paper description"
                }}
            ]
            """
            
            # Generate search results using Cerebras
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": search_prompt}],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response and handle potential errors
            try:
                search_results = json.loads(response.choices[0].message.content)
                return search_results if isinstance(search_results, list) else []
            except json.JSONDecodeError:
                print("Failed to parse search results JSON")
                return []
        
        except Exception as e:
            print(f"Error performing web search: {e}")
            return []

    async def fetch_and_ingest_paper(self, query: str) -> Dict[str, Any]:
        """
        Comprehensive paper fetching and ingestion workflow
        
        Args:
            query (str): Search query for the paper
        
        Returns:
            Dict with ingested paper details
        """
        try:
            # Step 1: Perform intelligent web search
            search_results = self.web_search_papers(query)
            
            if not search_results:
                print(f"No papers found for the query: {query}")
                return {}
            
            # Step 2: Select the most relevant paper
            selected_paper = search_results[0]  # First result
            
            # Step 3: Fetch paper content (simulated for this example)
            # In a real-world scenario, you'd implement proper web scraping
            paper_content = f"""
            Title: {selected_paper.get('title', 'Unknown Title')}
            Source: {selected_paper.get('url', 'Unknown Source')}
            Description: {selected_paper.get('description', 'No description')}
            
            Research details for the query: {query}
            """
            
            # Step 4: Extract structured paper details using Cerebras
            paper_details = self.citation_extractor.extract_paper_details(paper_content)
            
            # Step 5: Prepare paper for ingestion
            ingest_data = {
                'title': paper_details.get('title', selected_paper.get('title', 'Untitled')),
                'authors': paper_details.get('authors', []),
                'content': paper_details.get('abstract', paper_content),
                'citations': paper_details.get('potential_citations', []),
                'doi': f"doi:cerebras-{re.sub(r'[^a-zA-Z0-9]', '-', paper_details.get('title', 'unknown'))}",
                'source': selected_paper.get('url', 'Cerebras Web Search')
            }
            
            # Step 6: Ingest the paper with improved connection management
            async with self.explorer.get_async_db() as db:
                try:
                    result = await self.explorer.ingest_scientific_paper(ingest_data, db)
                    return result
                except Exception as e:
                    print(f"Ingestion error: {e}")
                    return {}
        
        except Exception as e:
            print(f"Paper fetching error: {e}")
            return {}

class ScientificLiteratureExplorer:
    def __init__(self, db_path='scientific_papers.db'):
        """
        Initialize the Scientific Literature Explorer
        
        Args:
            db_path (str): Path to SQLite database
        """
        self.db_path = db_path
        self._setup_database()

    def _setup_database(self):
        """
        Create database and necessary tables if they don't exist
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    doi TEXT PRIMARY KEY,
                    title TEXT,
                    authors TEXT,
                    content TEXT,
                    citations TEXT,
                    source TEXT,
                    ingestion_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def get_db(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Yield a database connection
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            yield conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
        finally:
            if conn:
                conn.close()

    def get_async_db(self):
        """
        Async context manager for database connection
        
        Returns:
            Async context manager for SQLite connection
        """
        class AsyncDBContext:
            def __init__(self, db_path):
                self.db_path = db_path
                self.conn = None

            async def __aenter__(self):
                self.conn = sqlite3.connect(self.db_path)
                return self.conn

            async def __aexit__(self, exc_type, exc, tb):
                if self.conn:
                    self.conn.close()
        
        return AsyncDBContext(self.db_path)

    async def ingest_scientific_paper(self, paper_data: Dict[str, Any], db: sqlite3.Connection) -> Dict[str, Any]:
        """
        Ingest a scientific paper into the database
        
        Args:
            paper_data (Dict): Paper details to ingest
            db (sqlite3.Connection): Database connection
        
        Returns:
            Dict with ingestion result
        """
        try:
            cursor = db.cursor()
            
            # Convert lists to comma-separated strings for storage
            authors = ','.join(paper_data.get('authors', []))
            citations = ','.join(paper_data.get('citations', []))
            
            # Insert or replace the paper
            cursor.execute('''
                INSERT OR REPLACE INTO papers 
                (doi, title, authors, content, citations, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                paper_data.get('doi', 'unknown'),
                paper_data.get('title', ''),
                authors,
                paper_data.get('content', ''),
                citations,
                paper_data.get('source', '')
            ))
            
            db.commit()
            
            return {
                'status': 'success',
                'doi': paper_data.get('doi', 'unknown'),
                'title': paper_data.get('title', '')
            }
        
        except Exception as e:
            print(f"Ingestion error: {e}")
            db.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }

def main():
    """Demonstration of Cerebras-powered paper fetching"""
    
    # Initialize explorer and fetcher
    explorer = ScientificLiteratureExplorer()
    fetcher = CebrasPaperFetcher(explorer)
    
    # Demonstrate fetching
    async def run_demo():
        # Fetch papers on various topics
        topics = [
            "Quantum Machine Learning",
            "Transformer Neural Networks",
            "AI Ethics and Bias"
        ]
        
        for topic in topics:
            print(f"\nFetching papers for: {topic}")
            paper = await fetcher.fetch_and_ingest_paper(topic)
            print("Ingested Paper:", paper.get('title', 'Not Found'))
    
    # Run the async demo
    asyncio.run(run_demo())

if __name__ == "__main__":
    main()