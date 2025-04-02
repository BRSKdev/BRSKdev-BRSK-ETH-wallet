from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from web3 import Web3
from eth_account import Account
import mysql.connector
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from decimal import Decimal
from datetime import datetime
from eth_account.hdaccount import generate_mnemonic

# Environment variables
load_dotenv()

# Base Models
class VersionResponse(BaseModel):
    version: str

class WalletCreate(BaseModel):
    wallet_name: str

class WalletResponse(BaseModel):
    address: str
    private_key: str
    wallet_name: str
    memoric_phrase: str | None = None

class WalletListResponse(BaseModel):
    address: str
    wallet_name: str
    balance: float
    created_at: datetime | None = None

class WalletImport(BaseModel):
    private_key: str
    wallet_name: str

class WalletSend(BaseModel):
    from_address: str
    to_address: str
    amount: float
    private_key: str

class TransactionResponse(BaseModel):
    id: int
    wallet_id: int
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    gas_used: float
    status: str
    created_at: datetime


# Database Manager Class
class DatabaseManager:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME')
        }
        self.version = os.getenv('APP_VERSION')

    def create_connection(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")

    def init_database(self):
        conn = self.create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallet_manager (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    version VARCHAR(10),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    address VARCHAR(42) UNIQUE,
                    private_key VARCHAR(66),
                    wallet_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    wallet_id INT,
                    tx_hash VARCHAR(66),
                    from_address VARCHAR(42),
                    to_address VARCHAR(42),
                    amount DECIMAL(18,8),
                    gas_used DECIMAL(18,8),
                    status VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (wallet_id) REFERENCES wallets(id)
                )
            """)

            cursor.execute("SELECT version FROM wallet_manager LIMIT 1")
            result = cursor.fetchone()

            if result is None:
                cursor.execute("""
                    INSERT INTO wallet_manager (version)
                    VALUES (%s)
                """, (self.version,))
            elif result[0] != self.version:
                cursor.execute("""
                    UPDATE wallet_manager
                    SET version = %s
                    WHERE version != %s
                """, (self.version, self.version))

            conn.commit()
        finally:
            cursor.close()
            conn.close()


# Ethereum Manager Class
class EthereumManager:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(f"https://sepolia.infura.io/v3/{os.getenv('INFURA_API_KEY')}"))

    def send_transaction(self, from_address: str, to_address: str, amount: float, private_key: str):
        try:
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key

            nonce = self.w3.eth.get_transaction_count(from_address)
            gas_price = self.w3.eth.gas_price

            transaction = {
                'nonce': nonce,
                'to': self.w3.to_checksum_address(to_address),
                'value': self.w3.to_wei(amount, 'ether'),
                'gas': 21000,
                'gasPrice': gas_price,
                'chainId': int(os.getenv('CHAIN_ID'))
            }

            # Sign the transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

            # Send the transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            return self.w3.to_hex(tx_hash)

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def refresh_transactions(self, conn, cursor) -> int:
        try:
            # Get all PENDING transactions
            cursor.execute("SELECT id, tx_hash FROM transactions WHERE status = 'PENDING'")
            pending_transactions = cursor.fetchall()

            updated_count = 0
            for tx in pending_transactions:
                try:
                    # Get the transaction from the blockchain
                    tx_receipt = self.w3.eth.get_transaction_receipt(tx['tx_hash'])

                    if tx_receipt is None:
                        continue  # Transaction is still PENDING

                    # Calculate the actual gas consumption in ETH
                    gas_used = float(self.w3.from_wei(tx_receipt.gasUsed * tx_receipt.effectiveGasPrice, 'ether'))

                    # Determine the status
                    status = "SUCCESS" if tx_receipt.status == 1 else "FAILED"

                    # Update the transaction in the database
                    cursor.execute("""
                        UPDATE transactions
                        SET status = %s, gas_used = %s
                        WHERE id = %s
                    """, (status, gas_used, tx['id']))

                    updated_count += 1

                except Exception as e:
                    print(f"Error updating transaction {tx['tx_hash']}: {str(e)}")
                    continue

            conn.commit()
            return updated_count

        except Exception as e:
            print(f"Error updating transactions: {str(e)}")
            return 0

# API Initialization
app = FastAPI()
db_manager = DatabaseManager()
eth_manager = EthereumManager()

# API Key Setup
API_KEY = os.getenv("X-API-Key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header or api_key_header != API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Fehlender oder falscher API Key")
    return api_key_header

# Send ETH POST Request
@app.post("/wallet/send")
async def send_eth(wallet_data: WalletSend, api_key: str = Depends(get_api_key)):
    conn = db_manager.create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM wallets WHERE address = %s", (wallet_data.from_address,))
        wallet = cursor.fetchone()
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        tx_hash = eth_manager.send_transaction(
            wallet_data.from_address,
            wallet_data.to_address,
            wallet_data.amount,
            wallet_data.private_key
        )

        cursor.execute("""
            INSERT INTO transactions
            (wallet_id, tx_hash, from_address, to_address, amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            wallet['id'],
            tx_hash,
            wallet_data.from_address,
            wallet_data.to_address,
            wallet_data.amount,
            'PENDING'
        ))

        conn.commit()
        return {"tx_hash": tx_hash}

    finally:
        cursor.close()
        conn.close()

