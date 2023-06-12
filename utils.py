import copy
import json
import typing

import cv2
import numpy as np


def load_simple_matrix_from_txt(path: str) -> list[list]:
    to_return = []
    with open(path, encoding="utf-8") as file:
        text = file.readlines()
        for line in text:
            to_add = []
            for i in line:
                if i != "\n":
                    to_add.append(i)
            to_return.append(to_add)
    return to_return


def init_matrix_superposition(i: int, j: int, superposition: typing.Any) -> list[list[typing.Any]]:
    to_return = []
    for _ii in range(i):
        to_return.append([copy.deepcopy(superposition)] * j)
    return to_return


def get_pixel_mapped(to_map: list[list], dictionary: dict) -> np.ndarray:
    temp = np.array(to_map)
    u, inv = np.unique(temp, return_inverse=True)
    shape = list(temp.shape)
    shape.append(3)
    return np.array([dictionary[x] for x in u], dtype=np.uint8)[inv].reshape(shape)


def stretch_image(image: np.ndarray, x: int, y: int) -> np.ndarray:
    return np.kron(image, np.ones((x, y, 1), dtype=np.uint8))


def record_video(history: list[np.ndarray], name: str = "output.avi", fps: int = 30) -> None:
    writer = cv2.VideoWriter(name, cv2.VideoWriter_fourcc(*"MJPG"), fps,
                             (history[0].shape[1], history[0].shape[0]))
    for frame in history:
        writer.write(frame.astype("uint8"))

    writer.release()
    pass


def record_history(history: list[list], path_to_dictionary: str = "SimpleDataColorMap", x: int = 10,
                   y: int = 10, fps: int = 30) -> None:
    to_record = []
    with open(path_to_dictionary) as f:
        dictionary = json.load(f)

    for state in history:
        to_record.append(stretch_image(get_pixel_mapped(state, dictionary), x, y))
    temp = [to_record[-1] for x in range(int(fps * 1.5))]
    to_record.extend(temp)
    record_video(to_record, fps=fps)
