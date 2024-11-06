# main.py
import asyncio
import os
from datetime import datetime
from enhanced_literature_assistant import EnhancedLiteratureAssistant, Paper

async def run_example():
    """Example script to demonstrate the Literature Assistant."""
    # Initialize with your Cerebras Cloud API key
    api_key = os.getenv('CEREBRAS_CLOUD_API_KEY', 'your_api_key')
    assistant = EnhancedLiteratureAssistant(api_key)

    # Create some sample papers for testing
    sample_papers = [
        Paper(
            title="Deep Learning Advances",
            content="This paper discusses recent advances in deep learning...",
            sections={"intro": "Introduction to deep learning...", "methods": "Our methods..."},
            references=["Paper1", "Paper2"],
            concepts=["deep learning", "neural networks"],
            processed_date=datetime.now().strftime("%Y-%m-%d")
        ),
        Paper(
            title="Natural Language Processing",
            content="Recent developments in NLP have shown...",
            sections={"intro": "Introduction to NLP...", "results": "Our findings..."},
            references=["Paper3", "Paper4"],
            concepts=["NLP", "transformers"],
            processed_date=datetime.now().strftime("%Y-%m-%d")
        )
    ]

    # Generate embeddings for sample papers
    print("Generating embeddings for sample papers...")
    for paper in sample_papers:
        paper.embedding = await assistant.generate_embedding(paper.content)
        assistant.papers[paper.title] = paper
        # Update citation graph
        for ref in paper.references:
            assistant.citation_graph.add_edge(paper.title, ref)

    # Try different features
    print("\n1. Testing semantic search...")
    results, search_time = await assistant.semantic_search_cached("deep learning")
    print(f"Search completed in {search_time:.2f} seconds")
    print(f"Found {len(results)} relevant papers")
    for paper in results:
        print(f"- {paper.title}")

    print("\n2. Generating visualizations...")
    # Create and save citation network visualization
    citation_fig = assistant.visualize_citation_network()
    citation_fig.write_html("citation_network.html")
    print("Citation network visualization saved as 'citation_network.html'")

    # Create and save concept trends visualization
    trends_fig = assistant.visualize_concept_trends()
    trends_fig.write_html("concept_trends.html")
    print("Concept trends visualization saved as 'concept_trends.html'")

    print("\n3. Testing batch analysis...")
    analysis_results = await assistant.analyze_batch(sample_papers)
    print("Batch analysis completed")
    print(f"Found concepts: {analysis_results['concepts']}")

if __name__ == "__main__":
    # Set up required packages
    try:
        import numpy as np
        import networkx as nx
        import plotly.graph_objects as go
        import plotly.express as px
        from cerebras_cloud_sdk import CerebrasCloudAPI
    except ImportError:
        print("Installing required packages...")
        os.system("pip install numpy networkx plotly cerebras-cloud-sdk-python")

    # Run the example
    asyncio.run(run_example())