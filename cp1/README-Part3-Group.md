# Coding Project 1 - Part 3

This directory contains our dispatch server `dispatch-server.py`, full client `full-client` and group feature client `full-client2` for Coding Project 1 - Part 3 for CSE 30264 - Computer Networks in Fall 2026.

| **Name** | **NetID** |
|---|---|
| Brandon Martinez | bmarti32 |
| Bae Reh | breh |

## Files

| **File** | **Description** |
|---|---|
| `dispatch/dispatch-server.py` | The dispatch server written in Python |
| `full-client` | The full client that talks to the dispatch server and calls `cgrab` |
| `full-client2` | The full client with our group features |
| `dispatch/clrtoscan/set6.txt` | Scanset using the public IP of `student11` |
| `cgrab.c` | The grab client written in C |
| `Makefile` | Builds `cgrab` in the `cp1` directory |

## Building

From the `cp1` directory:

```
make
```

## Running

### Dispatch Server

```
cd dispatch
python3 dispatch-server.py --port 54051 --maxfiles 2 --scansets clrtoscan/set5.txt
```

* `--maxfiles N` sends at most `N` random files per `CLRTOSCAN` (default `1000`).

* Handles `AUTHREQ`, `HELLO2` (`SIMPLE` or `HASH`), `RDYTOSCAN` and `CHANGESET`.

* Malformed packets are logged and skipped instead of crashing the server.

### Full Client

```
./full-client 129.74.152.141 54051 GoIrishBeatStanford AuthTest
./full-client 129.74.152.141 54051 RandomID 'AuthTestOnly39#'
```

* Logs in with `HELLO2 SIMPLE`, then loops: `RDYTOSCAN`, `cgrab` each file, sleep 15-30 seconds.

* A rejected token makes the client wait 5 seconds and log in again.

* Exits if the dispatch server does not reply within 5 seconds.

### Full Client 2

```
./full-client2 129.74.152.141 54051 GoIrishBeatStanford AuthTest
./full-client2 129.74.152.141 54051 GoIrishBeatStanford AuthTest --jobs 2
```

* Same arguments as `full-client`, plus `--jobs N` (default `4`) for the number of files grabbed at once.

## Group Features

### 1. HMAC-SHA256 Authentication

`HELLO2 SIMPLE` sends the password in plain text. The dispatch server and `full-client2` now use a challenge-response login instead, so the password is never sent:

```
C->S | AUTHREQ GoIrishBeatStanford
S->C | CHALLENGE 2f40beaeac9c407a6fefc3e7c4cd826a
C->S | HELLO2 GoIrishBeatStanford HASH 6281c0089b24b73f999b4b767a1a12310f29528b6e530685ac9a37c13ec851cb
S->C | RHELLO2 OK GoIrishBeatStanford 129.74.152.143 57913 HASH naVKRZbfz1u
```

* The server answers `AUTHREQ` with a random one-time nonce, only for IDs in the auth list.

* The client replies with `HMAC-SHA256(password, nonce)`, and the server checks it against its own copy of the password.

* Each nonce works only once, so a captured login cannot be replayed.

* IDs with no challenge (like `RandomID AuthTestOnly39#`) fall back to `HELLO2 SIMPLE`.

### 2. Interactive Shell

`full-client2` logs in, then gives a prompt with these commands:

* `list` - show the files to scan, numbered

* `grab [all | N ...]` - grab every file, or files `N ...` from `list`

* `watch` - the original full client loop, Control-C returns to the prompt

* `changeset SET [SECRET]` - switch the server's scanset (`SECRET` defaults to `SecretPwd`)

* `help` / `quit`

Each grab prints one `OK` or `FAIL` line per file with its MD5 or error. A dispatch timeout returns to the prompt instead of exiting.

### 3. Parallel Grabs with `concurrent.futures`

Each `cgrab` is its own process and TCP connection, so `grab` and `watch` run up to `--jobs` of them at once with a `ThreadPoolExecutor`, then print the results and total time.

### Example Session

Servers on `student11` (`129.74.152.141`), client on `student13` (`129.74.152.143`), using `set6.txt`.

