"""
Analytics Module
Provides trend analysis and insights for cryptocurrency data
"""

import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Analytics:
    """Perform analytics on cryptocurrency data"""
    
    @staticmethod
    def get_top_gainers(df, limit=5):
        """
        Get top gainers by 24h change percentage
        
        Args:
            df (DataFrame): Cryptocurrency data
            limit (int): Number of top gainers to return
        
        Returns:
            list: Top gainers sorted by change percentage
        """
        try:
            df_sorted = df.sort_values('change_24h_numeric', ascending=False)
            columns = ['rank', 'name', 'symbol', 'price', 'change_24h']
            if 'image_url' in df_sorted.columns:
                columns.append('image_url')
            result = df_sorted.head(limit)[columns].to_dict('records')
            logger.info(f"Retrieved {len(result)} top gainers")
            return result
        except Exception as e:
            logger.error(f"Error getting top gainers: {e}")
            return []
    
    @staticmethod
    def get_top_losers(df, limit=5):
        """
        Get top losers by 24h change percentage
        
        Args:
            df (DataFrame): Cryptocurrency data
            limit (int): Number of top losers to return
        
        Returns:
            list: Top losers sorted by change percentage
        """
        try:
            df_sorted = df.sort_values('change_24h_numeric', ascending=True)
            columns = ['rank', 'name', 'symbol', 'price', 'change_24h']
            if 'image_url' in df_sorted.columns:
                columns.append('image_url')
            result = df_sorted.head(limit)[columns].to_dict('records')
            logger.info(f"Retrieved {len(result)} top losers")
            return result
        except Exception as e:
            logger.error(f"Error getting top losers: {e}")
            return []
    
    @staticmethod
    def get_market_summary(df):
        """
        Get market summary statistics
        
        Args:
            df (DataFrame): Cryptocurrency data
        
        Returns:
            dict: Market summary with key metrics
        """
        try:
            summary = {
                "total_cryptos": len(df),
                "avg_price": f"${df['price_numeric'].mean():.2f}",
                "highest_price": f"${df['price_numeric'].max():.2f}",
                "lowest_price": f"${df['price_numeric'].min():.2f}",
                "avg_24h_change": f"{df['change_24h_numeric'].mean():.2f}%",
                "total_market_cap": f"${df['market_cap_numeric'].sum():,.0f}",
                "positive_change_count": len(df[df['change_24h_numeric'] > 0]),
                "negative_change_count": len(df[df['change_24h_numeric'] < 0])
            }
            logger.info("Market summary calculated")
            return summary
        except Exception as e:
            logger.error(f"Error calculating market summary: {e}")
            return {}
    
    @staticmethod
    def get_price_range_distribution(df, ranges=None):
        """
        Get distribution of cryptocurrencies by price range
        
        Args:
            df (DataFrame): Cryptocurrency data
            ranges (list): Price ranges (e.g., [0, 1, 100, 10000])
        
        Returns:
            dict: Distribution counts by price range
        """
        try:
            if ranges is None:
                ranges = [0, 1, 10, 100, 1000, 10000, 100000]
            
            distribution = {}
            for i in range(len(ranges) - 1):
                range_key = f"${ranges[i]}-${ranges[i+1]}"
                count = len(df[(df['price_numeric'] >= ranges[i]) & 
                              (df['price_numeric'] < ranges[i+1])])
                distribution[range_key] = count
            
            logger.info("Price distribution calculated")
            return distribution
        except Exception as e:
            logger.error(f"Error calculating distribution: {e}")
            return {}
    
    @staticmethod
    def get_historical_trend(df, days=7):
        """
        Get historical trend (requires data with timestamp column)
        
        Args:
            df (DataFrame): Historical cryptocurrency data
            days (int): Number of days to analyze
        
        Returns:
            dict: Trend data by date
        """
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            
            trend = df.groupby('date').agg({
                'price_numeric': 'mean',
                'change_24h_numeric': 'mean',
                'rank': 'count'
            }).rename(columns={'rank': 'samples'}).to_dict('index')
            
            logger.info(f"Historical trend calculated for {len(trend)} days")
            return trend
        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return {}
    
    @staticmethod
    def search_crypto(df, query):
        """
        Search for cryptocurrency by name or symbol
        
        Args:
            df (DataFrame): Cryptocurrency data
            query (str): Search query
        
        Returns:
            list: Matching cryptocurrencies
        """
        try:
            query_lower = query.lower()
            result = df[
                (df['name'].str.lower().str.contains(query_lower)) |
                (df['symbol'].str.lower().str.contains(query_lower))
            ]
            columns = ['rank', 'name', 'symbol', 'price', 'change_24h', 'market_cap']
            if 'image_url' in df.columns:
                columns.append('image_url')
            result = result[columns].to_dict('records')
            
            logger.info(f"Found {len(result)} results for '{query}'")
            return result
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
