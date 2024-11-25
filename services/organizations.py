from typing import Dict, List, Any
from .base import AWSService

class OrganizationsService(AWSService):
    @property
    def service_name(self) -> str:
        return 'organizations'

    def audit(self) -> Dict[str, Any]:
        try:
            org_info = self.client.describe_organization()['Organization']
            roots = self.client.list_roots()['Roots']
            
            accounts = []
            paginator = self.client.get_paginator('list_accounts')
            for page in paginator.paginate():
                accounts.extend(page['Accounts'])
                
            policies = []
            policy_types = self.client.list_policies(Filter='SERVICE_CONTROL_POLICY')
            paginator = self.client.get_paginator('list_policies')
            for page in paginator.paginate(Filter='SERVICE_CONTROL_POLICY'):
                policies.extend(page['Policies'])

            return {
                'organization': {
                    'Id': org_info['Id'],
                    'Arn': org_info['Arn'],
                    'FeatureSet': org_info['FeatureSet'],
                    'MasterAccountId': org_info['MasterAccountId'],
                    'MasterAccountEmail': org_info['MasterAccountEmail'],
                    'AvailablePolicyTypes': org_info.get('AvailablePolicyTypes', [])
                },
                'accounts': accounts,
                'policies': policies,
                'roots': roots
            }
            
        except Exception as e:
            print(f"Error auditing Organizations: {str(e)}")
            return {}