import os
import asyncio
import json
from typing import List, Dict, Any, Optional

from cerebras.cloud.sdk import Cerebras
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

class ScientificLiteratureExplorer:
    def __init__(self, model_name: str = "llama3.1-8b"):
        """
        Initialize the Scientific Literature Explorer with Cerebras inference.
        
        Args:
            model_name (str): Cerebras model for inference
        """
        # API and Client Setup
        self.api_key = "csk-3m4tcyxyvp9hwy9x4h3k38hpv8fkemy5mv3pdwhket5m4nxv"
        #self.api_key = os.environ.get("CEREBRAS_API_KEY")
        #if not self.api_key:
        #    raise ValueError("CEREBRAS_API_KEY must be set in environment variables")
        
        self.client = Cerebras(api_key=self.api_key)
        self.model_name = model_name
        
        # Data Structures
        self.paper_database: Dict[str, Dict[str, Any]] = {}
        self.citation_graph = nx.DiGraph()
        self.research_domains: Dict[str, List[str]] = {}

    async def ingest_scientific_paper(self, paper_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive paper ingestion with multi-dimensional analysis.
        
        Args:
            paper_details (Dict): Paper metadata and content
        
        Returns:
            Dict with comprehensive analysis results
        """
        try:
            # Comprehensive analysis request
            analysis_prompt = f"""Perform a comprehensive scientific paper analysis:
            Title: {paper_details.get('title', 'Untitled')}
            Content: {paper_details.get('content', '')}

            Provide:
            1. Key research domains
            2. Methodology summary
            3. Primary contributions
            4. Potential citation connections
            5. Research impact potential
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": analysis_prompt}],
                model=self.model_name
            )
            
            # Parse analysis
            analysis_result = response.choices[0].message.content
            
            # Structure paper data
            paper_id = paper_details.get('doi', hash(paper_details.get('title', '')))
            processed_paper = {
                'id': paper_id,
                'title': paper_details.get('title', 'Untitled'),
                'authors': paper_details.get('authors', []),
                'content': paper_details.get('content', ''),
                'analysis': analysis_result,
                'citations': paper_details.get('citations', []),
                'domains': [],
                'timestamp': pd.Timestamp.now().isoformat()  # Convert to ISO format string
            }
            
            # Update database and citation graph
            self.paper_database[paper_id] = processed_paper
            
            # Build citation connections
            for citation in processed_paper['citations']:
                self.citation_graph.add_edge(paper_id, citation)
            
            return processed_paper
        
        except Exception as e:
            print(f"Paper ingestion error: {e}")
            return {}

    async def semantic_research_discovery(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Advanced semantic search and research discovery.
        
        Args:
            query (str): Research exploration query
            top_k (int): Number of top results to return
        
        Returns:
            List of most relevant research papers
        """
        try:
            # Semantic search and research mapping
            discovery_prompt = f"""Perform an advanced semantic search and research mapping for the query: '{query}'

            Provide:
            1. Top {top_k} most relevant research papers
            2. Interconnected research domains
            3. Emerging research trends
            4. Potential breakthrough areas
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": discovery_prompt}],
                model=self.model_name
            )
            
            # Parse discovery results
            discovery_results = response.choices[0].message.content
            
            return [
                {
                    'query': query,
                    'results': discovery_results,
                    'timestamp': pd.Timestamp.now().isoformat()  # Convert to ISO format string
                }
            ]
        
        except Exception as e:
            print(f"Research discovery error: {e}")
            return []

    def visualize_research_landscape(self) -> go.Figure:
        """
        Generate an interactive research landscape visualization.
        
        Returns:
            Plotly interactive graph
        """
        # Convert citation graph to node and edge data
        nodes = list(self.citation_graph.nodes())
        edges = list(self.citation_graph.edges())
        
        # Create network layout
        G = nx.spring_layout(self.citation_graph)
        
        # Prepare edge traces
        edge_x, edge_y = [], []
        for edge in edges:
            x0, y0 = G[edge[0]]
            x1, y1 = G[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Prepare node traces
        node_x, node_y, node_text = [], [], []
        for node in nodes:
            x, y = G[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(self.paper_database.get(node, {}).get('title', 'Unknown'))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Research Connections',
                    xanchor='left',
                    titleside='right'
                )
            ),
            text=node_text
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='Scientific Research Landscape',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        )
        
        return fig

async def main():
    # Initialize explorer
    explorer = ScientificLiteratureExplorer()
    
    # Sample scientific papers for demonstration
    sample_papers = [
        {
            'title': 'Transformer Architectures in Natural Language Processing',
            'authors': ['A. Smith', 'B. Johnson'],
            'content': 'Detailed exploration of transformer model evolution...',
            'citations': [],
            'doi': 'doi:10.1000/transformers2023'
        },
        {
            'title': 'Quantum Computing: Algorithmic Breakthroughs',
            'authors': ['C. Lee', 'D. Wong'],
            'content': 'Comprehensive analysis of quantum computing algorithms...',
            'citations': ['doi:10.1000/transformers2023'],
            'doi': 'doi:10.1000/quantum2023'
        }
    ]
    
    # Ingest papers
    for paper in sample_papers:
        await explorer.ingest_scientific_paper(paper)
    
    # Perform semantic research discovery
    discovery_results = await explorer.semantic_research_discovery("machine learning advancements")
    print("Research Discovery Results:")
    print(json.dumps(discovery_results, indent=2))
    
    # Visualize research landscape
    fig = explorer.visualize_research_landscape()
    fig.write_html("research_landscape.html")
    print("\nResearch landscape visualization saved as 'research_landscape.html'")

if __name__ == "__main__":
    asyncio.run(main())