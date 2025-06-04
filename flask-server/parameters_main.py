from cell_parameter_metrics import *
from tqdm import tqdm

def get_cell_metrics(image, project, image_date, cell_mask, cropped_image, index):
    """
    Calculates the parameters for the segmentation at "index" in the image at location "project"/cell_images/"image_date"
    Author(s): Kaden Stillwagon

    Args:
        image (np.ndarray): pixel-matrix representation of grayscale image
        project (string): string specifying the project that the image is from
        image_date (string): datetime date specifying when the image was uploaded to the project
        cell_mask (np.ndarray): a binary mask of the segmenation at the current index
        cropped_image (np.ndarray): array of variable shape representing a grayscale image cropped to the cell mask.
        index (int): integer representing the index of the current segmentation in the image

    Returns:
        data (dict): dict containing the segmentations values for each parameter
    """
    #SHAPE METRICS
    border_points = get_border_pixels(cropped_image)
    sorted_border_points = get_clockwise_border_traversal(cropped_image, border_points)

    cell_perimeter = get_perimeter_new(cropped_image, border_points)
    cell_center = find_best_center(cropped_image, sorted_border_points)
    cell_area = area(cell_mask)
    radial_distances = get_radial_distances(cropped_image, cell_center, sorted_border_points)

    ##Major, Minor Axes
    
    #major_axis_pair, major_axis_distance = find_major_axis(cell_mask)
    #minor_axis_pair, minor_axis_distance = find_minor_axis(cell_mask, major_axis_pair)

    ##Convex Hull
    
    convex_hull_vertices, convex_hull_edges = get_convex_hull(cropped_image, border_points)
    convex_hull_area = get_convex_hull_area(cropped_image, convex_hull_edges)
    convex_hull_perimeter = get_convex_hull_perimeter(cropped_image, convex_hull_edges)

    ##Minimum Bounding Box
    
    minimum_area_bounding_box_vertices = get_minimum_bounding_box(cropped_image)

    bounding_radius_min, bounding_radius_max = bounding_radii(cell_mask)
    
    num_surrounding_cells = get_surrounding_cell_count(project, image_date, index)
    
    spikiness_metric = get_spikiness_by_perimeter_and_area(cell_mask, cell_perimeter, cell_area)
    elongation = get_elongation(cropped_image, minimum_area_bounding_box_vertices)
    #eccentricity = get_eccentricity(cell_mask, minor_axis_distance, major_axis_distance)
    compactness = get_compactness(cropped_image, cell_mask, cell_perimeter, cell_area)
    compactness_two = get_compactness_two(cropped_image, cell_center, cell_area)
    circularity_one = get_circularity(cropped_image, cell_mask, cell_perimeter, cell_area)
    circularity_two = get_circularity_two(cropped_image, cell_mask, cell_area, convex_hull_perimeter)
    circularity_three = get_circularity_three(cropped_image, cell_mask, cell_perimeter, cell_area)
    circularity_four = get_circularity_four(cropped_image, cell_center, radial_distances)
    convexity_one = get_convexity(cropped_image, cell_mask, cell_area, convex_hull_area)
    convexity_two = get_convexity_two(cropped_image, cell_perimeter, convex_hull_perimeter)
    roughness_one = get_roughness(cropped_image, cell_mask, cell_perimeter, convex_hull_perimeter)
    roughness_two = get_roughness_two(cropped_image, cell_center, sorted_border_points, radial_distances)
    roughness_three = get_roughness_three(cropped_image, cell_center, border_points)
    mean_crossings = count_mean_crossings(cropped_image, cell_center, radial_distances)
    mean_radial_distance = get_mean_radial_distance(cropped_image, cell_center, radial_distances)
    std_radial_distance = get_std_radial_distance(cropped_image, cell_center, radial_distances)
    entropy_of_radial_distance = get_entropy_of_radial_distance(cropped_image, cell_center, radial_distances)
    haralick_features, mean_haralick_features = get_haralick_features(cropped_image)

    #PIXEL METRICS
    
    mean_intensity, std_intensity, max_intensity, min_intensity, intensity_range = calculate_pixel_intensity_metrics(cropped_image, False)
    
    layer_avgs, gradient_metric = calculate_gradient_layer_by_layer(cropped_image)
    #gradient_magnitude, gradient_orientation = calculate_gradient_pixel_by_pixel(cropped_image, image)

    data = {
        'Perimeter': cell_perimeter,
        'Area': cell_area,
        'Convex Hull Area': convex_hull_area,
        'Convex Hull Perimeter': convex_hull_perimeter,
        'Min Bounding Radius': bounding_radius_min,
        'Max Bounding Radius': bounding_radius_max,
        'Number of Surrounding Cells': num_surrounding_cells,
        'Spikiness': spikiness_metric,
        'Elongation': elongation,
        'Compactness (1)': compactness,
        'Compactness (2)': compactness_two,
        'Circularity (1)': circularity_one,
        'Circularity (2)': circularity_two,
        'Circularity (3)': circularity_three,
        'Circularity (4)': circularity_four,
        'Convexity (1)': convexity_one,
        'Convexity (2)': convexity_two,
        'Roughness (1)': roughness_one,
        'Roughness (2)': roughness_two,
        'Roughness (3)': roughness_three,
        'Mean Radial Distance': mean_radial_distance,
        'Mean Radial Distance Crossings': mean_crossings,
        'STD Radial Distance': std_radial_distance,
        'Entropy of Radial Distance': entropy_of_radial_distance,
        'Mean Intensity': mean_intensity,
        'STD_Intensity': std_intensity,
        'Max Intensity': max_intensity,
        'Min Intensity': min_intensity,
        'Intensity Range': intensity_range,
        'Intensity Gradient Metric': gradient_metric
    }
    
    dir_index = 0
    for direction_features in haralick_features:
        dir_index += 1
        data[f'Haralick - Angular Second Moment (Direction {dir_index})'] = direction_features[0]
        data[f'Haralick - Contrast (Direction {dir_index})'] = direction_features[1]
        data[f'Haralick - Correlation (Direction {dir_index})'] = direction_features[2]
        data[f'Haralick - Sum of Squares: Variance (Direction {dir_index})'] = direction_features[3]
        data[f'Haralick - Inverse Difference Moment (Direction {dir_index})'] = direction_features[4]
        data[f'Haralick - Sum Average (Direction {dir_index})'] = direction_features[5]
        data[f'Haralick - Sum Variance (Direction {dir_index})'] = direction_features[6]
        data[f'Haralick - Sum Entropy (Direction {dir_index})'] = direction_features[7]
        data[f'Haralick - Entropy (Direction {dir_index})'] = direction_features[8]
        data[f'Haralick - Difference Variance (Direction {dir_index})'] = direction_features[9]
        data[f'Haralick - Difference Entropy (Direction {dir_index})'] = direction_features[10]
        data[f'Haralick - Information Measure Correlation 1 (Direction {dir_index})'] = direction_features[11]
        data[f'Haralick - Information Measure Correlation 2 (Direction {dir_index})'] = direction_features[12]
        data[f'Haralick - Maximal Correlation Coefficient (Direction {dir_index})'] = direction_features[13]

    data[f'Haralick - Angular Second Moment (Mean)'] = mean_haralick_features[0]
    data[f'Haralick - Contrast (Mean)'] = mean_haralick_features[1]
    data[f'Haralick - Correlation (Mean))'] = mean_haralick_features[2]
    data[f'Haralick - Sum of Squares: Variance (Mean)'] = mean_haralick_features[3]
    data[f'Haralick - Inverse Difference Moment (Mean)'] = mean_haralick_features[4]
    data[f'Haralick - Sum Average (Mean)'] = mean_haralick_features[5]
    data[f'Haralick - Sum Variance (Mean)'] = mean_haralick_features[6]
    data[f'Haralick - Sum Entropy (Mean)'] = mean_haralick_features[7]
    data[f'Haralick - Entropy (Mean)'] = mean_haralick_features[8]
    data[f'Haralick - Difference Variance (Mean)'] = mean_haralick_features[9]
    data[f'Haralick - Difference Entropy (Mean)'] = mean_haralick_features[10]
    data[f'Haralick - Information Measure Correlation 1 (Mean)'] = mean_haralick_features[11]
    data[f'Haralick - Information Measure Correlation 2 (Mean)'] = mean_haralick_features[12]
    data[f'Haralick - Maximal Correlation Coefficient (Mean)'] = mean_haralick_features[13]

    return data


