#!/usr/bin/env python3
# Token Generator & Account Creator
# Author: Kali-Tools
# Features: 
# - Generate various token types
# - Create accounts with configurable limits
# - Multi-threaded operations
# - Save results to files

import os
import sys
import time
import json
import random
import string
import threading
import argparse
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
MAX_ACCOUNTS = 1000  # Safety limit
DEFAULT_DELAY = 0.5   # Seconds between requests
TOKEN_LENGTH = 64
USERNAME_LENGTH = 8
PASSWORD_LENGTH = 12
DOMAINS = ["gmail.com", "yahoo.com", "protonmail.com", "outlook.com"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

class TokenGenerator:
    def __init__(self):
        self.generated = 0
        self.lock = threading.Lock()
        
    def generate(self, token_type="alphanumeric"):
        """Generate different types of tokens"""
        with self.lock:
            self.generated += 1
            
        if token_type == "hex":
            return ''.join(random.choices(string.hexdigits.upper(), k=TOKEN_LENGTH))
        elif token_type == "numeric":
            return ''.join(random.choices(string.digits, k=TOKEN_LENGTH))
        elif token_type == "uuid":
            return self._generate_uuid()
        elif token_type == "jwt":
            return self._generate_jwt()
        else:  # alphanumeric
            chars = string.ascii_letters + string.digits
            return ''.join(random.choices(chars, k=TOKEN_LENGTH))
    
    def _generate_uuid(self):
        return '-'.join([
            ''.join(random.choices(string.hexdigits.lower(), k=8)),
            ''.join(random.choices(string.hexdigits.lower(), k=4)),
            ''.join(random.choices(string.hexdigits.lower(), k=4)),
            ''.join(random.choices(string.hexdigits.lower(), k=4)),
            ''.join(random.choices(string.hexdigits.lower(), k=12))
        ])
    
    def _generate_jwt(self):
        header = json.dumps({"alg": "HS256", "typ": "JWT"}).encode('utf-8')
        payload = json.dumps({
            "sub": "user_" + ''.join(random.choices(string.digits, k=9)),
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600
        }).encode('utf-8')
        
        return (f"{header.decode('utf-8')}.{payload.decode('utf-8')}."
                f"{''.join(random.choices(string.hexdigits, k=64))}")

class AccountCreator:
    def __init__(self, delay=DEFAULT_DELAY):
        self.created = 0
        self.delay = delay
        self.lock = threading.Lock()
    
    def create_account(self, service="custom", username=None, password=None, email=None):
        """Simulate account creation with rate limiting"""
        time.sleep(self.delay)  # Rate limiting
        
        # Generate credentials if not provided
        if not username:
            username = self._generate_username()
        if not password:
            password = self._generate_password()
        if not email:
            email = self._generate_email(username)
        
        # Simulate account creation
        account_id = f"{service}_acc_{self.created+1:07d}"
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_agent = random.choice(USER_AGENTS)
        
        with self.lock:
            self.created += 1
            
        return {
            "service": service,
            "account_id": account_id,
            "username": username,
            "password": password,
            "email": email,
            "created_at": creation_date,
            "user_agent": user_agent,
            "status": "active" if random.random() > 0.1 else "pending"
        }
    
    def _generate_username(self):
        prefix = random.choice(["user", "admin", "test", "demo", "temp"])
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=USERNAME_LENGTH-4))
        return f"{prefix}_{suffix}"
    
    def _generate_password(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=PASSWORD_LENGTH))
    
    def _generate_email(self, username):
        domain = random.choice(DOMAINS)
        return f"{username}@{domain}"

def generate_tokens(num_tokens, token_type, output_file):
    """Generate tokens and save to file"""
    generator = TokenGenerator()
    tokens = []
    
    print(Fore.CYAN + f"\n[+] Generating {num_tokens} {token_type} tokens...")
    
    for i in range(num_tokens):
        token = generator.generate(token_type)
        tokens.append(token)
        sys.stdout.write(Fore.YELLOW + f"\rProgress: {i+1}/{num_tokens}")
        sys.stdout.flush()
    
    # Save to file
    with open(output_file, 'w') as f:
        for token in tokens:
            f.write(token + '\n')
    
    print(Fore.GREEN + f"\n\n[+] Saved {len(tokens)} tokens to {output_file}")

def create_accounts(num_accounts, service, output_file, delay=DEFAULT_DELAY, threads=5):
    """Create accounts with multi-threading"""
    if num_accounts > MAX_ACCOUNTS:
        print(Fore.RED + f"[-] Safety limit exceeded! Max accounts: {MAX_ACCOUNTS}")
        return
    
    creator = AccountCreator(delay)
    accounts = []
    lock = threading.Lock()
    
    print(Fore.CYAN + f"\n[+] Creating {num_accounts} {service} accounts with {threads} threads...")
    
    def worker():
        while True:
            with lock:
                if len(accounts) >= num_accounts:
                    return
                target = len(accounts) + 1
            
            account = creator.create_account(service)
            with lock:
                accounts.append(account)
            
            sys.stdout.write(Fore.YELLOW + f"\rProgress: {len(accounts)}/{num_accounts}")
            sys.stdout.flush()
    
    # Start threads
    thread_pool = []
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        thread_pool.append(t)
    
    # Wait for completion
    for t in thread_pool:
        t.join()
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(accounts, f, indent=2)
    
    print(Fore.GREEN + f"\n\n[+] Created {len(accounts)} accounts. Saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Token Generator & Account Creator",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Main commands
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Token generation command
    token_parser = subparsers.add_parser('tokens', help='Generate tokens')
    token_parser.add_argument('-n', '--number', type=int, required=True, help='Number of tokens to generate')
    token_parser.add_argument('-t', '--type', choices=['alphanumeric', 'hex', 'numeric', 'uuid', 'jwt'], 
                             default='alphanumeric', help='Token type (default: alphanumeric)')
    token_parser.add_argument('-o', '--output', default='tokens.txt', help='Output file (default: tokens.txt)')
    
    # Account creation command
    account_parser = subparsers.add_parser('accounts', help='Create accounts')
    account_parser.add_argument('-n', '--number', type=int, required=True, help='Number of accounts to create')
    account_parser.add_argument('-s', '--service', default='custom', help='Service name (default: custom)')
    account_parser.add_argument('-d', '--delay', type=float, default=DEFAULT_DELAY, 
                               help=f'Delay between requests in seconds (default: {DEFAULT_DELAY})')
    account_parser.add_argument('-o', '--output', default='accounts.json', help='Output file (default: accounts.json)')
    account_parser.add_argument('-T', '--threads', type=int, default=5, 
                               help='Number of threads to use (default: 5)')
    
    args = parser.parse_args()
    
    print(Fore.BLUE + Style.BRIGHT + r"""
     _______  ______   _______  _______  _______ 
    |   _   ||      | |       ||       ||       |
    |  |_|  ||  _    ||    ___||   _   ||  _____|
    |       || | |   ||   | __ |  | |  || |_____ 
    |       || |_|   ||   ||  ||  |_|  ||_____  |
    |   _   ||       ||   |_| ||       | _____| |
    |__| |__||______| |_______||_______||_______|
    """ + Style.RESET_ALL)
    
    try:
        if args.command == 'tokens':
            generate_tokens(args.number, args.type, args.output)
        elif args.command == 'accounts':
            create_accounts(args.number, args.service, args.output, args.delay, args.threads)
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Operation cancelled by user")
        sys.exit(1)

if __name__ == "__main__":
    main()
