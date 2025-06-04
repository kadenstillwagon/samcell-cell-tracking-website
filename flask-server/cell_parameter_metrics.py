import numpy as np
import mahotas
import cv2
import os
import time

#BASE METHODS

__show_border__ = False

"""
This method takes an image name and an optional cell number and returns the corresponding cell mask.
If no cell number is provided, a random cell will be selected.
"""
def get_cell_mask(project, image_date, cell=None, seg_out=None):
    if seg_out is None:
      seg_out = np.loadtxt(f'./projects/{project}/cell_images/{image_date}/segmentation_output.csv', delimiter=',')

    count = len(np.unique(seg_out)) - 1 # subtract 1 for background
    cell = np.random.randint(count+1) if cell is None else cell

    cell_mask = np.where(seg_out == cell, 1, 0)
    if np.sum(cell_mask) == 0:
        raise ValueError("There is no cell mask at this index.")
    else:
        return np.where(seg_out == cell, 1, 0)

"""
This method takes a mask and returns the corresponding cropped mask.
"""
def get_crop_mask(mask):
    return mask[np.argwhere(mask != 0)[:, 0].min():np.argwhere(mask != 0)[:, 0].max()+1, np.argwhere(mask != 0)[:, 1].min():np.argwhere(mask != 0)[:, 1].max()+1]

"""
This method takes an image name and returns the corresponding image cell.
"""
def get_img_cell_mask(project, image_date, mask):
    img = cv2.imread(f'./projects/{project}/cell_images/{image_date}/image_input.png', cv2.IMREAD_GRAYSCALE)
    return img*mask


def get_num_cell_segments(project, image_date):
    seg_out = np.loadtxt(f'./projects/{project}/cell_images/{image_date}/segmentation_output.csv', delimiter=',')
    return int(np.max(np.unique(seg_out))) + 1


def get_border_naive(mask:np.ndarray) -> np.ndarray:
    """
    Get Border Naive (as opposed to other potential approaches)
    Helper function checks neighbors of every pixel to see if it is a border pixel
    Author(s): Emilio Aponte

    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

    Returns:
        np.ndarray: Array of shape (W,H) representing a binary mask of the border. 1 = border, 0 = not border.
    """
    border = np.zeros(mask.shape, dtype=np.uint8)
    padded_mask = np.pad(mask, pad_width=1)
    for i in range(border.shape[0]):
        for j in range(border.shape[1]):
            if padded_mask[i+1, j+1] == 1 and (padded_mask[i, j+1] == 0 or padded_mask[i+2, j+1] == 0 or padded_mask[i+1, j] == 0 or padded_mask[i+1, j+2] == 0):
                border[i, j] = 1
    return border

def incenter(mask:np.ndarray) -> np.ndarray:
    """
    Central Coordinates (incenter)
    The incenter of a cell is the point inside the cell furthest from the edges.
    We find the point whose maximal edge distance is minimal.
    Author(s): Emilio Aponte


    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

    Returns:
        np.ndarray: Array of shape (2,) representing the incenter coordinates.
    """
    mask_coords = np.argwhere(mask)
    border_coords = np.argwhere(get_border_naive(mask))

    return mask_coords[np.linalg.norm(mask_coords[:, np.newaxis] - border_coords, axis=2).max(axis=1).argmin()]

def perimeter(mask:np.ndarray) -> float:
    """
    Perimeter
    The perimeter of a cell is the sum of the lengths of its edges.
    We order the border pixels by incenter angle and sum adjacent pixel distances (Euclidean L2 norm).
    Author(s): Emilio Aponte

    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

    Returns:
        float: The perimeter of the cell.
    """
    border = np.argwhere(get_border_naive(mask))
    dist = border - incenter(mask)
    border = border[np.argsort(np.arctan2(dist[:, 0], dist[:, 1]))]
    return np.sum(np.linalg.norm(border - np.roll(border, 1, axis=0), axis=1))

def area(mask:np.ndarray) -> float:
    """
    Area
    The area of a cell is the number of pixels in its interior.
    We count the number of interior pixels.
    Author(s): Emilio Aponte

    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

    Returns:
        float: The area of the cell.
    """
    return np.sum(mask, dtype=float)

def bounding_radii(mask:np.ndarray) -> tuple[float, float]:
    """
    Bounding circle radii
    The radii of inscribed and conscribed circles.
    We find the minimum and maximum edge distance from the incenter.
    Author(s): Emilio Aponte

    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

    Returns:
        tuple: The minimum and maximum edge distance from the incenter.
    """
    in_c = incenter(mask)
    dist = np.linalg.norm(in_c - np.argwhere(get_border_naive(mask)), axis=1)
    return dist.min(), dist.max()

