# BRSK ETH Wallet Client

A command-line interface for managing Ethereum wallets and transactions.

## Prerequisites

- Python 3.8 or higher
- pip (Python Package Manager)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory:
```env
HOST=http://localhost:8000 # Where the API is running
X-API-Key=your_secret_key
```

## Usage

Start the client:
```bash
python run.py
```

## Features

- Create new wallets with mnemonic phrases
- Import existing wallets using private keys
- Send ETH transactions
- View transaction history
- Switch between multiple wallets
- Real-time balance updates
- Secure wallet management
- Color-coded terminal interface

## Main Menu Options

1. Send ETH
2. Change wallet
3. Wallet Settings
   - Create new wallet
   - Import wallet
   - Delete current wallet
   - Show transactions
4. Exit

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
