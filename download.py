import subprocess
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove
import time
import json
import sys


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, "w") as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


# def get_playlist_length(address):
#     s = subprocess.run(
#         [
#             "youtube-dl",
#             address,
#             "--get-duration",
#             "--username",
#             "amir.mohseni7697@yahoo.com",
#             "--password",
#             "09137149220amM!",
#         ],
#         capture_output=False,
#     )
#     return len(s.stdout.decode("UTF-8").split("\n")) - 1


def get_plural_length(address, username, password):
    n_entries = 0
    p = subprocess.Popen(
        [
            "youtube-dl",
            address,
            "--dump-json",
            "--username",
            username,
            "--password",
            password,
        ],
        stdout=subprocess.PIPE,
    )
    while True:
        output = p.stdout.readline()
        if "n_entries" in output.decode("UTF-8"):
            pairs = output.decode("UTF-8").split(",")
            for pair in pairs:
                if "n_entries" in pair:
                    n_entries = pair.split(" ")[2]
            p.terminate()
            break
    return n_entries


def format_list_entries(filename, username, password):
    list_file = open(filename, "r+")
    lines = list_file.readlines()
    list_file.close()
    print("sleeping for 130 seconds...")
    time.sleep(130)
    for line in lines:
        line = line.replace("\n", "")
        if line.split("%")[2] != "0":
            continue
        address = line.split("%")[0]
        length = get_plural_length(address, username, password)
        print("Found length of {}".format(length))
        replace(filename, line, "{}%0%{}".format(line.split("%")[0], length))
        print("sleeping for 130 seconds...")
        time.sleep(130)


def start(filename, username, password, min_interval="120", max_interval="150"):
    list_file = open(filename, "r+")
    lines = list_file.readlines()
    list_file.close()

    for i, line in enumerate(lines):
        line = line.replace("\n", "")
        if line.split("%")[1] == line.split("%")[2]:
            continue
        address = line.split("%")[0]
        print("starting the download for: ", address)
        process = subprocess.Popen(
            [
                "youtube-dl",
                address,
                "-o",
                "./downloads/%(playlist)s/%(chapter_number)s - %(chapter)s/%(playlist_index)s - %(title)s.%(ext)s",
                "--min-sleep-interval",
                min_interval,
                "--max-sleep-interval",
                max_interval,
                "--username",
                username,
                "--password",
                password,
                "--playlist-start",
                str(int(line.split("%")[1]) + 1),
            ],
            stdout=subprocess.PIPE,
        )
        counter = int(line.split("%")[1])
        while True:
            output = process.stdout.readline()
            if counter == int(line.split("%")[2]):
                break
            if output:
                try:
                    if "100%" in output.decode("UTF-8"):
                        counter += 1
                        replace(
                            filename,
                            "{}%{}%{}".format(address, counter - 1, line.split("%")[2]),
                            "{}%{}%{}".format(address, counter, line.split("%")[2]),
                        )
                        print(
                            "Downloaded part {} of {} of playlist number {} | {}".format(
                                counter, line.split("%")[2], i + 1, line.split("%")[0]
                            )
                        )
                    if "Sleeping" in output.decode("UTF-8") or "%" in output.decode(
                        "UTF-8"
                    ):
                        print(output.decode("UTF-8"))
                except:
                    print("Some error in decoding the output! moving on ...")


if __name__ == "__main__":
    username = ""
    password = ""
    file = ""
    args = sys.argv
    try:
        username = args[args.index("--username") + 1]
        password = args[args.index("--password") + 1]
    except:
        print("moving on without username and password")
    file = args[args.index("--file") + 1]
    print("finding entries...")
    format_list_entries(file, username, password)
    print("starting the download...")
    start(file, username, password)
