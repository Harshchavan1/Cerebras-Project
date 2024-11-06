import os
from typing import List, Dict, Optional, Tuple
import asyncio
from functools import lru_cache
import numpy as np
from dataclasses import dataclass
from cerebras_cloud_sdk import Cerebras  # Updated import
import networkx as nx
from collections import defaultdict
import plotly.graph_objects as go
import plotly.express as px

@dataclass
class Paper:
    """Enhanced paper data class with metadata."""
    title: str
    content: str
    sections: Dict[str, str]
    references: List[str]
    embedding: Optional[np.ndarray] = None
    concepts: List[str] = None
    processed_date: str = None

class EnhancedLiteratureAssistant:
    def __init__(self, cerebras_api_key: str, cache_size: int = 1000):
        self.cerebras = Cerebras(api_key=cerebras_api_key)  # Updated initialization
        self.papers = {}
        self.citation_graph = nx.DiGraph()
        self.concept_graph = nx.Graph()
        self.cache_size = cache_size
        
    @lru_cache(maxsize=1000)
    async def generate_embedding(self, text: str) -> np.ndarray:
        """Cached embedding generation."""
        # Update to use cerebras-cloud-sdk methods
        response = await self.cerebras.embeddings.create(
            text=text,
            model="text-embedding"  # Specify the appropriate model name
        )
        embedding = response.embedding  # Adjust based on actual response structure
        return np.array(embedding)

    async def batch_process_papers(self, pdf_paths: List[str], batch_size: int = 5) -> List[Paper]:
        """Process multiple papers in parallel batches."""
        results = []
        for i in range(0, len(pdf_paths), batch_size):
            batch = pdf_paths[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.process_paper(path) for path in batch]
            )
            results.extend(batch_results)
            # Allow for system cool-down between batches
            if i + batch_size < len(pdf_paths):
                await asyncio.sleep(1)
        return results

    async def analyze_batch(self, papers: List[Paper]) -> Dict[str, List[str]]:
        """Parallel analysis of multiple papers."""
        concepts_tasks = [self.analyze_concepts(paper.content) for paper in papers]
        summaries_tasks = [self.generate_summary(paper) for paper in papers]
        
        concepts_results, summaries = await asyncio.gather(
            asyncio.gather(*concepts_tasks),
            asyncio.gather(*summaries_tasks)
        )
        
        return {
            'concepts': concepts_results,
            'summaries': summaries
        }

    def visualize_citation_network(self) -> go.Figure:
        """Create interactive citation network visualization."""
        pos = nx.spring_layout(self.citation_graph)
        
        # Create edges
        edge_x = []
        edge_y = []
        for edge in self.citation_graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        # Create nodes
        node_x = [pos[node][0] for node in self.citation_graph.nodes()]
        node_y = [pos[node][1] for node in self.citation_graph.nodes()]
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[node for node in self.citation_graph.nodes()],
            marker=dict(
                size=10,
                color='#1f77b4',
                line_width=2
            )
        ))
        
        return fig

    def visualize_concept_trends(self, timeframe: str = 'month') -> go.Figure:
        """Visualize concept trends over time."""
        concept_counts = defaultdict(lambda: defaultdict(int))
        
        for paper in self.papers.values():
            period = self._get_time_period(paper.processed_date, timeframe)
            for concept in paper.concepts:
                concept_counts[concept][period] += 1
        
        # Convert to DataFrame format for plotting
        data = []
        for concept, counts in concept_counts.items():
            for period, count in counts.items():
                data.append({
                    'concept': concept,
                    'period': period,
                    'count': count
                })
        
        fig = px.line(
            data,
            x='period',
            y='count',
            color='concept',
            title='Concept Trends Over Time'
        )
        return fig

    async def semantic_search_cached(self, query: str, top_k: int = 5) -> Tuple[List[Paper], float]:
        """Enhanced semantic search with caching and timing."""
        start_time = asyncio.get_event_loop().time()
        
        # Use cached embedding if available
        query_embedding = await self.generate_embedding(query)
        
        # Parallel similarity computation
        similarities = await asyncio.gather(*[
            self._compute_similarity(query_embedding, paper.embedding)
            for paper in self.papers.values()
        ])
        
        # Get top results
        paper_scores = list(zip(self.papers.values(), similarities))
        top_papers = sorted(paper_scores, key=lambda x: x[1], reverse=True)[:top_k]
        
        end_time = asyncio.get_event_loop().time()
        return [p for p, _ in top_papers], end_time - start_time

    async def _compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute embedding similarity."""
        return float(np.dot(emb1, emb2))

    def _get_time_period(self, date_str: str, timeframe: str) -> str:
        """Extract time period from date string."""
        # Implementation depends on your date format
        return date_str  # Simplified for demo

# Example usage
async def demo():
    assistant = EnhancedLiteratureAssistant("your_api_key")
    
    # Batch process papers
    papers = await assistant.batch_process_papers([
        "paper1.pdf", "paper2.pdf", "paper3.pdf"
    ])
    
    # Parallel analysis
    analysis = await assistant.analyze_batch(papers)
    
    # Generate visualizations
    citation_network = assistant.visualize_citation_network()
    concept_trends = assistant.visualize_concept_trends()
    
    # Cached semantic search
    results, search_time = await assistant.semantic_search_cached(
        "machine learning in biology"
    )
    print(f"Search completed in {search_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(demo())