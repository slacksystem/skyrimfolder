import pickle
from typing import List

from skyrimfolder.utils.filesystem import Directory, FileSystemEntry


# Save list to a pickle file
def save_to_pickle(entries: List[FileSystemEntry], filename: str):
    with open(filename, "wb") as file:
        pickle.dump(entries, file)


# Load list from a pickle file
def load_from_pickle(filename: str):
    with open(filename, "rb") as file:
        loaded_entries = pickle.load(file)
        return loaded_entries


def get_structure(path: str):
    directory = Directory(path)
    filelist = []
    for sub in directory.walk():
        filelist.append(sub.relative_to(directory))
    return filelist


def compare_files(path: str, filename: str):
    current_structure = set(get_structure(path))
    correct_structure = set(load_from_pickle(filename))
    extra_files = current_structure - correct_structure
    missing_files = correct_structure - current_structure
    if extra_files:
        print("The directory has the following extra file(s):")
        for file in extra_files:
            print(file)
    if missing_files:
        print("The directory is missing the following file(s):")
        for file in missing_files:
            print(file)
    print(
        "The directory is correct."
        if not extra_files and not missing_files
        else "The directory is incorrect."
    )


def main():
    compare_files("C:/Steam/steamapps/common/SkyrimVR", "SkyrimVR.pkl")


if __name__ == "__main__":
    main()
