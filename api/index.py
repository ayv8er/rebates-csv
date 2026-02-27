"""
Polymarket Rebates API for Vercel
Serverless function version
"""

from flask import Flask, request, Response, jsonify
import sys
import os

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fetch_rebates import fetch_rebates, results_to_csv
from datetime import datetime
import io

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """API documentation."""
    return jsonify({
        "name": "Polymarket Rebates API",
        "version": "1.0",
        "endpoints": {
            "/api/rebates": {
                "method": "GET",
                "description": "Fetch rebates for an address and date range",
                "parameters": {
                    "address": "Ethereum maker address (required)",
                    "start_date": "Start date in YYYY-MM-DD format (required)",
                    "end_date": "End date in YYYY-MM-DD format (required)",
                    "format": "Output format - 'csv' or 'json' (default: csv)"
                },
                "example": "/api/rebates?address=0x68146921dF11eaB44296dC4E58025CA84741a9E7&start_date=2026-02-01&end_date=2026-02-28&format=csv"
            },
            "/api/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        }
    })


@app.route('/api/rebates', methods=['GET'])
def get_rebates():
    """
    Fetch rebates for a given address and date range.

    Query Parameters:
        address: Ethereum maker address (required)
        start_date: Start date in YYYY-MM-DD format (required)
        end_date: End date in YYYY-MM-DD format (required)
        format: Output format - 'csv' or 'json' (default: csv)
    """
    # Get query parameters
    address = request.args.get('address')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    output_format = request.args.get('format', 'csv').lower()

    # Validate required parameters
    if not address:
        return jsonify({"error": "Missing required parameter: address"}), 400
    if not start_date:
        return jsonify({"error": "Missing required parameter: start_date"}), 400
    if not end_date:
        return jsonify({"error": "Missing required parameter: end_date"}), 400

    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Fetch rebates
    try:
        results = fetch_rebates(address, start_date, end_date)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch rebates: {str(e)}"}), 500

    # Return CSV format
    if output_format == 'csv':
        csv_data, total = results_to_csv(results)

        # Create response with CSV file download
        output = io.StringIO()
        output.write(csv_data)
        output.write(f"\n# Total rebated fees: {total:.6f} USDC\n")

        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=rebates_{address[:8]}_{start_date}_to_{end_date}.csv'
            }
        )
        return response

    # Return JSON format
    elif output_format == 'json':
        return jsonify({
            "address": address,
            "start_date": start_date,
            "end_date": end_date,
            "results": results
        })

    else:
        return jsonify({"error": "Invalid format. Use 'csv' or 'json'"}), 400


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "polymarket-rebates-api"})


# Vercel serverless function handler
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
