# services/lightsail.py
from typing import Dict, List, Any
from .base import AWSService
from botocore.exceptions import ClientError

class LightsailService(AWSService):
    @property 
    def service_name(self) -> str:
        return 'lightsail'

    def audit(self) -> List[Dict[str, Any]]:
        """Implement abstract audit method"""
        try:
            # Check if Lightsail is supported in this region
            self.client.get_regions()
            resources = []
            
            # Get instances
            instances = self._get_instances()
            resources.extend(instances)
            
            # Get databases
            databases = self._get_databases()
            resources.extend(databases)
            
            # Get containers
            containers = self._get_containers() 
            resources.extend(containers)
            
            return resources
            
        except ClientError as e:
            if 'Could not connect to the endpoint URL' in str(e):
                print(f"Lightsail is not available in region {self.region}")
            else:
                print(f"Error auditing Lightsail in {self.region}: {str(e)}")
            return []

    def _get_instances(self) -> List[Dict[str, Any]]:
        """Get Lightsail instances for the region"""
        instances = []
        try:
            paginator = self.client.get_paginator('get_instances')
            for page in paginator.paginate():
                for instance in page.get('instances', []):
                    instances.append({
                        'Region': self.region,
                        'Resource Type': 'Instance',
                        'Name': instance.get('name'),
                        'ARN': instance.get('arn'),
                        'Created': str(instance.get('createdAt')),
                        'Status': instance.get('state', {}).get('name'),
                        'Blueprint ID': instance.get('blueprintId'),
                        'Bundle ID': instance.get('bundleId'),
                        'Public IP': instance.get('publicIpAddress', 'N/A'),
                        'Private IP': instance.get('privateIpAddress', 'N/A'),
                        'Availability Zone': instance.get('location', {}).get('availabilityZone')
                    })
        except ClientError as e:
            print(f"Error getting Lightsail instances in {self.region}: {str(e)}")
        return instances

    def _get_databases(self) -> List[Dict[str, Any]]:
        databases = []
        try:
            paginator = self.client.get_paginator('get_relational_databases')
            for page in paginator.paginate():
                for db in page.get('relationalDatabases', []):
                    databases.append({
                        'Region': self.region,
                        'Resource Type': 'Database',
                        'Name': db.get('name'),
                        'ARN': db.get('arn'),
                        'Created': str(db.get('createdAt')),
                        'Status': db.get('state'),
                        'Engine': f"{db.get('engine')} {db.get('engineVersion')}",
                        'Master Username': db.get('masterUsername'),
                        'Public': db.get('publiclyAccessible'),
                        'Availability Zone': db.get('location', {}).get('availabilityZone')
                    })
        except ClientError as e:
            if 'Could not connect to the endpoint URL' in str(e):
                print(f"Note: Lightsail databases not available in region {self.region}")
            else:
                print(f"Error getting Lightsail databases in {self.region}: {str(e)}")
        return databases

    def _get_containers(self) -> List[Dict[str, Any]]:
        containers = []
        try:
            response = self.client.get_container_services()
            for container in response.get('containerServices', []):
                containers.append({
                    'Region': self.region,
                    'Resource Type': 'Container',
                    'Name': container.get('containerServiceName'),
                    'ARN': container.get('arn'),
                    'Created': str(container.get('createdAt')),
                    'Status': container.get('power'),
                    'Scale': container.get('scale'),
                    'Principal ARN': container.get('principalArn', 'N/A'),
                    'Location': container.get('location', {}).get('regionName')
                })
        except ClientError as e:
            if 'Could not connect to the endpoint URL' in str(e):
                print(f"Note: Lightsail containers not available in region {self.region}")
            else:
                print(f"Error getting Lightsail containers in {self.region}: {str(e)}")
        return containers