# -*- encoding: utf-8 -*-
"""
@File    :   mark_imgs.py
@Time    :   2024/07/22 16:50:42
@Author  :   GauthierLi
@Version :   1.0
@Contact :   lwklxh@163.com
@License :   Copyright (C) 2024 GauthierLi, All rights reserved.
"""

"""
usage: mark_imgs.py [-h] [--max_depth MAX_DEPTH] [--read_online] [--sp_name SP_NAME] folder

Image viewer with marking and navigation.

positional arguments:
  folder                The folder containing images.

options:
  -h, --help            show this help message and exit
  --max_depth MAX_DEPTH
                        The maximum depth of recursion for searching images.
  --read_online         Force online reading of image folders.
  --sp_name SP_NAME     Names for marked images.
  
使用：
    a 退后一帧
    d 前进一帧
    n 前进一个文件夹
    b 后退一个文件夹
    p 标记一张图片，写入路径到/tmp/{sp_name}.txt中
    o 取消标记
    r 前进到第几帧
"""


import argparse
import os
import pickle
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Set, Tuple

import cv2
from tqdm import tqdm

from gtools.registry import ARGS, FUNCTION

MODULE_NAME = "mark_imgs"
CACHE_PATH = "/tmp/.cache/read_file_offline.pkl"
OUT_PATH = "/tmp/oup_img.txt"


@ARGS.regist(module_name="mark_imgs")
def parse_args():
    parser = argparse.ArgumentParser(
        description="Image viewer with marking and navigation."
    )
    parser.add_argument("--folder", type=str, help="The folder containing images.")
    parser.add_argument(
        "--max_depth",
        "-m",
        type=int,
        default=3,
        help="The maximum depth of recursion for searching images.",
    )
    parser.add_argument(
        "--read_online",
        "-r",
        action="store_true",
        help="Force online reading of image folders.",
    )
    parser.add_argument(
        "--sp_name", type=str, default=None, help="Names for marked images."
    )
    parser.add_argument(
        "--baglist-specify", "-b", default=None, type=str, help="specified baglist"
    )
    parser.add_argument(
        "--camera",
        "-c",
        type=str,
        choices=["1", "2", "3", "4", "5", "6", "t2"],
        help="choose camera",
    )
    parser.add_argument(
        "--mark-type",
        "-t",
        type=str,
        choices=["images", "bags"],
        help="mark type",
    )
    parser.add_argument(
        "--big",
        action="store_true",
        help="use big image size.",
    )
    return parser


def check_folder_for_images(folder: str) -> Optional[str]:
    """Check if a folder contains any image files. Return folder path if it does."""
    try:
        if any(
            file.lower().endswith((".png", ".jpg", ".jpeg"))
            for file in os.listdir(folder)
        ):
            return folder
    except PermissionError:
        pass
    return None


def list_image_folders(
    root_folder: str, max_depth: int, read_online: bool = False
) -> List[str]:
    """List directories containing images, considering max_depth."""

    def _list_image_folders(folder: str, current_depth: int) -> List[str]:
        if current_depth > max_depth:
            return []

        directories = set()
        try:
            # # 解包后的格式
            # pattern = r'[A-Za-z0-9-]+_[0-9]{8}_[0-9]{6}'
            # if re.search(pattern, folder.split('/')[-1]):
            #     directories.append(folder)
            subfiles = os.listdir(folder)
            for entry in tqdm(subfiles, total=len(subfiles)):
                if entry.endswith((".png", ".jpg", ".jpeg")):
                    directories.add(folder)
                    continue
                entry_path = os.path.join(folder, entry)
                if os.path.isdir(entry_path):
                    # matches = re.search(pattern, entry_path)
                    # if matches:
                    #     directories.append(entry_path)
                    # else:
                    directories = directories.union(
                        _list_image_folders(entry_path, current_depth + 1)
                    )
        except PermissionError:
            pass

        return directories

    if not read_online and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)

    with ThreadPoolExecutor(max_workers=128) as executor:
        future = executor.submit(_list_image_folders, root_folder, 0)
        directories = future.result()

    with open(CACHE_PATH, "wb") as f:
        pickle.dump(directories, f)

    return directories


