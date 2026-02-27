#!/usr/bin/env python3
"""
Polymarket Rebates Fetcher
Fetches rebate payouts for a given address across a date range.
"""

import argparse
import requests
from datetime import datetime, timedelta
import json
import csv
import sys


def fetch_rebates(maker_address, start_date, end_date):
    """
    Fetch rebates for a given address across a date range.

    Args:
        maker_address: Ethereum address to query
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD), inclusive

    Returns:
        List of responses for each date
    """
    base_url = "https://clob.polymarket.com/rebates/current"

    # Parse dates
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        print(f"Error parsing dates: {e}", file=sys.stderr)
        print("Please use YYYY-MM-DD format", file=sys.stderr)
        sys.exit(1)

    if start > end:
        print("Error: Start date must be before or equal to end date", file=sys.stderr)
        sys.exit(1)

    results = []
    current = start

    # Iterate through each date in the range (inclusive)
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")

        params = {
            "date": date_str,
            "maker_address": maker_address
        }

        print(f"Fetching rebates for {date_str}...", file=sys.stderr)

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            results.append({
                "date": date_str,
                "data": data
            })

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {date_str}: {e}", file=sys.stderr)
            results.append({
                "date": date_str,
                "error": str(e)
            })

        # Move to next day
        current += timedelta(days=1)

    return results


def results_to_csv(results):
    """
    Convert results to CSV format and calculate total.

    Args:
        results: List of date/data dictionaries

    Returns:
        Tuple of (csv_string, total_rebates)
    """
    rows = []
    total_rebates = 0.0

    for item in results:
        date = item.get("date")
        data = item.get("data")

        if data and isinstance(data, list):
            for rebate in data:
                rows.append({
                    "date": date,
                    "condition_id": rebate.get("condition_id", ""),
                    "asset_address": rebate.get("asset_address", ""),
                    "maker_address": rebate.get("maker_address", ""),
                    "rebated_fees_usdc": rebate.get("rebated_fees_usdc", "0")
                })
                # Add to total
                try:
                    total_rebates += float(rebate.get("rebated_fees_usdc", 0))
                except (ValueError, TypeError):
                    pass

    # Create CSV string
    if not rows:
        return "No rebate data found", 0.0

    output = []
    fieldnames = ["date", "condition_id", "asset_address", "maker_address", "rebated_fees_usdc"]

    # Use StringIO to create CSV in memory
    from io import StringIO
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    return csv_buffer.getvalue(), total_rebates


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Polymarket rebate payouts for an address across a date range"
    )
    parser.add_argument(
        "address",
        help="Ethereum maker address (e.g., 0x68146921dF11eaB44296dC4E58025CA84741a9E7)"
    )
    parser.add_argument(
        "start_date",
        help="Start date in YYYY-MM-DD format (e.g., 2026-02-01)"
    )
    parser.add_argument(
        "end_date",
        help="End date in YYYY-MM-DD format (e.g., 2026-02-18), inclusive"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: print to stdout)",
        default=None
    )
    parser.add_argument(
        "--pretty",
        help="Pretty print JSON output",
        action="store_true"
    )
    parser.add_argument(
        "--csv",
        help="Output as CSV format instead of JSON",
        action="store_true"
    )

    args = parser.parse_args()

    # Fetch rebates
    results = fetch_rebates(args.address, args.start_date, args.end_date)

    # Format output
    if args.csv:
        output, total = results_to_csv(results)
        print(f"\nTotal rebated fees: {total:.6f} USDC", file=sys.stderr)
    else:
        if args.pretty:
            output = json.dumps(results, indent=2)
        else:
            output = json.dumps(results)

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\nResults saved to {args.output}", file=sys.stderr)
    else:
        print(output)

    print(f"\nFetched rebates for {len(results)} days", file=sys.stderr)


if __name__ == "__main__":
    main()
