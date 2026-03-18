### Analysis Agent

# analysis_agent.py

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Specialized agent for data analysis and insights
    """
    
    def __init__(self, agent_id: str, config: Dict):
        self.agent_id = agent_id
        self.config = config
        self.capabilities = [
            'statistical_analysis',
            'trend_detection',
            'anomaly_detection',
            'correlation_analysis'
        ]
    
    async def execute(self, task: Dict) -> Dict:
        """
        Execute analysis task
        """
        action = task['action']
        parameters = task['parameters']
        
        try:
            if action == 'statistical_analysis':
                result = await self.statistical_analysis(parameters)
            elif action == 'trend_detection':
                result = await self.trend_detection(parameters)
            elif action == 'anomaly_detection':
                result = await self.anomaly_detection(parameters)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return {
                'status': 'success',
                'analysis': result,
                'metadata': {
                    'agent_id': self.agent_id,
                    'action': action,
                    'confidence': result.get('confidence', 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
    
    async def statistical_analysis(self, params: Dict) -> Dict:
        """
        Perform statistical analysis on dataset
        """
        data = params['data']
        df = pd.DataFrame(data)
        
        analysis = {
            'summary_statistics': {},
            'distributions': {},
            'insights': []
        }
        
        # Calculate summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            analysis['summary_statistics'][col] = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'q25': float(df[col].quantile(0.25)),
                'q75': float(df[col].quantile(0.75))
            }
            
            # Test for normality
            _, p_value = stats.normaltest(df[col].dropna())
            analysis['distributions'][col] = {
                'is_normal': p_value > 0.05,
                'p_value': float(p_value)
            }
        
        # Generate insights
        analysis['insights'] = self.generate_insights(analysis)
        analysis['confidence'] = 0.95
        
        return analysis
    
    async def trend_detection(self, params: Dict) -> Dict:
        """
        Detect trends in time series data
        """
        data = params['data']
        time_column = params['time_column']
        value_column = params['value_column']
        
        df = pd.DataFrame(data)
        df[time_column] = pd.to_datetime(df[time_column])
        df = df.sort_values(time_column)
        
        # Calculate trend
        x = np.arange(len(df))
        y = df[value_column].values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        trend = {
            'direction': 'increasing' if slope > 0 else 'decreasing',
            'slope': float(slope),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'confidence': float(1 - p_value)
        }
        
        return trend
    
    async def anomaly_detection(self, params: Dict) -> Dict:
        """
        Detect anomalies in dataset
        """
        data = params['data']
        column = params['column']
        method = params.get('method', 'zscore')
        
        df = pd.DataFrame(data)
        values = df[column].values
        
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(values))
            threshold = params.get('threshold', 3)
            anomalies = z_scores > threshold
        elif method == 'iqr':
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            anomalies = (values < lower_bound) | (values > upper_bound)
        
        anomaly_indices = np.where(anomalies)[0].tolist()
        
        return {
            'anomaly_count': len(anomaly_indices),
            'anomaly_indices': anomaly_indices,
            'anomaly_percentage': len(anomaly_indices) / len(values) * 100,
            'method': method,
            'confidence': 0.90
        }
    
    def generate_insights(self, analysis: Dict) -> List[str]:
        """
        Generate human-readable insights from analysis
        """
        insights = []
        
        for col, stats in analysis['summary_statistics'].items():
            if stats['std'] / stats['mean'] > 0.5:
                insights.append(
                    f"{col} shows high variability (CV > 0.5)"
                )
            
            if analysis['distributions'][col]['is_normal']:
                insights.append(
                    f"{col} follows normal distribution"
                )
        
        return insights