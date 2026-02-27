# Polymarket Rebates Fetcher

A Python script to fetch rebate payouts from Polymarket for a given maker address across a date range.

## Features

- Fetch rebates for any Ethereum address
- Query across a date range (inclusive of start and end dates)
- Export results to JSON or CSV format
- Pretty print option for readable output
- Error handling for failed requests
- **REST API endpoint** for programmatic access with CSV downloads

## Installation

1. Clone this repository
2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

**Note:** Make sure your virtual environment is activated first:
```bash
source venv/bin/activate
```

Basic usage:

```bash
python fetch_rebates.py <ADDRESS> <START_DATE> <END_DATE>
```

### Arguments

- `ADDRESS`: Ethereum maker address (e.g., `0x68146921dF11eaB44296dC4E58025CA84741a9E7`)
- `START_DATE`: Start date in YYYY-MM-DD format (e.g., `2026-02-01`)
- `END_DATE`: End date in YYYY-MM-DD format (e.g., `2026-02-18`) - inclusive

### Options

- `-o, --output FILE`: Save results to a file instead of printing to stdout
- `--pretty`: Pretty print JSON output with indentation

### Examples

1. Fetch rebates and print to console:
```bash
python fetch_rebates.py 0x68146921dF11eaB44296dC4E58025CA84741a9E7 2026-02-01 2026-02-18
```

2. Fetch rebates with pretty formatting:
```bash
python fetch_rebates.py 0x68146921dF11eaB44296dC4E58025CA84741a9E7 2026-02-01 2026-02-18 --pretty
```

3. Save results to a file:
```bash
python fetch_rebates.py 0x68146921dF11eaB44296dC4E58025CA84741a9E7 2026-02-01 2026-02-18 -o rebates.json --pretty
```

4. Fetch rebates for a single day:
```bash
python fetch_rebates.py 0x68146921dF11eaB44296dC4E58025CA84741a9E7 2026-02-18 2026-02-18
```

5. Export as CSV with total calculation:
```bash
python fetch_rebates.py 0x68146921dF11eaB44296dC4E58025CA84741a9E7 2026-02-01 2026-02-28 --csv -o rebates.csv
```

## API Server

You can run this as a REST API server that others can call to get CSV downloads.

### Running the API Server

1. Make sure your virtual environment is activated:
```bash
source venv/bin/activate
```

2. Start the server:
```bash
python api.py
```

The server will start on `http://localhost:5001` (Port 5000 is often used by AirPlay on macOS)

### API Endpoints

#### GET /rebates

Fetch rebates and download as CSV or JSON.

**Query Parameters:**
- `address` (required): Ethereum maker address
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `format` (optional): Output format - `csv` (default) or `json`

**Example:**
```bash
# Download CSV file
curl "http://localhost:5001/rebates?address=0x68146921dF11eaB44296dC4E58025CA84741a9E7&start_date=2026-02-01&end_date=2026-02-28" -o rebates.csv

# Get JSON response
curl "http://localhost:5001/rebates?address=0x68146921dF11eaB44296dC4E58025CA84741a9E7&start_date=2026-02-01&end_date=2026-02-28&format=json"

# From browser
http://localhost:5001/rebates?address=0x68146921dF11eaB44296dC4E58025CA84741a9E7&start_date=2026-02-01&end_date=2026-02-28
```

#### GET /health

Health check endpoint.

#### GET /

API documentation and available endpoints.

## Output Format

The script outputs a JSON array with one object per date:

```json
[
  {
    "date": "2026-02-01",
    "data": {
      // API response data
    }
  },
  {
    "date": "2026-02-02",
    "data": {
      // API response data
    }
  }
]
```

If an error occurs for a specific date, the response will include an error field instead:

```json
{
  "date": "2026-02-01",
  "error": "Error message"
}
```

## API Endpoint

This script queries the Polymarket CLOB API:
```
https://clob.polymarket.com/rebates/current?date=YYYY-MM-DD&maker_address=ADDRESS
```

## Deploying to Vercel

To deploy this API to Vercel and make it accessible from anywhere:

### Prerequisites
- A Vercel account (free tier works great)
- Vercel CLI installed: `npm install -g vercel`

### Deployment Steps

1. **Initialize git repository** (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. **Deploy to Vercel**:
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? (accept default or choose your own)
- In which directory is your code located? **./**
- Want to override settings? **N**

3. **Your API is now live!** Vercel will give you a URL like:
```
https://your-project-name.vercel.app
```

### Using Your Deployed API

Once deployed, anyone can access your API:

```bash
# Download CSV
curl "https://your-project-name.vercel.app/api/rebates?address=0x68146921dF11eaB44296dC4E58025CA84741a9E7&start_date=2026-02-01&end_date=2026-02-28" -o rebates.csv

# Or open in browser:
https://your-project-name.vercel.app/api/rebates?address=0x68146921dF11eaB44296dC4E58025CA84741a9E7&start_date=2026-02-01&end_date=2026-02-28
```

### Environment Variables (Optional)

If you need to add environment variables later:
```bash
vercel env add
```

### Redeploy After Changes

```bash
git add .
git commit -m "Your changes"
vercel --prod
```

## License

MIT