def compute_mean_dataset(dataset):
    """
    Computes the mean of each parameter in the image and returns as a dictionary
    Author(s): Kaden Stillwagon

    Args:
        dataset (list): list containing a cell index and list of metrics for each segmentation in the image

    Returns:
        mean_dataset (dict): dict containing the mean value for each parameter in the image
    """
    mean_dataset = {}
    for key in dataset[0]['Metrics'].keys():
        mean_dataset[key] = dataset[0]['Metrics'][key]

    for i in range(1, len(dataset)):
        cell_data = dataset[i]['Metrics']
        for key in list(cell_data.keys()):
            mean_dataset[key] += cell_data[key]

    for key in list(mean_dataset.keys()):
        mean_dataset[key] = mean_dataset[key] / len(dataset)

    
    return mean_dataset

def create_metric_dataset_for_single_image(project, image_date):
    """
    Creates a dataset containing the parameters for every segmentation in the image at "project"/cell_images/"image_date"
    Author(s): Kaden Stillwagon

    Args:
        project (string): string specifying the project that the image is from
        image_date (string): datetime date specifying when the image was uploaded to the project

    Returns:
        dataset (list): list containing a cell index and list of metrics for each segmentation in the image
        mean_dataset (dict): dict containing the mean value for each parameter in the image
    """
    dataset = []
    image = get_sample_image(project=project, image_date=image_date)
    segmentations = get_sample_segmentation(project=project, image_date=image_date)
    #for i in range(18, 30):
    for i in tqdm(range(1, get_num_cell_segments(project, image_date))):
        try:
            cell_mask = get_cell_mask(project, image_date, i, segmentations)
            masked_image = get_mask_pixel_intensities(image, cell_mask)
            cropped_image = crop_to_mask(masked_image)

            data = get_cell_metrics(image, project, image_date, cell_mask, cropped_image, i)
            if data['Area'] != 0 and data['Convex Hull Area'] != 0 and data['Elongation'] != np.inf and data['Perimeter'] != 0 and data['Convex Hull Perimeter'] != 0 and data['STD Radial Distance'] != 0:
                dataset.append({
                    'Cell Index': i,
                    'Metrics': data
                })
            print(f'Cell Mask {i}: Done')
        except Exception as e:
            print(f'Cell Mask {i}: {e}')
        continue

    mean_dataset = compute_mean_dataset(dataset)

    return dataset, mean_dataset

