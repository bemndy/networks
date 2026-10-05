# Coding Project 1 - Part 1

This directory contains our grab client (`cgrab`) and the `batchgrab` helper script for Coding Project 1 - Part 1 for CSE 30264 - Computer Networks in Fall 2026.

| **Name** | **NetID** |
|---|---|
| TODO | TODO |

## Files

| **File** | **Description** |
|---|---|
| `grab/cgrab.c` | The grab client written in C |
| `grab/Makefile` | Builds `cgrab` in the `grab` directory |
| `batchgrab` | Shell script that fetches every file listed in a `CLRTOSCAN` response |

## Building

From the `grab` directory:

```
make
```

**Note:** *`cgrab` links against OpenSSL (`-lcrypto`) to compute the MD5 checksum of the downloaded file. The OpenSSL development headers need to be present on the machine doing the build.*

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
cd grab
../batchgrab ../dispatch/clrtoscan/set4.txt
```

* Lines starting with `#`, blank lines, and the `CLRTOSCAN`, `START-LIST`, and `END-LIST` lines are skipped.

* A file that fails (bad authorization, unknown file) prints an error and the script moves on to the next line.

## Caveats

* `batchgrab` calls `./cgrab`, so it needs to be run from the directory containing `cgrab` (the `grab` directory).

* When the server returns an error, `cgrab` only prints the start of the response (e.g. `INFO-RESP`) rather than the full line. It still exits with a non-zero status.

* The MD5 checksum is printed but not automatically compared against the server's value.
