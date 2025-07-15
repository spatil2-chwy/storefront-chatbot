import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

# Import data parser
from data_parser import EvaluationDataParser

# Initialize the Dash app
app = dash.Dash(__name__, title="LLM Evaluation Dashboard")
app.config.suppress_callback_exceptions = True

# Initialize data parser
data_parser = EvaluationDataParser()

# Sample data files (hardcoded for now)
SAMPLE_FILES = {
    "eval": "../../logs/logs/eval_20250715_151449_Lucy dev.json",
    "llm_eval": "../../logs/llm_evaluations/llm_eval_eval_20250715_151449_Lucy dev.json", 
    "quantitative": "../../logs/quantitative_reports/quantitative_report_20250715_151651.json"
}

# Load data
try:
    eval_data = data_parser.load_eval_data(SAMPLE_FILES["eval"])
    llm_eval_data = data_parser.load_llm_eval_data(SAMPLE_FILES["llm_eval"])
    quantitative_data = data_parser.load_quantitative_data(SAMPLE_FILES["quantitative"])
    print("✅ Data loaded successfully!")
    print(f"Eval data keys: {list(eval_data.keys()) if eval_data else 'None'}")
    print(f"LLM eval data keys: {list(llm_eval_data.keys()) if llm_eval_data else 'None'}")
    print(f"Quantitative data keys: {list(quantitative_data.keys()) if quantitative_data else 'None'}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    eval_data = {}
    llm_eval_data = {}
    quantitative_data = {}

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🔍 LLM Product Recommendation Pipeline Dashboard", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
        html.Hr()
    ]),
    
    # Navigation tabs
    dcc.Tabs([
        # Tab 1: Session Overview
        dcc.Tab(label="📊 Session Overview", children=[
            html.Div([
                html.H2("Session Details", style={'color': '#34495e'}),
                html.Div(id='session-overview-content')
            ], style={'padding': '20px'})
        ]),
        
        # Tab 2: Query-to-Response Flow
        dcc.Tab(label="🔄 Query Flow", children=[
            html.Div([
                html.H2("Query Processing Pipeline", style={'color': '#34495e'}),
                html.Div(id='query-flow-content')
            ], style={'padding': '20px'})
        ]),
        
        # Tab 3: Product Results
        dcc.Tab(label="🛍️ Product Results", children=[
            html.Div([
                html.H2("Product Retrieval Analysis", style={'color': '#34495e'}),
                html.Div(id='product-results-content')
            ], style={'padding': '20px'})
        ]),
        
        # Tab 4: Evaluation Scores
        dcc.Tab(label="📈 Evaluation Metrics", children=[
            html.Div([
                html.H2("LLM Evaluation Analysis", style={'color': '#34495e'}),
                html.Div(id='evaluation-scores-content')
            ], style={'padding': '20px'})
        ]),
        
        # Tab 5: System Performance
        dcc.Tab(label="⚡ System Metrics", children=[
            html.Div([
                html.H2("Performance & Analytics", style={'color': '#34495e'}),
                html.Div(id='system-metrics-content')
            ], style={'padding': '20px'})
        ])
    ], style={'marginTop': '20px'})
])

