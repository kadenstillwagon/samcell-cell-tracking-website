import numpy as np
from datetime import datetime
import os


def convert_image_names_to_datetimes(imgs_names):
    """
    Converts the img names in a multi-image upload into datetimes
    Name should contain: YYYYMMDDHHMMSS at the end
    Author(s): Kaden Stillwagon

    Args:
        imgs_names (np.ndarray): numpy array of the names of each of the image in a multi-image upload

    Returns:
        img_datetimes (list): list of datetimes corresponding to when each image in a multi-image upload was taken
    """
    img_datetimes = []
    for img_name in imgs_names:
        datetime_string = img_name[-16:-4]
        if datetime_string[-1] == ')':
            datetime_string = datetime_string[:-3]
        
        date_time = datetime.strptime(datetime_string, "%y%m%d%H%M%S")
        img_datetimes.append(date_time.strftime("%Y-%m-%dT%H:%M:%S"))

    return img_datetimes


if __name__ == '__main__':
    print(np.sort(os.listdir(f'projects/Dying HEKs 2025-03-17/cell_images')).shape)