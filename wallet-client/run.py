import os
import sys
import time
import random
import json
import base64
import requests
from dotenv import load_dotenv

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Import API Key from vars.py or .env
try:
    from vars import api_key
except ImportError:
    load_dotenv(dotenv_path=resource_path('.env'))
    api_key = os.getenv("X-API-Key")

if not api_key:
    print("\033[91mError: X-API-Key not found in .env or vars.py\033[0m")
    sys.exit(1)

# Realistic typing function
def realistic_typing(text):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(random.uniform(0.05, 0.1))
    print()

# Client Class
class Client:
    def __init__(self):
        self.base_url = os.getenv("HOST")
        self.api_key = api_key
        self.headers = {"X-API-Key": self.api_key}
        self.version = self.get_version()
        self.wallets = []
        self.get_wallets()
        self.current_wallet = None
        os.system("clear")

    def get_version(self):
        try:
            response = requests.get(f"{self.base_url}/version", headers=self.headers)
            if response.status_code == 403:
                print("\033[91mError: Invalid API-Key\033[0m")
                sys.exit(1)
            return response.json()["version"]
        except Exception as e:
            print(f"\033[91mError: Failed to connect to the API: {e}\033[0m")
            sys.exit(1)

    def get_wallets(self):
        try:
            response = requests.get(f"{self.base_url}/wallets", headers=self.headers)
            if response.status_code == 200:
                self.wallets = response.json()
            else:
                print(f"\033[91mError: {response.text}\033[0m")
                self.wallets = []
        except Exception as e:
            print(f"\033[91mError: Failed to get wallets: {e}\033[0m")
            self.wallets = []

    def create_wallet(self):
        os.system("clear")
        print("\n\033[92mCreate new wallet\033[0m\n")
        try:
            wallet_name = input("Wallet Name > ")
            response = requests.post(
                f"{self.base_url}/wallet/create",
                headers=self.headers,
                json={"wallet_name": wallet_name}
            )
            if response.status_code == 200:
                wallet_data = response.json()
                print("\n\033[92mWallet successfully created!\033[0m")
                print(f"\nWallet Name: \033[92m{wallet_data['wallet_name']}\033[0m")
                print(f"Address: \033[92m{wallet_data['address']}\033[0m")
                print(f"Private Key: \033[93m{wallet_data['private_key']}\033[0m")
                if wallet_data.get('memoric_phrase'):
                    print("\n\033[91mIMPORTANT: Save this Memoric Phrase securely!\033[0m")
                    print(f"\033[93m{wallet_data['memoric_phrase']}\033[0m")

                print("\n\033[91mIMPORTANT: Save the Private Key and the Memoric Phrase securely!\033[0m")
                print("\033[91mIf you lose them, you will not be able to access your Wallet!\033[0m")
                input("\nPress Enter to continue...")

                self.get_wallets()
                self.current_wallet = self.wallets[-1]
            else:
                print(f"\n\033[91mError: {response.text}\033[0m")
                time.sleep(2)
        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m")
            time.sleep(2)

    def import_wallet(self):
        os.system("clear")
        print("\n\033[92mImport wallet\033[0m\n")
        try:
            wallet_name = input("Wallet Name > ")
            private_key = input("Private Key > ")
            response = requests.post(
                f"{self.base_url}/wallet/import",
                headers=self.headers,
                json={
                    "wallet_name": wallet_name,
                    "private_key": private_key
                }
            )
            if response.status_code == 200:
                print("\n\033[92mWallet successfully imported!\033[0m")
                time.sleep(1)
                self.get_wallets()
                self.current_wallet = self.wallets[-1]
            else:
                print(f"\n\033[91mError: {response.text}\033[0m")
                time.sleep(2)
        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m")
            time.sleep(2)

    def delete_wallet(self):
        if not self.current_wallet:
            os.system("clear")
            print("\n\033[91mNo wallet selected!\033[0m")
            time.sleep(1.8)
            return
        try:
            os.system("clear")
            print("\n\033[92mWallet löschen\033[0m")
            print(f"\nWallet: \033[92m{self.current_wallet['wallet_name']}\033[0m")
            print(f"Address: \033[92m{self.current_wallet['address']}\033[0m")
            print(f"\nDo you really want to delete this wallet?")
            print(f"Type \033[91m{self.current_wallet['address']} delete\033[0m to confirm")
            choice = input("\n> ")
            if choice.lower() != f"{self.current_wallet['address']} delete".lower():
                print("\n\033[91mDeletion process aborted!\033[0m")
                time.sleep(1.8)
                return

            response = requests.delete(
                f"{self.base_url}/wallet/{self.current_wallet['address']}",
                headers=self.headers
            )

            if response.status_code == 200:
                print("\n\033[92mWallet successfully deleted!\033[0m")

                time.sleep(1.8)
                self.get_wallets()
                if self.wallets:
                    self.current_wallet = self.wallets[0]
                else:
                    self.current_wallet = {"address": "No wallet selected", "balance": 0}
            else:
                print(f"\n\033[91mError: {response.text}\033[0m")
                input("\nPress Enter to continue...")
        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m")
            input("\nPress Enter to continue...")

    def show_transactions(self):
        os.system("clear")
        if not self.current_wallet:
            print("\n\033[91mNo wallet selected!\033[0m")
            time.sleep(1.8)
            return

        print("\n\033[92mShow transactions\033[0m")
        print(f"Wallet: [\033[92m{self.current_wallet['wallet_name']}\033[0m] \033[92m{self.current_wallet['address']}\033[0m")

        response = requests.get(
            f"{self.base_url}/wallet/{self.current_wallet['address']}/transactions",
            headers=self.headers
        )

        if response.status_code == 200:
            transactions = response.json()
            print("\n\033[92mTransactions updated!\033[0m")
            time.sleep(1)
            os.system("clear")

            print("\n\033[92mShow transactions\033[0m")
            print(f"Wallet: [\033[92m{self.current_wallet['wallet_name']}\033[0m] \033[92m{self.current_wallet['address']}\033[0m")

            if not transactions:
                print("\n\033[93mNo transactions found\033[0m")
                input("\nPress Enter to continue...")
                return

            print(f"\n\033[93m{len(transactions)} transactions found\033[0m")

            for transaction in transactions:
                print("\n" + "="*60)
                print(f"\nTransaction Hash: \033[92m{transaction['tx_hash']}\033[0m")
                print(f"Timestamp: {transaction['created_at']}")
                print(f"Sender: \033[94m{transaction['from_address']}\033[0m")
                print(f"Receiver: \033[94m{transaction['to_address']}\033[0m")
                print(f"Amount: \033[1m{transaction['amount']} ETH\033[0m")
                print(f"Gas: {transaction['gas_used']} ETH")
                status_color = "\033[92m" if transaction['status'] == "SUCCESS" else "\033[93m" if transaction['status'] == "PENDING" else "\033[91m"
                print(f"Status: {status_color}{transaction['status']}\033[0m")

            print("\n" + "="*60)
            input("\nPress Enter to continue...")
        else:
            print(f"\n\033[91mError: {response.text}\033[0m")
            input("\nPress Enter to continue...")

    def settings(self):
        while True:
            os.system("clear")
            print("\n\033[92mWallet Settings\033[0m\n")
            print("1  Create new wallet")
            print("2  Import wallet")
            print("3  Delete current wallet")
            print("4  Show transactions")
            print("5  Back")

            option = input("\nOption > ")

            if option == "1":
                self.create_wallet()
            elif option == "2":
                self.import_wallet()
            elif option == "3":
                self.delete_wallet()
            elif option == "4":
                self.show_transactions()
            elif option == "5":
                os.system("clear")
                break
            else:
                print("\n\033[91mInvalid option\033[0m")
                time.sleep(1.8)

    def change_wallet(self):
        os.system("clear")
        print("\n\033[92mVerfügbare Wallets:\033[0m")
        if not self.wallets:
            print("\n\033[91mNo wallets available!\033[0m")
            time.sleep(1.8)
            return
        for i, wallet in enumerate(self.wallets):
            balance = str(wallet['balance'])
            if '.' in balance and len(balance.split('.')[1]) > 4:
                balance = balance.split('.')[0] + '.' + balance.split('.')[1][:4] + '...'
            print(f"{i+1} - \033[92m[{wallet['wallet_name']}]\033[0m {wallet['address']} - {balance} ETH")

        try:
            choice = int(input("\nNummer > ")) - 1
            if 0 <= choice < len(self.wallets):
                self.current_wallet = self.wallets[choice]
                print(f"\n\033[92mWallet erfolgreich gewechselt\033[0m")
                time.sleep(1.8)
                os.system("clear")
            else:
                print("\n\033[91mInvalid selection\033[0m")
                time.sleep(1.8)
        except ValueError:
            print("\n\033[91mInvalid input\033[0m")
            time.sleep(1.8)
            os.system("clear")

    def send_eth(self):
        os.system("clear")
        if not self.current_wallet:
            print("\n\033[91mNo wallet selected!\033[0m")
            time.sleep(1.8)
            return
        try:
            to_address = input("Empfänger-Adresse > ")
            amount = float(input("ETH Menge > "))

            response = requests.get(
                f"{self.base_url}/wallet/{self.current_wallet['address']}",
                headers=self.headers
            )
            if response.status_code != 200:
                print(f"\n\033[91mError fetching private key: {response.text}\033[0m")
                input("\nPress Enter to continue...")
                return

            wallet_data = response.json()
            private_key = wallet_data["private_key"]

            data = {
                "from_address": self.current_wallet['address'],
                "to_address": to_address,
                "amount": amount,
                "private_key": private_key
            }

            response = requests.post(f"{self.base_url}/wallet/send", headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"\n\033[92mTransaction sent: {response.json()['tx_hash']}\033[0m")
                print(f"Receiver: \033[94m{to_address}\033[0m")
                print(f"Amount: \033[94m{amount} ETH\033[0m")
                print(f"To track the status of the transaction, go to the \033[94mWallet Settings\033[0m and select \033[94mShow transactions\033[0m.")
                input("\nPress Enter to continue...")
            else:
                error_detail = response.json().get('detail', response.text)
                print(f"\n\033[91mError: {error_detail}\033[0m")
                input("\nPress Enter to continue...")

        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m")
            input("\nPress Enter to continue...")

    def menu(self):
        os.system("clear")
        while True:
            print("\n\033[92mETH Wallet Manager\033[0m", end=" ")
            print(f"v{self.version}")
            print(f"Wallet:\t\t{self.current_wallet['address'] if self.current_wallet else ' '}")
            print(f"Balance:\t{self.current_wallet['balance'] if self.current_wallet else ' '}\n")
            print("1  Send ETH")
            print("2  Change wallet")
            print("3  Wallet Settings")
            print("4  Exit")

            option = input("\nOption > ")

            if option == "1":
                self.send_eth()
            elif option == "2":
                self.change_wallet()
            elif option == "3":
                self.settings()
            elif option == "4" or option == "exit":
                time.sleep(1.4)
                realistic_typing("\033[91mProgramm wird beendet...\033[0m")
                break
            else:
                print("\n\033[91mInvalid option\033[0m")


if __name__ == "__main__":
    client = Client()
    if client.wallets:
        client.current_wallet = client.wallets[0]
    else:
        client.current_wallet = {"address": "No wallet selected", "balance": 0.00}
    client.menu()
