"""
Data Processing Module
Cleans and structures cryptocurrency data using Pandas
"""

import pandas as pd
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and clean cryptocurrency data"""
    
    @staticmethod
    def clean_price(price_str):
        """Convert price string to float"""
        try:
            # Remove $ and commas
            clean = price_str.replace("$", "").replace(",", "")
            return float(clean)
        except:
            return None
    
    @staticmethod
    def clean_percentage(change_str):
        """Convert percentage string to float"""
        try:
            # Remove % and spaces
            clean = change_str.replace("%", "").strip()
            return float(clean)
        except:
            return None
    
    @staticmethod
    def clean_market_cap(market_cap_str):
        """Convert market cap string to float"""
        try:
            clean = market_cap_str.replace("$", "").replace(",", "")
            
            # Handle billion, million, trillion
            if "T" in clean:
                return float(clean.replace("T", "")) * 1e12
            elif "B" in clean:
                return float(clean.replace("B", "")) * 1e9
            elif "M" in clean:
                return float(clean.replace("M", "")) * 1e6
            else:
                return float(clean)
        except:
            return None
    
    @staticmethod
    def process_crypto_data(raw_data):
        """
        Process raw scraped data
        
        Args:
            raw_data (list): List of raw crypto dictionaries
        
        Returns:
            DataFrame: Processed cryptocurrency data
        """
        try:
            # Create DataFrame
            df = pd.DataFrame(raw_data)
            
            # Add timestamp
            df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if 'image_url' not in df.columns:
                df['image_url'] = ''
            
            # Clean numeric columns
            df['price_numeric'] = df['price'].apply(DataProcessor.clean_price)
            df['change_24h_numeric'] = df['change_24h'].apply(DataProcessor.clean_percentage)
            df['market_cap_numeric'] = df['market_cap'].apply(DataProcessor.clean_market_cap)
            
            # Reorder columns
            df = df[['timestamp', 'rank', 'name', 'symbol', 'image_url', 'price', 'price_numeric', 
                     'change_24h', 'change_24h_numeric', 'market_cap', 'market_cap_numeric']]
            
            logger.info(f"Processed {len(df)} rows")
            return df
        
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def filter_by_price(df, min_price=None, max_price=None):
        """Filter cryptocurrencies by price range"""
        if min_price:
            df = df[df['price_numeric'] >= min_price]
        if max_price:
            df = df[df['price_numeric'] <= max_price]
        return df
    
    @staticmethod
    def filter_by_change(df, min_change=None, max_change=None):
        """Filter cryptocurrencies by 24h change"""
        if min_change is not None:
            df = df[df['change_24h_numeric'] >= min_change]
        if max_change is not None:
            df = df[df['change_24h_numeric'] <= max_change]
        return df
    
    @staticmethod
    def get_display_data(df):
        """Get formatted data for display (without numeric columns)"""
        if 'image_url' not in df.columns:
            df = df.copy()
            df['image_url'] = ''
        return df[['timestamp', 'rank', 'name', 'symbol', 'image_url', 'price', 'change_24h', 'market_cap']].to_dict('records')
