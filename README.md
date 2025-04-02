# BRSK ETH Wallet

A command-line Ethereum wallet manager with a Python-based API backend. This project allows you to manage multiple Ethereum wallets, send transactions, and track transaction history on the Sepolia testnet.

## Project Structure

- `wallet-api/` - FastAPI backend service for wallet management
- `wallet-client/` - Command-line interface for interacting with the API

## Features

- Create new Ethereum wallets with mnemonic phrases
- Import existing wallets using private keys
- Send ETH transactions
- Track transaction history
- Multiple wallet management
- Real-time transaction status updates
- Secure API authentication
- MySQL database for persistent storage

## Quick Start

1. Set up the API:
```bash
cd wallet-api
pip install -r requirements.txt
python run.py
```

2. Set up the Client:
```bash
cd wallet-client
pip install -r requirements.txt
python run.py
```

For detailed setup instructions, please refer to the respective README files in each directory.

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
