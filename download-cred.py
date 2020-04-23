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


def get_cred(cred_filename, index):
    cred_file = open(cred_filename, "r")
    for i, line in zip(range(index + 1), cred_file):
        if i == index:
            cred_file.close()
            return line.replace("\n", "").split("%")
    cred_file.close()
    return None


def get_sleep_time(cred_filename, itereation_time):
    cred_file = open(cred_filename, "r")
    line_counter = 0
    for line in cred_file:
        line_counter += 1
    cred_file.close()
    return itereation_time / line_counter


def get_cred_numbers(cred_filename):
    cred_file = open(cred_filename, "r")
    line_counter = 0
    for line in cred_file:
        line_counter += 1
    cred_file.close()
    return line_counter


def start(filename, cred_filename, iteration_time=140):
    list_file = open(filename, "r+")
    lines = list_file.readlines()
    list_file.close()

    current_cred_index = 0

    for i, line in enumerate(lines):
        line = line.replace("\n", "")
        if line.split("%")[1] == line.split("%")[2]:
            continue
        address = line.split("%")[0]
        print("starting the download for: ", address)
        counter = int(line.split("%")[1])
        while counter < int(line.split("%")[2]):
            cred = get_cred(cred_filename, current_cred_index)
            print("===================================================")
            print("Using credential: {}".format(cred[0]))
            download_start_time = time.time()
            process = subprocess.Popen(
                [
                    "youtube-dl",
                    address,
                    "-o",
                    "./downloads/%(playlist)s/%(chapter_number)s - %(chapter)s/%(playlist_index)s - %(title)s.%(ext)s",
                    "--username",
                    cred[0],
                    "--password",
                    cred[1],
                    "--playlist-items",
                    str(int(line.split("%")[1]) + 1),
                ],
                stdout=subprocess.PIPE,
            )
            while True:
                output = process.stdout.readline()
                if output:
                    try:
                        if "100%" in output.decode("UTF-8"):
                            counter += 1
                            current_cred_index = (
                                current_cred_index + 1
                            ) % get_cred_numbers(cred_filename)
                            replace(
                                filename,
                                "{}%{}%{}".format(
                                    address, counter - 1, line.split("%")[2]
                                ),
                                "{}%{}%{}".format(address, counter, line.split("%")[2]),
                            )
                            print(
                                "Downloaded part {} of {} of playlist number {} | {}".format(
                                    counter,
                                    line.split("%")[2],
                                    i + 1,
                                    line.split("%")[0],
                                )
                            )
                            download_finish_time = time.time()
                            download_duration = int(
                                download_finish_time - download_start_time
                            )
                            sleep_t = get_sleep_time(cred_filename, iteration_time)
                            # if download_duration < sleep_t:
                            #     print(
                            #         "Sleeping for {}s".format(
                            #             sleep_t - download_duration
                            #         )
                            #     )
                            #     time.sleep(sleep_t - download_duration)
                            print("Sleeping for {}s".format(sleep_t))
                            time.sleep(sleep_t)
                            break
                    except:
                        print("Some error in decoding the output! moving on ...")


if __name__ == "__main__":
    file = ""
    args = sys.argv
    file = args[args.index("--file") + 1]
    cred = args[args.index("--cred") + 1]
    # print("finding entries...")
    # format_list_entries(file, username, password)
    print("starting the download...")
    start(file, cred)
