import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import re
import os
from pathlib import Path
import sys

# Add the server directory to Python path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.evaluation.llm_evaluation import evaluate_single_log
from src.evaluation.quantitative_evaluation import generate_performance_report

# Page configuration
st.set_page_config(
    page_title="🔍 Storefront Chatbot Evaluation Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown('<div class="main-header">🔍 Storefront Chatbot Evaluation Dashboard</div>', unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FFFFFF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #FFFFFF;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .pet-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem;
    }
    .compact-pet-card {
        display: inline-block;
        margin: 0.25rem;
        padding: 0.75rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 8px;
        color: white;
        min-width: 200px;
        text-align: center;
    }
    .compact-pet-card h5 {
        margin: 0 0 0.5rem 0;
    }
    .compact-pet-card p {
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    .compact-pet-card .pet-details {
        font-size: 0.8rem;
    }
    .score-excellent { color: #28a745; font-weight: bold; }
    .score-good { color: #ffc107; font-weight: bold; }
    .score-poor { color: #dc3545; font-weight: bold; }
    .pipeline-step {
        background: #000000;
        border-left: 4px solid #007bff;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .health-metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    .health-metric-card:hover {
        transform: translateY(-2px);
    }
    .health-metric-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .health-metric-card .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .health-metric-card .metric-description {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    .response-type-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .response-type-card h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .response-type-card .percentage {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metrics-section {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .status-excellent { color: #28a745; }
    .status-good { color: #ffc107; }
    .status-poor { color: #dc3545; }
    .query-sample-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .query-sample-card h4 {
        margin: 0 0 1rem 0;
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
    }
    .query-item {
        background: rgba(255,255,255,0.1);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid rgba(255,255,255,0.3);
    }
    .query-item:hover {
        background: rgba(255,255,255,0.15);
        border-left-color: rgba(255,255,255,0.6);
    }
    .query-number {
        font-weight: bold;
        color: #ffd700;
        margin-right: 0.5rem;
    }
    .query-text {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .query-more {
        text-align: center;
        font-style: italic;
        opacity: 0.8;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: rgba(255,255,255,0.05);
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

class EvaluationDashboard:
    def __init__(self):
        # Get the server directory (parent of src/evaluation)
        server_dir = Path(__file__).parent.parent.parent
        self.logs_dir = server_dir / "logs" / "logs"
        self.llm_eval_dir = server_dir / "logs" / "llm_evaluations"
        self.quantitative_dir = server_dir / "logs" / "quantitative_reports"
        
        # Ensure directories exist
        self.llm_eval_dir.mkdir(parents=True, exist_ok=True)
        self.quantitative_dir.mkdir(parents=True, exist_ok=True)
        
        self.eval_data = None
        self.llm_eval_data = None
        self.quantitative_data = None
        self.all_logs_data = []
        self.available_queries = []
        self.query_to_file_mapping = {}
    
    def load_available_queries(self):
        """Load all available queries from log files"""
        if not self.logs_dir.exists():
            st.error(f"Logs directory {self.logs_dir} does not exist")
            return
        
        self.available_queries = []
        self.query_to_file_mapping = {}
        
        for log_file in self.logs_dir.glob("eval_*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                raw_query = log_data.get('raw_user_query', 'Unknown Query')
                if raw_query and raw_query != 'Unknown Query':
                    # Truncate long queries for display
                    display_query = raw_query[:100] + "..." if len(raw_query) > 100 else raw_query
                    self.available_queries.append(display_query)
                    self.query_to_file_mapping[display_query] = str(log_file)
                    
            except Exception as e:
                st.error(f"Error loading log file {log_file}: {e}")
    
    def get_log_file_for_query(self, selected_query):
        """Get the log file path for a selected query"""
        return self.query_to_file_mapping.get(selected_query)
    
    def load_eval_data(self, log_file_path):
        """Load evaluation data from a log file"""
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                self.eval_data = json.load(f)
            return True
        except Exception as e:
            st.error(f"Error loading evaluation data: {e}")
            return False
    
    def get_llm_eval_file_path(self, log_file_path):
        """Get the corresponding LLM evaluation file path"""
        log_filename = Path(log_file_path).stem
        # Clean the filename to avoid any special characters that might cause issues
        clean_filename = re.sub(r'[^\w\-_.]', '_', log_filename)
        return self.llm_eval_dir / f"llm_eval_{clean_filename}.json"
    
    def run_llm_evaluation(self, log_file_path):
        """Run LLM evaluation for a log file"""
        try:
            # Check if evaluation already exists
            llm_eval_path = self.get_llm_eval_file_path(log_file_path)
            
            if llm_eval_path.exists():
                # Load existing evaluation
                with open(llm_eval_path, 'r', encoding='utf-8') as f:
                    self.llm_eval_data = json.load(f)
                return True
            
            # Run new evaluation
            with st.spinner("Running LLM evaluation..."):
                evaluation_result = evaluate_single_log(str(log_file_path), save_result=True, output_path=str(llm_eval_path))
                
                if evaluation_result.get("error"):
                    st.error(f"LLM evaluation failed: {evaluation_result['error']}")
                    return False
                
                # Load the saved evaluation
                with open(llm_eval_path, 'r', encoding='utf-8') as f:
                    self.llm_eval_data = json.load(f)
                
                st.success("LLM evaluation completed!")
                return True
                
        except Exception as e:
            st.error(f"Error running LLM evaluation: {e}")
            return False
    
    def load_quantitative_data(self):
        """Load or generate quantitative data"""
        try:
            # Check if recent quantitative report exists
            quant_files = list(self.quantitative_dir.glob("quantitative_report_*.json"))
            if quant_files:
                # Load the most recent report
                latest_file = max(quant_files, key=os.path.getctime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.quantitative_data = json.load(f)
                return True
            
            # Generate new quantitative report
            with st.spinner("Generating quantitative analysis..."):
                report = generate_performance_report(str(self.logs_dir))
                
                # Save the report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.quantitative_dir / f"quantitative_report_{timestamp}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                
                self.quantitative_data = report
                st.success("Quantitative analysis completed!")
                return True
                
        except Exception as e:
            st.error(f"Error loading quantitative data: {e}")
            return False
    
    def load_all_logs_for_analysis(self):
        """Load all log files for query analysis"""
        self.all_logs_data = []
        
        if not self.logs_dir.exists():
            return
        
        for log_file in self.logs_dir.glob("eval_*.json"):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                self.all_logs_data.append(log_data)
            except Exception as e:
                st.error(f"Error loading log file {log_file}: {e}")

    def analyze_query_types(self):
        """Analyze query types from all loaded logs"""
        if not self.all_logs_data:
            return {}
        
        query_types = {
            'product_queries': [],
            'article_queries': [],
            'general_queries': [],
            'query_categories': {}
        }
        
        for log in self.all_logs_data:
            raw_query = log.get('raw_user_query', '')
            tool_calls = log.get('tool_calls', [])
            
            # Categorize based on tool calls
            has_product_search = any(tool.get('tool_name') == 'search_products' for tool in tool_calls)
            has_article_search = any(tool.get('tool_name') == 'search_articles' for tool in tool_calls)
            
            if has_product_search:
                query_types['product_queries'].append(raw_query)
            elif has_article_search:
                query_types['article_queries'].append(raw_query)
            else:
                query_types['general_queries'].append(raw_query)
            
            # Extract categories from tool calls
            for tool in tool_calls:
                arguments = tool.get('arguments', {})
                categories = arguments.get('category_level_1', []) + arguments.get('category_level_2', [])
                for category in categories:
                    if category:
                        query_types['query_categories'][category] = query_types['query_categories'].get(category, 0) + 1
        
        return query_types

    def extract_user_info(self, user_context):
        """Extract user information from user context"""
        user_info = {}
        if not user_context:
            return user_info
  
        # Extract user info section
        user_info_pattern = re.search(
            r'Customer:\s*(.*?)\n'
            r'Location:\s*(.*?)\n'
            r'Customer Profile:\s*(.*?)\n'
            r'Dietary Preferences:\s*(.*?)\n'
            r'Preferred Brands:\s*(.*?)(?=\n[A-Z]|\n\n|$)',
            user_context,
            re.DOTALL
        )

        user_info = {}
        if user_info_pattern:
            user_info['customer_name'] = user_info_pattern.group(1).strip()
            user_info['location'] = user_info_pattern.group(2).strip()
            user_info['customer_profile'] = user_info_pattern.group(3).strip()
            user_info['dietary_preferences'] = user_info_pattern.group(4).strip()
            user_info['preferred_brands'] = user_info_pattern.group(5).strip()

        return user_info

    def extract_pet_info(self, user_context):
        """Extract pet information from user context"""
        pets = []
        if not user_context:
            return pets
        
        # Extract pets section
        pet_section = re.search(r'Pets \(\d+\):(.*?)(?=\n\n|\Z)', user_context, re.DOTALL)
        if not pet_section:
            return pets
        
        # Parse individual pets
        pet_matches = re.findall(r'Pet \d+:\nName: (.*?)\nBreed: (.*?)\n(?:Age: (.*?)\n)?(?:Life Stage: (.*?)\n)?(?:Size: (.*?)\n)?(?:Weight: (.*?)\n)?', pet_section.group(1), re.DOTALL)
        
        for match in pet_matches:
            pets.append({
                'name': match[0].strip(),
                'breed': match[1].strip(),
                'age': match[2].strip() if match[2] else 'Unknown',
                'life_stage': match[3].strip() if match[3] else 'Unknown',
                'size': match[4].strip() if match[4] else 'Unknown',
                'weight': match[5].strip() if match[5] else 'Unknown'
            })
        
        return pets
    
    def get_score_color_class(self, score):
        """Get CSS class for score coloring"""
        if score >= 8:
            return "score-excellent"
        elif score >= 6:
            return "score-good"
        else:
            return "score-poor"
    
    def render_user_info(self):
        """Render user information section"""
        if not self.eval_data:
            return
        
        user_context = self.eval_data.get('user_context', '')
        user_info = self.extract_user_info(user_context)
        pets = self.extract_pet_info(user_context)
        
        st.markdown('<div class="section-header">👤 User Information</div>', unsafe_allow_html=True)

        if user_info:
            # Expander for detailed information
            with st.expander(f"{user_info['customer_name']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Customer Profile:**")
                    st.info(user_info['customer_profile'])
                    
                    st.markdown("**Dietary Preferences:**")
                    st.info(user_info['dietary_preferences'])
                
                    st.markdown("**Preferred Brands:**")
                    st.info(user_info['preferred_brands'])

                with col2:
                    if pets:
                        st.markdown("**Pets:**")
                        for pet in pets:
                            st.info(f"**{pet['name']}** - {pet['breed']} - {pet['age']} - {pet['size']} - {pet['weight']}")
    
    def render_pipeline_flow(self):
        """Render query processing pipeline flow"""
        if not self.eval_data:
            return
        
        st.markdown('<div class="section-header">🔄 Query Processing Flow</div>', unsafe_allow_html=True)
        
        # Query transformation
        original_query = self.eval_data.get('raw_user_query', 'N/A')
        tool_calls = self.eval_data.get('tool_calls', [])
        
        # Show pipeline steps
        with st.expander("📝 Pipeline Steps", expanded=True):
            st.markdown(f"**1. Original Query:** `{original_query}`")
            
            for i, tool in enumerate(tool_calls):
                tool_name = tool.get('tool_name', 'Unknown')
                arguments = tool.get('arguments', {})
                
                st.markdown(f"**2. Enhanced Query:** `{arguments.get('query', 'N/A')}`")

                st.markdown(f"""
**{i+3}. Tool:** `{tool_name}`  
**Category 1:** `{', '.join(arguments.get('category_level_1', []) or ['None'])}`  
**Category 2:** `{', '.join(arguments.get('category_level_2', []) or ['None'])}`  
**Excluded Ingredients:** `{', '.join(arguments.get('excluded_ingredients', []) or ['None'])}`  
**Include Ingredients:** `{', '.join(arguments.get('required_ingredients', []) or ['None'])}`
""")    
        # Performance metrics
        tool_calls = self.eval_data.get('tool_calls', [])
        
        if tool_calls:
            # Determine which search time to display based on tool calls
            has_article_search = any(tool.get('tool_name') == 'search_articles' for tool in tool_calls)
            has_product_search = any(tool.get('tool_name') == 'search_products' for tool in tool_calls)
            
            if has_article_search and has_product_search:
                # Both tools used - show both
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_time = self.eval_data.get('total_processing_time')
                    total_time = total_time if total_time is not None else 0
                    st.metric("⏱️ Total Processing Time", f"{total_time:.2f}s")
                with col2:
                    article_search_time = self.eval_data.get('article_search_time')
                    article_search_time = article_search_time if article_search_time is not None else 0
                    st.metric("📰 Article Search Time", f"{article_search_time:.2f}s")
                with col3:
                    product_search_time = self.eval_data.get('product_search_time')
                    product_search_time = product_search_time if product_search_time is not None else 0
                    st.metric("🛍️ Product Search Time", f"{product_search_time:.2f}s")
                with col4:
                    llm_time = self.eval_data.get('llm_response_time')
                    llm_time = llm_time if llm_time is not None else 0
                    st.metric("🤖 LLM Response Time", f"{llm_time:.2f}s")
            elif has_article_search:
                # Only article search
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_time = self.eval_data.get('total_processing_time')
                    total_time = total_time if total_time is not None else 0
                    st.metric("⏱️ Total Processing Time", f"{total_time:.2f}s")
                with col2:
                    article_search_time = self.eval_data.get('article_search_time')
                    article_search_time = article_search_time if article_search_time is not None else 0
                    st.metric("📰 Article Search Time", f"{article_search_time:.2f}s")
                with col3:
                    llm_time = self.eval_data.get('llm_response_time')
                    llm_time = llm_time if llm_time is not None else 0
                    st.metric("🤖 LLM Response Time", f"{llm_time:.2f}s")
            elif has_product_search:
                # Only product search
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_time = self.eval_data.get('total_processing_time')
                    total_time = total_time if total_time is not None else 0
                    st.metric("⏱️ Total Processing Time", f"{total_time:.2f}s")
                with col2:
                    product_search_time = self.eval_data.get('product_search_time')
                    product_search_time = product_search_time if product_search_time is not None else 0
                    st.metric("🛍️ Product Search Time", f"{product_search_time:.2f}s")
                with col3:
                    llm_time = self.eval_data.get('llm_response_time')
                    llm_time = llm_time if llm_time is not None else 0
                    st.metric("🤖 LLM Response Time", f"{llm_time:.2f}s")
            else:
                # Other tools - show generic search time
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_time = self.eval_data.get('total_processing_time')
                    total_time = total_time if total_time is not None else 0
                    st.metric("⏱️ Total Processing Time", f"{total_time:.2f}s")
                with col2:
                    search_time = self.eval_data.get('product_search_time')
                    search_time = search_time if search_time is not None else 0
                    st.metric("🔍 Search Time", f"{search_time:.2f}s")
                with col3:
                    llm_time = self.eval_data.get('llm_response_time')
                    llm_time = llm_time if llm_time is not None else 0
                    st.metric("🤖 LLM Response Time", f"{llm_time:.2f}s")
        else:
            # No tool calls - only show total and LLM time
            col1, col2 = st.columns(2)
            with col1:
                total_time = self.eval_data.get('total_processing_time')
                total_time = total_time if total_time is not None else 0
                st.metric("⏱️ Total Processing Time", f"{total_time:.2f}s")
            with col2:
                llm_time = self.eval_data.get('llm_response_time')
                llm_time = llm_time if llm_time is not None else 0
                st.metric("🤖 LLM Response Time", f"{llm_time:.2f}s")
    
    def render_evaluation_scores(self):
        """Render LLM evaluation scores based on response type"""
        if not self.llm_eval_data:
            return
        
        response_type = self.llm_eval_data.get('metadata', {}).get('response_type', 'unknown')
        
        st.markdown(f'<div class="section-header">📊 Evaluation Scores - {response_type.replace("_", " ").title()}</div>', unsafe_allow_html=True)
        
        if response_type == "direct_response":
            self._render_direct_response_scores()
        elif response_type == "article_search":
            self._render_article_search_scores()
        else:  # product_search
            self._render_product_search_scores()
    
    def _render_direct_response_scores(self):
        """Render scores for direct response evaluations"""
        if not self.llm_eval_data:
            return
            
        scores = {
            'Query Understanding': self.llm_eval_data.get('query_understanding_score', 0),
            'Response Appropriateness': self.llm_eval_data.get('response_appropriateness', 0),
            'Engagement Quality': self.llm_eval_data.get('engagement_quality', 0),
            'Helpfulness': self.llm_eval_data.get('helpfulness', 0),
            'Tone and Personality': self.llm_eval_data.get('tone_and_personality', 0)
        }
        
        # Overall score
        overall_score = self.llm_eval_data.get('overall_score', 0)
        st.info(f"Overall Score: {overall_score}/10")
        
        # Radar chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself',
            name='Scores',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12))
            ),
            showlegend=False,
            title="Direct Response Performance Radar Chart",
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed scores with reasoning
        with st.expander("📝 Detailed Analysis", expanded=True):
            for metric, score in scores.items():
                reasoning_key = f"{metric.lower().replace(' ', '_')}_reasoning"
                reasoning = self.llm_eval_data.get(reasoning_key, "No reasoning available")
                
                score_class = self.get_score_color_class(score)
                st.info(f"{metric}: {score}/10")
                st.markdown(f"**Reasoning:** {reasoning}")
    
    def _render_article_search_scores(self):
        """Render scores for article search evaluations"""
        if not self.llm_eval_data:
            return
            
        scores = {
            'Query Understanding': self.llm_eval_data.get('query_understanding_score', 0),
            'Tool Selection': self.llm_eval_data.get('tool_selection_accuracy', 0),
            'Article Relevance': self.llm_eval_data.get('article_relevance', 0),
            'Content Quality': self.llm_eval_data.get('content_quality', 0),
            'Reference Link Quality': self.llm_eval_data.get('reference_link_quality', 0),
            'Response Structure': self.llm_eval_data.get('response_structure', 0),
            'Actionability': self.llm_eval_data.get('actionability', 0)
        }
        
        # Overall score
        overall_score = self.llm_eval_data.get('overall_score', 0)
        st.info(f"Overall Score: {overall_score}/10")
        
        # Radar chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself',
            name='Scores',
            line_color='#f093fb',
            fillcolor='rgba(240, 147, 251, 0.3)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12))
            ),
            showlegend=False,
            title="Article Search Performance Radar Chart",
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed scores with reasoning
        with st.expander("📝 Detailed Analysis", expanded=True):
            for metric, score in scores.items():
                reasoning_key = f"{metric.lower().replace(' ', '_')}_reasoning"
                reasoning = self.llm_eval_data.get(reasoning_key, "No reasoning available")
                
                score_class = self.get_score_color_class(score)
                st.info(f"{metric}: {score}/10")
                st.markdown(f"**Reasoning:** {reasoning}")
    
    def _render_product_search_scores(self):
        """Render scores for product search evaluations"""
        if not self.llm_eval_data:
            return
            
        scores = {
            'Query Understanding': self.llm_eval_data.get('query_understanding_score', 0),
            'Tool Selection': self.llm_eval_data.get('tool_selection_accuracy', 0),
            'Search Relevance': self.llm_eval_data.get('search_relevance_score', 0),
            'Product Relevance': self.llm_eval_data.get('product_relevance_score', 0),
            'Product Diversity': self.llm_eval_data.get('product_diversity_score', 0),
            'Brand Preference': self.llm_eval_data.get('brand_preference_alignment', 0),
            'Response Helpfulness': self.llm_eval_data.get('response_helpfulness', 0)
        }
        
        # Overall score
        overall_score = self.llm_eval_data.get('overall_score', 0)
        st.info(f"Overall Score: {overall_score}/10")
        
        # Radar chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself',
            name='Scores',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12))
            ),
            showlegend=False,
            title="Product Search Performance Radar Chart",
            height=500
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed scores with reasoning
        with st.expander("📝 Detailed Analysis", expanded=True):
            for metric, score in scores.items():
                reasoning_key = f"{metric.lower().replace(' ', '_')}_reasoning"
                reasoning = self.llm_eval_data.get(reasoning_key, "No reasoning available")
                
                score_class = self.get_score_color_class(score)
                st.info(f"{metric}: {score}/10")
                st.markdown(f"**Reasoning:** {reasoning}")
    
    def render_product_analysis(self):
        """Render product retrieval analysis - only for product search responses"""
        if not self.eval_data:
            return
        
        # Check if this is a product search response
        tool_calls = self.eval_data.get('tool_calls', [])
        is_product_search = any(tool.get('tool_name') == 'search_products' for tool in tool_calls)
        
        if not is_product_search:
            return
        
        products = self.eval_data.get('product_results', [])
        if not products:
            return
        
        st.markdown('<div class="section-header">🛍️ Product Retrieval Analysis</div>', unsafe_allow_html=True)
        
        df = pd.DataFrame(products)
        
        # Summary metrics at the top
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_price = df['price'].mean()
            st.markdown(f"""
            <div class="health-metric-card">
                <h3>💰 Average Price</h3>
                <div class="metric-value">${avg_price:.2f}</div>
                <div class="metric-description">Mean product price</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_rating = df['rating'].mean()
            st.markdown(f"""
            <div class="health-metric-card">
                <h3>⭐ Average Rating</h3>
                <div class="metric-value">{avg_rating:.1f}/5</div>
                <div class="metric-description">Mean product rating</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            unique_brands = df['brand'].nunique()
            st.markdown(f"""
            <div class="health-metric-card">
                <h3>🏷️ Brand Diversity</h3>
                <div class="metric-value">{unique_brands}</div>
                <div class="metric-description">Unique brands</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            price_range = f"${df['price'].min():.0f} - ${df['price'].max():.0f}"
            st.markdown(f"""
            <div class="health-metric-card">
                <h3>📊 Price Range</h3>
                <div class="metric-value">{price_range}</div>
                <div class="metric-description">Min - Max price</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced price distribution with better styling
            fig_price = px.histogram(
                df, 
                x='price', 
                nbins=min(8, len(df)), 
                title='Price Distribution',
                color_discrete_sequence=['#667eea'],
                opacity=0.8
            )
            fig_price.update_layout(
                showlegend=False, 
                height=400,
                title_font_size=16,
                title_font_color='#FFFFFF',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF'),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    title_font_color='#FFFFFF'
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    title_font_color='#FFFFFF'
                )
            )
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            # Enhanced rating distribution
            fig_rating = px.histogram(
                df, 
                x='rating', 
                nbins=min(6, len(df)), 
                title='Rating Distribution',
                color_discrete_sequence=['#f093fb'],
                opacity=0.8
            )
            fig_rating.update_layout(
                showlegend=False, 
                height=400,
                title_font_size=16,
                title_font_color='#FFFFFF',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#FFFFFF'),
                xaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    title_font_color='#FFFFFF'
                ),
                yaxis=dict(
                    gridcolor='rgba(255,255,255,0.1)',
                    title_font_color='#FFFFFF'
                )
            )
            st.plotly_chart(fig_rating, use_container_width=True)
        
        # Brand distribution with better styling
        brand_counts = df['brand'].value_counts()
        fig_brand = px.pie(
            values=brand_counts.values, 
            names=brand_counts.index,
            title='Brand Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_brand.update_layout(
            height=400,
            title_font_size=16,
            title_font_color='#FFFFFF',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FFFFFF'),
            legend=dict(font=dict(color='#FFFFFF'))
        )
        st.plotly_chart(fig_brand, use_container_width=True)
        
        # Enhanced product table with better styling
        with st.expander("📋 Product Details", expanded=True):
            # Create a styled dataframe
            styled_df = df[['rank', 'title', 'brand', 'price', 'rating']].copy()
            styled_df['price'] = [f"${x:.2f}" for x in styled_df['price']]
            styled_df['rating'] = [f"{x:.1f} ⭐" for x in styled_df['rating']]
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "rank": st.column_config.NumberColumn("Rank", format="%d"),
                    "title": st.column_config.TextColumn("Product Name", width="large"),
                    "brand": st.column_config.TextColumn("Brand", width="medium"),
                    "price": st.column_config.TextColumn("Price", width="small"),
                    "rating": st.column_config.TextColumn("Rating", width="small")
                }
            )
    
    def render_article_analysis(self):
        """Render article analysis - only for article search responses"""
        if not self.eval_data:
            return
        
        # Check if this is an article search response
        tool_calls = self.eval_data.get('tool_calls', [])
        is_article_search = any(tool.get('tool_name') == 'search_articles' for tool in tool_calls)
        
        if not is_article_search:
            return
        
        st.markdown('<div class="section-header">📰 Article Analysis</div>', unsafe_allow_html=True)
        
        # Extract article information from chat history
        chat_history = self.eval_data.get('chat_history', [])
        articles = []
        
        for item in chat_history:
            if item.get('type') == 'function_call_output' and 'article' in str(item.get('output', '')).lower():
                output = item.get('output', '')
                # Try to extract article titles and links
                lines = output.split('\n')
                current_article = {}
                for line in lines:
                    if line.startswith('Article'):
                        if current_article:
                            articles.append(current_article)
                        current_article = {'title': line}
                    elif line.startswith('Link:'):
                        current_article['link'] = line.replace('Link:', '').strip()
                    elif line.startswith('Summary:'):
                        current_article['summary'] = line.replace('Summary:', '').strip()
                
                if current_article:
                    articles.append(current_article)
        
        if articles:
            st.info(f"Found {len(articles)} articles")
            
            for i, article in enumerate(articles, 1):
                with st.expander(f"Article {i}: {article.get('title', 'Unknown')}", expanded=True):
                    if 'summary' in article:
                        st.markdown("**Summary:**")
                        st.write(article['summary'])
                    
                    if 'link' in article:
                        st.markdown("**Link:**")
                        st.write(article['link'])
        else:
            st.info("No articles found in the response")
    

    
    def render_quantitative_analysis_tab(self):
        """Render the quantitative analysis tab with system health and query analysis"""
        if not self.quantitative_data and not self.all_logs_data:
            st.info("No quantitative data available. Please ensure logs exist in logs/logs/ directory.")
            return
        
        if self.all_logs_data:
            query_analysis = self.analyze_query_types()
            
            # Sample queries by type with beautiful cards
            st.markdown("### 🔍 Sample Queries by Type")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🛍️ Product Queries**")
                product_queries = query_analysis.get('product_queries', [])
                if product_queries:
                    for i, query in enumerate(product_queries[:5], 1):
                        st.markdown(f"""
                        <div class="query-sample-card">
                            <div class="query-item">
                                <span class="query-number">#{i}</span>
                                <span class="query-text">{query}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    if len(product_queries) > 5:
                        st.markdown(f"""
                        <div class="query-more">
                            ... and {len(product_queries) - 5} more product queries
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="query-sample-card">
                        <div class="query-item">
                            <span class="query-text">No product queries found</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**📰 Article Queries**")
                article_queries = query_analysis.get('article_queries', [])
                if article_queries:
                    for i, query in enumerate(article_queries[:5], 1):
                        st.markdown(f"""
                        <div class="query-sample-card">
                            <div class="query-item">
                                <span class="query-number">#{i}</span>
                                <span class="query-text">{query}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    if len(article_queries) > 5:
                        st.markdown(f"""
                        <div class="query-more">
                            ... and {len(article_queries) - 5} more article queries
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="query-sample-card">
                        <div class="query-item">
                            <span class="query-text">No article queries found</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("**💬 General Queries**")
                general_queries = query_analysis.get('general_queries', [])
                if general_queries:
                    for i, query in enumerate(general_queries[:5], 1):
                        st.markdown(f"""
                        <div class="query-sample-card">
                            <div class="query-item">
                                <span class="query-number">#{i}</span>
                                <span class="query-text">{query}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    if len(general_queries) > 5:
                        st.markdown(f"""
                        <div class="query-more">
                            ... and {len(general_queries) - 5} more general queries
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="query-sample-card">
                        <div class="query-item">
                            <span class="query-text">No general queries found</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # System Health Metrics
        if self.quantitative_data:
            st.markdown('<div class="section-header">⚡ System Health Metrics</div>', unsafe_allow_html=True)
            
            metrics = self.quantitative_data.get('metrics', {})
            recommendations = self.quantitative_data.get('recommendations', [])
            
            # Response Type Distribution with beautiful cards
            response_type_dist = metrics.get('response_type_distribution', {})
            if response_type_dist:
                
                st.markdown("### 📊 Response Type Distribution")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    direct_pct = response_type_dist.get('direct_response', 0)
                    st.markdown(f"""
                    <div class="response-type-card">
                        <h3>💬 Direct Responses</h3>
                        <div class="percentage">{direct_pct:.1f}%</div>
                        <div class="metric-description">General conversation queries</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    article_pct = response_type_dist.get('article_search', 0)
                    st.markdown(f"""
                    <div class="response-type-card">
                        <h3>📰 Article Searches</h3>
                        <div class="percentage">{article_pct:.1f}%</div>
                        <div class="metric-description">Educational content queries</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    product_pct = response_type_dist.get('product_search', 0)
                    st.markdown(f"""
                    <div class="response-type-card">
                        <h3>🛍️ Product Searches</h3>
                        <div class="percentage">{product_pct:.1f}%</div>
                        <div class="metric-description">Product recommendation queries</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Performance KPIs with beautiful cards
            
            st.markdown("### ⚡ Performance KPIs")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                avg_time = metrics.get('avg_total_processing_time', 0)
                status_class = "status-excellent" if avg_time <= 5 else "status-good" if avg_time <= 10 else "status-poor"
                status_icon = "🟢" if avg_time <= 5 else "🟡" if avg_time <= 10 else "🔴"
                st.markdown(f"""
                <div class="health-metric-card">
                    <h3>{status_icon} Response Time</h3>
                    <div class="metric-value">{avg_time:.1f}s</div>
                    <div class="metric-description">Average total processing</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                avg_time = metrics.get('avg_product_search_time', 0)
                status_class = "status-excellent" if avg_time <= 2 else "status-good" if avg_time <= 5 else "status-poor"
                status_icon = "🟢" if avg_time <= 2 else "🟡" if avg_time <= 5 else "🔴"
                st.markdown(f"""
                <div class="health-metric-card">
                    <h3>{status_icon} Product Search</h3>
                    <div class="metric-value">{avg_time:.1f}s</div>
                    <div class="metric-description">Average search time</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                avg_time = metrics.get('avg_article_search_time', 0)
                status_class = "status-excellent" if avg_time <= 2 else "status-good" if avg_time <= 5 else "status-poor"
                status_icon = "🟢" if avg_time <= 2 else "🟡" if avg_time <= 5 else "🔴"
                st.markdown(f"""
                <div class="health-metric-card">
                    <h3>{status_icon} Article Search</h3>
                    <div class="metric-value">{avg_time:.1f}s</div>
                    <div class="metric-description">Average search time</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                success_rate = metrics.get('success_rate', 0)
                status_class = "status-excellent" if success_rate >= 95 else "status-good" if success_rate >= 90 else "status-poor"
                status_icon = "🟢" if success_rate >= 95 else "🟡" if success_rate >= 90 else "🔴"
                st.markdown(f"""
                <div class="health-metric-card">
                    <h3>{status_icon} Success Rate</h3>
                    <div class="metric-value">{success_rate:.1f}%</div>
                    <div class="metric-description">Query success rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                slow_queries = metrics.get('slow_queries_percentage', 0)
                status_class = "status-excellent" if slow_queries <= 5 else "status-good" if slow_queries <= 10 else "status-poor"
                status_icon = "🟢" if slow_queries <= 5 else "🟡" if slow_queries <= 10 else "🔴"
                st.markdown(f"""
                <div class="health-metric-card">
                    <h3>{status_icon} Slow Queries</h3>
                    <div class="metric-value">{slow_queries:.1f}%</div>
                    <div class="metric-description">Queries > 10s</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Product Search Metrics (only show if there are product searches)
            if metrics.get('avg_products_returned', 0) > 0:
                
                st.markdown("### 🛍️ Product Search Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_products = metrics.get('avg_products_returned', 0)
                    st.markdown(f"""
                    <div class="health-metric-card">
                        <h3>📦 Products Returned</h3>
                        <div class="metric-value">{avg_products:.1f}</div>
                        <div class="metric-description">Average per query</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    brand_diversity = metrics.get('brand_diversity', 0)
                    status_class = "status-excellent" if brand_diversity > 0.8 else "status-good" if brand_diversity > 0.6 else "status-poor"
                    status_icon = "🟢" if brand_diversity > 0.8 else "🟡" if brand_diversity > 0.6 else "🔴"
                    st.markdown(f"""
                    <div class="health-metric-card">
                        <h3>{status_icon} Brand Diversity</h3>
                        <div class="metric-value">{brand_diversity:.2f}</div>
                        <div class="metric-description">Diversity score (0-1)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    price_range = metrics.get('price_range', {})
                    min_price = price_range.get('min', 0)
                    max_price = price_range.get('max', 0)
                    st.markdown(f"""
                    <div class="health-metric-card">
                        <h3>💰 Price Range</h3>
                        <div class="metric-value">${min_price:.0f}-${max_price:.0f}</div>
                        <div class="metric-description">Product price range</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Article Search Metrics (only show if there are article searches)
            if metrics.get('avg_articles_returned', 0) > 0:
                
                st.markdown("### 📰 Article Search Metrics")
                
                avg_articles = metrics.get('avg_articles_returned', 0)
                st.markdown(f"""
                <div class="health-metric-card" style="max-width: 300px; margin: 0 auto;">
                    <h3>📰 Articles Returned</h3>
                    <div class="metric-value">{avg_articles:.1f}</div>
                    <div class="metric-description">Average per query</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Recommendations with better styling
            if recommendations:
                
                st.markdown("### 💡 System Recommendations")
                
                for rec in recommendations:
                    if "Critical" in rec:
                        st.error(f"🚨 {rec}")
                    elif "Warning" in rec:
                        st.warning(f"⚠️ {rec}")
                    else:
                        st.info(f"ℹ️ {rec}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Run the dashboard"""
        # Load available queries and quantitative data on startup
        self.load_available_queries()
        self.load_quantitative_data()
        self.load_all_logs_for_analysis()
        
        # Sidebar for query selection
        st.sidebar.title("🔍 Query Selection")
        
        # Show status information
        st.sidebar.markdown(f"**📊 Total Queries:** {len(self.available_queries)}")
        if self.quantitative_data:
            st.sidebar.markdown(f"**✅ Quantitative Analysis:** Available")
        else:
            st.sidebar.markdown(f"**⏳ Quantitative Analysis:** Generating...")
        
        if not self.available_queries:
            st.sidebar.warning("No evaluation logs found in logs/logs/ directory")
            st.info("Please run some queries first to see evaluation data")
            return
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data", help="Reload logs and regenerate analysis"):
            st.rerun()
        
        # pre-pend empty string to available_queries
        self.available_queries = [''] + self.available_queries
        # Query selection dropdown
        selected_query = st.sidebar.selectbox(
            "Select a query to analyze:",
            options=self.available_queries,
            index=0 if self.available_queries else None,
            help="Choose a query to see detailed analysis"
        )
        
        if selected_query:
            # Get the corresponding log file
            log_file_path = self.get_log_file_for_query(selected_query)
            
            if log_file_path:
                # Load evaluation data
                if self.load_eval_data(log_file_path):
                    # Run LLM evaluation if needed
                    self.run_llm_evaluation(log_file_path)
                    st.sidebar.success("✅ Data loaded successfully!")
                else:
                    st.sidebar.error("❌ Failed to load evaluation data")
                    return
            else:
                st.sidebar.error("❌ Could not find log file for selected query")
                return
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Individual Session Analysis", "📈 Quantitative Analysis"])
        
        with tab1:
            # Individual session analysis
            if self.eval_data:
                self.render_user_info()
                self.render_pipeline_flow()
                self.render_product_analysis()
                self.render_article_analysis()
                self.render_evaluation_scores()
            else:
                st.info("Select a query from the sidebar to see detailed analysis")
        
        with tab2:
            # Quantitative analysis
            self.render_quantitative_analysis_tab()

# Run the dashboard
if __name__ == "__main__":
    dashboard = EvaluationDashboard()
    dashboard.run()