def specify_bags(
    bag_list: Set[str], cam: str, max_depth: int, read_online: bool = False
) -> List[str]:
    if not read_online and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)
    if cam != "t2":
        cam = "camera_" + cam
    else:
        cam = "traffic_2"
    ROOT = r"/mnt/csi-data-aly/shared/public/gauthierli/data/clean_data/tag_optim"
    ROOTs = [
        os.path.join(ROOT, "foggy"),
        os.path.join(ROOT, "cloudy"),
        os.path.join(ROOT, "heavy_rainy"),
        os.path.join(ROOT, "rainy"),
        os.path.join(ROOT, "sand_storm"),
        os.path.join(ROOT, "small_rainy"),
        os.path.join(ROOT, "snow"),
        os.path.join(ROOT, "sunny"),
        r"/mnt/csi-data-gfs/lidar/deeproute_all/samples",
        r"/mnt/csi-data-aly/shared/public/gauthierli/data",
        r"/mnt/csi-data-aly/shared/public/gauthierli/data/drfile_snow_infer",
        r"/mnt/csi-data-aly/shared/public/gauthierli/hma_tmp_path/imgs",
    ]
    directories = set()
    for bag in tqdm(bag_list, total=len(bag_list)):
        if bag.endswith(".jpg"):
            cnts = bag.split("/")[:-1]
            cnts[-2] = cam
            directory = "/".join(cnts)
            directories.add(directory)
        else:
            if ("/" in bag) and ("." in bag):
                bag = bag.split("/")[-2]
            if "." in bag:
                bag = bag.split(".")[0]
            for root in ROOTs:
                if os.path.isdir(img_dir := os.path.join(root, cam, bag)):
                    directories.add(img_dir)
                    break

    directories = list(directories)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(directories, f)

    return directories


def list_images_in_folder(folder_path: str) -> List[str]:
    """List all image files in a given folder."""
    images = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    images.sort()
    return images


