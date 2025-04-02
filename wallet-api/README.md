# BRSK ETH Wallet API

A FastAPI-based backend service for managing Ethereum wallets and transactions on the Sepolia testnet.

## Features

- ETH Wallet Management
- REST API for Wallet Operations
- MySQL Database Integration
- Secure Transaction Processing
- Comprehensive Error Handling

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python Package Manager)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up MySQL database:
```sql
CREATE DATABASE eth_wallet_manager;
```

## Configuration

Create a `.env` file in the root directory with the following environment variables:

```env
X-API-Key=your_secret_key_for_safe_requests
INFURA_API_KEY=your_infura_key
APP_VERSION=1.0
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=eth_wallet_manager
CHAIN_ID=11155111 #Sepolia testnet
```

## Usage

Start the API server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Wallet Management
- `POST /wallet/create` - Create a new wallet with mnemonic phrase
- `POST /wallet/import` - Import an existing wallet using private key
- `DELETE /wallet/{address}` - Delete a wallet
- `GET /wallet/{address}` - Get wallet details and balance
- `GET /wallets` - List all wallets

### Transactions
- `POST /wallet/send` - Send ETH to another address
- `GET /wallet/{address}/transactions` - Get transaction history for a wallet
- `GET /transactions` - Get all transactions

### System
- `GET /version` - Get API version

## Database Schema

The API uses MySQL with the following tables:
- `wallets` - Stores wallet information
- `transactions` - Tracks transaction history
- `wallet_manager` - System configuration

## Development

For development, we recommend using a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
venv\Scripts\activate     # On Windows
```

## License

MIT License

Copyright (c) 2024 BRSK ETH Wallet

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
