from typing import Set

def read_txt(txt_file: str):
    """Read bag names from a text file.

    Args:
        txt_file (str): Path to the text file containing bag names

    Returns:
        set: Set of bag names
    """
    bags = set()
    with open(txt_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            bags.add(line.strip())
    return bags


def write_bags(bags: Set[str], save_path: str):
    """Write bag names to a text file.

    Args:
        bags (Set[str]): Set of bag names to write
        save_path (str): Path to save the text file
    """
    with open(save_path, "w") as f:
        for bag in bags:
            f.write(bag)
            f.write("\n")
