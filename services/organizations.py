from typing import Dict, List, Any
from .base import AWSService
from botocore.exceptions import ClientError

class OrganizationsService(AWSService):
    @property
    def service_name(self) -> str:
        return 'organizations'

    def audit(self) -> Dict[str, Any]:
        try:
            org_info = self.client.describe_organization()
            # If we get here, organization exists
            return self._audit_organization()
        except ClientError as e:
            if 'AWSOrganizationsNotInUseException' in str(e):
                return {
                    'organization': None,
                    'accounts': [{
                        'Id': 'ROOT',
                        'Name': 'Root Account',
                        'Status': 'ACTIVE',
                        'Type': 'ROOT',
                        'Message': 'AWS Organizations not in use'
                    }],
                    'policies': [],
                    'roots': []
                }
            print(f"Error accessing Organizations: {str(e)}")
            return {}

    def _audit_organization(self) -> Dict[str, Any]:
        org_info = self.client.describe_organization()['Organization']
        roots = self.client.list_roots()['Roots']
        
        accounts = []
        paginator = self.client.get_paginator('list_accounts')
        for page in paginator.paginate():
            accounts.extend(page['Accounts'])
            
        policies = []
        try:
            paginator = self.client.get_paginator('list_policies')
            for page in paginator.paginate(Filter='SERVICE_CONTROL_POLICY'):
                policies.extend(page['Policies'])
        except ClientError:
            pass  # Policies might not be enabled

        return {
            'organization': org_info,
            'accounts': accounts,
            'policies': policies,
            'roots': roots
        }