def show_image(
    image_path: str,
    folder_idx: int,
    total_folders: int,
    frame_idx: int,
    total_frame: int,
) -> None:
    """Show the image using OpenCV."""
    img = cv2.imread(image_path)
    h, w, _ = img.shape
    ratio = h / w
    nh, nw = int(ratio * 1920), 1920
    img = cv2.resize(img, (nw, nh))
    if not os.getenv("notext"):
        img = cv2.putText(
            img,
            "/".join(image_path.split("/")[-2:]),
            (48, 48),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        img = cv2.putText(
            img,
            f"Folder: {folder_idx}/{total_folders}, Frame: {frame_idx}/{total_frame}",
            (48, 88),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (0, 255, 0),
            2,
        )
    cv2.imshow("Image Viewer", img)


def save_txt(bags: list, file_name: str):
    """
    Save a list of strings to a text file.
    """
    with open(file_name, "w") as file:
        for bag in bags:
            file.write(f"{bag}\n")
    print(f"Saved {len(bags)} bags to {file_name}.")


def process_key_event(
    key: int,
    folder_index: int,
    image_index: int,
    image_folders: List[str],
    current_images: List[str],
    marked_paths: Dict[str, int],
    mark_type: str,
) -> Tuple[int]:
    """Process keyboard events and update indices accordingly."""
    if key == ord("q"):
        return "end", -1  # Exit the loop
    elif key == ord("d"):
        image_index += 1
    elif key == ord("a"):
        image_index -= 1
    elif key == ord("n"):
        image_index = len(current_images)
    elif key == ord("b"):
        folder_index -= 1
        image_index = "back"
    elif key == ord("p"):
        if image_index >= 0 and image_index < len(current_images):
            current_image_path = current_images[image_index]
            if mark_type == "bags":
                current_image_path = current_image_path.split("/")[-2]
            if current_image_path not in marked_paths:
                with open(OUT_PATH, "a") as f:
                    f.write(current_image_path + "\n")
                marked_paths[current_image_path] = (folder_index, image_index)
                print(f"Marked: {current_image_path} at {OUT_PATH}")
    elif key == ord("o"):
        current_image_path = (
            current_images[image_index]
            if 0 <= image_index < len(current_images)
            else None
        )
        if mark_type == "bags":
            current_image_path = current_image_path.split("/")[-2]
        if current_image_path and current_image_path in marked_paths:
            with open(OUT_PATH, "r") as f:
                lines = f.readlines()
            with open(OUT_PATH, "w") as f:
                for line in lines:
                    if line.strip() != current_image_path:
                        f.write(line)
            print(f"Deleted: {current_image_path}")
            del marked_paths[current_image_path]
    elif key == ord("r"):
        marked_index = int(input("Enter the index to return to: "))
        if marked_index in [v[1] for v in marked_paths.values()]:
            folder_index, _ = next(
                (k, v[1]) for k, v in marked_paths.items() if v[1] == marked_index
            )
            current_images = list_images_in_folder(image_folders[folder_index])
            image_index = marked_index

    return folder_index, image_index


def saved_bags(image_folders: List[str], bags: Set[str]):
    bags = list(bags)
    founded_bags = []
    matched_ids = []
    for folder in image_folders:
        bag_pre = folder.split("/")[-1]
        for i in range(len(bags)):
            if i in matched_ids:
                continue
            if bags[i].startswith(bag_pre):
                matched_ids.append(i)
                founded_bags.append(bags[i])
    save_txt(founded_bags, "/tmp/founded_bags.txt")


@FUNCTION.regist(module_name=f"mark_imgs")
def main(args: argparse.Namespace) -> None:
    if args.sp_name is not None:
        OUT_PATH = OUT_PATH.replace("oup_img", args.sp_name)
        print(OUT_PATH)

    with open(OUT_PATH, "w"):
        pass

    os.makedirs(r"/tmp/.cache", exist_ok=True)
    bags: Set[str] = set()
    if baglist_path := args.baglist_specify:
        with open(baglist_path, "r") as f:
            for line in f.readlines():
                bags.add(line.strip())
    folder: str = args.folder
    max_depth: int = args.max_depth
    read_online: bool = args.read_online
    if len(bags) == 0:
        image_folders: List[str] = list(
            list_image_folders(folder, max_depth, read_online)
        )
    else:
        image_folders: List[str] = list(
            specify_bags(bags, args.camera, max_depth, read_online)
        )
    print(len(image_folders))
    image_folders.sort()
    if args.mark_type == "bags":
        saved_bags(image_folders, bags)
    marked_paths: Dict[str, int] = {}

    folder_index: int = 0
    image_index: int = 0
    back_flag = 0
    current_images: List[str] = []

    while True:
        if folder_index < 0:
            print("First folder reached.")
            folder_index = 0
            image_index = 0
            continue
        if folder_index >= len(image_folders):
            print("No more folders to display.")
            folder_index = len(image_folders) - 1
            continue
        # Load images from the current folder
        if not current_images:
            current_folder = image_folders[folder_index]
            print(f"current_folder: {folder_index + 1} / {len(image_folders)}")
            current_images = list_images_in_folder(current_folder)
            image_index = 0 if back_flag == 0 else len(current_images) - 1
            back_flag = 0

        # print(image_index)
        # if not current_images:
        #     folder_index += 1
        #     current_images = []
        #     continue

        if image_index < 0:
            folder_index = max(0, folder_index - 1)
            current_images = []
            back_flag = 1
            continue
        elif image_index >= len(current_images):
            folder_index += 1
            current_images = []
            continue

        current_image_path: str = current_images[image_index]
        show_image(
            current_image_path,
            folder_index,
            len(image_folders),
            image_index,
            len(current_images),
        )

        key: int = cv2.waitKey(0) & 0xFF  # Wait for key press and get ASCII code

        folder_index, image_index = process_key_event(
            key,
            folder_index,
            image_index,
            image_folders,
            current_images,
            marked_paths,
            args.mark_type,
        )
        print(
            "\r# ------------------",
            "\nfolder_index: ",
            folder_index,
            "\nimage_index: ",
            image_index,
            "\nlen(current_images): ",
            len(current_images),
        )
        if image_index == "back":
            current_images = []

        if folder_index == "end":
            break

    cv2.destroyAllWindows()
