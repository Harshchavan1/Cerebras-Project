import os
import re
import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Third-party imports
from cerebras.cloud.sdk import Cerebras

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CebrasCitationExtractor:
    """
    Advanced citation and paper details extraction using Cerebras AI
    """
    def __init__(self, cerebras_client, model_name: str = "llama3.1-8b"):
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
        Extract structured paper details using Cerebras AI
        
        Args:
            raw_content (str): Raw text content to analyze
        
        Returns:
            Dict with extracted paper details
        """
        try:
            extraction_prompt = f"""
            Analyze the following research text and extract structured information:
            
            Text: {raw_content[:2000]}  # Limit input to prevent excessive token usage
            
            Please provide a detailed response in JSON format with:
            {{
                "title": "Extracted Paper Title",
                "authors": ["Author 1", "Author 2"],
                "abstract": "Concise research summary",
                "key_contributions": ["Contribution 1", "Contribution 2"],
                "research_domains": ["Domain 1", "Domain 2"],
                "potential_citations": ["Citation DOI 1", "Citation DOI 2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"Error extracting paper details: {e}")
            return {}

    def extract_advanced_research_context(self, raw_content: str) -> Dict[str, Any]:
        """
        Perform advanced research context extraction using Cerebras
        
        Args:
            raw_content (str): Raw text content to analyze
        
        Returns:
            Comprehensive research context dictionary
        """
        try:
            extraction_prompt = f"""
            Analyze the research text and provide an advanced, structured context:

            Text: {raw_content[:3000]}  # Limit input length

            Provide a JSON response with:
            {{
                "research_paradigm": "Research approach description",
                "theoretical_framework": "Primary theoretical foundation",
                "methodological_approach": "Research methodology",
                "core_concepts": ["Concept 1", "Concept 2"],
                "potential_applications": ["Application 1", "Application 2"],
                "innovation_score": 0.0-1.0
            }}
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt}],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"Advanced context extraction error: {e}")
            return {}

class CebrasPaperFetcher:
    """
    Cerebras-powered paper fetching and web search
    """
    def __init__(self, model_name: str = "llama3.1-8b"):
        """
        Initialize Cerebras-powered Paper Fetcher
        
        Args:
            model_name (str): Cerebras model for inference
        """
        self.api_key = "csk-3m4tcyxyvp9hwy9x4h3k38hpv8fkemy5mv3pdwhket5m4nxv"
        #if not self.api_key:
        #    raise ValueError("Cerebras API key must be set in environment variable CEREBRAS_API_KEY")
        
        self.client = Cerebras(api_key=self.api_key)
        self.model_name = model_name
        self.citation_extractor = CebrasCitationExtractor(self.client, model_name)

    def web_search_papers(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform an intelligent web search for research papers
        
        Args:
            query (str): Search query for research papers
            num_results (int): Number of papers to fetch
        
        Returns:
            List of paper search results
        """
        if not query or len(query.strip()) < 2:
            logger.warning("Invalid search query")
            return []

        try:
            search_prompt = f"""
            Perform an academic web search for the most relevant research papers on:
            "{query}"
            
            Provide {num_results} most academically significant papers.
            Strictly return a JSON array with: title, url, description
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": search_prompt}],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            
            search_results = json.loads(response.choices[0].message.content)
            return search_results if isinstance(search_results, list) else []
        
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    def fetch_paper_details(self, query: str) -> Dict[str, Any]:
        """
        Fetch paper details for a given research topic
        
        Args:
            query (str): Search query for the paper
        
        Returns:
            Dict with paper details
        """
        try:
            search_results = self.web_search_papers(query)
            
            if not search_results:
                logger.info(f"No papers found for query: {query}")
                return {}
            
            selected_paper = search_results[0]
            
            paper_content = f"""
            Title: {selected_paper.get('title', 'Unknown Title')}
            Source: {selected_paper.get('url', 'Unknown Source')}
            Description: {selected_paper.get('description', 'No description')}
            
            Research details for query: {query}
            """
            
            paper_details = self.citation_extractor.extract_paper_details(paper_content)
            
            ingest_data = {
                'title': paper_details.get('title', selected_paper.get('title', 'Untitled')),
                'authors': paper_details.get('authors', []),
                'content': paper_details.get('abstract', paper_content),
                'citations': paper_details.get('potential_citations', []),
                'doi': f"doi:cerebras-{re.sub(r'[^a-zA-Z0-9]', '-', paper_details.get('title', 'unknown'))}",
                'source': selected_paper.get('url', 'Cerebras Web Search')
            }
            
            return ingest_data
        
        except Exception as e:
            logger.error(f"Paper fetching error: {e}")
            return {}

class ScientificLiteratureExplorer:
    """
    Core class for scientific literature exploration and management
    """
    def __init__(self, db_path: str = 'scientific_papers.db'):
        """
        Initialize the Scientific Literature Explorer
        
        Args:
            db_path (str): Path to SQLite database
        """
        self.db_path = db_path
        self.paper_fetcher = CebrasPaperFetcher()
        self._setup_database()

    def _setup_database(self) -> None:
        """
        Create database and necessary tables if they don't exist
        """
        try:
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
        except sqlite3.Error as e:
            logger.error(f"Database setup error: {e}")

    def load_papers(self) -> List[Dict[str, Any]]:
        """
        Load existing papers from the database
        
        Returns:
            List of paper dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT doi, title, authors, content, source FROM papers")
                papers = cursor.fetchall()
                
                return [
                    {
                        "doi": paper[0], 
                        "title": paper[1], 
                        "authors": paper[2].split(',') if paper[2] else [], 
                        "content": paper[3],
                        "source": paper[4]
                    } for paper in papers
                ]
        except sqlite3.Error as e:
            logger.error(f"Error loading papers: {e}")
            return []

    def ingest_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest a scientific paper into the database
        
        Args:
            paper_data (Dict): Paper details to ingest
        
        Returns:
            Dict with ingestion result
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                authors = ','.join(paper_data.get('authors', []))
                citations = ','.join(paper_data.get('citations', []))
                
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
                
                conn.commit()
                
                return {
                    'status': 'success',
                    'doi': paper_data.get('doi', 'unknown'),
                    'title': paper_data.get('title', '')
                }
        
        except sqlite3.Error as e:
            logger.error(f"Ingestion error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def fetch_and_ingest_research_paper(self, query: str) -> Dict[str, Any]:
        """
        Fetch a research paper by query and ingest into the database
        
        Args:
            query (str): Search query for the paper
        
        Returns:
            Dict with ingestion result
        """
        paper_details = self.paper_fetcher.fetch_paper_details(query)
        
        if not paper_details:
            return {
                'status': 'error',
                'message': 'Could not fetch paper details'
            }
        
        return self.ingest_paper(paper_details)

    def recommend_papers(self, base_paper_doi: str, num_recommendations: int = 5) -> List[Dict[str, Any]]:
        """
        Generate intelligent research paper recommendations
        
        Args:
            base_paper_doi (str): DOI of the base paper
            num_recommendations (int): Number of recommendations to generate
        
        Returns:
            List of recommended papers
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT title, content FROM papers WHERE doi = ?", (base_paper_doi,))
                base_paper = cursor.fetchone()
                
                if not base_paper:
                    return []
                
                recommendation_prompt = f"""
                Analyze the research paper and generate {num_recommendations} 
                highly relevant research paper recommendations:
                
                Base Paper Title: {base_paper[0]}
                Base Paper Content: {base_paper[1][:2000]}
                
                Return a JSON array of recommendations with:
                [
                    {{
                        "title": "Recommended Paper Title",
                        "rationale": "Recommendation reason",
                        "relevance_score": 0.0-1.0
                    }}
                ]
                """
                
                response = self.paper_fetcher.client.chat.completions.create(
                    messages=[{"role": "user", "content": recommendation_prompt}],
                    model=self.paper_fetcher.model_name,
                    response_format={"type": "json_object"}
                )
                
                recommendations = json.loads(response.choices[0].message.content)
                return recommendations
        
        except Exception as e:
            logger.error(f"Paper recommendation error: {e}")
            return []

    def analyze_research_trends(self, time_window: int = 2) -> Dict[str, Any]:
        """
        Analyze research trends and emerging domains
        
        Args:
            time_window (int): Number of years to consider for trend analysis
        
        Returns:
            Comprehensive research trend analysis
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=time_window*365)
                
                cursor.execute("""
                    SELECT content, source, ingestion_date 
                    FROM papers 
                    WHERE ingestion_date >= ?
                """, (cutoff_date.strftime('%Y-%m-%d'),))
                
                recent_papers = cursor.fetchall()
                
                if not recent_papers:
                    return {"status": "insufficient_data"}
                
                consolidated_content = " ".join([paper[0] for paper in recent_papers])
                
                trend_analysis_prompt = f"""
                Analyze research trends in this consolidated content:
                
                Content: {consolidated_content[:4000]}
                
                Provide a JSON response with emerging domains, research momentum, 
                and innovation landscape insights.
                """
                
                response = self.paper_fetcher.client.chat.completions.create(
                    messages=[{"role": "user", "content": trend_analysis_prompt}],
                    model=self.paper_fetcher.model_name,
                    response_format={"type": "json_object"}
                )
                
                return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            logger.error(f"Research trend analysis error: {e}")
            return {"status": "error", "message": str(e)}

# Optional: Add main block for direct script testing
if __name__ == "__main__":
    explorer = ScientificLiteratureExplorer()
    print("Scientific Literature Explorer initialized successfully.")