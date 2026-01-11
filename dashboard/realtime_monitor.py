"""
Real-time Monitoring Dashboard for TruthProbe
Provides live visualization of deception detection metrics
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List
import asyncio
import threading
import queue

class RealTimeTruthMonitor:
    """
    Real-time monitoring dashboard for deception detection
    """
    
    def __init__(self, detector):
        self.detector = detector
        self.metrics_history = []
        self.alerts = []
        self.app = dash.Dash(__name__, 
                           external_stylesheets=[dbc.themes.DARKLY],
                           title="TruthProbe Live Monitor")
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("🔍 TruthProbe Live Monitor", 
                           className="text-center mb-4"),
                    html.P("Real-time deception detection for LLM responses",
                          className="text-center text-muted")
                ])
            ]),
            
            # Alert Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🚨 Active Alerts", 
                                      className="bg-danger text-white"),
                        dbc.CardBody([
                            html.Div(id="alerts-container",
                                    children=[html.P("No active alerts", 
                                                    className="text-muted")])
                        ])
                    ], className="mb-4")
                ], width=12)
            ]),
            
            # Main Metrics
            dbc.Row([
                # Risk Score Gauge
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Overall Risk Score"),
                        dbc.CardBody([
                            dcc.Graph(id="risk-gauge", 
                                     config={'displayModeBar': False})
                        ])
                    ], className="mb-4")
                ], width=4),
                
                # Method Distribution
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Detection Method Distribution"),
                        dbc.CardBody([
                            dcc.Graph(id="method-distribution")
                        ])
                    ], className="mb-4")
                ], width=8)
            ]),
            
            # Time Series Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Score History"),
                        dbc.CardBody([
                            dcc.Graph(id="risk-history")
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Analysis Input
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Manual Analysis"),
                        dbc.CardBody([
                            dbc.Textarea(id="input-query",
                                        placeholder="Enter query...",
                                        className="mb-2",
                                        rows=2),
                            dbc.Textarea(id="input-response",
                                        placeholder="Enter LLM response...",
                                        className="mb-2",
                                        rows=4),
                            dbc.Button("Analyze Response",
                                     id="analyze-button",
                                     color="primary",
                                     className="w-100"),
                            html.Div(id="analysis-result",
                                    className="mt-3")
                        ])
                    ])
                ], width=12)
            ]),
            
            # Update Interval
            dcc.Interval(
                id="interval-component",
                interval=2000,  # Update every 2 seconds
                n_intervals=0
            ),
            
            # Data Storage
            dcc.Store(id="metrics-store"),
            dcc.Store(id="alerts-store")
        ], fluid=True)
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output("risk-gauge", "figure"),
             Output("method-distribution", "figure"),
             Output("risk-history", "figure"),
             Output("alerts-container", "children"),
             Output("analysis-result", "children")],
            [Input("interval-component", "n_intervals"),
             Input("analyze-button", "n_clicks")],
            [State("input-query", "value"),
             State("input-response", "value")]
        )
        def update_dashboard(n_intervals, n_clicks, query, response):
            """Update all dashboard components"""
            
            # Generate gauge chart
            gauge_fig = self._create_gauge_chart()
            
            # Generate method distribution chart
            dist_fig = self._create_distribution_chart()
            
            # Generate history chart
            history_fig = self._create_history_chart()
            
            # Update alerts
            alerts_display = self._get_alerts_display()
            
            # Handle manual analysis
            analysis_result = ""
            if n_clicks and query and response:
                result = self.detector.analyze_response(query, response)
                analysis_result = self._format_analysis_result(result)
            
            return gauge_fig, dist_fig, history_fig, alerts_display, analysis_result
        
    def _create_gauge_chart(self) -> go.Figure:
        """Create risk score gauge chart"""
        if not self.metrics_history:
            current_risk = 0.3
        else:
            current_risk = self.metrics_history[-1]["overall_risk"]
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current_risk * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Current Risk"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': current_risk * 100
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        return fig
    
    def _create_distribution_chart(self) -> go.Figure:
        """Create detection method distribution chart"""
        if not self.metrics_history:
            # Default data
            methods = ["Semantic", "Logical", "Factual", "Confidence"]
            scores = [0.25, 0.25, 0.25, 0.25]
        else:
            latest = self.metrics_history[-1]
            methods = list(latest["method_scores"].keys())
            scores = list(latest["method_scores"].values())
        
        fig = go.Figure(data=[
            go.Bar(x=methods, y=scores, marker_color=['#636EFA', '#EF553B', '#00CC96', '#AB63FA'])
        ])
        
        fig.update_layout(
            title="Detection Method Contributions",
            yaxis_title="Score",
            yaxis_range=[0, 1],
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig
    
    def _create_history_chart(self) -> go.Figure:
        """Create risk score history chart"""
        if not self.metrics_history:
            # Create sample data
            times = [datetime.now() - timedelta(minutes=i) for i in range(10, -1, -1)]
            risks = np.random.uniform(0.1, 0.8, 11)
        else:
            times = [m["timestamp"] for m in self.metrics_history[-50:]]
            risks = [m["overall_risk"] for m in self.metrics_history[-50:]]
        
        fig = go.Figure()
        
        # Risk line
        fig.add_trace(go.Scatter(
            x=times,
            y=risks,
            mode='lines+markers',
            name='Risk Score',
            line=dict(color='red', width=2),
            marker=dict(size=6)
        ))
        
        # Threshold areas
        fig.add_hrect(y0=0.7, y1=1.0, 
                     line_width=0, fillcolor="red", opacity=0.2,
                     annotation_text="High Risk", annotation_position="top left")
        fig.add_hrect(y0=0.4, y1=0.7, 
                     line_width=0, fillcolor="yellow", opacity=0.2,
                     annotation_text="Moderate Risk")
        
        fig.update_layout(
            title="Risk Score History (Last 50 Analyses)",
            xaxis_title="Time",
            yaxis_title="Risk Score",
            yaxis_range=[0, 1],
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig
    
    def _get_alerts_display(self):
        """Get formatted alerts display"""
        if not self.alerts:
            return [html.P("No active alerts", className="text-muted")]
        
        alert_items = []
        for alert in self.alerts[-5:]:  # Last 5 alerts
            alert_type = "danger" if alert["level"] == "high" else "warning"
            alert_items.append(
                dbc.Alert([
                    html.Strong(f"{alert['timestamp'].strftime('%H:%M:%S')}: "),
                    alert["message"]
                ], color=alert_type, className="mb-2")
            )
        
        return alert_items
    
    def _format_analysis_result(self, result: Dict) -> html.Div:
        """Format analysis result for display"""
        return html.Div([
            html.H5("Analysis Result", className="mt-3"),
            dbc.Badge(f"Risk Score: {result['overall_risk_score']:.3f}", 
                     color="danger" if result['overall_risk_score'] > 0.7 
                     else "warning" if result['overall_risk_score'] > 0.4 
                     else "success",
                     className="mb-2"),
            html.P(result['verdict'], className="lead"),
            html.Hr(),
            html.H6("Detailed Findings:"),
            html.Ul([
                html.Li(f"{det.method.value}: {det.score:.3f} - {det.explanation}")
                for det in result["detections"]
            ])
        ])
    
    def add_metric(self, analysis_result: Dict):
        """Add new metric to history"""
        timestamp = datetime.now()
        
        metric = {
            "timestamp": timestamp,
            "overall_risk": analysis_result["overall_risk_score"],
            "method_scores": {det.method.value: det.score 
                            for det in analysis_result["detections"]},
            "query": analysis_result["query"],
            "verdict": analysis_result["verdict"]
        }
        
        self.metrics_history.append(metric)
        
        # Check for alerts
        if analysis_result["overall_risk_score"] > 0.7:
            self.alerts.append({
                "timestamp": timestamp,
                "level": "high",
                "message": f"High risk detected: {analysis_result['query'][:50]}..."
            })
        elif analysis_result["overall_risk_score"] > 0.4:
            self.alerts.append({
                "timestamp": timestamp,
                "level": "medium",
                "message": f"Moderate risk: {analysis_result['query'][:50]}..."
            })
        
        # Keep history manageable
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-500:]
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-50:]
    
    def run(self, host="0.0.0.0", port=8050):
        """Start the dashboard server"""
        print(f"🚀 Starting TruthProbe Dashboard at http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=False)

# Example usage integration
if __name__ == "__main__":
    # Initialize enhanced detector
    detector = EnhancedTruthDetector()
    
    # Create and run dashboard
    monitor = RealTimeTruthMonitor(detector)
    
    # Simulate some metrics for demo
    import threading
    import time
    
    def simulate_metrics():
        """Simulate incoming metrics for demo"""
        while True:
            time.sleep(3)
            mock_result = {
                "overall_risk_score": np.random.uniform(0.1, 0.9),
                "detections": [],
                "query": f"Sample query {len(monitor.metrics_history)}",
                "verdict": "Testing"
            }
            monitor.add_metric(mock_result)
    
    # Start simulation in background
    sim_thread = threading.Thread(target=simulate_metrics, daemon=True)
    sim_thread.start()
    
    # Run dashboard
    monitor.run()
