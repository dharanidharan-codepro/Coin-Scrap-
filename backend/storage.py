"""
Storage Module
Handles CSV export and file management
"""

import os
import csv
from datetime import datetime
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVStorage:
    """Handle CSV storage operations"""
    
    def __init__(self, data_dir="../data"):
        """
        Initialize storage manager
        Args:
            data_dir (str): Directory to store CSV files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_csv_path(self, filename="crypto_data.csv"):
        """Get full path for CSV file"""
        return os.path.join(self.data_dir, filename)
    
    def save_data(self, df, filename="crypto_data.csv", mode="append"):
        """
        Save data to CSV file
        
        Args:
            df (DataFrame): Data to save
            filename (str): Output filename
            mode (str): 'append' or 'overwrite'
        """
        try:
            filepath = self.get_csv_path(filename)

            # Standardize column names for export
            rename_map = {
                'price_numeric': 'price_num',
                'change_24h_numeric': 'change_24h_num',
                'market_cap_numeric': 'market_cap_num'
            }
            df_copy = df.copy()
            df_copy.rename(columns=rename_map, inplace=True)

            # Desired column order
            cols = ['timestamp', 'rank', 'name', 'symbol', 'image_url', 'price', 'price_num',
                    'change_24h', 'change_24h_num', 'market_cap', 'market_cap_num']

            # Ensure all columns exist
            for c in cols:
                if c not in df_copy.columns:
                    df_copy[c] = ''

            if mode == "overwrite" or not os.path.exists(filepath):
                df_copy.to_csv(filepath, index=False, columns=cols)
                logger.info(f"CSV saved: {filepath}")
            else:
                existing_columns = pd.read_csv(filepath, nrows=0).columns.tolist()
                if existing_columns != cols:
                    existing_data = pd.read_csv(filepath)
                    for column in cols:
                        if column not in existing_data.columns:
                            existing_data[column] = ''
                    existing_data = existing_data.reindex(columns=cols, fill_value='')
                    existing_data.to_csv(filepath, index=False, columns=cols)
                # Append mode without writing header
                df_copy.to_csv(filepath, mode='a', header=False, index=False, columns=cols)
                logger.info(f"Data appended to: {filepath}")
            
            return filepath
        
        except Exception as e:
            logger.error(f"Save error: {e}")
            return None
    
    def load_data(self, filename="crypto_data.csv"):
        """Load CSV data"""
        try:
            filepath = self.get_csv_path(filename)
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                # Rename columns back to in-memory standard if present
                rename_map = {
                    'price_num': 'price_numeric',
                    'change_24h_num': 'change_24h_numeric',
                    'market_cap_num': 'market_cap_numeric'
                }
                df.rename(columns=rename_map, inplace=True)
                if 'image_url' not in df.columns:
                    df['image_url'] = ''
                logger.info(f"Loaded {len(df)} rows from {filepath}")
                return df
            else:
                logger.warning(f"File not found: {filepath}")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Load error: {e}")
            return pd.DataFrame()
    
    def export_filtered(self, df, filename="crypto_export.csv"):
        """Export filtered data to new CSV"""
        try:
            filepath = self.get_csv_path(filename)

            # Standardize column names and order as in save_data
            rename_map = {
                'price_numeric': 'price_num',
                'change_24h_numeric': 'change_24h_num',
                'market_cap_numeric': 'market_cap_num'
            }
            df_copy = df.copy()
            df_copy.rename(columns=rename_map, inplace=True)
            cols = ['timestamp', 'rank', 'name', 'symbol', 'image_url', 'price', 'price_num',
                    'change_24h', 'change_24h_num', 'market_cap', 'market_cap_num']
            for c in cols:
                if c not in df_copy.columns:
                    df_copy[c] = ''

            df_copy.to_csv(filepath, index=False, columns=cols)
            logger.info(f"Filtered data exported: {filepath}")
            return filepath
        
        except Exception as e:
            logger.error(f"Export error: {e}")
            return None
    
    def get_all_files(self):
        """List all CSV files in data directory"""
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            return files
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def delete_file(self, filename):
        """Delete a CSV file"""
        try:
            filepath = self.get_csv_path(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
