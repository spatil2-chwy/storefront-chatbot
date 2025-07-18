import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import re

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
</style>
""", unsafe_allow_html=True)

class EvaluationDashboard:
    def __init__(self):
        self.eval_data = None
        self.llm_eval_data = None
        self.quantitative_data = None
        self.all_logs_data = []  # Store all individual log files for query analysis
    
    def load_data(self, eval_file, llm_eval_file, quantitative_file):
        """Load evaluation data from uploaded files"""
        try:
            self.eval_data = json.loads(eval_file.read()) if eval_file else None
            self.llm_eval_data = json.loads(llm_eval_file.read()) if llm_eval_file else None
            self.quantitative_data = json.loads(quantitative_file.read()) if quantitative_file else None
            return True
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def load_all_logs(self, log_files):
        """Load all individual log files for query analysis"""
        self.all_logs_data = []
        if not log_files:
            return
        
        for log_file in log_files:
            try:
                log_data = json.loads(log_file.read())
                self.all_logs_data.append(log_data)
            except Exception as e:
                st.error(f"Error loading log file {log_file.name}: {str(e)}")
    
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
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Price distribution
            fig_price = px.histogram(df, x='price', nbins=10, title='Price Distribution',
                                   color_discrete_sequence=['#667eea'])
            fig_price.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            # rating distribution
            fig_rating = px.histogram(df, x='rating', nbins=10, title='Rating Distribution',
                                   color_discrete_sequence=['#667eea'])
            fig_rating.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_rating, use_container_width=True)

        with col3:
            # Brand distribution
            brand_counts = df['brand'].value_counts()
            fig_brand = px.pie(values=brand_counts.values, names=brand_counts.index,
                             title='Brand Distribution', color_discrete_sequence=px.colors.qualitative.Set3)
            fig_brand.update_layout(height=300)
            st.plotly_chart(fig_brand, use_container_width=True)
        
        # Product table
        with st.expander("📋 Product Details", expanded=True):
            st.dataframe(
                df[['rank', 'title', 'brand', 'price', 'rating']].round(2),
                use_container_width=True,
                hide_index=True
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
            st.info("Upload quantitative data or individual log files to see analysis")
            return
        
        # Query Type Analysis
        if self.all_logs_data:
            st.markdown('<div class="section-header">🔍 Query Type Analysis</div>', unsafe_allow_html=True)
            
            query_analysis = self.analyze_query_types()
            
            # Query distribution
            col1, col2, col3 = st.columns(3)
            
            with col1:
                product_count = len(query_analysis.get('product_queries', []))
                total_queries = len(self.all_logs_data)
                product_pct = (product_count / total_queries * 100) if total_queries > 0 else 0
                st.metric("🛍️ Product Queries", f"{product_count} ({product_pct:.1f}%)")
            
            with col2:
                article_count = len(query_analysis.get('article_queries', []))
                article_pct = (article_count / total_queries * 100) if total_queries > 0 else 0
                st.metric("📰 Article Queries", f"{article_count} ({article_pct:.1f}%)")
            
            with col3:
                general_count = len(query_analysis.get('general_queries', []))
                general_pct = (general_count / total_queries * 100) if total_queries > 0 else 0
                st.metric("💬 General Queries", f"{general_count} ({general_pct:.1f}%)")
            
            # Query categories chart
            categories = query_analysis.get('query_categories', {})
            if categories:
                st.markdown("#### Query Categories Distribution")
                fig_categories = px.bar(
                    x=list(categories.keys()),
                    y=list(categories.values()),
                    title="Query Categories",
                    color_discrete_sequence=['#667eea']
                )
                fig_categories.update_layout(
                    xaxis_title="Category",
                    yaxis_title="Count",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_categories, use_container_width=True)
            
            # Sample queries by type
            with st.expander("📝 Sample Queries by Type", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🛍️ Product Queries:**")
                    product_queries = query_analysis.get('product_queries', [])
                    for i, query in enumerate(product_queries[:5], 1):
                        st.markdown(f"{i}. {query[:50]}{'...' if len(query) > 50 else ''}")
                    if len(product_queries) > 5:
                        st.markdown(f"... and {len(product_queries) - 5} more")
                
                with col2:
                    st.markdown("**📰 Article Queries:**")
                    article_queries = query_analysis.get('article_queries', [])
                    for i, query in enumerate(article_queries[:5], 1):
                        st.markdown(f"{i}. {query[:50]}{'...' if len(query) > 50 else ''}")
                    if len(article_queries) > 5:
                        st.markdown(f"... and {len(article_queries) - 5} more")
                
                with col3:
                    st.markdown("**💬 General Queries:**")
                    general_queries = query_analysis.get('general_queries', [])
                    for i, query in enumerate(general_queries[:5], 1):
                        st.markdown(f"{i}. {query[:50]}{'...' if len(query) > 50 else ''}")
                    if len(general_queries) > 5:
                        st.markdown(f"... and {len(general_queries) - 5} more")
        
        # System Health Metrics (existing functionality)
        if self.quantitative_data:
            st.markdown('<div class="section-header">⚡ System Health Metrics</div>', unsafe_allow_html=True)
            
            metrics = self.quantitative_data.get('metrics', {})
            recommendations = self.quantitative_data.get('recommendations', [])
            
            # Response type distribution
            response_type_dist = metrics.get('response_type_distribution', {})
            if response_type_dist:
                st.markdown("#### Response Type Distribution")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    direct_pct = response_type_dist.get('direct_response', 0)
                    st.metric("💬 Direct Responses", f"{direct_pct:.1f}%")
                
                with col2:
                    article_pct = response_type_dist.get('article_search', 0)
                    st.metric("📰 Article Searches", f"{article_pct:.1f}%")
                
                with col3:
                    product_pct = response_type_dist.get('product_search', 0)
                    st.metric("🛍️ Product Searches", f"{product_pct:.1f}%")
            
            # KPI metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                avg_time = metrics.get('avg_total_processing_time')
                avg_time = avg_time if avg_time is not None else 0
                color = "🔴" if avg_time > 15 else "🟡" if avg_time > 10 else "🟢"
                st.metric(f"{color} Avg Response Time", f"{avg_time:.1f}s")

            with col2:
                avg_time = metrics.get('avg_product_search_time')
                avg_time = avg_time if avg_time is not None else 0
                color = "🔴" if avg_time > 15 else "🟡" if avg_time > 10 else "🟢"
                st.metric(f"{color} Avg Product Search", f"{avg_time:.1f}s")
            
            with col3:
                avg_time = metrics.get('avg_article_search_time')
                avg_time = avg_time if avg_time is not None else 0
                color = "🔴" if avg_time > 15 else "🟡" if avg_time > 10 else "🟢"
                st.metric(f"{color} Avg Article Search", f"{avg_time:.1f}s")
            
            with col4:
                success_rate = metrics.get('success_rate')
                success_rate = success_rate if success_rate is not None else 0
                color = "🟢" if success_rate > 95 else "🟡" if success_rate > 90 else "🔴"
                st.metric(f"{color} Success Rate", f"{success_rate:.1f}%")
            
            with col5:
                slow_queries = metrics.get('slow_queries_percentage')
                slow_queries = slow_queries if slow_queries is not None else 0
                color = "🔴" if slow_queries > 20 else "🟡" if slow_queries > 10 else "🟢"
                st.metric(f"{color} Slow Queries", f"{slow_queries:.1f}%")
            
            # Product-specific metrics (only show if there are product searches)
            if metrics.get('avg_products_returned', 0) > 0:
                st.markdown("#### Product Search Metrics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_products = metrics.get('avg_products_returned', 0)
                    st.metric("📦 Avg Products Returned", f"{avg_products:.1f}")
                
                with col2:
                    brand_diversity = metrics.get('brand_diversity', 0)
                    color = "🟢" if brand_diversity > 0.8 else "🟡" if brand_diversity > 0.6 else "🔴"
                    st.metric(f"{color} Brand Diversity", f"{brand_diversity:.2f}")
                
                with col3:
                    price_range = metrics.get('price_range', {})
                    min_price = price_range.get('min', 0)
                    max_price = price_range.get('max', 0)
                    st.metric("💰 Price Range", f"${min_price:.0f}-${max_price:.0f}")
            
            # Article-specific metrics (only show if there are article searches)
            if metrics.get('avg_articles_returned', 0) > 0:
                st.markdown("#### Article Search Metrics")
                avg_articles = metrics.get('avg_articles_returned', 0)
                st.metric("📰 Avg Articles Returned", f"{avg_articles:.1f}")
            
            # Recommendations
            if recommendations:
                st.markdown("#### Recommendations")
                for rec in recommendations:
                    if "Critical" in rec:
                        st.error(rec)
                    elif "Warning" in rec:
                        st.warning(rec)
                    else:
                        st.info(rec)
    
    def run(self):
        """Run the dashboard"""
        # Sidebar for file upload
        st.sidebar.title("📁 Upload Evaluation Data")
        
        # Individual session analysis files
        st.sidebar.markdown("### Individual Session Analysis")
        eval_file = st.sidebar.file_uploader("Pipeline Log (JSON)", type=['json'], key="eval", help='Contains session details, query processing steps, tool calls, and performance metrics')
        llm_eval_file = st.sidebar.file_uploader("LLM Evaluation (JSON)", type=['json'], key="llm_eval", help='Contains qualitative scores (1-10) for different evaluation dimensions')
        
        # Quantitative analysis files
        st.sidebar.markdown("### Quantitative Analysis")
        quantitative_file = st.sidebar.file_uploader("Quantitative Report (JSON)", type=['json'], key="quant", help='Contains aggregated metrics and system recommendations')
        log_files = st.sidebar.file_uploader("Individual Log Files (JSON)", type=['json'], key="logs", accept_multiple_files=True, help='Upload multiple individual log files for query type analysis')
        
        # Load data
        data_loaded = False
        if eval_file or llm_eval_file or quantitative_file or log_files:
            if self.load_data(eval_file, llm_eval_file, quantitative_file):
                data_loaded = True
            
            if log_files:
                self.load_all_logs(log_files)
                data_loaded = True
            
            if data_loaded:
                st.sidebar.success("✅ Data loaded successfully!")
        
        if not data_loaded:
            st.info("Please upload evaluation data files to begin analysis")
            return
        
        # Create tabs
        tab1, tab2 = st.tabs(["📊 Individual Session Analysis", "📈 Quantitative Analysis"])
        
        with tab1:
            # Individual session analysis
            if eval_file or llm_eval_file:
                self.render_user_info()
                self.render_pipeline_flow()
                self.render_product_analysis()
                self.render_article_analysis()
                self.render_evaluation_scores()
            else:
                st.info("Upload individual session files (Pipeline Log and/or LLM Evaluation) to see detailed analysis")
        
        with tab2:
            # Quantitative analysis
            self.render_quantitative_analysis_tab()

# Run the dashboard
if __name__ == "__main__":
    dashboard = EvaluationDashboard()
    dashboard.run()