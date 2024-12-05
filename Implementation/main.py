import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from cerebras.cloud.sdk import Cerebras

class EnhancedLiteratureAssistant:
    def __init__(self, model_name: str = "llama3.1-8b"):
        """
        Initialize the Literature Assistant with Cerebras SDK.
        
        Args:
            model_name (str): Name of the Cerebras model to use
        """
        # Retrieve API key from environment
        api_key = "csk-3m4tcyxyvp9hwy9x4h3k38hpv8fkemy5mv3pdwhket5m4nxv"
        #api_key = os.environ.get("CEREBRAS_API_KEY")
        #if not api_key:
        #    raise ValueError("CEREBRAS_API_KEY must be set in environment variables")
        
        # Create Cerebras client
        self.client = Cerebras(api_key=api_key)
        
        # Selected model
        self.model_name = model_name
        
        # Chat history and paper storage
        self.chat_history: List[Dict[str, str]] = []
        self.papers: Dict[str, Dict[str, Any]] = {}

    async def process_paper(self, paper_content: str) -> Dict[str, Any]:
        """
        Process a research paper using Cerebras model.
        
        Args:
            paper_content (str): Full text of the paper
        
        Returns:
            Dict with analysis results
        """
        try:
            # Use chat completion for paper analysis
            response = self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Analyze this research paper and provide a comprehensive summary, key concepts, and research methods:\n\n{paper_content}"
                }],
                model=self.model_name
            )
            
            # Extract analysis details
            analysis = {
                'summary': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'processing_time': response.time_info.total_time
            }
            
            return analysis
        except Exception as e:
            print(f"Paper analysis error: {e}")
            return {}

    async def semantic_search(self, query: str, papers: List[Dict]) -> List[Dict]:
        """
        Perform semantic search across papers using Cerebras model.
        
        Args:
            query (str): Search query
            papers (List[Dict]): List of papers to search
        
        Returns:
            List of matching papers with relevance scores
        """
        try:
            # Use chat completion for semantic search
            response = self.client.chat.completions.create(
                messages=[{
                    "role": "user", 
                    "content": f"Rank the following papers by relevance to this query: '{query}'\n\n" + 
                               "\n---\n".join([p.get('title', '') + ": " + p.get('content', '') for p in papers])
                }],
                model=self.model_name
            )
            
            # Parse response to extract ranked papers
            ranked_results = response.choices[0].message.content
            
            # Additional processing could be done here to extract precise rankings
            return [
                {
                    'title': paper['title'],
                    'content': paper['content'],
                    'relevance_description': ranked_results
                } for paper in papers
            ]
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []

    def add_paper(self, title: str, content: str):
        """
        Add a paper to the assistant's collection.
        
        Args:
            title (str): Title of the paper
            content (str): Full text of the paper
        """
        self.papers[title] = {
            'title': title,
            'content': content,
            'added_timestamp': datetime.now().isoformat()  # Cross-platform timestamp
        }

async def main():
    # Initialize the literature assistant
    assistant = EnhancedLiteratureAssistant()

    # Add sample papers
    sample_papers = [
        {
            'title': 'Advanced Machine Learning Techniques',
            'content': """This research paper explores cutting-edge machine learning algorithms 
            with a focus on transformer architectures and their applications in natural 
            language processing. Key contributions include novel attention mechanisms 
            and improved training strategies for large language models."""
        },
        {
            'title': 'Neural Network Optimization Strategies',
            'content': """An in-depth analysis of optimization techniques for neural networks, 
            discussing gradient descent variants, regularization methods, and emerging 
            approaches to improve model convergence and generalization."""
        }
    ]

    # Process and add papers
    for paper in sample_papers:
        assistant.add_paper(paper['title'], paper['content'])
        
        # Analyze each paper
        analysis = await assistant.process_paper(paper['content'])
        print(f"\nAnalysis for {paper['title']}:")
        print(f"Summary: {analysis.get('summary', 'No summary available')}")
        print(f"Tokens Used: {analysis.get('tokens_used', 'N/A')}")
        print(f"Processing Time: {analysis.get('processing_time', 'N/A')}")

    # Perform semantic search
    print("\nSemantic Search Results:")
    search_results = await assistant.semantic_search(
        "machine learning optimization", 
        list(assistant.papers.values())
    )
    
    for result in search_results:
        print(f"- {result['title']}")
        print(f"  Relevance Notes: {result.get('relevance_description', 'No details')}")
        print()

if __name__ == "__main__":
    asyncio.run(main())