Terminal 1, `student11`, grab server:

```
bmarti32@student11:~/classes/cse30264/networks/cp1/grab$ python3 stock/server-grab.py --port 54051 files.json
...
Grab Server now listening on 54051 for new connections
Waiting for a new connection....
# one connection per cgrab, all coming from student13
Connected by ('129.74.152.143', 36840)
Sending a chunk of 15 bytes
Waiting for a new connection....
Connected by ('129.74.152.143', 36856)
Sending a chunk of 15 bytes
Waiting for a new connection....
```

Terminal 2, `student11`, dispatch server:

```
bmarti32@student11:~/classes/cse30264/networks/cp1/dispatch$ python3 dispatch-server.py --port 54051 --maxfiles 2 --scansets clrtoscan/set6.txt
Dispatch Server listening on UDP port 54051 (maxfiles=2)...
# HMAC login: nonce out, digest back, the password is never sent
Received message: AUTHREQ GoIrishBeatStanford
Sending response: CHALLENGE 2f40beaeac9c407a6fefc3e7c4cd826a
Received message: HELLO2 GoIrishBeatStanford HASH 6281c0089b24b73f999b4b767a1a12310f29528b6e530685ac9a37c13ec851cb
Sending response: RHELLO2 OK GoIrishBeatStanford 129.74.152.143 57913 HASH naVKRZbfz1u
# 'list' in the shell, --maxfiles 2 picks 2 random files
Received message: RDYTOSCAN GoIrishBeatStanford naVKRZbfz1u
Sending response: CLRTOSCAN OK GoIrishBeatStanford 2 data/F002.dat 129.74.152.141 54051 AFE4c3982a data/F001.dat 129.74.152.141 54051 AuthSimple
# 'changeset' in the shell
Received message: CHANGESET SecretPwd clrtoscan/set6.txt
Sending response: CHANGESET OK clrtoscan/set6.txt
```

Terminal 3, `student13`, `full-client2`:

```
bmarti32@student13:~/classes/cse30264/networks/cp1$ ./full-client2 129.74.152.141 54051 GoIrishBeatStanford AuthTest
logged in as GoIrishBeatStanford via HASH (token naVKRZbfz1u)
type 'help' for commands
GoIrishBeatStanford> help
commands:
  list                    show the files the server wants scanned
  grab [all | N ...]      grab every file, or files N ... from list (4 at a time)
  watch                   list and grab every 15-30 seconds until Ctrl-C
  changeset SET [SECRET]  switch the scanset, (changeset scansets/set3.json)
  help                    show this message
  quit                    exit the shell
GoIrishBeatStanford> list
1 data/F002.dat 129.74.152.141:54051 AFE4c3982a
2 data/F001.dat 129.74.152.141:54051 AuthSimple
GoIrishBeatStanford> grab
OK data/F002.dat Computed MD5: 5cdba7cb556dd21f793c8d60a2150211
OK data/F001.dat Computed MD5: 5cdba7cb556dd21f793c8d60a2150211
2/2 grabbed in 0.01s
GoIrishBeatStanford> changeset clrtoscan/set6.txt
CHANGESET OK clrtoscan/set6.txt
GoIrishBeatStanford> quit
Shutting down Full Client gracefully...
```

## Caveats

* `full-client2` reads each dispatch reply with `recvfrom(65535)` instead of `recvfrom(2048)`. Anything past the buffer size is dropped, so with 2048 bytes a `CLRTOSCAN` with more than about 45 files is cut off and the client fails parsing it. 65535 is the largest possible UDP datagram. This was only changed in full-client2 not full-client.

* The stock grab server handles one connection at a time, so against a single grab server the `--jobs` connections wait in line and the parallel grabs are not faster. They are faster when the scanset spreads files across several grab servers.

* Both full clients save into the `scans` directory next to the script. Two clients running from the same checkout share it, so run them from separate copies of the repository.

## Credit

  * The `compute_file_md5` function in `cgrab.c` is based on OpenSSL
  site (https://wiki.openssl.org/index.php/EVP_Message_Digests).
