from typing import Dict, List, Any
from .base import AWSService
from botocore.exceptions import ClientError

class LightsailService(AWSService):
    @property
    def service_name(self) -> str:
        return 'lightsail'

    def audit(self) -> List[Dict[str, Any]]:
        resources = []
        try:
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
        except Exception as e:
            print(f"Error auditing Lightsail in {self.region}: {str(e)}")
            return []

    def _get_instances(self) -> List[Dict[str, Any]]:
        instances = []
        try:
            paginator = self.client.get_paginator('get_instances')
            for page in paginator.paginate():
                for instance in page['instances']:
                    instances.append({
                        'Region': self.region,
                        'Resource Type': 'Instance',
                        'Name': instance['name'],
                        'ARN': instance['arn'],
                        'Created': str(instance['createdAt']),
                        'Status': instance['state']['name'],
                        'Blueprint ID': instance['blueprintId'],
                        'Bundle ID': instance['bundleId'],
                        'Public IP': instance.get('publicIpAddress', 'N/A'),
                        'Private IP': instance.get('privateIpAddress', 'N/A'),
                        'Availability Zone': instance['location']['availabilityZone']
                    })
        except Exception as e:
            print(f"Error getting Lightsail instances: {str(e)}")
        return instances

    def _get_databases(self) -> List[Dict[str, Any]]:
        databases = []
        try:
            paginator = self.client.get_paginator('get_relational_databases')
            for page in paginator.paginate():
                for db in page['relationalDatabases']:
                    databases.append({
                        'Region': self.region,
                        'Resource Type': 'Database',
                        'Name': db['name'],
                        'ARN': db['arn'],
                        'Created': str(db['createdAt']),
                        'Status': db['state'],
                        'Engine': f"{db['engine']} {db['engineVersion']}",
                        'Master Username': db['masterUsername'],
                        'Public': db['publiclyAccessible'],
                        'Availability Zone': db['location']['availabilityZone']
                    })
        except Exception as e:
            print(f"Error getting Lightsail databases: {str(e)}")
        return databases

    def _get_containers(self) -> List[Dict[str, Any]]:
        containers = []
        try:
            paginator = self.client.get_paginator('get_container_services')
            for page in paginator.paginate():
                for container in page['containerServices']:
                    containers.append({
                        'Region': self.region,
                        'Resource Type': 'Container',
                        'Name': container['containerServiceName'],
                        'ARN': container['arn'],
                        'Created': str(container['createdAt']),
                        'Status': container['state'],
                        'Power': container['power'],
                        'Scale': container['scale'],
                        'Principal ARN': container['principalArn'],
                        'Availability Zone': container['location']['availabilityZone']
                    })
        except Exception as e:
            print(f"Error getting Lightsail containers: {str(e)}")
        return containers