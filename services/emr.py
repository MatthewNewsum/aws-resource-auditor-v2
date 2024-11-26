from typing import Dict, List, Any
from .base import AWSService
from botocore.exceptions import ClientError

class EMRService(AWSService):
    @property
    def service_name(self) -> str:
        return 'emr'

    def audit(self) -> List[Dict[str, Any]]:
        try:
            clusters = []
            paginator = self.client.get_paginator('list_clusters')
            for page in paginator.paginate():
                for cluster in page['Clusters']:
                    cluster_detail = self._get_cluster_details(cluster['Id'])
                    if cluster_detail:
                        clusters.append(cluster_detail)
            return clusters
        except ClientError as e:
            print(f"Error auditing EMR in {self.region}: {str(e)}")
            return []

    def _get_cluster_details(self, cluster_id: str) -> Dict[str, Any]:
        try:
            cluster = self.client.describe_cluster(ClusterId=cluster_id)['Cluster']
            instances = self.client.list_instances(ClusterId=cluster_id)['Instances']
            steps = self.client.list_steps(ClusterId=cluster_id)['Steps']

            return {
                'Region': self.region,
                'Cluster ID': cluster['Id'],
                'Name': cluster['Name'],
                'State': cluster['Status']['State'],
                'State Change Reason': cluster['Status'].get('StateChangeReason', {}).get('Message', 'N/A'),
                'Creation Time': str(cluster.get('Status', {}).get('Timeline', {}).get('CreationDateTime', 'N/A')),
                'End Time': str(cluster.get('Status', {}).get('Timeline', {}).get('EndDateTime', 'N/A')),
                'Applications': [app['Name'] + ' ' + app['Version'] for app in cluster.get('Applications', [])],
                'Instance Count': len(instances),
                'Master Type': cluster.get('InstanceGroups', [{}])[0].get('InstanceType', 'N/A'),
                'Core Type': cluster.get('InstanceGroups', [{}, {}])[1].get('InstanceType', 'N/A') if len(cluster.get('InstanceGroups', [])) > 1 else 'N/A',
                'Step Count': len(steps),
                'Auto Terminate': cluster.get('AutoTerminate', False),
                'Termination Protected': cluster.get('TerminationProtected', False),
                'Release Label': cluster.get('ReleaseLabel', 'N/A'),
                'VPC ID': cluster.get('Ec2InstanceAttributes', {}).get('Vpc', 'N/A'),
                'Subnet ID': cluster.get('Ec2InstanceAttributes', {}).get('Ec2SubnetId', 'N/A'),
                'Security Groups': ', '.join(cluster.get('Ec2InstanceAttributes', {}).get('EmrManagedMasterSecurityGroup', [])),
                'Service Role': cluster.get('ServiceRole', 'N/A'),
                'Tags': str(cluster.get('Tags', {}))
            }
        except ClientError:
            return None