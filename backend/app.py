"""
Flask Backend Application
Main API server for Cryptocurrency Price Tracker
"""

from flask import Flask, jsonify, request, send_file, send_from_directory
from scraper import CryptoScraper
from processor import DataProcessor
from storage import CSVStorage
from analytics import Analytics
import logging
import os
from datetime import datetime
import io
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Add CORS headers manually
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# Initialize storage
storage = CSVStorage(data_dir="../data")


@app.route('/', methods=['GET'])
def root():
    """Serve the frontend HTML"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serve frontend static files (CSS, JS)"""
    if path != "" and os.path.exists(os.path.join('../frontend', path)):
        return send_from_directory('../frontend', path)
    return send_from_directory('../frontend', 'index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape_crypto():
    """Scrape latest cryptocurrency data"""
    try:
        # Accept numeric limits or the string 'all'
        limit_raw = request.json.get('limit', 10) if request.json else 10
        if isinstance(limit_raw, str) and limit_raw.lower() == 'all':
            limit = 'all'
        else:
            try:
                limit = int(limit_raw)
            except Exception:
                limit = 10

        raw_data = CryptoScraper().scrape_top_crypto(limit=limit)
        if not raw_data:
            return jsonify({"error": "No market data returned by CoinGecko"}), 502
        
        # Process data
        df = DataProcessor.process_crypto_data(raw_data)
        
        # Save to CSV (append mode for historical logging)
        storage.save_data(df, mode="append")
        
        display_data = DataProcessor.get_display_data(df)
        
        return jsonify({
            "success": True,
            "count": len(display_data),
            "data": display_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    except Exception as e:
        logger.error(f"Scrape endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/data', methods=['GET'])
def get_data():
    """Get stored cryptocurrency data"""
    try:
        df = storage.load_data()
        
        if df.empty:
            return jsonify({"data": [], "count": 0})
        
        # Get latest entry for each crypto (most recent timestamp)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_df = df.sort_values('timestamp').drop_duplicates('name', keep='last')
        
        display_data = DataProcessor.get_display_data(latest_df)
        
        return jsonify({
            "success": True,
            "count": len(display_data),
            "data": display_data
        })
    
    except Exception as e:
        logger.error(f"Get data endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/gainers', methods=['GET'])
def get_gainers():
    """Get top gainers"""
    try:
        limit = request.args.get('limit', 5, type=int)
        df = storage.load_data()
        
        if df.empty:
            return jsonify({"data": []})
        
        # Filter for latest scraped data per coin
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_df = df.sort_values('timestamp').drop_duplicates('name', keep='last')
        
        gainers = Analytics.get_top_gainers(latest_df, limit=limit)
        
        return jsonify({
            "success": True,
            "data": gainers
        })
    
    except Exception as e:
        logger.error(f"Gainers endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/losers', methods=['GET'])
def get_losers():
    """Get top losers"""
    try:
        limit = request.args.get('limit', 5, type=int)
        df = storage.load_data()
        
        if df.empty:
            return jsonify({"data": []})
        
        # Filter for latest scraped data per coin
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_df = df.sort_values('timestamp').drop_duplicates('name', keep='last')
        
        losers = Analytics.get_top_losers(latest_df, limit=limit)
        
        return jsonify({
            "success": True,
            "data": losers
        })
    
    except Exception as e:
        logger.error(f"Losers endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    """Get market summary"""
    try:
        df = storage.load_data()
        
        if df.empty:
            return jsonify({"data": {}})
        
        # Filter for latest scraped data per coin
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_df = df.sort_values('timestamp').drop_duplicates('name', keep='last')
        
        summary = Analytics.get_market_summary(latest_df)
        
        return jsonify({
            "success": True,
            "data": summary
        })
    
    except Exception as e:
        logger.error(f"Summary endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search():
    """Search for cryptocurrency"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        df = storage.load_data()
        
        if df.empty:
            return jsonify({"data": []})
        
        # Filter for latest scraped data per coin
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_df = df.sort_values('timestamp').drop_duplicates('name', keep='last')
        
        results = Analytics.search_crypto(latest_df, query)
        
        return jsonify({
            "success": True,
            "query": query,
            "count": len(results),
            "data": results
        })
    
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/export', methods=['GET'])
def export_csv():
    """Export data as CSV file"""
    try:
        df = storage.load_data()
        
        if df.empty:
            return jsonify({"error": "No data to export"}), 400

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_scrape = df['timestamp'].max()
        df = df.loc[df['timestamp'] == latest_scrape]
        
        # Create CSV in memory
        # Standardize column names and order before export
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

        csv_buffer = io.StringIO()
        df_copy.to_csv(csv_buffer, index=False, columns=cols)
        
        # Send file
        csv_buffer.seek(0)
        filename = f"crypto_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        logger.error(f"Export endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """List all CSV files"""
    try:
        files = storage.get_all_files()
        return jsonify({
            "success": True,
            "files": files,
            "count": len(files)
        })
    
    except Exception as e:
        logger.error(f"List files error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    logger.info("Starting Cryptocurrency Price Tracker API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
