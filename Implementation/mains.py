import os
import re
import json
import sqlite3
from typing import Dict, Any, List

# Cerebras SDK
from cerebras.cloud.sdk import Cerebras

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
        conn = sqlite3.connect(self.db_path)
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
        conn.close()

    def get_db_connection(self):
        """
        Get a database connection
        
        Returns:
            sqlite3.Connection: Database connection
        """
        return sqlite3.connect(self.db_path)

    def load_papers(self) -> List[Dict[str, Any]]:
        """
        Load existing papers from the database
        
        Returns:
            List of paper dictionaries
        """
        conn = self.get_db_connection()
        try:
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
        except Exception as e:
            print(f"Error loading papers: {e}")
            return []
        finally:
            conn.close()

    def ingest_paper(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest a scientific paper into the database
        
        Args:
            paper_data (Dict): Paper details to ingest
        
        Returns:
            Dict with ingestion result
        """
        conn = self.get_db_connection()
        try:
            cursor = conn.cursor()
            
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
            
            conn.commit()
            
            return {
                'status': 'success',
                'doi': paper_data.get('doi', 'unknown'),
                'title': paper_data.get('title', '')
            }
        
        except Exception as e:
            print(f"Ingestion error: {e}")
            conn.rollback()
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            conn.close()