def radial_profile(mask:np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Radial profile
    The distance from incenter to edge as a function of rotation
    We find the distance from the incenter to each boundary pixel.
    Author(s): Emilio Aponte

    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

    Returns:
        tuple: The angles and distances from the incenter to each boundary pixel.
    """
    dist = np.argwhere(get_border_naive(mask)) - incenter(mask)
    atan = np.arctan2(dist[:, 0], dist[:, 1])
    return np.sort(atan), np.linalg.norm(dist, axis=1)[np.argsort(atan)]


#########################
    #CELL PARAMETERS
#########################
def find_center_new(cropped_image):
  """
  Find Center
  Finds the visual center of the image by finding the pixel that has the minimal sum of the different between the pixels below/above it and left/right of it.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      tuple: Row, column coordinates of the center of the cell mask.
  """
  closest_center_metric = 100000
  closest_center_coords = (0, 0)
  for i in range(len(cropped_image)):
    for j in range(len(cropped_image[i])):
      if cropped_image[i][j] > 0:
        num_above = np.count_nonzero(cropped_image[0:i, :])
        num_below = np.count_nonzero(cropped_image[i:len(cropped_image), :])
        num_left = np.count_nonzero(cropped_image[:, 0:j])
        num_right = np.count_nonzero(cropped_image[:, j:len(cropped_image[i])])

        center_metric = np.abs(num_above - num_below) + np.abs(num_left - num_right)
        if center_metric < closest_center_metric:
          closest_center_metric = center_metric
          closest_center_coords = (i, j)

  return closest_center_coords


############################
  #PIXEL INTENSITY METRICS
############################
# Read in original image
def get_sample_image(project, image_date = '2025-01-15_14:35:11'):
  """
  Get Sample Image
  We get the sample image from the outputs folder and return it as a grayscale image.
  Author(s): Kaden Stillwagon

  Args:
    img_name (str): name of image folder that contains raw output and original image.

  Returns:
      (np.ndarray): pixel-matrix representation of grayscale image
  """
  image = cv2.imread(f'./projects/{project}/cell_images/{image_date}/image_input.png')
  gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  return gray_image

def get_sample_segmentation(project, image_date = '2025-01-15_14:35:11'):
  """
  Get Sample Segmentation
  We get the sample segmentation from the folder and return it.
  Author(s): Kaden Stillwagon

  Args:
    image_date (str): name of image and segmentation folder that contains raw output and original image.

  Returns:
      (np.ndarray): pixel-matrix representation of image segmentations
  """
  segmentation = np.loadtxt(f'./projects/{project}/cell_images/{image_date}/segmentation_output.csv', delimiter=',')

  return segmentation



def get_highlighted_mask(image, mask):
  rgb_image = np.stack((image,) * 3, axis=-1)

  mask_indices = np.where(mask > 0)
  mask_indices_x = mask_indices[0]
  mask_indices_y = mask_indices[1]
  
  for i in range(len(mask_indices_x)):
    rgb_image[mask_indices_x[i]][mask_indices_y[i]] = [255, 0, 0]

  return rgb_image


def get_mask_pixel_intensities(image, mask):
  """
  Get Mask Pixel Intensities
  We multipy the (grayscaled) original image by the cell mask so that only the pixels of the cell mask (with their original intensities) are preserved.
  All other pixels are set to 0.
  Author(s): Kaden Stillwagon

  Args:
    image (np.ndarray): array of shape (W,H) representing a grayscale image.
    mask (np.ndarray): array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background

  Returns:
      (np.ndarray): array of shape (W,H) representing a grayscale image with only the pixels of the cell mask preserved.
  """
  mask_pixel_intensities = np.multiply(image, mask)

  return mask_pixel_intensities


def calculate_gradient_pixel_by_pixel(cropped_image, original_image):
  """
  Calculate Gradient Pixel By Pixel
  Calculates the gradient magnitude and orientation of the cell mask by calculating the gradient magnitude and orienation of each pixel in the mask and averaging over the entire mask.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    original_image (np.ndarray): array of shape (W,H) representing a grayscale image.

  Returns:
      tuple: The average magnitude and direction of the gradients in the cell mask.
  """
  # inspiration: https://pyimagesearch.com/2021/05/12/image-gradients-with-opencv-sobel-and-scharr/#:~:text=North:,the%20x%20and%20y%20direction.
  gradient_magnitude = 0
  gradient_orientation = 0

  for i in range(0, len(cropped_image)):
    if np.sum(cropped_image[i]) > 0:
      for j in range(0, len(cropped_image[i])):
        if i > 0 and i < len(cropped_image) - 1 and j > 0 and j < len(cropped_image[i]) - 1 and cropped_image[i][j] > 0 and cropped_image[i+1][j] > 0 and cropped_image[i-1][j] > 0 and cropped_image[i][j+1] > 0 and cropped_image[i][j-1] > 0:
          d_x = int(original_image[i+1][j]) - int(original_image[i-1][j])
          d_y = int(original_image[i][j+1]) - int(original_image[i][j-1])

          magnitude = np.sqrt(d_x**2 + d_y**2)
          orientation = np.arctan2(d_y, d_x) * (180 / np.pi)

          gradient_magnitude += magnitude
          gradient_orientation += orientation

  avg_gradient_magnitude = gradient_magnitude / np.count_nonzero(cropped_image)
  avg_gradient_orientation = gradient_orientation / np.count_nonzero(cropped_image)

  return avg_gradient_magnitude, avg_gradient_orientation


def crop_to_mask(masked_image):
  """
  Crop To Mask
  Crop the masked image to the size of the cell mask.
  Author(s): Kaden Stillwagon

  Args:
    masked_image (np.ndarray): array of shape (W,H) representing a grayscale image with only the pixels of the cell mask preserved.

  Returns:
      (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
  """
  coords = np.where(masked_image > 0)
  top = np.min(coords[0])
  bottom = np.max(coords[0])
  left = np.min(coords[1])
  right = np.max(coords[1])

  cropped_image = masked_image[top:bottom+1, left:right+1]

  return cropped_image


def calculate_gradient_layer_by_layer(cropped_image):
  """
  Calculate Gradient Layer by Layer
  Calculates the gradient magnitude and orientation of the cell mask.
  First computes the average pixel intensity of each layer of the cell mask.
  Calculates the absolute difference between the average pixel intensity in one layer to the next (moving inwards) and sums over each layer of the mask.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      tuple(np.ndarray, float): An array of the average pixel intensities from each layer, and the summation of change in average pixel intensity from layer to layer (the gradient metric).
  """
  cont = True
  cropped_image_last = cropped_image.copy()
  cropped_image_next = cropped_image.copy()
  layer_avgs = []
  while cont:
    removed_layer = []
    possible_points = np.argwhere(cropped_image_last > 0)
    for point in possible_points:
      if point[0] > 0 and point[0] < len(cropped_image_last) - 1 and point[1] > 0 and point[1] < len(cropped_image_last[point[0]]) - 1 and cropped_image_last[point[0] + 1][point[1]] > 0 and cropped_image_last[point[0] - 1][point[1]] > 0 and cropped_image_last[point[0]][point[1] + 1] > 0 and cropped_image_last[point[0]][point[1] - 1] > 0:
        continue
      else:
        cropped_image_next[point[0]][point[1]] = 0
        removed_layer.append(cropped_image[point[0]][point[1]])

    layer_avgs.append(np.mean(removed_layer))
    cropped_image_last = cropped_image_next.copy()
    if np.sum(cropped_image_last) == 0:
      cont = False

  gradient_metric = 0
  for i in range(1, len(layer_avgs)):
    gradient_metric += np.abs(layer_avgs[i] - layer_avgs[i-1])

  #gradient_metric /= len(layer_avgs)

  return layer_avgs, gradient_metric


def display_layer_gradient(cropped_image):
  """
  Display Layer Gradient
  Computes the average pixel intensity of each layer of the cell mask and displays the mask with each layer colored by its average pixel intensity.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      N/A
  Displays:
      Cropped cell mask with each layer colored by its average pixel intensity.
  """
  cont = True
  layer_avgs = []
  layer_coords = []
  while cont:
    new_mask = []
    removed_layer = []
    curr_layer_coords = []
    for i in range(len(cropped_image)):
      new_mask_row = []
      for j in range(len(cropped_image[i])):
        if cropped_image[i][j] > 0 and i > 0 and i < len(cropped_image) - 1 and j > 0 and j < len(cropped_image[i]) -1 and cropped_image[i+1][j] > 0 and cropped_image[i-1][j] > 0 and cropped_image[i][j+1] > 0 and cropped_image[i][j-1] > 0:
            new_mask_row.append(cropped_image[i][j])
        else:
          new_mask_row.append(0)
          if cropped_image[i][j] > 0:
            removed_layer.append(cropped_image[i][j])
            curr_layer_coords.append((i, j))
      new_mask.append(new_mask_row)

    layer_avgs.append(np.mean(removed_layer))
    layer_coords.append(curr_layer_coords)
    if np.sum(new_mask) == 0:
      cont = False
    else:
      cropped_image = np.array(new_mask)

  new_img = cropped_image.copy()
  for i in range(len(cropped_image)):
    for j in range(len(cropped_image[i])):
      for k in range(len(layer_coords)):
        if (i, j) in layer_coords[k]:
          new_img[i][j] = layer_avgs[k]

  #plt.imshow(new_img, cmap='gray')
  #plt.show()


  #gradient_metric /= len(layer_avgs)


def calculate_pixel_intensity_metrics(cropped_image, display_histogram=False):
  """
  Calculate Pixel Intensity Metrics
  Computes the mean intensity, standard deviation of intensity, max intensity, min intensity, and intensity range of the cell mask.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      tuple: The mean intensity, standard deviation of intensity, max intensity, min intensity, and intensity range of the cell mask.
  Displays:
      Histogram of pixel intensities in the cell mask.
  """
  # source: https://static-content.springer.com/esm/art%3A10.1186%2Fgb-2006-7-10-r100/MediaObjects/13059_2006_1368_MOESM4_ESM.pdf
    # for metric idea
  #display_histogram = True
  mean_intensity = np.mean(cropped_image, where=cropped_image > 0, dtype=float)
  std_intensity = np.std(cropped_image, where=cropped_image > 0, dtype=float)
  max_intensity = float(np.max(cropped_image, where=cropped_image > 0, initial=0))
  min_intensity = float(np.min(cropped_image, where=cropped_image > 0, initial=255))
  intensity_range = max_intensity - min_intensity

  if display_histogram:
    flattened_cropped_image = cropped_image.flatten()
    # plt.hist(flattened_cropped_image, bins='auto', range=(min_intensity, max_intensity))
    # plt.title('Histogram of Pixel Intensities')
    # plt.xlabel('Pixel Intensity')
    # plt.ylabel('Frequency')
    #plt.show()

  # haralick measures "texture" of the image (returns 4x13 matrix describing texture)
    # sources:
      #https://cvexplained.wordpress.com/2020/07/22/10-6-haralick-texture/
      #https://onlinelibrary.wiley.com/doi/full/10.1002/cyto.a.23984#support-information-section
  # features = mahotas.features.haralick(cropped_image).mean(axis=0)
  # features = mahotas.features.haralick(cropped_image)
  # print(features)

  return mean_intensity, std_intensity, max_intensity, min_intensity, intensity_range


def count_pixel_neighbors(mask, i, j):
  """
  Count Pixel Neighbors
  Counts the number of pixels bordering a pixel (left, right, above, below)
  Author(s): Kaden Stillwagon

  Args:
    mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

  Returns:
      int: The number of pixels bordering a pixel (left, right, above, below).
  """
  neighbors = 0

  if i > 0 and mask[i-1][j] > 0:
    neighbors += 1
  if i < len(mask) - 1 and mask[i+1][j] > 0:
    neighbors += 1
  if j > 0 and mask[i][j-1] > 0:
    neighbors += 1
  if j < len(mask[i]) - 1 and mask[i][j+1] > 0:
    neighbors += 1

  return neighbors

def perimeter_by_border(mask):
  """
  Perimeter By Border
  Calculates perimeter of the mask by counting the number of edges in the mask.
  For each pixel in the border of the mask, calculate 4 - its number of neighbors, sum over each pixel in the border.
  Author(s): Kaden Stillwagon

  Args:
    mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

  Returns:
      int: The perimeter of the mask represented by the number of edges in the mask.
  """
  perimeter = 0
  #curr_layer_coords = []
  for i in range(len(mask)):
    if np.sum(mask[i]) == 0:
      continue
    for j in range(len(mask[i])):
      if mask[i][j] > 0:
        if i > 0 and i < len(mask) - 1 and j > 0 and j < len(mask[i]) -1 and mask[i+1][j] > 0 and mask[i-1][j] > 0 and mask[i][j+1] > 0 and mask[i][j-1] > 0:
            continue
        else:
          perimeter += (4 - count_pixel_neighbors(mask, i, j))
          #curr_layer_coords.append((i, j))

  return perimeter


def find_center(cropped_image):
  """
  Find Center
  Finds the visual center of the image by stripping away the layers of the cell mask until reaching the center pixels.
  If multiple pixels remain in final layer, calculate average of their coords and find the closest pixel to that average.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      tuple: Row, column coordinates of the center of the cell mask.
  """
  cont = True
  original_cropped_image = cropped_image.copy()
  while cont:
    new_mask = []
    for i in range(len(cropped_image)):
      new_mask_row = []
      for j in range(len(cropped_image[i])):
        if cropped_image[i][j] > 0 and i > 0 and i < len(cropped_image) - 1 and j > 0 and j < len(cropped_image[i]) -1 and cropped_image[i+1][j] > 0 and cropped_image[i-1][j] > 0 and cropped_image[i][j+1] > 0 and cropped_image[i][j-1] > 0:
            new_mask_row.append(cropped_image[i][j])
        else:
          new_mask_row.append(0)
      new_mask.append(new_mask_row)

    if np.sum(new_mask) == 0:
      cont = False
    else:
      cropped_image = np.array(new_mask)

  if np.count_nonzero(cropped_image) > 1:
    x_tot = 0
    y_tot = 0
    for i in range(len(cropped_image)):
      if np.sum(cropped_image[i]) > 0:
        for j in range(len(cropped_image[i])):
          if cropped_image[i][j] > 0:
            x_tot += i
            y_tot += j

    x_center = x_tot / np.count_nonzero(cropped_image)
    y_center = y_tot / np.count_nonzero(cropped_image)

    closest_x = 0
    closest_y = 0
    closest_dist = 1500
    for i in range(len(original_cropped_image)):
      if np.sum(original_cropped_image[i]) > 0:
        for j in range(len(original_cropped_image[i])):
          if original_cropped_image[i][j] > 0:
            x_dist = i - x_center
            y_dist = j - y_center
            dist = np.sqrt(x_dist**2 + y_dist**2)
            if dist < closest_dist:
              closest_dist = dist
              closest_x = i
              closest_y = j

    cropped_image = np.zeros(cropped_image.shape)
    cropped_image[closest_x][closest_y] = 255

  #plt.imshow(cropped_image, cmap='gray')
  #plt.show()

  center_coords = np.where(cropped_image > 0)

  return (center_coords[0][0], center_coords[1][0])



########################
  #SURROUNDING CELLS
########################



def get_perimeter(mask):
    """
    Perimeter of Cell
    Returns a binary mask of the exterior perimeter (not including cell)
    Author(s): Alissa Gaddis

    Args:
        mask (np.ndarray): Array of shape (W,H) representing a binary mask of the
        cell. 1 = cell, 0 = background.

    Returns:
        border (np.ndarray): Array of shape (W,H) of a binary mask of the
        exterior perimeter. 1 = perimeter, 0 = background.
    """
    border = np.zeros(mask.shape, dtype=np.uint8)
    padded_mask = np.pad(mask, pad_width=((1,1),))

    dim_1_min = max(0, np.argwhere(padded_mask != 0)[:, 0].min()-1)
    dim_1_max = min(padded_mask.shape[0]-1, np.argwhere(padded_mask != 0)[:, 0].max()+2)
    dim_2_min = max(0, np.argwhere(padded_mask != 0)[:, 1].min()-1)
    dim_2_max = min(padded_mask.shape[1]-1, np.argwhere(padded_mask != 0)[:, 1].max()+2)
    # print(dim_1_min, ":", dim_1_max, ",", dim_2_min, ":", dim_2_max)

    crop_mask = padded_mask[dim_1_min:dim_1_max-1, dim_2_min:dim_2_max]
    # print(crop_mask.shape)
    crop_border = np.zeros(crop_mask.shape, dtype=np.uint8)
    for i in range(1, crop_border.shape[0]-2):
        for j in range(1, crop_border.shape[1]-2):
            if crop_mask[i,j] == 0 and (crop_mask[i-1,j-1] == 1 or crop_mask[i-1,j] == 1 or crop_mask[i-1,j+1] == 1
                                        or crop_mask[i,j-1] == 1                            or crop_mask[i,j+1] == 1
                                        or crop_mask[i+1,j-1] == 1 or crop_mask[i+1,j] == 1 or crop_mask[i+1,j+1] == 1):
                crop_border[i,j] = 1

    if dim_1_max > border.shape[0]:
        adjust_amount = (dim_1_max - border.shape[0]) + 1
        dim_1_min -= adjust_amount
        dim_1_max -= adjust_amount
    if dim_2_max > border.shape[1]:
        adjust_amount = (dim_2_max - border.shape[1]) + 1
        dim_2_min -= adjust_amount
        dim_2_max -= adjust_amount

    border[dim_1_min:dim_1_max-1, dim_2_min:dim_2_max] = crop_mask

    return border


def get_surrounding_cell_count(project, image_date, cell):
  """
  Surrounding Cell Count
  Returns the number of cells surrounding a mask. If no cell specified, one is
  chosen at random.
  Author(s): Alissa Gaddis

  Args:
      img_name (string): name of reference image to the raw_output from SamCell.
      cell (int, optional): cell to find neighbors of.

  Returns:
      The number of neighboring cells to a specified cell.
  """
  if (cell is not None and type(cell) is int):
    mask = get_cell_mask(project, image_date, cell)
  else:
    mask = get_cell_mask(project, image_date)

  seg_out = np.loadtxt(f'./projects/{project}/cell_images/{image_date}/segmentation_output.csv', delimiter=',')
  border = get_perimeter(mask)

  if __show_border__:
    plt.imshow(get_crop_mask(border*seg_out))
    plt.title('Surrounding Cells')
    #plt.show()

  cell_count = np.unique(seg_out*border)
  return len(cell_count)-1 if 0 in cell_count else len(cell_count)



###########################
  #MAJOR AND MINOR AXES
###########################

def is_edge(mask, point):
  """
  Checks if a given point in a mask is an edge.

  Args:
    mask: a binary array with 1 representing the shape and 0 background
    point: the point within the mask

  Returns:
    boolean
  """
  if point[0] >= mask.shape[0] or point[1] >= mask.shape[1]: return False
  if mask[point[0], point[1]] != 1: return False

  dim_1_min = max(0, point[0]-1)
  dim_1_max = min(mask.shape[0]-1, point[0]+1)
  dim_2_min = max(0, point[1]-1)
  dim_2_max = min(mask.shape[1]-1, point[1]+1)

  return any(mask[dim_1_min:dim_1_max, dim_2_min:dim_2_max].reshape(-1) == 0)


from scipy.ndimage import convolve

def find_edges(binary_mask, cutoff=0):
  """
  Uses a convolution filter to find only the edges of the shape

  args:
  binary_mask: the binary mask of the shape, use the full image size without cropping
  cutoff: the cutoff of the convolution. Default is 0, so the edges will be multiple
  pixels thick. A cutoff of 3 will be sparse and not a continuous line.

  returns:
  edge_mask: full-size mask of only the edges of the shape
  """
  # Define a kernel to detect edges
  kernel = np.array([[1, 1, 1],
                      [1, -8, 1],
                      [1, 1, 1]])

  # Convolve the binary mask with the kernel
  edges = convolve(get_crop_mask(binary_mask), kernel, mode='constant', cval=0)

  # Create a binary mask of the edges
  edge_mask = (abs(edges) > cutoff).astype(int)
  full_edge_mask = binary_mask.copy()
  full_edge_mask[np.argwhere(binary_mask != 0)[:,0].min():np.argwhere(binary_mask != 0)[:,0].max()+1,
                  np.argwhere(binary_mask != 0)[:,1].min():np.argwhere(binary_mask != 0)[:,1].max()+1] = edge_mask

  return full_edge_mask

if __show_border__:
  border = find_edges(mask)
  plt.imshow(border)
  plt.show()
  plt.imshow(get_crop_mask(border))
  plt.show()



def find_major_axis(mask) -> tuple:
  edges = find_edges(mask, cutoff=1)
  y, x = np.where(edges == 1)
  coords = np.array(list(zip(y, x)))

  # find major axis
  alldist = np.linalg.norm(coords[:, np.newaxis] - coords, axis=2)
  max_dist = np.max(alldist)
  max_pair = coords[np.where(alldist == max_dist)[0]]


  if __show_border__:
    max_pair, max_dist = find_major_axis(mask)
    show_mask = mask.copy()
    print(f"Max distance: {max_dist}")
    print(f"Max pair: {max_pair}")
    show_mask[max_pair[:,0], max_pair[:,1]] = 2
    # show_mask[0 + np.argwhere(mask != 0)[:, 0].min(), 5 + np.argwhere(mask != 0)[:, 1].min()] = 3
    plt.imshow(get_crop_mask(show_mask))
    plt.show()

  return max_pair, max_dist


def find_minor_axis(mask, major_axis_pair):
  """
  Finds the minor axis of the shape as the inverse of the major axis, across the
  center of the cell

  args:
  mask: a binary mask of the shape
  major_axis_pair: the major axis points on the edge of the shape

  returns:
  minor_axis_pair: the minor axis points on the edge of the shape
  min_dist: the distance between the points
  """
  vector = (major_axis_pair[1][0] - major_axis_pair[0][0], major_axis_pair[1][1] - major_axis_pair[0][1])
  minor_axis_vector = np.array((-vector[1], vector[0]), dtype=float)
  center = find_center_new(mask)

  unit_vector = np.array(minor_axis_vector / np.linalg.norm(minor_axis_vector + 1e-5), dtype=float)

  if np.array_equal(unit_vector, [0,0]): unit_vector = np.array([1, 1])

  points = np.array([np.add(center, unit_vector), np.subtract(center, unit_vector)], dtype=float)

  # print(points, mask.shape)
  # print(minor_axis_vector)

  # plt.show()
  while not (is_edge(mask, points[0].astype(int)) and is_edge(mask, points[1].astype(int))) and all(points.reshape(-1) > 0.0) and all(points[:,0] <= mask.shape[0]-1) and all(points[:,1] <= mask.shape[1]-1):
    for i in range(points.shape[0]):
      if not is_edge(mask, points[i].astype(int)) and all(points[i] > 0.0) and int(points[i][0]) <= mask.shape[0]-1 and int(points[i][1]) <= mask.shape[1]-1:
        unit_vector_copy = -unit_vector if i == 1 else unit_vector
        if mask[int(points[i][0]), int(points[i][1])] == 0:
          points[i] -= unit_vector_copy
        else:
          points[i] += unit_vector_copy

  if __show_border__:
    center = find_center_new(mask)
    major_axis_pair, _ = find_major_axis(mask)
    minor_axis_pair, min_dist = find_minor_axis(mask, major_axis_pair)
    show_mask = mask.copy()
    show_mask[center[0], center[1]] = 4
    show_mask[major_axis_pair[:,0], major_axis_pair[:,1]] = 2
    show_mask[minor_axis_pair[:,0], minor_axis_pair[:,1]] = 3
    plt.imshow(show_mask)
    plt.show()
    plt.imshow(get_crop_mask(show_mask))
    plt.show()

  return (points.astype(int), np.linalg.norm((points[0] - points[1])))



#####################
    #CONVEX HULL
#####################
def get_border_pixels(cropped_image):
  """
  Get Border Pixels
  Finds and returns the border pixels of the segmentation.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      NDArray: The border pixels of the segmentation
  """
  border_points = []
  for i in range(len(cropped_image)):
    for j in range(len(cropped_image[i])):
      if cropped_image[i][j] > 0:
        if i > 0 and i < len(cropped_image) - 1 and j > 0 and j < len(cropped_image[i]) -1 and cropped_image[i+1][j] > 0 and cropped_image[i-1][j] > 0 and cropped_image[i][j+1] > 0 and cropped_image[i][j-1] > 0:
          continue
        else:
          border_points.append((i, j))

  return border_points

def plot_border(cropped_image):
  """
  Plot Border
  Plots border of the segmentation.
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      N/A

  Displays:
      The border of the segmentation
  """
  border_points = get_border_pixels(cropped_image)
  new_img = np.zeros((cropped_image.shape[0], cropped_image.shape[1]))
  for point in border_points:
    new_img[point[0]][point[1]] = 255

  #plt.imshow(new_img, cmap='gray')
  #plt.show()

def cross_multiply(p1, p2, p3):
  """
  Cross Multiply
  Cross multiplies three points and returns the result
  Author(s): Kaden Stillwagon

  Args:
    p1: first point
    p2: second point
    p3: third point

  Returns:
      float: The cross of the first, second, and third point
  """
  return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])


def get_convex_hull(cropped_image, border_points=None):
  """
  Get Convex Hull
  Returns the convex hull of the segmentation using Andrew's monotone chain convex hull algorithm
  Source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Geometry/Convex_hull/Monotone_chain
  Author(s): Kaden Stillwagon

  Args:
      cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      NDArray: The vertices and edges of the convex hull
  """
  if border_points == None:
    border_points = sorted(get_border_pixels(cropped_image)) # sorts by x-coords, sorts by y-coord if tie
  else:
    border_points = sorted(border_points)

  lower_hull = []
  for p in border_points:
      while len(lower_hull) >= 2 and cross_multiply(lower_hull[-2], lower_hull[-1], p) <= 0:
          lower_hull.pop()
      lower_hull.append(p)

  upper_hull = []
  for p in reversed(border_points):
      while len(upper_hull) >= 2 and cross_multiply(upper_hull[-2], upper_hull[-1], p) <= 0:
          upper_hull.pop()
      upper_hull.append(p)


  full_hull_vertices = lower_hull[:-1] + upper_hull[:-1]

  new_img = np.zeros((cropped_image.shape[0], cropped_image.shape[1]))
  for point in border_points:
    new_img[point[0]][point[1]] = 255
  # for point in convex_hull_points:
  #   new_img[point[0]][point[1]] = 100

  full_hull_edges = []
  for i in range(len(full_hull_vertices)):
    x1, y1 = full_hull_vertices[i]
    x2, y2 = full_hull_vertices[(i+1) % len(full_hull_vertices)]
    full_hull_edges.append([(x1, y1), (x2, y2)])
    #plt.plot([y1, y2], [x1, x2], color='red')

  # plt.imshow(new_img, cmap='gray')
  # plt.show()

  return full_hull_vertices, full_hull_edges


def get_convex_hull_area(cropped_image, convex_hull_edges=None):
  """
  Get Convex Hull Area
  Gauss's Shoelace Formula
  Source: https://blogs.sas.com/content/iml/2022/11/02/area-perimeter-convex-hull.html
  Source 2: https://en.wikipedia.org/wiki/Shoelace_formula
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      float: the area of the convex hull of the segmentation
  """
  if convex_hull_edges == None:
    convex_hull_vertices, convex_hull_edges = get_convex_hull(cropped_image)
  area = 0
  for edge in convex_hull_edges:
    area += edge[0][0] * edge[1][1] - edge[1][0] * edge[0][1]
  area = np.abs(area) / 2
  return area


def get_convex_hull_perimeter(cropped_image, convex_hull_edges=None):
  """
  Get Convex Hull Perimeter
  Sums the lengths of the edges of the convex hull to get its perimeter
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      float: the perimeter of the convex hull of the segmentation
  """
  if convex_hull_edges == None:
    convex_hull_vertices, convex_hull_edges = get_convex_hull(cropped_image)
  perimeter = 0
  for edge in convex_hull_edges:
    perimeter += np.sqrt(np.power(edge[1][0] - edge[0][0], 2) + np.power(edge[1][1] - edge[0][1], 2))
  return perimeter


##########################
  #MINIMUM BOUNDING BOX
##########################

# Rotating Calipers Algorithms
# source: https://www.geometrictools.com/Documentation/MinimumAreaRectangle.pdf
def convert_hull_vertices_to_new_coordinate_plane(hull_vertices, angle):
  """
  Convert Hull Vertices to New Coordinate Plane
  Converts the hull vertices to a new coordinate plane based on the angle of the convex hull edge
  Author(s): Kaden Stillwagon

  Args:
      hull_vertices (np.ndarray): the vertices of the convex hull
      angle (float): the angle of the convex hull edge

  Returns:
      NDArray: The vertices of the convex hull in the new coordinate plane
  """
  converted_hull_vertices = []
  for vertex in hull_vertices:
    converted_vertice_x = np.cos(angle) * (vertex[0]) - np.sin(angle) * (vertex[1])
    converted_vertice_y = np.sin(angle) * (vertex[0]) + np.cos(angle) * (vertex[1])
    converted_hull_vertices.append((converted_vertice_x, converted_vertice_y))

  return converted_hull_vertices

def convert_to_original_plane(converted_vertice, angle):
  """
  Convert to Original Plane
  Converts the hull vertices back to the originaal coordinate plane
  Author(s): Kaden Stillwagon

  Args:
      converted_vertices (np.ndarray): the vertices of the convex hull converted to the new plane
      angle (float): the angle of the convex hull edge

  Returns:
      NDArray: The vertices of the convex hull in the original coordinate plane
  """
  original_vertice_x = np.cos(-angle) * (converted_vertice[0]) - np.sin(-angle) * (converted_vertice[1])
  original_vertice_y = np.sin(-angle) * (converted_vertice[0]) + np.cos(-angle) * (converted_vertice[1])
  return (original_vertice_x, original_vertice_y)

def find_bounding_box(converted_hull_vertices):
  """
  Find Bounding Box
  Finds the Bounding Box of converted hull vertices
  Author(s): Kaden Stillwagon

  Args:
      converted_hull_vertices (np.ndarray): the vertices of the convex hull converted to the new plane

  Returns:
      NDArray: The vertices of the bounding box of the converted hull vertices
  """
  max_x = np.max(np.array(converted_hull_vertices)[:, 0])
  min_x = np.min(np.array(converted_hull_vertices)[:, 0])
  max_y = np.max(np.array(converted_hull_vertices)[:, 1])
  min_y = np.min(np.array(converted_hull_vertices)[:, 1])

  top_left = (min_x, min_y)
  top_right = (min_x, max_y)
  bottom_left = (max_x, min_y)
  bottom_right = (max_x, max_y)

  return (top_left, top_right, bottom_left, bottom_right)

def get_minimum_bounding_box(cropped_image):
  """
  Get Minimum Bounding Box
  Finds the Bounding Box with the minimum area by iterating through different edges of the convex hull as starting edges for the bounding box
  Rotating Calipers Algorithm
  Source: https://www.geometrictools.com/Documentation/MinimumAreaRectangle.pdf
  Author(s): Kaden Stillwagon

  Args:
      cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      NDArray: The vertices of the minimum area bounding box in vertices of the original plane
  """
  padded_image = np.pad(cropped_image, 40, mode='constant', constant_values=0)
  convex_hull_vertices, convex_hull_edges = get_convex_hull(padded_image)

  minimum_area_bounding_box = 1000000
  minimum_area_bounding_box_vertices = []
  minimum_perimeter_bounding_box = 1000000
  minimum_perimeter_bounding_box_vertices = []
  for edge in convex_hull_edges:
    initial_axis_dir = np.array((edge[1][0] - edge[0][0], edge[1][1] - edge[0][1]) / np.sqrt(np.power(edge[1][0] - edge[0][0], 2) + np.power(edge[1][1] - edge[0][1], 2)))
    angle = np.arctan2(initial_axis_dir[1], initial_axis_dir[0])
    #print(edge)
    #print(initial_axis_dir)
    #print(angle * (180/np.pi))
    #perp_axis_dir = np.array((-initial_axis_dir[1], initial_axis_dir[0]))
    converted_hull_vertices = convert_hull_vertices_to_new_coordinate_plane(convex_hull_vertices, angle)
    #print(converted_hull_vertices)
    top_left_converted, top_right_converted, bottom_left_converted, bottom_right_converted = find_bounding_box(converted_hull_vertices)
    top_left = np.round(convert_to_original_plane(top_left_converted, angle))
    top_right = np.round(convert_to_original_plane(top_right_converted, angle))
    bottom_left = np.round(convert_to_original_plane(bottom_left_converted, angle))
    bottom_right = np.round(convert_to_original_plane(bottom_right_converted, angle))

    top_length = np.sqrt(np.power(top_right[0] - top_left[0], 2) + np.power(top_right[1] - top_left[1], 2))
    side_length = np.sqrt(np.power(bottom_right[0] - top_right[0], 2) + np.power(bottom_right[1] - top_right[1], 2))
    area = top_length * side_length
    perimeter = 2 * (top_length + side_length)
    if area < minimum_area_bounding_box:
      minimum_area_bounding_box = area
      minimum_area_bounding_box_vertices = [top_left, top_right, bottom_left, bottom_right]
    if perimeter < minimum_perimeter_bounding_box:
      minimum_perimeter_bounding_box = perimeter
      minimum_perimeter_bounding_box_vertices = [top_left, top_right, bottom_left, bottom_right]

    # plt.plot([top_left[1], top_right[1]], [top_left[0], top_right[0]], color='red')
    # plt.plot([top_left[1], bottom_left[1]], [top_left[0], bottom_left[0]], color='red')
    # plt.plot([top_right[1], bottom_right[1]], [top_right[0], bottom_right[0]], color='red')
    # plt.plot([bottom_left[1], bottom_right[1]], [bottom_left[0], bottom_right[0]], color='red')

    # plt.imshow(padded_image, cmap='gray')
    # plt.show()


  # plt.title('Minimum Area Bounding Box')
  # plt.plot([minimum_area_bounding_box_vertices[0][1], minimum_area_bounding_box_vertices[1][1]], [minimum_area_bounding_box_vertices[0][0], minimum_area_bounding_box_vertices[1][0]], color='red')
  # plt.plot([minimum_area_bounding_box_vertices[0][1], minimum_area_bounding_box_vertices[2][1]], [minimum_area_bounding_box_vertices[0][0], minimum_area_bounding_box_vertices[2][0]], color='red')
  # plt.plot([minimum_area_bounding_box_vertices[1][1], minimum_area_bounding_box_vertices[3][1]], [minimum_area_bounding_box_vertices[1][0], minimum_area_bounding_box_vertices[3][0]], color='red')
  # plt.plot([minimum_area_bounding_box_vertices[2][1], minimum_area_bounding_box_vertices[3][1]], [minimum_area_bounding_box_vertices[2][0], minimum_area_bounding_box_vertices[3][0]], color='red')

  # plt.imshow(padded_image, cmap='gray')
  # plt.show()

  # plt.title('Minimum Perimeter Bounding Box')
  # plt.plot([minimum_perimeter_bounding_box_vertices[0][1], minimum_perimeter_bounding_box_vertices[1][1]], [minimum_perimeter_bounding_box_vertices[0][0], minimum_perimeter_bounding_box_vertices[1][0]], color='red')
  # plt.plot([minimum_perimeter_bounding_box_vertices[0][1], minimum_perimeter_bounding_box_vertices[2][1]], [minimum_perimeter_bounding_box_vertices[0][0], minimum_perimeter_bounding_box_vertices[2][0]], color='red')
  # plt.plot([minimum_perimeter_bounding_box_vertices[1][1], minimum_perimeter_bounding_box_vertices[3][1]], [minimum_perimeter_bounding_box_vertices[1][0], minimum_perimeter_bounding_box_vertices[3][0]], color='red')
  # plt.plot([minimum_perimeter_bounding_box_vertices[2][1], minimum_perimeter_bounding_box_vertices[3][1]], [minimum_perimeter_bounding_box_vertices[2][0], minimum_perimeter_bounding_box_vertices[3][0]], color='red')

  # plt.imshow(padded_image, cmap='gray')
  # plt.show()

  return minimum_area_bounding_box_vertices#, minimum_perimeter_bounding_box_vertices


#########################
  #NEW PERIMETER METRIC
#########################

def get_perimeter_new(cropped_image, border_points = None):
  """
  Get Perimeter New
  8  1  2
  7  x  3
  6  5  4
  x = curr point
  numbers are order in which surrouding pixels are looked at
  Mimics the clockwise traversal algorithm, summing the perimiter by adding 1 if the next point
  is straight from the current point, or sqrt(2) if the next point is diagonal
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      float: the perimeter of the cell segmentation
  """
  if border_points == None:
    border_points = get_border_pixels(cropped_image)

  leftmost_point_index = np.argmin(np.array(border_points)[:, 1])
  leftmost_point = border_points[leftmost_point_index]
  traversal = [leftmost_point]

  perimeter = 0
  current_point = leftmost_point
  while True:
    next_points = [(current_point[0] - 1, current_point[1]),
                   (current_point[0] - 1, current_point[1] + 1),
                   (current_point[0], current_point[1] + 1),
                   (current_point[0] + 1, current_point[1] + 1),
                   (current_point[0] + 1, current_point[1]),
                   (current_point[0] + 1, current_point[1] - 1),
                   (current_point[0], current_point[1] - 1),
                   (current_point[0] - 1, current_point[1] - 1)]
    straight_points = [(current_point[0] - 1, current_point[1]),
                   (current_point[0], current_point[1] + 1),
                   (current_point[0] + 1, current_point[1]),
                   (current_point[0], current_point[1] - 1)]
    diagonal_points = [(current_point[0] - 1, current_point[1] + 1),
                    (current_point[0] + 1, current_point[1] + 1),
                   (current_point[0] + 1, current_point[1] - 1),
                   (current_point[0] - 1, current_point[1] - 1)]
    found = False
    for next_point in next_points:
      if found == False:
        if next_point in border_points:
          if next_point not in traversal:
            traversal.append(next_point)
            current_point = next_point
            if next_point in straight_points:
              perimeter += 1
            elif next_point in diagonal_points:
              perimeter += np.sqrt(2)
            found = True
    if found == False:
      if len(traversal) == len(border_points):
        break
      else:
        end = False
        found_2 = False
        back = 1
        while found_2 == False:
          if back > 20:
            end = True
            break
          curr_point = traversal[-back]
          next_points = [(curr_point[0] - 1, curr_point[1]),
                   (curr_point[0] - 1, curr_point[1] + 1),
                   (curr_point[0], curr_point[1] + 1),
                   (curr_point[0] + 1, curr_point[1] + 1),
                   (curr_point[0] + 1, curr_point[1]),
                   (curr_point[0] + 1, curr_point[1] - 1),
                   (curr_point[0], curr_point[1] - 1),
                   (curr_point[0] - 1, curr_point[1] - 1)]
          straight_points = [(current_point[0] - 1, current_point[1]),
                        (current_point[0], current_point[1] + 1),
                        (current_point[0] + 1, current_point[1]),
                        (current_point[0], current_point[1] - 1)]
          diagonal_points = [(current_point[0] - 1, current_point[1] + 1),
                          (current_point[0] + 1, current_point[1] + 1),
                        (current_point[0] + 1, current_point[1] - 1),
                        (current_point[0] - 1, current_point[1] - 1)]
          found = False
          for next_point in next_points:
            if found == False:
              if next_point in border_points:
                if next_point not in traversal:
                  traversal.append(next_point)
                  current_point = next_point
                  if next_point in straight_points:
                    perimeter += 1
                  elif next_point in diagonal_points:
                    perimeter += np.sqrt(2)
                  found = True
                  found_2 = True
          if found == False:
            back += 1
        if end == True:
          break

  return perimeter



###############################
  #CLOCKWISE BORDER TRAVERSAL
###############################

def get_clockwise_border_traversal(cropped_image, border_points=None):
  """
  Get Clockwise Border Traversal
  8  1  2
  7  x  3
  6  5  4
  x = curr point
  numbers are order in which surrouding pixels are looked at
  Starting at the leftmost point, find the next point by searching for it in order show above
  Continue until all points have been visited (may ignore some points that should not be a part of the border)
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      NDArray: the clockwise traversal of the border points
  """
  if border_points == None:
    border_points = get_border_pixels(cropped_image)

  leftmost_point_index = np.argmin(np.array(border_points)[:, 1])
  leftmost_point = border_points[leftmost_point_index]
  traversal = [leftmost_point]

  current_point = leftmost_point
  while True:
    next_points = [(current_point[0] - 1, current_point[1]),
                   (current_point[0] - 1, current_point[1] + 1),
                   (current_point[0], current_point[1] + 1),
                   (current_point[0] + 1, current_point[1] + 1),
                   (current_point[0] + 1, current_point[1]),
                   (current_point[0] + 1, current_point[1] - 1),
                   (current_point[0], current_point[1] - 1),
                   (current_point[0] - 1, current_point[1] - 1)]
    found = False
    for next_point in next_points:
      if found == False:
        if next_point in border_points:
          if next_point not in traversal:
            traversal.append(next_point)
            current_point = next_point
            found = True
    if found == False:
      if len(traversal) == len(border_points):
        break
      else:
        end = False
        found_2 = False
        back = 1
        while found_2 == False:
          if back > 20:
            end = True
            break
          curr_point = traversal[-back]
          next_points = [(curr_point[0] - 1, curr_point[1]),
                   (curr_point[0] - 1, curr_point[1] + 1),
                   (curr_point[0], curr_point[1] + 1),
                   (curr_point[0] + 1, curr_point[1] + 1),
                   (curr_point[0] + 1, curr_point[1]),
                   (curr_point[0] + 1, curr_point[1] - 1),
                   (curr_point[0], curr_point[1] - 1),
                   (curr_point[0] - 1, curr_point[1] - 1)]
          found = False
          for next_point in next_points:
            if found == False:
              if next_point in border_points:
                if next_point not in traversal:
                  traversal.append(next_point)
                  current_point = next_point
                  found = True
                  found_2 = True
          if found == False:
            back += 1
        if end == True:
          break



  new_plot = np.zeros((cropped_image.shape[0], cropped_image.shape[1]))
  curr_color = 255
  for point in traversal:
    new_plot[point[0]][point[1]] = curr_color
    curr_color -= 2
  # plt.imshow(new_plot, cmap='gray')
  # plt.show()
  return traversal





####################
  #NEW BEST CENTER
####################

def find_best_center(cropped_image, sorted_border_points=None):
  """
  Find Best Center
  Calculates the radial distances of the sorted border points for each possible center
  Finds the center with the least variance in radial distances
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      tuple: the coordinates of the center with the least variance in radial distances
  """
  minimum_variance_radial_distance_center = 100000000000
  minimum_variance_center_coords = (0, 0)

  if sorted_border_points == None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)

  test_points = np.argwhere(cropped_image > 0)

  squared_x_distances = []
  squared_y_distances = []
  for i in range(np.min(test_points[:, 0]), np.max(test_points[:, 0]) + 1):
    squared_x_distances.append(np.power(np.array(sorted_border_points)[:, 0] - i, 2))
  for j in range(np.min(test_points[:, 1]), np.max(test_points[:, 1]) + 1):
    squared_y_distances.append(np.power(np.array(sorted_border_points)[:, 1] - j, 2))

  for point in test_points:
    radial_distances = np.sqrt(squared_x_distances[point[0]] + squared_y_distances[point[1]])

    variance = np.var(radial_distances)

    if variance < minimum_variance_radial_distance_center:
      minimum_variance_radial_distance_center = variance
      minimum_variance_center_coords = (point[0], point[1])

  return minimum_variance_center_coords





######################
  #RADIAL DISTANCES
######################

def get_radial_distances(cropped_image, center_coords, sorted_border_points=None):
  """
  Get Radial Distances
  Calculates the radial distances of the border points to the center sorted by clockwise traversal
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      NDArray: the radial distances of the border points to the center sorted by clockwise traversal
  """
  if sorted_border_points is None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)

  radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  return radial_distances



###########################
  #PLOT RADIAL DISTANCES
###########################

def get_radial_distance_plot(cropped_image, center_coords):
  """
  Get Radial Distance Plot
  Plots the radial distances of the border points sorted by clockwise traversal
  to the center with the least variance in radial distances
  Also plots the mean radial distance
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      N/A
  Displays:
      Plot of the radial distances of the border points sorted by clockwise traversal
      to the center with the least variance in radial distances as well as the mean radial distance
  """
  #sorted_border_points = get_border_pixels_sorted_by_angle_to_point(cropped_image, center_coords)
  sorted_border_points = get_clockwise_border_traversal(cropped_image)
  #NOTE - would be better with clockwise border traversal

  radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  normalized_radial_distances = radial_distances / np.max(radial_distances)

  #mean_radial_distance = np.mean(normalized_radial_distances)
  mean_radial_distance = np.mean(radial_distances)

  # plt.plot(normalized_radial_distances)
  #plt.plot(radial_distances)
  #plt.axhline(y=mean_radial_distance, color='r', linestyle='-')
  #plt.show()




#################################
  #SORT PIXEL BY ANGLE TO POINT
#################################


def get_border_pixels_sorted_by_angle_to_point(cropped_image, point):
  """
  Get Border Pixels Sorted By Angle to Point
  Returns the border points of the cell segmentation sorted by angle to the point provided
  NOT CURRENTLY IN USE
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    point (tuple): tuple representing the point to sort the border points by

  Returns:
      NDArray: the border points of the cell segmentation sorted by angle to the point provided
  """
  border_points = get_border_pixels(cropped_image)
  angles = {}
  for border_point in border_points:
    angle = np.arctan2(border_point[1] - point[1], border_point[0] - point[0])
    angles[border_point] = angle

  sorted_angles = dict(sorted(angles.items(), key=lambda item: item[1]))
  return list(sorted_angles.keys())









##########################

  #NEW SHAPE PARAMETERS

##########################




################
  #ELONGATION
################

def get_elongation(cropped_image, minimum_area_bounding_box_vertices=None):
  """
  Get Elongation
  Source: https://link.springer.com/article/10.1007/s11356-023-26388-5?fromPaywallRec=true
  Elongation = I / L
    I - the shortest axis of the particle’s minimum bounding box
    L - the longest axis of the particle’s minimum bounding box
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      float: the elongation metric of the segmentation
  """
  if minimum_area_bounding_box_vertices == None:
    minimum_area_bounding_box_vertices = get_minimum_bounding_box(cropped_image)
  top_left, top_right, bottom_left, bottom_right = minimum_area_bounding_box_vertices
  top_length = np.sqrt(np.power(top_left[0] - top_right[0], 2) + np.power(top_left[1] - top_right[1], 2))
  side_length = np.sqrt(np.power(bottom_left[0] - top_left[0], 2) + np.power(bottom_left[1] - top_left[1], 2))
  long_side = max(top_length, side_length)
  short_side = min(top_length, side_length)

  elongation = short_side / long_side

  return elongation





#################
  #ECCENTRICITY
#################

def get_eccentricity(mask, minor_axis_length=None, major_axis_length=None):
  """
  Get Eccentricity
  Source: http://www.cyto.purdue.edu/cdroms/micro2/content/education/wirth10.pdf
  Eccentricity = Minor Axis Length / Major Axis Length
  Author(s): Kaden Stillwagon

  Args:
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the eccentricity metric of the segmentation
  """

  if major_axis_length == None:
    major_axis, major_axis_length = find_major_axis(mask)
  if minor_axis_length == None:
    minor_axis, minor_axis_length = find_minor_axis(mask, major_axis)

  eccentricity = minor_axis_length / minor_axis_length

  return eccentricity





################
  #COMPACTNESS
################

def get_compactness(cropped_image, mask, segmentation_perimeter=None, segmentation_area=None):
  """
  Get Compactness
  Source: https://www.spiedigitallibrary.org/conference-proceedings-of-spie/3661/0000/Effects-of-image-resolution-and-segmentation-method-on-automated-mammographic/10.1117/12.348654.short#_=_
  Compactness = P^2 / A
    P - perimeter of segmentation
    A - area of segmentation
  Note: Same as Circularity Three
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the compactness metric of the segmentation
  """

  if segmentation_perimeter == None:
    segmentation_perimeter = get_perimeter_new(cropped_image)
  if segmentation_area == None:
    segmentation_area = area(mask)

  compactness = (segmentation_perimeter**2) / segmentation_area

  return compactness

def get_compactness_two(cropped_image, center_coords, cell_area):
  """
  Get Compactness
  Source: https://cellprofiler-manual.s3.amazonaws.com/CellProfiler-3.0.0/modules/measurement.html
  Compactness = mean squared distance of objects pixels from center divided by area
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation
    cell_area (int): area of the cell segmentation

  Returns:
      float: the compactness metric of the segmentation
  """

  possible_points = np.argwhere(cropped_image > 0)

  mean_squared_distances_to_center = 0
  for point in possible_points:
    mean_squared_distances_to_center += np.power(point[0] - center_coords[0], 2) + np.power(point[1] - center_coords[1], 2)

  compactness = (mean_squared_distances_to_center / cell_area**2)

  return compactness





################
  #CIRCULARITY
################

def get_circularity(cropped_image, mask, segmentation_perimeter=None, segmentation_area=None):
  """
  Get Circularity
  Source: https://link.springer.com/article/10.1007/s11356-023-26388-5?fromPaywallRec=true
  Circularity = 4πA/P^2
    A - area of segmentation
    P - perimeter of segmentation
  This is the ratio of the circumference of a circle of the same area as the
  segmentation to the actual circumference of the segmentation
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the circularity metric of the segmentation
  """

  if segmentation_area == None:
    segmentation_area = area(mask)
  if segmentation_perimeter == None:
    segmentation_perimeter = get_perimeter_new(cropped_image)

  circularity = (4 * np.pi * segmentation_area) / (segmentation_perimeter**2)

  return circularity

def get_circularity_two(cropped_image, mask, segmentation_area=None, convex_hull_perimeter=None):
  """
  Get Circularity Two
  Source: http://www.cyto.purdue.edu/cdroms/micro2/content/education/wirth10.pdf
  Circularity = 4πA/Pc^2
    A - area of segmentation
    Pc - perimeter of convex hull
  This is the ratio of the area of the segmentation to the area of a circle with the same
  convex perimeter
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the second circularity metric of the segmentation
  """

  if segmentation_area == None:
    segmentation_area = area(mask)
  if convex_hull_perimeter == None:
    convex_hull_perimeter = get_convex_hull_perimeter(cropped_image)

  circularity = (4 * np.pi * segmentation_area) / (convex_hull_perimeter**2)

  return circularity

def get_circularity_three(cropped_image, mask, segmentation_perimeter=None, segmentation_area=None):
  """
  Get Circularity Three
  Source: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=251116
  Circularity = P^2/A
    P - perimeter of segmentation
    A - area of segmentation
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the third circularity metric of the segmentation
  """

  if segmentation_perimeter == None:
    segmentation_perimeter = get_perimeter_new(cropped_image)
  if segmentation_area == None:
    segmentation_area = area(mask)

  circularity = (segmentation_perimeter**2) / segmentation_area

  return circularity

def get_circularity_four(cropped_image, center_coords, radial_distances=None):
    """
    Get Circularity Four
    Source: https://aapm.onlinelibrary.wiley.com/doi/epdf/10.1118/1.597707?saml_referrer
    Circularity = mean radial distance of boundary / standard deviation of radial distance of boundary
    Author(s): Kaden Stillwagon

    Args:
        cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
        center_coords (tuple): coordinates of the center of the cell segmentation

    Returns:
        float: the fourth circularity metric of the segmentation
    """
    if radial_distances is None:
        sorted_border_points = get_clockwise_border_traversal(cropped_image)

        radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

    normalized_radial_distances = radial_distances / np.max(radial_distances)

    mean_radial_distance = np.mean(normalized_radial_distances)
    std_radial_distance = np.std(normalized_radial_distances)


    if std_radial_distance == 0:
        raise ValueError('STD Radial Distance is zero, can\'t calculate circularity (4)')        
    circularity = mean_radial_distance / std_radial_distance

    return circularity




##############
  #CONVEXITY
##############

def get_convexity(cropped_image, mask, segmentation_area=None, convex_hull_area=None):
  """
  Get Convexity
  Source: https://link.springer.com/article/10.1007/s11356-023-26388-5?fromPaywallRec=true
  Convexity = A / Ac
    A - area of the segmentation
    Ac - area of the convex hull of the segmentation
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the convexity metric of the segmentation
  """
  if segmentation_area == None:
    segmentation_area = area(mask)
  if convex_hull_area == None:
    convex_hull_area = get_convex_hull_area(cropped_image)

  convexity = segmentation_area / convex_hull_area

  return convexity


def get_convexity_two(cropped_image, segmentation_perimeter=None, convex_hull_perimeter=None):
  """
  Get Convexity Two
  Source: http://www.cyto.purdue.edu/cdroms/micro2/content/education/wirth10.pdf
  Convexity = Pc / P
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

  Returns:
      float: the second convexity metric of the segmentation
  """

  if segmentation_perimeter == None:
    segmentation_perimeter = get_perimeter_new(cropped_image)
  if convex_hull_perimeter == None:
    convex_hull_perimeter = get_convex_hull_perimeter(cropped_image)

  convexity = convex_hull_perimeter / segmentation_perimeter

  return convexity





##############
  #ROUGHNESS
##############

def get_roughness(cropped_image, mask, segmentation_perimeter=None, convex_hull_perimeter=None):
  """
  Get Roughness
  Source: https://link.springer.com/article/10.1007/s11356-023-26388-5?fromPaywallRec=true
  Roughness = P / Pc
    P - perimeter of the segmentation
    Pc - perimeter of the convex hull of the segmentation
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    mask (np.ndarray): array of variable shape representing a binary mask of the cell

  Returns:
      float: the roughness metric of the segmentation
  """
  if segmentation_perimeter == None:
    segmentation_perimeter = get_perimeter_new(cropped_image)
  if convex_hull_perimeter == None:
    convex_hull_perimeter = get_convex_hull_perimeter(cropped_image)

  roughness = segmentation_perimeter / convex_hull_perimeter

  return roughness

def get_roughness_two(cropped_image, center_coords, sorted_border_points=None, radial_distances=None):
  """
  Get Roughness Two
  Source: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=251116
  Roughness = look in notes/source
    Takes the average over intervals that sum of the absolute difference between the radial
    distance of 3 adjacent border points
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      float: the second roughness metric of the segmentation
  """
  if sorted_border_points is None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)
  if radial_distances is None:
    radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  normalized_radial_distances = radial_distances / np.max(radial_distances)

  intervals = int(len(sorted_border_points) / 3)
  intervals_size = int(len(normalized_radial_distances) / intervals)

  total_roughness = 0
  for i in range(intervals):
    start = i * intervals_size
    end = (i + 1) * intervals_size
    interval_roughness = 0
    for j in range(start, end):
      if j + 2 < len(normalized_radial_distances):
        interval_roughness += abs(normalized_radial_distances[j] - normalized_radial_distances[j + 1])

    total_roughness += interval_roughness

  avg_roughness = total_roughness / intervals

  return avg_roughness


def get_roughness_three(cropped_image, center_coords, border_points=None):
  """
  Get Roughness Three
  Source: https://aapm.onlinelibrary.wiley.com/doi/epdf/10.1118/1.597707?saml_referrer
  Roughness - number of angles w/ multiple points / total number of angles
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      float: the third roughness metric of the segmentation
  """

  if border_points is None:
    border_points = get_border_pixels(cropped_image)

  angles = {}
  for point in border_points:
    angle = np.arctan2(point[1] - center_coords[1], point[0] - center_coords[0])
    if angle in angles.keys():
      angles[angle] += 1
    else:
      angles[angle] = 1

  angles_with_multiple_points = 0
  for angle in angles.keys():
    if angles[angle] > 1:
      angles_with_multiple_points += 1

  roughness = angles_with_multiple_points / len(angles)

  return roughness


def count_mean_crossings(cropped_image, center_coords, radial_distances=None):
  """
  Count Mean Crossings
  Counts the number of times that the radial distance of the border points sorted by clockwise traversal
  to the center moves from above the mean radial distance to below the mean radial distance or vice versa
  Note: could be used for a roughness measure
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      int: the number of times the radial distance cross the mean
  """
  if radial_distances is None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)

    radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  mean_radial_distance = np.mean(radial_distances)

  crossings = 0
  for i in range(1, len(radial_distances)):
    if radial_distances[i - 1] > mean_radial_distance and radial_distances[i] < mean_radial_distance:
      crossings += 1
    elif radial_distances[i - 1] < mean_radial_distance and radial_distances[i] > mean_radial_distance:
      crossings += 1

  return crossings






#############################
  #RADIAL DISTANCE MEASURES
#############################

def get_mean_radial_distance(cropped_image, center_coords, radial_distances=None):
  """
  Get Mean Radial Distance
  Returns the mean of the radial distances to the center
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      float: the mean of the radial distances to the center
  """
  if radial_distances is None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)

    radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  normalized_radial_distances = radial_distances / np.max(radial_distances)

  mean_radial_distance = np.mean(normalized_radial_distances)

  return mean_radial_distance


def get_std_radial_distance(cropped_image, center_coords, radial_distances=None):
  """
  Get STD Radial Distance
  Returns the std of the radial distances to the center
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      float: the std of the radial distances to the center
  """
  if radial_distances is None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)

    radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  normalized_radial_distances = radial_distances / np.max(radial_distances)

  std_radial_distance = np.std(normalized_radial_distances)

  return std_radial_distance


def get_entropy_of_radial_distance(cropped_image, center_coords, radial_distances=None):
  """
  Get Entropy of Radial Distance
  Source: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=251116
  Entropy = -summation from k = 1 to 100, probability of k * log(probability of k)
  Author(s): Kaden Stillwagon

  Args:
    cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
    center_coords (tuple): coordinates of the center of the cell segmentation

  Returns:
      float: the entorpy of the radial distances to the center
  """

  if radial_distances is None:
    sorted_border_points = get_clockwise_border_traversal(cropped_image)

    radial_distances = np.sqrt(np.power(np.array(sorted_border_points)[:, 0] - center_coords[0], 2) + np.power(np.array(sorted_border_points)[:, 1] - center_coords[1], 2))

  normalized_radial_distances = radial_distances / np.max(radial_distances)

  probs = []
  intervals = 100
  for i in range(intervals):
    in_range = np.where((normalized_radial_distances >= i / intervals) & (normalized_radial_distances < (i + 1) / intervals))[0]
    probs.append(len(in_range) / len(normalized_radial_distances))


  # plt.hist(radial_distances, bins='auto', range=(np.min(radial_distances) - 10, np.max(radial_distances) + 10))
  # plt.show()

  entropy = 0
  for prob in probs:
    if prob != 0:
      entropy -= prob * np.log2(prob)

  return entropy





###############################
  #HARALICK TEXTURE FEATURES
###############################

def get_haralick_features(cropped_image):
    """
    Get Haralick Features
    Source: https://mahotas.readthedocs.io/en/latest/, https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=4309314
    Returns 4x14 vector of haralick features in 4 directions and a 1x14 vector of mean haralick features
    Features:
        1) Angular Second Moment (ASM)
        2) Contrast
        3) Correlation
        4) Sum of Squares: Variance
        5) Inverse Difference Moment (IDM)
        6) Sum Average
        7) Sum Variance
        8) Sum Entropy
        9) Entropy
        10) Difference Variance
        11) Difference Entropy
        12) Information Measure of Correlation 1
        13) Information Measure of Correlation 2
        14) Maximal Correlation Coefficient
    Author(s): Kaden Stillwagon

    Args:
        cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.

    Returns:
        np.ndarray: 4x14 vector of haralick features in 4 directions
        np.ndarray: 1x14 vector of mean haralick features
    """

    features = mahotas.features.haralick(cropped_image, compute_14th_feature=True, ignore_zeros=False)
    mean_features = np.mean(features, axis=0)
    return features, mean_features






##############
  #SPIKINESS
##############

def get_spikiness_by_perimeter_and_area(mask, cell_perimeter=None, cell_area=None):
  """
  Get Spikiness by Perimeter and Area
  Calculates the spikiness of a cell mask by taking the ratio of its perimeter to its area.
  The larger this value (the smaller the area of the cell compared to its perimeter), the more spiky the cell is.
  Motivation:
    -We generally think of shapes with fewer sides as more spiky (i.e. a triangle is spikier than a circle (consider circle to have infinite sides) or an octagon)
    -We also know that, given the same perimeter, shapes with fewer sides (that are therefore less spiky) have a larger area.
      -Example: Perimeter = 10
        -Area of Circle(inf sides): 7.96
        -Area of Decagon(10 sides): 7.69
        -Area of Octagon(8 sides): 7.54
        -Area of Hexagon(6 sides): 7.22
        -Area of Pentagon(5 sides): 6.88
        -Area of Square(4 sides): 6.25
        -Area of Triangle(3 sides): 4.81 (equilateral)
    -Therefore, by taking the ratio of perimeter to area, we know that masks that have a larger ratio
      will have smaller areas compared to perimeter and therefore will have fewer sides and be more "spiky"
  Author(s): Kaden Stillwagon

  Args:
    mask (np.ndarray): Array of shape (W,H) representing a binary mask of the cell. 1 = cell, 0 = background.

  Returns:
      float: The spikiness of the cell mask representated as a ratio of its perimeter to its area.
  """

  if cell_perimeter == None:
    cell_perimeter = get_perimeter_new(mask)
  if cell_area == None:
    cell_area = area(mask)

  return cell_perimeter / cell_area




##################################
  #3D PLOT OF SEGMENT PARAMETERS
##################################

if False:
  from google.colab import output
  output.enable_custom_widget_manager()
  from mpl_toolkits.mplot3d import Axes3D


def plot_3d_parameter_clouds(param1, param1_name, param2, param2_name, param3, param3_name):
  """
  Plot 3D Parameter Clouds
  Plots 3 parameters into 3d graph.
  Author(s): Kaden Stillwagon

  Args:
    param1 (np.ndarray): array of variable shape representing the values of the first parameter.
    param1_name (str): name of the first parameter.
    param2 (np.ndarray): array of variable shape representing the values of the  second parameter.
    param2_name (str): name of the second parameter.
    param3 (np.ndarray): array of variable shape representing the values of the the third parameter.
    param3_name (str): name of the third parameter.

  Returns:
      N/A
  Displays:
      3D plot of values from the 3 parameters.
  """
  # Creating a 3D scatter plot
#   fig = plt.figure()
#   ax = fig.add_subplot(111, projection='3d')
#   ax.scatter(param1, param2, param3, c='r', marker='o')

#   ax.set_xlabel(f'{param1_name}')
#   ax.set_ylabel(f'{param2_name}')
#   ax.set_zlabel(f'{param3_name}')

  #plt.show()


def get_metrics_from_all_segments(project, inImage = 'sample_img'):
  """
  Get Metrics from all Segments
  Calculates all metrics from all cell segmentations in the image and stores arrays of each metric in a dictionary
  Author(s): Kaden Stillwagon

  Args:
    inImage (str): name of image folder that contains raw output and original image.

  Returns:
      dict: Dictionary of arrays of each metric from all cell segmentations in the image.
  """
  ##NOT USED, FUNCTION IN parameters_main.py

  image = get_sample_image(inImage)

  metrics = {
    # Shape Metrics
      'perimeters': [],
      'areas': [],
      'bounding radii min': [],
      'bounding radii max': [],
      'num surrounding cells': [],
      'spikiness': [],

    # Pixel Intensity Metrics
      'mean intensities': [],
      'std intensities': [],
      'min intensities': [],
      'max intensities': [],
      'intensity ranges': [],
      'gradient magnitude by pixel metrics': [],
      'gradient orientation by pixel metrics': [],
      'gradient magnitude by layer metrics': []
  }


  for i in range(1, 292):
    try:
      cell_mask = get_cell_mask(project, inImage, i)
      masked_image = get_mask_pixel_intensities(image, cell_mask)
      cropped_image = crop_to_mask(masked_image)

      #SHAPE METRICS
      cell_perimeter = perimeter(cell_mask)
      cell_area = area(cell_mask)
      bounding_radius_min, bounding_radius_max = bounding_radii(cell_mask)
      num_surrounding_cells = get_surrounding_cell_count(inImage, i)
      spikiness_metric = get_spikiness_by_perimeter_and_area(cell_mask)
      metrics['perimeters'].append(cell_perimeter)
      metrics['areas'].append(area)
      metrics['bounding radii min'].append(bounding_radius_min)
      metrics['bounding radii max'].append(bounding_radius_max)
      metrics['num surrounding cells'].append(num_surrounding_cells)
      metrics['spikiness'].append(spikiness_metric)


      #PIXEL INTENSITY METRICS
      mean_intensity, std_intensity, max_intensity, min_intensity, intensity_range = calculate_pixel_intensity_metrics(cropped_image)
      metrics['mean intensities'].append(mean_intensity)
      metrics['std intensities'].append(std_intensity)
      metrics['min intensities'].append(min_intensity)
      metrics['max intensities'].append(max_intensity)
      metrics['intensity ranges'].append(intensity_range)
      gradient_magnitude, gradient_orientation = calculate_gradient_pixel_by_pixel(cropped_image, image)
      metrics['gradient magnitude by pixel metrics'].append(gradient_magnitude)
      metrics['gradient orientation by pixel metrics'].append(gradient_orientation)

      center_coords = find_center(cropped_image)

      layer_avgs, gradient_metric = calculate_gradient_layer_by_layer(cropped_image)
      metrics['gradient magnitude by layer metrics'].append(gradient_metric)

      print(f'Cell Mask {i}: Perimeter: {cell_perimeter} Area: {cell_area} Bounding Radius Min: {bounding_radius_min} Bounding Radius Max: {bounding_radius_max} Num Surrounding Cells: {num_surrounding_cells} Spikiness: {spikiness_metric} Mean Intensity: {mean_intensity} STD Intensity: {std_intensity} Min Intensity: {min_intensity} Max Intensity: {max_intensity} Intensity Range: {intensity_range} Gradient Magnitude by Layer: {gradient_metric}')
    except:
      continue

  return metrics


def run_and_plot_all_segments(inImage = 'sample_img'):
  """
  Run and Plot All Segments
  Calculates all metrics from all cell segmentations in the image and plots 3 chosen parameters on 3D graph.
  Author(s): Kaden Stillwagon

  Args:
    inImage (str): name of image folder that contains raw output and original image.

  Returns:
      N/A
  Displays:
      3D plot of values from 3 parameters of all cell segmentations
  """
  #%matplotlib inline

  metrics = get_metrics_from_all_segments('sample_img')
  print(metrics)

  #%matplotlib widget
  plot_3d_parameter_clouds(np.array(metrics['spikiness']), 'Spikiness', np.array(metrics['gradient magnitude by layer metrics']), 'Gradient Magnitude', np.array(metrics['num surrounding cells']), 'Num Surrounding Cells')
  #%matplotlib inline
