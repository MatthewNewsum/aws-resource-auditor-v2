# service_collectors.py
from typing import List, Dict, Any
import boto3
import logging

class LightsailCollector:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
    def collect_resources(self, client) -> List[Dict[str, Any]]:
        """Collect Lightsail resources with proper pagination handling"""
        resources = []
        
        try:
            # Get instances (paginated)
            paginator = client.get_paginator('get_instances')
            for page in paginator.paginate():
                resources.extend(page.get('instances', []))
                
            # Get container services (non-paginated)
            try:
                container_response = client.get_container_services()
                resources.extend(container_response.get('containerServices', []))
            except client.exceptions.ClientError as e:
                self.logger.warning(f"Error getting Lightsail container services: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error collecting Lightsail resources: {str(e)}")
            
        return resources