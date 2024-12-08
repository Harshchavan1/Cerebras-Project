import streamlit as st
import pandas as pd
import plotly.express as px
import traceback
import scholarly

# Import the updated explorer and other necessary components
from mains import ScientificLiteratureExplorer
from performance_logger import PerformanceLogger
from performance_visualization import CebrarasPerformanceDemo

class ScientificLiteratureApp:
    def __init__(self):
        """
        Initialize the Streamlit application for Scientific Literature Explorer
        """
        st.set_page_config(
            page_title="Scientific Literature Explorer", 
            page_icon="🔬",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Add error checking for explorer initialization
        try:
            # Initialize core components
            self.explorer = ScientificLiteratureExplorer()
            
            # Verify that essential methods exist
            required_methods = ['load_papers', 'fetch_and_ingest_research_paper', 'recommend_papers', 'analyze_research_trends', 'ingest_paper']
            for method in required_methods:
                if not hasattr(self.explorer, method):
                    raise AttributeError(f"ScientificLiteratureExplorer is missing required method '{method}'")
        except Exception as e:
            st.error(f"Failed to initialize Scientific Literature Explorer: {e}")
            traceback.print_exc()
            self.explorer = None
            return
        
        # Initialize session state with error handling
        if 'papers' not in st.session_state:
            try:
                papers = self.explorer.load_papers()
                st.session_state.papers = papers
            except Exception as e:
                st.error(f"Error loading papers: {e}")
                st.session_state.papers = []
        
        # Initialize other session states
        if 'advanced_search' not in st.session_state:
            st.session_state.advanced_search = False
        
        # Initialize recommendation and trend analysis session states
        if 'selected_paper_recommendations' not in st.session_state:
            st.session_state.selected_paper_recommendations = None
        if 'research_trends' not in st.session_state:
            st.session_state.research_trends = None
        self.performance_logger = PerformanceLogger()    

    def render_paper_explorer(self):
        """
        Render the paper exploration interface with enhanced visualization and new features
        """
        # Check if explorer is initialized
        if not hasattr(self, 'explorer') or self.explorer is None:
            st.error("Explorer not initialized. Please restart the application.")
            return

        st.header("📚 Paper Collection")
        
        # Get papers from session state
        papers = st.session_state.get('papers', [])
        
        if not papers:
            st.info("No papers discovered yet. Use the search above to find research.")
            return
        
        # Convert to DataFrame
        try:
            df = pd.DataFrame(papers)
            
            # Layout with tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📄 Paper Details", 
                "📊 Analytics", 
                "📈 Visualizations", 
                "🔍 Paper Recommendations",
                "🌐 Research Trends"
            ])
            
            with tab1:
                # Add a selection mechanism for papers
                paper_titles = [paper['title'] for paper in papers]
                selected_title = st.selectbox("Select a Paper", paper_titles)
    
                # Find the selected paper details
                selected_paper = next((paper for paper in papers if paper['title'] == selected_title), None)
    
                if selected_paper:
                    # Display paper details
                    st.markdown(f"### {selected_paper['title']}")
                    st.markdown(f"**Authors:** {', '.join(selected_paper.get('authors', ['N/A']))}")
                    st.markdown(f"**DOI:** {selected_paper.get('doi', 'N/A')}")
        
                    # Expandable content section
                    with st.expander("Paper Content"):
                        st.write(selected_paper.get('content', 'No content available'))
        
                    # Add recommendation button
                    if st.button("Get Paper Recommendations"):
                        with st.spinner("Generating intelligent recommendations..."):
                            recommendations = self.explorer.recommend_papers(selected_paper['doi'])
                            st.session_state.selected_paper_recommendations = recommendations
                else:
                    st.info("No paper selected")
            
            with tab2:
                st.subheader("📊 Paper Analytics")
                if not papers:
                    st.info("No papers to analyze")
                    return
    
                # Basic analytics
                df = pd.DataFrame(papers)
                col1, col2 = st.columns(2)
    
                with col1:
                    st.metric("Total Papers", len(papers))
                    st.metric("Unique Authors", len(set([author for paper in papers for author in paper.get('authors', [])])))
    
                with col2:
                    st.metric("Total Citations", sum(
                        sum(paper.get('citations', [0]) if isinstance(paper.get('citations'), list) else [0]) 
                        for paper in papers
                    ))

            with tab3:
                st.subheader("📈 Research Visualizations")
                if not papers:
                    st.info("No papers to visualize")
                    return
    
                # Visualization options
                viz_type = st.selectbox("Select Visualization", [
                    "Authors Distribution", 
                    "Citations Network", 
                    "Research Sources"
                ])
    
                if viz_type == "Authors Distribution":
                    # Author frequency visualization
                    author_counts = {}
                    for paper in papers:
                        for author in paper.get('authors', []):
                            author_counts[author] = author_counts.get(author, 0) + 1
        
                    top_authors = dict(sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
                    fig = px.bar(
                        x=list(top_authors.keys()), 
                        y=list(top_authors.values()), 
                        title="Top 10 Authors by Paper Count"
                    )
                    st.plotly_chart(fig)
            
            with tab4:
                st.subheader("📚 Intelligent Paper Recommendations")
                
                if st.session_state.selected_paper_recommendations:
                    recommendations = st.session_state.selected_paper_recommendations
                    
                    for rec in recommendations:
                        st.markdown(f"### {rec['title']}")
                        st.markdown(f"**Relevance Score:** {rec.get('relevance_score', 'N/A')}")
                        st.markdown(f"**Rationale:** {rec.get('rationale', 'No specific rationale provided')}")
                        st.markdown(f"**Research Synergy:** {rec.get('potential_research_synergy', 'Not specified')}")
                        st.markdown("---")
                else:
                    st.info("Select a paper and click 'Get Paper Recommendations' to see suggestions")
            
            with tab5:
                st.subheader("🌐 Research Landscape Analysis")
                
                # Trend analysis button
                if st.button("Analyze Research Trends"):
                    with st.spinner("Performing comprehensive research trend analysis..."):
                        trends = self.explorer.analyze_research_trends()
                        st.session_state.research_trends = trends
                
                # Display research trends
                if st.session_state.research_trends:
                    trends = st.session_state.research_trends
                    
                    if trends.get('status') == 'error':
                        st.error(f"Trend analysis failed: {trends.get('message', 'Unknown error')}")
                    elif trends.get('status') == 'insufficient_data':
                        st.warning("Not enough recent papers to perform trend analysis")
                    else:
                        # Emerging Domains
                        st.markdown("### 🚀 Emerging Research Domains")
                        for domain in trends.get('emerging_domains', []):
                            st.markdown(f"**{domain['domain_name']}**")
                            st.markdown(f"- Growth Potential: {domain.get('growth_potential', 'N/A')}")
                            st.markdown(f"- Key Characteristics: {', '.join(domain.get('key_characteristics', []))}")
                            st.markdown(f"- Interdisciplinary Overlap: {', '.join(domain.get('interdisciplinary_overlap', []))}")
                            st.markdown("---")
                        
                        # Research Momentum
                        st.markdown("### 📊 Research Momentum")
                        momentum = trends.get('research_momentum_indicators', {})
                        st.markdown(f"**Most Active Research Areas:** {', '.join(momentum.get('most_active_research_areas', []))}")
                        st.markdown(f"**Declining Research Interests:** {', '.join(momentum.get('declining_research_interests', []))}")
                        
                        # Innovation Landscape
                        st.markdown("### 💡 Innovation Landscape")
                        innovation = trends.get('innovation_landscape', {})
                        st.markdown(f"**Breakthrough Potential Domains:** {', '.join(innovation.get('breakthrough_potential_domains', []))}")
                        
                        # Global Research Sentiment
                        st.markdown("### 🌍 Global Research Sentiment")
                        sentiment = trends.get('global_research_sentiment', {})
                        st.markdown(f"**Optimism Index:** {sentiment.get('optimism_index', 'N/A')}")
                        st.markdown(f"**Collaborative Intensity:** {sentiment.get('collaborative_intensity', 'N/A')}")
                else:
                    st.info("Click 'Analyze Research Trends' to get insights into the current research landscape")
        
        except Exception as e:
            st.error(f"Error rendering paper details: {e}")
            traceback.print_exc()

    def render_search_section(self):
        """
        Render the paper search interface with advanced options
        """
        # Check if explorer is initialized
        if not hasattr(self, 'explorer') or self.explorer is None:
            st.error("Explorer not initialized. Please restart the application.")
            return

        st.header("🔍 Paper Discovery")
        
        # Toggleable advanced search
        st.session_state.advanced_search = st.checkbox("Advanced Search Options")
        
        # Search input
        search_query = st.text_input(
            "Enter a research topic", 
            placeholder="e.g., Quantum Machine Learning"
        )
        
        # Advanced search options
        min_content_length = 50  # Default value
        search_scope = "Standard"  # Default value
        
        if st.session_state.advanced_search:
            col1, col2 = st.columns(2)
            with col1:
                min_content_length = st.slider(
                    "Minimum Content Length", 
                    min_value=50, 
                    max_value=500, 
                    value=100
                )
            with col2:
                search_scope = st.selectbox(
                    "Search Scope",
                    ["Global", "Recent", "Comprehensive", "Standard"]
                )
        
        # Search button
        if st.button("Discover Papers", type="primary"):
            with st.spinner("Searching for papers..."):
                try:
                    # Validate search query
                    if not search_query.strip():
                        st.warning("Please enter a search query")
                        return
                    
                    # Attempt to fetch and ingest a real paper
                    result = self.explorer.fetch_and_ingest_research_paper(search_query)
                    
                    if result['status'] == 'success':
                        st.success(f"Successfully discovered: {result.get('title', 'Unknown Paper')}")
                        # Refresh papers list
                        st.session_state.papers = self.explorer.load_papers()
                    else:
                        # Fallback to demo paper if real paper fetch fails
                        demo_ingest_data = {
                            'doi': f'doi:demo-{search_query.replace(" ", "-")}',
                            'title': f"Research Insights: {search_query}",
                            'authors': ["Research Team"],
                            'content': f"""
                            Exploratory overview of {search_query}
                            
                            Key Points:
                            - Preliminary research insights
                            - Scope: {search_scope}
                            - Minimum Content Length: {min_content_length}
                            
                            This is a demonstration entry due to limited search results.
                            """,
                            'citations': [],
                            'source': 'Demonstration Repository'
                        }
                        
                        fallback_result = self.explorer.ingest_paper(demo_ingest_data)
                        if fallback_result['status'] == 'success':
                            st.info("Created a demo paper due to limited search results")
                            st.session_state.papers = self.explorer.load_papers()
                        else:
                            st.error("Failed to discover or create a paper")
                
                except Exception as e:
                    st.error(f"Error during paper discovery: {e}")
                    traceback.print_exc()
    def render_scholarly_update_section(self):
        """
        Render the Scholarly paper database update interface
        """
        # Check if explorer is initialized
        if not hasattr(self, 'explorer') or self.explorer is None:
            st.error("Explorer not initialized. Please restart the application.")
            return

        st.header("🌐 Update Paper Database from Scholarly")
    
        # Search input for Scholarly update
        scholarly_query = st.text_input(
            "Enter a research topic to update database", 
            placeholder="e.g., Machine Learning Algorithms"
        )
    
        # Number of papers to fetch
        max_papers = st.slider(
            "Maximum Papers to Fetch", 
            min_value=5, 
            max_value=50, 
            value=10
        )
    
        # Update button
        if st.button("Update Database from Scholarly", type="primary"):
            with st.spinner("Updating database from Scholarly..."):
                try:
                    # Validate search query
                    if not scholarly_query.strip():
                        st.warning("Please enter a search query")
                        return
                
                    # Attempt to update database
                    update_result = self.explorer.update_database_from_scholarly(
                        scholarly_query, 
                        max_papers=max_papers
                    )
                
                    if update_result['status'] == 'success':
                        st.success(f"Successfully updated database!")
                        st.write(f"Ingested Papers: {update_result['ingested_papers']}")
                        st.write(f"Skipped Papers: {update_result['skipped_papers']}")
                    
                        # Refresh papers list
                        st.session_state.papers = self.explorer.load_papers()
                    else:
                        st.error(f"Database update failed: {update_result.get('message', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"Error during Scholarly database update: {e}")
                    traceback.print_exc()

    def render_dashboard(self):
        """
        Render the overall application dashboard
        """
        st.title("🌐 Scientific Literature Explorer")
        
        # Add a performance demo tab
        tab1, tab2, tab3, tab4 = st.tabs([
            "Search & Explore", 
            "🚀 Performance Demo",
            "📚 Scholarly Update", 
            "About"
        ])
        
        with tab1:
            self.render_search_section()
            self.render_paper_explorer()
        
        with tab2:
            # Performance demonstration section
            CebrarasPerformanceDemo.render_performance_dashboard(self.explorer)

        with tab3:
            self.render_scholarly_update_section()

        with tab4:
            st.header("About Scientific Literature Explorer")
            st.markdown("""
            ## Powered by Cerebras AI
            
            ### Key Features:
            - Intelligent Paper Search
            - Research Trend Analysis
            - Paper Recommendations
            - High-Performance Inference
            
            #### Performance Highlights:
            - Near Real-time Inference
            - Low-Latency AI Processing
            - Diverse Research Tasks
            """)
        
    def run(self):
        """
        Run the Streamlit application
        """
        self.render_dashboard()

def main():
    """
    Entry point for the Streamlit application
    """
    app = ScientificLiteratureApp()
    app.run()

if __name__ == "__main__":
    main()