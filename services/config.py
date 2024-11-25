from typing import Dict, List, Any
from .base import AWSService

class ConfigService(AWSService):
    @property
    def service_name(self) -> str:
        return 'config'

    def audit(self) -> List[Dict[str, Any]]:
        resources = []
        
        try:
            # Get recorders
            recorders = self.client.describe_configuration_recorders()
            recorder_statuses = self.client.describe_configuration_recorder_status()['ConfigurationRecordersStatus'] if recorders['ConfigurationRecorders'] else []
            
            # Get rules
            rules = []
            paginator = self.client.get_paginator('describe_config_rules')
            for page in paginator.paginate():
                rules.extend(page['ConfigRules'])
            
            # Get aggregators
            aggregators = self.client.describe_configuration_aggregators()['ConfigurationAggregators']
            
            resources.append({
                'Region': self.region,
                'Recorders': len(recorders['ConfigurationRecorders']),
                'Recorders Active': len([s for s in recorder_statuses if s['recording']]),
                'Rules': len(rules),
                'Rules Active': len([r for r in rules if r['ConfigRuleState'] == 'ACTIVE']),
                'Aggregators': len(aggregators),
                'Recorder Details': recorders['ConfigurationRecorders'],
                'Rule Details': rules,
                'Aggregator Details': aggregators
            })
            
        except Exception as e:
            print(f"Error auditing Config in {self.region}: {str(e)}")
            
        return resources