# Callback for Session Overview
@app.callback(
    Output('session-overview-content', 'children'),
    Input('session-overview-content', 'children')
)
def update_session_overview(children):
    if not eval_data:
        return html.Div([
            html.H3("❌ No Session Data Available", style={'color': '#e74c3c'}),
            html.P("Please check that the evaluation data files are properly loaded.")
        ])
    
    try:
        # Extract session info
        session_id = eval_data.get('session_id', 'N/A')
        timestamp = eval_data.get('timestamp', 'N/A')
        raw_query = eval_data.get('raw_user_query', 'N/A')
        
        # Parse user context for pet info
        user_context = eval_data.get('user_context', '')
        pets_info = data_parser.extract_pets_info(user_context)
        
        # Get tool calls
        tool_calls = eval_data.get('tool_calls', [])
        
        return html.Div([
            # Session metadata
            html.Div([
                html.H3("Session Information", style={'color': '#2980b9'}),
                html.Div([
                    html.P(f"📅 Timestamp: {timestamp}"),
                    html.P(f"🆔 Session ID: {session_id}"),
                    html.P(f"⏱️ Processing Time: {eval_data.get('total_processing_time', 0):.2f}s")
                ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
            ]),
            
            html.Br(),
            
            # User query
            html.Div([
                html.H3("User Query", style={'color': '#2980b9'}),
                html.Div([
                    html.P(f"💬 {raw_query}", style={'fontSize': '18px', 'fontWeight': 'bold'})
                ], style={'backgroundColor': '#e8f5e8', 'padding': '15px', 'borderRadius': '5px'})
            ]),
            
            html.Br(),
            
            # Pet information
            html.Div([
                html.H3("Pet Information", style={'color': '#2980b9'}),
                html.Div([
                    html.Div([
                        html.H4(f"🐕 {pet['name']} ({pet['breed']})", style={'color': '#27ae60'}),
                        html.P(f"Age: {pet['age']} | Size: {pet['size']} | Weight: {pet['weight']}lbs")
                    ], style={'marginBottom': '10px', 'padding': '10px', 'backgroundColor': '#f0f8ff', 'borderRadius': '5px'})
                    for pet in pets_info
                ])
            ]),
            
            html.Br(),
            
            # Tool usage
            html.Div([
                html.H3("Tools Used", style={'color': '#2980b9'}),
                html.Div([
                    html.Div([
                        html.H4(f"🔧 {tool['tool_name']}", style={'color': '#e67e22'}),
                        html.Pre(json.dumps(tool['arguments'], indent=2), 
                                style={'backgroundColor': '#f5f5f5', 'padding': '10px', 'borderRadius': '5px', 'overflow': 'auto'})
                    ], style={'marginBottom': '15px'})
                    for tool in tool_calls
                ])
            ])
        ])
    except Exception as e:
        return html.Div([
            html.H3("❌ Error Loading Session Data", style={'color': '#e74c3c'}),
            html.P(f"Error: {str(e)}")
        ])

# Callback for Query Flow
@app.callback(
    Output('query-flow-content', 'children'),
    Input('query-flow-content', 'children')
)
def update_query_flow(children):
    if not eval_data:
        return html.Div([
            html.H3("❌ No Query Flow Data Available", style={'color': '#e74c3c'}),
            html.P("Please check that the evaluation data files are properly loaded.")
        ])
    
    try:
        chat_history = eval_data.get('chat_history', [])
        
        return html.Div([
            html.H3("Query Processing Steps", style={'color': '#2980b9'}),
            
            # Chat history visualization
            html.Div([
                html.Div([
                    html.Div([
                        html.H4(f"Step {i+1}: {msg.get('role', 'unknown').title()}", 
                               style={'color': '#e74c3c' if msg.get('role') == 'user' else '#27ae60'}),
                        html.Div([
                            html.Pre(msg.get('content', '')[:500] + ('...' if len(msg.get('content', '')) > 500 else ''), 
                                    style={'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '5px', 'overflow': 'auto'})
                        ]),
                        
                        # Show function calls if present
                        html.Div([
                            html.H5("🔧 Function Call:", style={'color': '#f39c12'}),
                            html.Pre(json.dumps(msg.get('arguments', {}), indent=2),
                                    style={'backgroundColor': '#fff3cd', 'padding': '10px', 'borderRadius': '5px', 'overflow': 'auto'})
                        ]) if msg.get('type') == 'function_call' else None,
                        
                        # Show function outputs if present
                        html.Div([
                            html.H5("📤 Function Output:", style={'color': '#17a2b8'}),
                            html.Pre(msg.get('output', ''),
                                    style={'backgroundColor': '#d1ecf1', 'padding': '10px', 'borderRadius': '5px', 'overflow': 'auto'})
                        ]) if msg.get('type') == 'function_call_output' else None
                    ], style={'marginBottom': '20px', 'padding': '15px', 'border': '1px solid #dee2e6', 'borderRadius': '8px'})
                    for i, msg in enumerate(chat_history)
                ])
            ]),
            
            # Performance metrics
            html.Div([
                html.H3("Performance Breakdown", style={'color': '#2980b9', 'marginTop': '30px'}),
                html.Div([
                    html.Div([
                        html.H4("⏱️ Timing Analysis"),
                        html.P(f"Total Processing: {eval_data.get('total_processing_time', 0):.2f}s"),
                        html.P(f"Function Call: {eval_data.get('function_call_time', 0):.2f}s"),
                        html.P(f"Tool Execution: {eval_data.get('tool_execution_time', 0):.2f}s"),
                        html.P(f"Product Search: {eval_data.get('product_search_time', 0):.2f}s"),
                        html.P(f"LLM Response: {eval_data.get('llm_response_time', 0):.2f}s")
                    ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px'})
                ])
            ])
        ])
    except Exception as e:
        return html.Div([
            html.H3("❌ Error Loading Query Flow Data", style={'color': '#e74c3c'}),
            html.P(f"Error: {str(e)}")
        ])

# Callback for Product Results
@app.callback(
    Output('product-results-content', 'children'),
    Input('product-results-content', 'children')
)
def update_product_results(children):
    if not eval_data:
        return html.Div([
            html.H3("❌ No Product Results Data Available", style={'color': '#e74c3c'}),
            html.P("Please check that the evaluation data files are properly loaded.")
        ])
    
    try:
        products = eval_data.get('product_results', [])
        if not products:
            return html.Div([
                html.H3("❌ No Products Returned", style={'color': '#e74c3c'}),
                html.P("No products were found in the evaluation data.")
            ])
        
        # Create DataFrame for analysis
        df = pd.DataFrame(products)
        
        # Product table
        product_table = dash_table.DataTable(
            id='product-table',
            columns=[
                {"name": "Rank", "id": "rank"},
                {"name": "Product", "id": "title"},
                {"name": "Brand", "id": "brand"},
                {"name": "Price ($)", "id": "price", "type": "numeric", "format": {"specifier": ".2f"}},
                {"name": "Rating", "id": "rating", "type": "numeric", "format": {"specifier": ".2f"}}
            ],
            data=df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#2980b9', 'color': 'white', 'fontWeight': 'bold'},
            page_size=10
        )
        
        # Create visualizations
        fig_price = px.histogram(df, x='price', nbins=10, title='Price Distribution',
                                labels={'price': 'Price ($)', 'count': 'Number of Products'})
        fig_price.update_layout(showlegend=False)
        
        brand_counts = df.groupby('brand').size().reset_index()
        brand_counts.columns = ['brand', 'count']
        fig_brand = px.bar(brand_counts, x='brand', y='count', title='Products by Brand')
        fig_brand.update_layout(xaxis_tickangle=-45)
        
        fig_rating = px.histogram(df, x='rating', nbins=10, title='Rating Distribution',
                                 labels={'rating': 'Rating', 'count': 'Number of Products'})
        fig_rating.update_layout(showlegend=False)
        
        return html.Div([
            html.H3("Product Analysis", style={'color': '#2980b9'}),
            
            # Summary stats
            html.Div([
                html.Div([
                    html.H4("📊 Summary Statistics"),
                    html.P(f"Total Products: {len(products)}"),
                    html.P(f"Average Price: ${df['price'].mean():.2f}"),
                    html.P(f"Average Rating: {df['rating'].mean():.2f}"),
                    html.P(f"Price Range: ${df['price'].min():.2f} - ${df['price'].max():.2f}"),
                    html.P(f"Brands: {df['brand'].nunique()}")
                ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'})
            ]),
            
            # Product table
            html.Div([
                html.H4("Product List"),
                product_table
            ], style={'marginBottom': '30px'}),
            
            # Charts
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_price)
                ], style={'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(figure=fig_brand)
                ], style={'width': '50%', 'display': 'inline-block'})
            ]),
            
            html.Div([
                dcc.Graph(figure=fig_rating)
            ], style={'width': '100%'})
        ])
    except Exception as e:
        return html.Div([
            html.H3("❌ Error Loading Product Results", style={'color': '#e74c3c'}),
            html.P(f"Error: {str(e)}")
        ])

# Callback for Evaluation Scores
@app.callback(
    Output('evaluation-scores-content', 'children'),
    Input('evaluation-scores-content', 'children')
)
def update_evaluation_scores(children):
    if not llm_eval_data:
        return html.Div([
            html.H3("❌ No Evaluation Data Available", style={'color': '#e74c3c'}),
            html.P("Please check that the LLM evaluation data files are properly loaded.")
        ])
    
    try:
        # Extract scores
        scores = {
            'Query Understanding': llm_eval_data.get('query_understanding_score', 0),
            'Tool Selection': llm_eval_data.get('tool_selection_accuracy', 0),
            'Search Relevance': llm_eval_data.get('search_relevance_score', 0),
            'Query Enhancement': llm_eval_data.get('query_enhancement_quality', 0),
            'Product Relevance': llm_eval_data.get('product_relevance_score', 0),
            'Product Diversity': llm_eval_data.get('product_diversity_score', 0),
            'Brand Alignment': llm_eval_data.get('brand_preference_alignment', 0),
            'Response Helpfulness': llm_eval_data.get('response_helpfulness', 0),
            'Follow-up Quality': llm_eval_data.get('follow_up_question_quality', 0)
        }
        
        # Create radar chart
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself',
            name='Evaluation Scores',
            line_color='#2980b9'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False,
            title="Evaluation Scores Radar Chart"
        )
        
        # Create bar chart
        fig_bar = px.bar(x=list(scores.keys()), y=list(scores.values()), 
                        title="Evaluation Scores by Category")
        fig_bar.update_layout(xaxis_tickangle=-45, yaxis_range=[0, 10])
        
        # Extract analysis
        overall_score = llm_eval_data.get('overall_score', 0)
        overall_assessment = llm_eval_data.get('overall_assessment', 'No assessment available')
        bottlenecks = llm_eval_data.get('bottlenecks_identified', [])
        suggestions = llm_eval_data.get('optimization_suggestions', [])
        strengths = llm_eval_data.get('strengths', [])
        
        return html.Div([
            html.H3("LLM Evaluation Analysis", style={'color': '#2980b9'}),
            
            # Overall score
            html.Div([
                html.H4(f"Overall Score: {overall_score}/10", style={'color': '#27ae60' if overall_score >= 7 else '#e74c3c'}),
                html.P(overall_assessment, style={'fontStyle': 'italic'})
            ], style={'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'}),
            
            # Charts
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_radar)
                ], style={'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Graph(figure=fig_bar)
                ], style={'width': '50%', 'display': 'inline-block'})
            ]),
            
            # Analysis sections
            html.Div([
                html.Div([
                    html.H4("✅ Strengths", style={'color': '#27ae60'}),
                    html.Ul([html.Li(strength) for strength in strengths])
                ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
                
                html.Div([
                    html.H4("⚠️ Bottlenecks", style={'color': '#e74c3c'}),
                    html.Ul([html.Li(bottleneck) for bottleneck in bottlenecks])
                ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
                
                html.Div([
                    html.H4("💡 Suggestions", style={'color': '#f39c12'}),
                    html.Ul([html.Li(suggestion) for suggestion in suggestions])
                ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'})
            ])
        ])
    except Exception as e:
        return html.Div([
            html.H3("❌ Error Loading Evaluation Data", style={'color': '#e74c3c'}),
            html.P(f"Error: {str(e)}")
        ])

# Callback for System Metrics
@app.callback(
    Output('system-metrics-content', 'children'),
    Input('system-metrics-content', 'children')
)
def update_system_metrics(children):
    if not quantitative_data:
        return html.Div([
            html.H3("❌ No System Metrics Data Available", style={'color': '#e74c3c'}),
            html.P("Please check that the quantitative data files are properly loaded.")
        ])
    
    try:
        metrics = quantitative_data.get('metrics', {})
        recommendations = quantitative_data.get('recommendations', [])
        
        # Create KPI cards
        kpi_cards = html.Div([
            html.Div([
                html.H3(f"{metrics.get('avg_total_processing_time', 0):.2f}s", style={'color': '#e74c3c' if metrics.get('avg_total_processing_time', 0) > 15 else '#27ae60'}),
                html.P("Avg Processing Time")
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f"{metrics.get('success_rate', 0):.1f}%", style={'color': '#27ae60'}),
                html.P("Success Rate")
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f"{metrics.get('avg_products_returned', 0)}", style={'color': '#2980b9'}),
                html.P("Avg Products Returned")
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px', 'flex': '1'}),
            
            html.Div([
                html.H3(f"${metrics.get('avg_product_price', 0):.2f}", style={'color': '#f39c12'}),
                html.P("Avg Product Price")
            ], style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px', 'flex': '1'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'})
        
        # Tool usage pie chart
        tool_usage = metrics.get('tool_usage_distribution', {})
        if tool_usage:
            fig_tools = px.pie(values=list(tool_usage.values()), names=list(tool_usage.keys()), 
                              title="Tool Usage Distribution")
        else:
            fig_tools = go.Figure()
            fig_tools.add_annotation(text="No tool usage data available", x=0.5, y=0.5, showarrow=False)
        
        # Performance warnings
        warnings_html = html.Div([
            html.H4("🚨 Performance Warnings", style={'color': '#e74c3c'}),
            html.Ul([html.Li(rec) for rec in recommendations])
        ]) if recommendations else html.Div()
        
        return html.Div([
            html.H3("System Performance Metrics", style={'color': '#2980b9'}),
            
            kpi_cards,
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=fig_tools)
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    html.H4("📊 Detailed Metrics"),
                    html.P(f"Avg Product Search Time: {metrics.get('avg_product_search_time', 0):.2f}s"),
                    html.P(f"Avg LLM Response Time: {metrics.get('avg_llm_response_time', 0):.2f}s"),
                    html.P(f"Avg Product Rating: {metrics.get('avg_product_rating', 0):.2f}"),
                    html.P(f"Brand Diversity: {metrics.get('brand_diversity', 0):.2f}"),
                    html.P(f"Queries with Context: {metrics.get('queries_with_context', 0):.1f}%"),
                    html.P(f"Slow Queries (>10s): {metrics.get('slow_queries_percentage', 0):.1f}%")
                ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px'})
            ]),
            
            warnings_html
        ])
    except Exception as e:
        return html.Div([
            html.H3("❌ Error Loading System Metrics", style={'color': '#e74c3c'}),
            html.P(f"Error: {str(e)}")
        ])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050) 