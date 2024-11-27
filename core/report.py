import pandas as pd
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
import json
import os
import xlsxwriter
import logging
from pathlib import Path

class ReportGenerator:
    def __init__(self, results: Dict[str, Any], output_dir: str):
        self.results = results if results else {'regions': {}, 'global_services': {}}
        self.output_dir = output_dir
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.errors = []
        
        # Define services once
        self.services = {
            'EC2': 'ec2',
            'RDS': 'rds', 
            'VPC': 'vpc',
            'Lambda': 'lambda',
            'DynamoDB': 'dynamodb',
            'Bedrock': 'bedrock',
            'Elasticsearch': 'elasticsearch',
            'Lightsail': 'lightsail'
        }
        
        # Setup logging first
        self._setup_logging()
        self.logger.info("Report generator initialized")

    def _setup_logging(self):
        """Configure logging to both file and console"""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers = []
        
        # Create logs directory
        log_dir = Path(self.output_dir) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        log_file = log_dir / f'audit_log_{self.timestamp}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _log_error(self, error_msg: str, error: Exception):
        """Log error and store for summary"""
        full_error = f"{error_msg}: {str(error)}"
        self.logger.error(full_error)
        self.errors.append(full_error)

    def _print_error_summary(self):
        """Print summary of all errors encountered"""
        if self.errors:
            self.logger.error("\n=== Error Summary ===")
            for i, error in enumerate(self.errors, 1):
                self.logger.error(f"{i}. {error}")
            self.logger.error("==================\n")

    def _convert_datetimes(self, data: List[Dict]) -> List[Dict]:
        """Convert timezone-aware datetimes to naive UTC"""
        if not data:
            return []
            
        converted_data = []
        for item in data:
            if not isinstance(item, dict):
                continue
                
            converted_item = {}
            for key, value in item.items():
                try:
                    if isinstance(value, datetime):
                        if value.tzinfo is not None:
                            converted_item[key] = value.astimezone(timezone.utc).replace(tzinfo=None)
                        else:
                            converted_item[key] = value
                    else:
                        converted_item[key] = value
                except Exception as e:
                    self._log_error(f"Error converting datetime for key {key}", e)
                    converted_item[key] = value
            converted_data.append(converted_item)
        return converted_data

    def _write_empty_service_message(self, writer: pd.ExcelWriter, sheet_name: str, header_format: Any):
        """Write a message for empty services"""
        try:
            df = pd.DataFrame([{
                'Message': 'No services of this type are configured in this AWS account'
            }])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            worksheet.set_column('A:A', 60)
            worksheet.write('A1', 'Message', header_format)
        except Exception as e:
            self._log_error(f"Error writing empty service message for {sheet_name}", e)

    def _write_dataframe(self, writer: pd.ExcelWriter, sheet_name: str, data: List[Dict], header_format: Any):
        """Write data to Excel worksheet"""
        try:
            if not data:
                self._write_empty_service_message(writer, sheet_name, header_format)
                return

            df = pd.DataFrame(self._convert_datetimes(data))
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(df.columns):
                worksheet.write(0, idx, col, header_format)
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.set_column(idx, idx, max_length)
        except Exception as e:
            self._log_error(f"Error writing dataframe for {sheet_name}", e)

    def _write_global_resources(self, writer: pd.ExcelWriter, header_format: Any):
        """Write global resources data"""
        try:
            for service, data in self.results.get('global_services', {}).items():
                sheet_name = f"Global_{service.capitalize()}"
                self._write_dataframe(writer, sheet_name, data, header_format)
        except Exception as e:
            self._log_error("Error writing global resources", e)

    def _write_regional_resources(self, writer: pd.ExcelWriter, header_format: Any):
        """Write regional resources data"""
        try:
            for region, region_data in self.results.get('regions', {}).items():
                if not region_data:
                    continue
                    
                for service, data in region_data.items():
                    sheet_name = f"{region}_{service.capitalize()}"
                    self._write_dataframe(writer, sheet_name, data, header_format)
        except Exception as e:
            self._log_error("Error writing regional resources", e)

    def _write_resource_usage_by_region(self, writer: pd.ExcelWriter, header_format: Any):
        """Write resource usage summary by region"""
        try:
            usage_data = []
            
            for region, region_data in self.results.get('regions', {}).items():
                if not region_data:
                    continue
                    
                row = {'Region': region}
                for service_name, service_key in self.services.items():
                    data = region_data.get(service_key)
                    row[service_name] = len(data) if isinstance(data, list) else 0
                usage_data.append(row)
                
            if usage_data:
                df = pd.DataFrame(usage_data)
                df.to_excel(writer, sheet_name='Resource_Usage_By_Region', index=False)
                
                worksheet = writer.sheets['Resource_Usage_By_Region']
                for idx, col in enumerate(df.columns):
                    worksheet.write(0, idx, col, header_format)
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.set_column(idx, idx, max_length)
            else:
                self._write_empty_service_message(writer, 'Resource_Usage_By_Region', header_format)
        except Exception as e:
            self._log_error("Error writing resource usage by region", e)

    def _generate_excel_report(self) -> str:
        """Generate Excel report with all AWS resources"""
        try:
            excel_path = os.path.join(self.output_dir, f'aws_inventory_{self.timestamp}.xlsx')
            
            with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'border': 1
                })
                
                self._write_global_resources(writer, header_format)
                self._write_regional_resources(writer, header_format)
                self._write_resource_usage_by_region(writer, header_format)
                
            return excel_path
        except Exception as e:
            self._log_error("Error generating Excel report", e)
            raise

    def _save_json_report(self) -> str:
        """Save results to JSON file"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            json_path = os.path.join(self.output_dir, f'aws_inventory_{self.timestamp}.json')
            with open(json_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            return json_path
        except Exception as e:
            self._log_error("Error saving JSON report", e)
            raise

    def generate_reports(self) -> Tuple[str, str]:
        """Generate JSON and Excel reports"""
        try:
            self.logger.info("Starting report generation...")
            json_path = self._save_json_report()
            self.logger.info(f"JSON report saved to: {json_path}")
            
            excel_path = self._generate_excel_report()
            self.logger.info(f"Excel report saved to: {excel_path}")
            
            self.logger.info("Report generation complete!")
            self._print_error_summary()
            return json_path, excel_path
        except Exception as e:
            self._log_error("Failed to generate reports", e)
            self._print_error_summary()
            raise