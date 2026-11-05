import socket
import argparse
import random
import string
import json
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    parser = argparse.ArgumentParser(description="UDP Dispatch Server for CP1 Part 2")
    parser.add_argument("--port", type=int, default=54000, help="Port between 54000 and 54150")
    parser.add_argument("--auth", type=str, default=os.path.join(HERE, "authlists/auth1.csv"), help="Path to auth CSV file")
    parser.add_argument("--scansets", type=str, default=os.path.join(HERE, "scansets/set1.json"), help="Path to scanset JSON file")
    parser.add_argument("--secret", type=str, default="SecretPwd", help="Secret password for CHANGESET")
    return parser.parse_args()

def load_auth_table(auth_filepath):
    auth_table = {}
    if os.path.exists(auth_filepath):
        with open(auth_filepath, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    auth_table[row[0].strip()] = row[1].strip()
    return auth_table

def load_scanset(scanset_filepath):
    """
    Loads scan set data from either a JSON file or a clrtoscan text file.
    Returns a dict with a list of file info dicts.
    """
    if not os.path.exists(scanset_filepath):
        print(f"Warning: File '{scanset_filepath}' not found.")
        return None

    # 1. Try reading as JSON
    try:
        with open(scanset_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data[0]["File"]:
                print(f"Loaded scan set from JSON: {data}")
                return data
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass  # Not a JSON file, try parsing as text below

    # 2. Parse as clrtoscan text file
    # Format per line: <FileName> <GrabServerIP> <GrabServerPort> <AuthToken>
    files = []
    try:
        with open(scanset_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    files.append({"File": parts[0], "Server": parts[1], "Port": parts[2], "Auth": parts[3]})
    except Exception as e:
        print(f"Error reading scanset text file: {e}")

    # 3. Fallback dummy item if file was empty
    if not files:
        return None

    return files
def generate_token():
    length = random.randint(8, 12)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    args = parse_args()
    port = args.port
    secret_pwd = args.secret
    auth_table = load_auth_table(args.auth)
    current_scanset = load_scanset(args.scansets)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    sock.settimeout(1.0)

    print(f"Dispatch Server listening on UDP port {port}...")
    tokens = {}  # Map client_id -> AUTHTOKEN

    try:
        while True:
            try:
                data, addr = sock.recvfrom(2048)
                message = data.decode('utf-8').strip()
                parts = message.split()
                print(f"Received message {' '.join(parts)}")

                if not parts:
                    continue

                cmd = parts[0]

                # --- HELLO2 <ID> <AUTHMODE> <AUTHINFO> ---
                if cmd == "HELLO2" and len(parts) >= 4:
                    client_id = parts[1]
                    auth_mode = parts[2]
                    auth_info = parts[3]

                    # Verify auth info (Check bypass or CSV table)
                    if auth_info == "AuthTestOnly39#" or auth_table.get(client_id) == auth_info:
                        token = generate_token()
                        tokens[client_id] = token
                        client_ip, client_port = addr
                        resp = f"RHELLO2 OK {client_id} {client_ip} {client_port} SIMPLE {token}\n"
                    else:
                        resp = f"RHELLO2 BADPWD {client_id}\n"

                    print(f"Sending response: {resp.strip()}")
                    sock.sendto(resp.encode('utf-8'), addr)


                # --- RDYTOSCAN <ID> <AUTHTOKEN> ---
                elif cmd == "RDYTOSCAN" and len(parts) >= 3:
                    client_id = parts[1]
                    provided_token = parts[2]

                    if client_id in tokens and tokens[client_id] == provided_token:
                        # Build the CLRTOSCAN response with formatted list of all files in scanset 
                        if current_scanset:
                            resp = f"CLRTOSCAN OK {client_id} {len(current_scanset)}"
                            for obj in current_scanset:
                                for fields in obj.values():
                                    resp += f" {fields}"
                        else:
                            resp = f"CLRTOSCAN OK {client_id} 0\n"
                    else:
                        resp = f"CLRTOSCAN BADPWD BadPassword\n"

                    print(f"Sending response: {resp.strip()}")
                    sock.sendto(resp.encode('utf-8'), addr)

                # --- CHANGESET <AUTH> <SetName> ---
                elif cmd == "CHANGESET" and len(parts) >= 3:
                    provided_auth = parts[1]
                    set_name = parts[2]

                    if provided_auth == secret_pwd:
                        new_scanset = load_scanset(os.path.join(HERE, set_name))
                        if new_scanset:
                            current_scanset = new_scanset
                            resp = f"CHANGESET OK {set_name}\n"
                        else:
                            resp = f"CHANGESET ERROR FileNotFound\n"
                    else:
                        resp = f"CHANGESET BADPWD\n"

                    print(f"Sending response: {resp.strip()}")
                    sock.sendto(resp.encode('utf-8'), addr)

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\nShutting down Dispatch Server gracefully...")
        sock.close()

if __name__ == "__main__":
    main()