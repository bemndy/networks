import socket
import argparse
import random
import string
import json 
import csv

def parse_args():
    parser = argparse.ArgumentParser(description="UDP Dispatch Server for part 2")
    parser.add_argument("--port", type=int, default=54000, help="Port between 54000 and 54150")
    parser.add_argument("--auth", type=str, default="auth.csv", help="Path to auth CSV file")
    parser.add_argument("--scansets", type=str, default="set1.json", help="Path to scanset JSON file")
    return parser.parse_args()

def generate_token():
    length = random.randint(8, 12)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    args = parse_args()
    port = args.port

    #make udp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    sock.settimeout(1.0)
    print(f"Dispatch Server listening on UDP port {port}...")

    tokens = {} #Map client id to token

    try:
        while True:
            try:
                data, addr = sock.recvfrom(2048)
                message = data.decode('utf-8').strip()
                parts = message.split()

                if not parts:
                    continue

                cmd = parts[0]

                if cmd == "HELLO2":
                    client_id = parts[1]
                    auth_mode = parts[2]
                    auth_info = parts[3]

                    #TODO:Verify client_id
                    token = generate_token()
                    tokens[client_id] = token

                    client_ip, client_port = addr
                    resp = f"RHELLO2 OK {client_id} {client_ip} {client_port} SIMPLE {token}\n"
                    sock.sendto(resp.encode('utf-8'), addr)
                elif cmd == "RDYTOSCAN":
                    client_id = parts[1]
                    provided_token = parts[2]

                    if client_id in tokens and tokens[client_id] == provided_token:
                        # TODO: Format CLRTOSCAN OK response using data from JSON file
                        pass
                    else:
                        resp = f"CLRTOSCAN BADPWD BadPassword\n"
                        sock.sendto(resp.encode('utf-8'), addr)

                elif cmd == "CHANGESET":
                    secret_pwd=parts[1]
                    set_name = parts[2]
                    # TODO: Handle dataset reload logic
                    pass

            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nShutting down Dispatch Server gracefully...")
        sock.close()

if __name__ == "__main__":
    main()
                