from typing import Dict, List, Any
from .base import AWSService
from botocore.exceptions import ClientError

class ElasticsearchService(AWSService):
    @property
    def service_name(self) -> str:
        return 'es'  # AWS Elasticsearch service client name

    def audit(self) -> List[Dict[str, Any]]:
        resources = []
        try:
            domains = self.client.list_domain_names()['DomainNames']
            
            for domain in domains:
                domain_info = self._get_domain_details(domain['DomainName'])
                if domain_info:
                    resources.append(domain_info)
                    
            return resources
        except Exception as e:
            print(f"Error auditing Elasticsearch in {self.region}: {str(e)}")
            return []

    def _get_domain_details(self, domain_name: str) -> Dict[str, Any]:
        try:
            domain = self.client.describe_elasticsearch_domain(DomainName=domain_name)['DomainStatus']
            tags = self.client.list_tags(ARN=domain['ARN'])['TagList']
            
            return {
                'Region': self.region,
                'Domain Name': domain['DomainName'],
                'ARN': domain['ARN'],
                'Created': str(domain.get('Created', 'N/A')),
                'Deleted': str(domain.get('Deleted', 'N/A')),
                'Endpoint': domain.get('Endpoints', {}).get('vpc', 'N/A'),
                'Elasticsearch Version': domain.get('ElasticsearchVersion', 'N/A'),
                'Instance Type': domain.get('ElasticsearchClusterConfig', {}).get('InstanceType', 'N/A'),
                'Instance Count': domain.get('ElasticsearchClusterConfig', {}).get('InstanceCount', 0),
                'Dedicated Master Enabled': domain.get('ElasticsearchClusterConfig', {}).get('DedicatedMasterEnabled', False),
                'Zone Awareness Enabled': domain.get('ElasticsearchClusterConfig', {}).get('ZoneAwarenessEnabled', False),
                'Storage Type': domain.get('EBSOptions', {}).get('VolumeType', 'N/A'),
                'Storage Size': f"{domain.get('EBSOptions', {}).get('VolumeSize', 0)} GB",
                'VPC': domain.get('VPCOptions', {}).get('VPCId', 'N/A'),
                'Subnets': ', '.join(domain.get('VPCOptions', {}).get('SubnetIds', [])),
                'Security Groups': ', '.join(domain.get('VPCOptions', {}).get('SecurityGroupIds', [])),
                'Access Policies': str(domain.get('AccessPolicies', 'N/A')),
                'Automated Snapshot Start Hour': domain.get('SnapshotOptions', {}).get('AutomatedSnapshotStartHour', 'N/A'),
                'Processing': domain.get('Processing', False),
                'Upgrade Processing': domain.get('UpgradeProcessing', False),
                'Tags': ', '.join([f"{tag['Key']}={tag['Value']}" for tag in tags])
            }
        except Exception as e:
            print(f"Error processing domain {domain_name}: {str(e)}")
            return None