# Enable HD Wallet Features
Account.enable_unaudited_hdwallet_features()

# Create wallet POST Request
@app.post("/wallet/create", response_model=WalletResponse)
async def create_wallet(wallet_data: WalletCreate, api_key: str = Depends(get_api_key)):
    try:
        mnemonic = generate_mnemonic(num_words=12, lang="english")
        account = Account.from_mnemonic(mnemonic)
        conn = db_manager.create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO wallets (address, private_key, wallet_name)
                VALUES (%s, %s, %s)
            """, (account.address, account.key.hex(), wallet_data.wallet_name))

            conn.commit()

            return WalletResponse(
                address=account.address,
                private_key=account.key.hex(),
                wallet_name=wallet_data.wallet_name,
                memoric_phrase=mnemonic
            )
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Wallet: {str(e)}")
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Wallet-Erstellung: {str(e)}")

# Get wallet GET Request
@app.get("/wallet/{address}", response_model=WalletResponse)
async def get_wallet(address: str, api_key: str = Depends(get_api_key)):
    conn = db_manager.create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM wallets WHERE address = %s", (address,))
        wallet = cursor.fetchone()

        if wallet is None:
            raise HTTPException(status_code=404, detail="Wallet nicht gefunden")

        balance = eth_manager.w3.eth.get_balance(address)
        wallet['balance'] = eth_manager.w3.from_wei(balance, 'ether')

        return wallet
    finally:
        cursor.close()
        conn.close()

# Delete wallet DELETE Request
@app.delete("/wallet/{address}")
async def delete_wallet(address: str, api_key: str = Depends(get_api_key)):
    conn = db_manager.create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM wallets WHERE address = %s", (address,))
        wallet = cursor.fetchone()

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet nicht gefunden")

        cursor.execute("DELETE FROM transactions WHERE wallet_id = %s", (wallet['id'],))

        cursor.execute("DELETE FROM wallets WHERE id = %s", (wallet['id'],))

        conn.commit()
        return {"message": "Wallet successfully deleted"}

    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Get all wallets GET Request
@app.get("/wallets", response_model=list[WalletListResponse])
async def get_all_wallets(api_key: str = Depends(get_api_key)):
    conn = db_manager.create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT address, wallet_name, created_at FROM wallets")
        wallets = cursor.fetchall()

        for wallet in wallets:
            balance = eth_manager.w3.eth.get_balance(wallet['address'])
            wallet['balance'] = eth_manager.w3.from_wei(balance, 'ether')

        return wallets
    finally:
        cursor.close()
        conn.close()

# Import wallet POST Request
@app.post("/wallet/import", response_model=WalletResponse)
async def import_wallet(wallet_data: WalletImport, api_key: str = Depends(get_api_key)):
    try:
        if not wallet_data.private_key.startswith('0x'):
            wallet_data.private_key = '0x' + wallet_data.private_key

        account = Account.from_key(wallet_data.private_key)
        conn = db_manager.create_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO wallets (address, private_key, wallet_name)
                VALUES (%s, %s, %s)
            """, (account.address, wallet_data.private_key, wallet_data.wallet_name))

            conn.commit()

            return WalletResponse(
                address=account.address,
                private_key=wallet_data.private_key,
                wallet_name=wallet_data.wallet_name
            )
        except mysql.connector.Error as e:
            raise HTTPException(
                status_code=500,
                detail=f"Fehler beim Speichern der importierten Wallet: {str(e)}"
            )
        finally:
            cursor.close()
            conn.close()

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Ungültiger Private Key"
        )

# Get all transactions GET Request
@app.get("/transactions", response_model=list[TransactionResponse])
async def get_all_transactions(api_key: str = Depends(get_api_key)):
    conn = db_manager.create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT transactions.*, wallets.address as from_address, wallets.wallet_name FROM transactions JOIN wallets ON transactions.wallet_id = wallets.id")
        transactions = cursor.fetchall()

        return transactions
    finally:
        cursor.close()
        conn.close()

# Get wallet transactions GET Request
@app.get("/wallet/{address}/transactions", response_model=list[TransactionResponse])
async def get_wallet_transactions(address: str, api_key: str = Depends(get_api_key)):
    conn = db_manager.create_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        updated_count = eth_manager.refresh_transactions(conn, cursor)
        cursor.execute("SELECT id FROM wallets WHERE address = %s", (address,))
        wallet = cursor.fetchone()

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        cursor.execute("""
            SELECT
                t.id,
                t.wallet_id,
                t.tx_hash,
                t.from_address,
                t.to_address,
                CAST(t.amount AS FLOAT) as amount,
                COALESCE(CAST(t.gas_used AS FLOAT), 0.0) as gas_used,
                t.status,
                t.created_at
            FROM transactions t
            WHERE t.wallet_id = %s
            ORDER BY t.created_at DESC
        """, (wallet['id'],))

        transactions = cursor.fetchall()
        return transactions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

# Get version GET Request
@app.get("/version", response_model=VersionResponse)
async def get_version(api_key: str = Depends(get_api_key)):
    return {"version": db_manager.version}

# Startup Event POST Request
@app.on_event("startup")
async def startup_event():
    db_manager.init_database()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
