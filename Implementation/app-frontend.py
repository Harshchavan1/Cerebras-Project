import streamlit as st
import pandas as pd
import os

# Import the updated explorer and other necessary components
from mains import ScientificLiteratureExplorer

class ScientificLiteratureApp:
    def __init__(self):
        """
        Initialize the Streamlit application for Scientific Literature Explorer
        """
        st.set_page_config(
            page_title="Scientific Literature Explorer", 
            page_icon="🔬",
            layout="wide"
        )
        
        # Initialize core components
        self.explorer = ScientificLiteratureExplorer()
        
        # Initialize session state with error handling
        if 'papers' not in st.session_state:
            try:
                papers = self.explorer.load_papers()
                st.session_state.papers = papers
            except Exception as e:
                st.error(f"Error loading papers: {e}")
                st.session_state.papers = []
    
    def render_search_section(self):
        """
        Render the paper search interface
        """
        st.header("🔍 Paper Discovery")
        
        # Search input
        search_query = st.text_input(
            "Enter a research topic", 
            placeholder="e.g., Quantum Machine Learning"
        )
        
        # Search button
        if st.button("Discover Papers", type="primary"):
            with st.spinner("Searching for papers..."):
                # Create a sample paper for demonstration
                ingest_data = {
                    'doi': f'doi:demo-{search_query.replace(" ", "-")}',
                    'title': f"Research on {search_query}",
                    'authors': ["Anonymous Researcher"],
                    'content': f"A comprehensive exploration of {search_query} in contemporary research.",
                    'citations': [],
                    'source': 'Demo Source'
                }
                
                # Ingest paper
                result = self.explorer.ingest_paper(ingest_data)
                
                if result['status'] == 'success':
                    st.success(f"Successfully discovered: {result.get('title', 'Unknown Paper')}")
                    # Refresh papers list
                    st.session_state.papers = self.explorer.load_papers()
                else:
                    st.error("Failed to discover paper")
    
    def render_paper_explorer(self):
        """
        Render the paper exploration interface
        """
        st.header("📚 Paper Collection")
        
        # Get papers from session state
        papers = st.session_state.get('papers', [])
        
        if not papers:
            st.info("No papers discovered yet. Use the search above to find research.")
            return
        
        # Convert to DataFrame
        try:
            df = pd.DataFrame(papers)
            
            # Paper selection
            selected_paper = st.selectbox(
                "Select a Paper", 
                df['title'], 
                index=0
            )
            
            # Display selected paper details
            paper_details = df[df['title'] == selected_paper].iloc[0]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Paper Details")
                st.markdown(f"**DOI:** {paper_details['doi']}")
                st.markdown(f"**Source:** {paper_details['source']}")
                st.text_area("Content", paper_details['content'], height=200)
            
            with col2:
                st.subheader("Quick Stats")
                st.metric("Title Length", len(str(paper_details['title'])))
                st.metric("Content Length", len(str(paper_details['content'])))
        
        except Exception as e:
            st.error(f"Error rendering paper details: {e}")
    
    def render_dashboard(self):
        """
        Render the overall application dashboard
        """
        st.title("🌐 Scientific Literature Explorer")
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["🔍 Search", "📊 Papers"])
        
        with tab1:
            self.render_search_section()
        
        with tab2:
            self.render_paper_explorer()
    
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
