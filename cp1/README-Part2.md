# Coding Project 1 - Part 2

This directory contains our grab client (`cgrab`) and the `batchgrab` helper script, our dispatch server `dispatch-server.py`, change-set script `change-set` and full client `full-client` for Coding Project 1 - Part 2 for CSE 30264 - Computer Networks in Fall 2026.

| **Name** | **NetID** |
|---|---|
| Brandon Martinez | bmarti32 |
| Bae Reh | breh

## Files

| **File** | **Description** |
|---|---|
| `cgrab.c` | The grab client written in C |
| `Makefile` | Builds `cgrab` in the `cp1` directory |
| `batchgrab` | Shell script that fetches every file listed in a `CLRTOSCAN` response |
| `dispatch/dispatch-server.py` | The dispatch server written in Python |
| `change-set` | Script to change the scanset on the dispatch server |
| `full-client` | The full client that talks to the dispatch server and calls `cgrab` |

## Building

From the `cp1` directory:

```
make
```

## Running

### cgrab

`cgrab` takes in four parameters: the name of the file, the hostname / IP address of the grab server, the port number for the grab server, and the authorization token to use.

```
./cgrab data/F001.dat 127.0.0.1 54000 AuthSimple
```

* The client sends `INFO FILE AUTH` first to get the size of the file, then sends `GRAB FILE AUTH` over the same connection.

* The file name is sent exactly as given (e.g. `data/F001.dat`) since that is how the grab server identifies the file.

* The downloaded file is saved into the `scans` sub-directory under the part of the name after the last `/`. For example, `data/F001.dat` is saved as `scans/F001.dat`. The `scans` directory is created if needed and an existing file is overwritten without prompting.

* The client keeps reading until it has received the number of bytes reported by `INFO`, so both text and binary files are saved exactly.

* The MD5 checksum of the saved file is printed so it can be compared by hand against the one from `INFO-RESP`.

### batchgrab

`batchgrab` takes in a single file containing the results of a `CLRTOSCAN` response, one file per line, and calls `cgrab` for each one.

```
./batchgrab dispatch/clrtoscan/set4.txt
```

* Lines starting with `#`, blank lines, and the `CLRTOSCAN`, `START-LIST`, and `END-LIST` lines are skipped.

* A file that fails (bad authorization, unknown file) prints an error and the script moves on to the next line.

## Dispatch Server

```
python3 dispatch/dispatch-server.py --port 54000 --auth authlists/auth1.csv --scansets scansets/set1.json --secret SecretPwd
```

* All arguments are optional. Defaults: port `54000`, `authlists/auth1.csv`, `scansets/set1.json`, secret `SecretPwd`.

* Handles `HELLO2`, `RDYTOSCAN` and `CHANGESET`. Each `HELLO2` generates a new 8-12 character `AUTHTOKEN`; only the newest token for an ID is accepted. `AuthTestOnly39#` only works for `HELLO2`.

* `CHANGESET SecretPwd <SetName>` accepts either a JSON from `scansets/` or a text file from `clrtoscan/`. A missing or empty set replies `CHANGESET ERROR FileNotFound`; a wrong password replies `CHANGESET BADPWD`.

## Change Set

```
./change-set 127.0.0.1 54000 scansets/set3.json
./change-set 127.0.0.1 54000 scansets/set3.json --secret WrongPwd
```

* Takes the server, port and new set name. The secret defaults to `SecretPwd`; `--secret` overrides it (used to test a denied change).

* Set names are relative to the `dispatch` directory.

## Full Client

```
./full-client 127.0.0.1 54000 GoIrishBeatStanford AuthTest
./full-client 127.0.0.1 54000 RandomID AuthTestOnly39#
```

* Sends `HELLO2` once, then loops: `RDYTOSCAN`, runs `cgrab` for every file in the `CLRTOSCAN`, then sleeps 15-30 seconds.

* Downloaded files are saved to `cp1/scans`.

* Control-C exits gracefully. A rejected `HELLO2` prints the error and exits.

## Caveats

* `batchgrab` calls `./cgrab`, so it needs to be run from the `cp1` directory.

* When the server returns an error, `cgrab` only prints the start of the response (e.g. `INFO-RESP`) rather than the full line. It still exits with a non-zero status.

* The MD5 checksum is printed but not automatically compared against the server's value.

* HERE = os.path.dirname(os.path.abspath(__file__)) was used in path-dependent arguments/subprocess calls in our python files, this was done to ensure that the scripts can be run from any directory for the grader ! (preferably from root of directory)

## Credit

  * The `compute_file_md5` function in `cgrab.c` is based on OpenSSL 
  site (https://wiki.openssl.org/index.php/EVP_Message_Digests).