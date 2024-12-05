#!/usr/bin/env python3
import argparse
import boto3
import os
import xlsxwriter
from core.auditor import AWSAuditor
from core.report import ReportGenerator
from config.settings import AVAILABLE_SERVICES, DEFAULT_MAX_WORKERS

def valid_regions(session: boto3.Session) -> list:
    ec2 = session.client('ec2')
    available_regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]
    return available_regions

def parse_arguments(regions: list):
    parser = argparse.ArgumentParser(description='AWS Resource Audit Tool')
    parser.add_argument('--regions', choices=regions, nargs='+', type=str,
                       help='Comma-separated list of regions or "all"',
                       default='all')
    parser.add_argument('--services', type=str, 
                       help=f'Comma-separated list of services {AVAILABLE_SERVICES}',
                       default='all')
    parser.add_argument('--output-dir', type=str,
                       help='Directory for output files',
                       default='results')
    return parser.parse_args()

def main():
    session = boto3.Session()
    regions = valid_regions(session)
    args = parse_arguments(regions)
    
    try:
        services = args.services.lower().split(',') if args.services != 'all' else AVAILABLE_SERVICES
        
        auditor = AWSAuditor(session, regions, services)
        results = auditor.run_audit(max_workers=DEFAULT_MAX_WORKERS)
        
        os.makedirs(args.output_dir, exist_ok=True)
        report_generator = ReportGenerator(results, args.output_dir)
        report_generator.generate_reports()
        
    except Exception as e:
        print(f"Error during audit: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())