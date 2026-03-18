## Specialist Agent Examples

### Data Extraction Agent

# data_extraction_agent.py

import requests
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DataExtractionAgent:
    """
    Specialized agent for extracting data from various sources
    """
    
    def __init__(self, agent_id: str, config: Dict):
        self.agent_id = agent_id
        self.config = config
        self.capabilities = [
            'fetch_api_data',
            'query_database',
            'read_csv_file',
            'parse_json'
        ]
    
    async def execute(self, task: Dict) -> Dict:
        """
        Execute data extraction task
        """
        action = task['action']
        parameters = task['parameters']
        
        try:
            if action == 'fetch_api_data':
                result = await self.fetch_api_data(parameters)
            elif action == 'query_database':
                result = await self.query_database(parameters)
            elif action == 'read_csv_file':
                result = await self.read_csv_file(parameters)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return {
                'status': 'success',
                'data': result,
                'metadata': {
                    'agent_id': self.agent_id,
                    'action': action,
                    'record_count': len(result) if isinstance(result, list) else 1
                }
            }
            
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            raise
    
    async def fetch_api_data(self, params: Dict) -> List[Dict]:
        """
        Fetch data from REST API
        """
        url = params['url']
        headers = params.get('headers', {})
        query_params = params.get('query_params', {})
        
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        
        data = response.json()
        
        # Transform if needed
        if 'transform' in params:
            data = self.transform_data(data, params['transform'])
        
        return data
    
    async def query_database(self, params: Dict) -> List[Dict]:
        """
        Query database and return results
        """
        # Implementation depends on database type
        # This is a simplified example
        query = params['query']
        connection_string = params['connection_string']
        
        # Execute query (pseudo-code)
        # results = db.execute(query)
        
        return []  # Return actual results
    
    async def read_csv_file(self, params: Dict) -> List[Dict]:
        """
        Read CSV file and return as list of dicts
        """
        file_path = params['file_path']
        
        df = pd.read_csv(file_path)
        
        # Apply filters if specified
        if 'filters' in params:
            for column, value in params['filters'].items():
                df = df[df[column] == value]
        
        return df.to_dict('records')
    
    def transform_data(self, data: Any, transform_spec: Dict) -> Any:
        """
        Transform data according to specification
        """
        # Implement transformations
        if transform_spec['type'] == 'filter':
            return [item for item in data if self.matches_filter(item, transform_spec)]
        elif transform_spec['type'] == 'map':
            return [self.map_item(item, transform_spec) for item in data]
        
        return data