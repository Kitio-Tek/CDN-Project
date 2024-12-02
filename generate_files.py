# Script to generate files with 1kB of size, each file contains the same letter as its name

import string

file_size = 1 * 2**10  # 1kB
origin_files_folder = "origin/files/"

for letter in list(string.ascii_lowercase):
    with open(origin_files_folder + letter, "wb") as f:
        for _ in range(file_size):
            f.write(bytes(letter, "utf-8"))
