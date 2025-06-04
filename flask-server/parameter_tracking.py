import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime
import matplotlib.pyplot as plt


def normalize_dataset(image_set_parameters):
    """
    Normalizes dataset by finding the max value for each parameter and dividing every value of that parameter by that maximum value
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every image in the image set

    Returns:
        normalized_image_set_parameters (list): list containing the data and the normalized parameters of every image in the image set
    """
    max_values = {}
    for key in image_set_parameters[0]['Parameters'].keys():
        max_values[key] = 0
        for image_parameters in image_set_parameters:
            if abs(image_parameters['Parameters'][key]) > abs(max_values[key]):
                max_values[key] = image_parameters['Parameters'][key]
    
    normalized_image_set_parameters = []
    for i in range(len(image_set_parameters)):
        normalized_image_set_parameters.append({
            'Date': image_set_parameters[i]['Date'],
            'Parameters': {}
        })

        for key in image_set_parameters[i]['Parameters'].keys():
            normalized_image_set_parameters[i]['Parameters'][key] = image_set_parameters[i]['Parameters'][key] / max_values[key]

    return normalized_image_set_parameters


def get_parameter_list_from_condition(image_set_parameters, condition):
    """
    Finds and returns the parameters that have the highest value for the given condition
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every image in the image set
        condition (string): string specifying the condition to pick the parameters by

    Returns:
        three_highest_condition_metrics (list): list containing the three conditions that have the highest value for the given condition
    """
    normalized_image_set_parameters = normalize_dataset(image_set_parameters)

    normalized_sequential_metric_values = {}
    sequential_metric_values = {}
    feature_analysis_dict = {}
    for key in image_set_parameters[0]['Parameters'].keys():
        normalized_sequential_metric_values[key] = [{
            'Date': normalized_image_set_parameters[0]['Date'],
            'Value': normalized_image_set_parameters[0]['Parameters'][key]
        }]
        sequential_metric_values[key] = [{
            'Date': image_set_parameters[0]['Date'],
            'Value': image_set_parameters[0]['Parameters'][key]
        }]
        feature_analysis_dict[key] = {}

    for i in range(1, len(image_set_parameters)):
        for key in image_set_parameters[i]['Parameters'].keys():
            normalized_sequential_metric_values[key].append({
                'Date': normalized_image_set_parameters[i]['Date'],
                'Value': normalized_image_set_parameters[i]['Parameters'][key]
            })
            sequential_metric_values[key].append({
                'Date': image_set_parameters[i]['Date'],
                'Value': image_set_parameters[i]['Parameters'][key]
            })

    for key in normalized_sequential_metric_values.keys():
        normalized_sequential_metric_values[key] = list(sorted(normalized_sequential_metric_values[key], key=lambda item: item['Date']))
        sequential_metric_values[key] = list(sorted(sequential_metric_values[key], key=lambda item: item['Date']))


    #print(normalized_sequential_metric_values)

    datetimes_array = [datetime.fromisoformat(value.get('Date')).timestamp() for value in sequential_metric_values['Area']]

    for i in range(0, len(image_set_parameters)):
        for key in list(image_set_parameters[i]['Parameters'].keys()):
            feature_analysis_dict[key]['Variance'] = np.var([value.get('Value') for value in normalized_sequential_metric_values[key]])
            feature_analysis_dict[key]['Range'] = np.max([value.get('Value') for value in normalized_sequential_metric_values[key]]) - np.min([value.get('Value') for value in normalized_sequential_metric_values[key]])
            feature_analysis_dict[key]['Time Correlation'] = np.abs(np.corrcoef([value.get('Value') for value in sequential_metric_values[key]], datetimes_array)[0, 1])



    if condition == 'Max Variance':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Variance'], reverse=True))
    if condition == 'Min Variance':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Variance'], reverse=False))
    if condition == 'Max Range':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Range'], reverse=True))
    if condition == 'Min Range':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Range'], reverse=False))
    if condition == 'Max Time Correlation':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Time Correlation'], reverse=True))
    if condition == 'Min Time Correlation':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Time Correlation'], reverse=False))

    three_highest_condition_metrics = list(condition_sorted_analysis_dict.keys())[:3]
    #print(condition_sorted_analysis_dict)
    print(f'Highest {condition} Metrics: {three_highest_condition_metrics}')

    return three_highest_condition_metrics


def find_specific_condition_parameters(image_set_parameters, condition):
    """
    Returns a dictionary of the parameters values of the three highest metrics on the given condition for each image, sorted by image_date
    Looking at average parameters, not all cell masks
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every image in the image set
        condition (string): string specifying the condition to pick the parameters by

    Returns:
        top_condition_dict (dict): dictionary containing parameters values of the three highest metrics on the given condition for each image, sorted by image_date
    """
    three_highest_condition_metrics = get_parameter_list_from_condition(image_set_parameters, condition)

    top_condition_dict = {}
    for metric in three_highest_condition_metrics:
        sequential_metrics = []
        for image_parameters in image_set_parameters:
            sequential_metrics.append({
                'Date': image_parameters['Date'],
                'Value': image_parameters['Parameters'][metric],
            })

        sorted_sequential_metrics = list(sorted(sequential_metrics, key=lambda item: item['Date']))
        top_condition_dict[metric] = sorted_sequential_metrics

    return top_condition_dict
    
    
def find_parameter_values(image_set_parameters, parameter):
    """
    Returns a dictionary of the parameters values for a specific parameter for each image, sorted by image_date
    Looking at average parameters, not all cell masks
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every image in the image set
        parameter (string): string specifying the parameter

    Returns:
        parameter_dict (dict): dictionary containing parameters values for the specified parameter for each image, sorted by image_date
    """
    parameter_dict = {}
    if 'Principal Component' in parameter:
        pc_dict = get_pca_features_average_masks(image_set_parameters)
        parameter_dict[parameter] = pc_dict[parameter]
    else:
        image_set_parameters = image_set_parameters['Average']
        sequential_metric_values = [{
            'Date': image_set_parameters[0]['Date'],
            'Value': image_set_parameters[0]['Parameters'][parameter]
        }]

        for i in range(1, len(image_set_parameters)):
            sequential_metric_values.append({
                'Date': image_set_parameters[i]['Date'],
                'Value': image_set_parameters[i]['Parameters'][parameter]
            })

        sequential_metric_values = list(sorted(sequential_metric_values, key=lambda item: item['Date']))

        parameter_dict[parameter] = sequential_metric_values

    return parameter_dict




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    FULL DATASET - All Cell Masks
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def find_specific_condition_parameters_all_masks(image_set_parameters, condition):
    """
    Returns a dictionary of the parameters values of the three highest metrics on the given condition for each segmentation mask in each image, sorted by image_date
    Looking at average parameters, not all cell masks
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set
        condition (string): string specifying the condition to pick the parameters by

    Returns:
        top_condition_dict (dict): dictionary containing parameters values of the three highest metrics on the given condition for each segmentation mask in each image, sorted by image_date
    """
    three_highest_condition_metrics = get_parameter_list_from_condition(image_set_parameters['Average'], condition)

    top_condition_dict = {}
    for metric in three_highest_condition_metrics:
        individual_cell_sequential_metrics = []
        for image_parameters in image_set_parameters['Individual']:

            individual_cell_sequential_metric_values = []
            for parameter_set in image_parameters['Parameters']:
                #individual_cell_sequential_metric_values.append(parameter_set[metric])
                individual_cell_sequential_metric_values.append(parameter_set['Metrics'][metric])

            individual_cell_sequential_metrics.append({
                'Date': image_parameters['Date'],
                'Values': individual_cell_sequential_metric_values,
            })

        sorted_individual_cell_sequential_metrics = list(sorted(individual_cell_sequential_metrics, key=lambda item: item['Date']))
        top_condition_dict[metric] = sorted_individual_cell_sequential_metrics

    return top_condition_dict


def find_parameter_values_all_masks(image_set_parameters, parameter):
    """
    Returns a dictionary of the parameters values for a specific parameter for each segmentation mask in each image, sorted by image_date
    Looking all cell masks
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set
        parameter (string): string specifying the parameter

    Returns:
        parameter_dict (dict): dictionary containing parameters values for the specified parameter for each segmentation mask in each image, sorted by image_date
    """
    parameter_dict = {}
    #print(parameter)

    individual_cell_sequential_metrics = []
    if 'Principal Component' in parameter:
        pc_dict = get_pca_features_all_masks(image_set_parameters)
        #print(pc_dict.keys())
        individual_cell_sequential_metrics = pc_dict[parameter]
    else:
        for image_parameters in image_set_parameters['Individual']:
            individual_cell_sequential_metric_values = []
            for parameter_set in image_parameters['Parameters']:
                #individual_cell_sequential_metric_values.append(parameter_set[parameter])
                individual_cell_sequential_metric_values.append(parameter_set['Metrics'][parameter])

            individual_cell_sequential_metrics.append({
                'Date': image_parameters['Date'],
                'Values': individual_cell_sequential_metric_values,
            })

    sorted_individual_cell_sequential_metrics = list(sorted(individual_cell_sequential_metrics, key=lambda item: item['Date']))
    parameter_dict[parameter] = sorted_individual_cell_sequential_metrics

    return parameter_dict



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    FULL DATSET - ALL CELL MASKS - SINGLE IMAGE
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def normalize_single_image_dataset(metric_dictionary):
    """
    Normalizes dataset by finding the max value for each parameter and dividing every value of that parameter by that maximum value
    Single Image
    Author(s): Kaden Stillwagon

    Args:
        metric_dictionary (dict): dict containing the parameters of every segmentation in the image, in format {"parameter": [list of parameter values]}

    Returns:
        normalized_metric_dictionary (dict): dict containing the normalized parameters of every segmentation in the image
    """
    normalized_metric_dictionary = {}
    for key in metric_dictionary.keys():
        normalized_metric_dictionary[key] = metric_dictionary[key] / np.max(metric_dictionary[key])

    return normalized_metric_dictionary


def four_highest_condition_metrics_single_image(image_parameters, condition):
    """
    Finds and returns the top four parameters that have the highest value for the given condition
    Author(s): Kaden Stillwagon

    Args:
        image_parameters (list): dict containing the parameters of every segmentation in the image
        condition (string): string specifying the condition to pick the parameters by

    Returns:
        four_highest_condition_metrics (list): list containing the four conditions that have the highest value for the given condition
        metric_dictionary (dict): dict containing the parameters of every segmentation in the image, in format {"parameter": [list of parameter values]}
    """
    metric_dictionary = {}
    feature_analysis_dict = {}
    for key in image_parameters[0]['Metrics'].keys():
        metric_dictionary[key] = []
        feature_analysis_dict[key] = {}
        for cell_parameters in image_parameters:
            metric_dictionary[key].append(cell_parameters['Metrics'][key])

    normalized_metric_dictionary = normalize_single_image_dataset(metric_dictionary)

    for key in normalized_metric_dictionary.keys():
        feature_analysis_dict[key]['Variance'] = np.var(normalized_metric_dictionary[key])
        feature_analysis_dict[key]['Range'] = np.max(normalized_metric_dictionary[key]) - np.min(normalized_metric_dictionary[key])

    
    if condition == 'Max Variance':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Variance'], reverse=True))
    if condition == 'Min Variance':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Variance'], reverse=False))
    if condition == 'Max Range':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Range'], reverse=True))
    if condition == 'Min Range':
        condition_sorted_analysis_dict = dict(sorted(feature_analysis_dict.items(), key=lambda item: item[1]['Range'], reverse=False))

    four_highest_condition_metrics = list(condition_sorted_analysis_dict.keys())[:4]
    print(f'Highest {condition} Metrics: {four_highest_condition_metrics}')

    return four_highest_condition_metrics, metric_dictionary



def find_specific_condition_parameters_all_masks_single_image(image_parameters, condition):
    """
    Returns a dictionary of the parameters values of the four highest metrics on the given condition for each segmentation mask in the image
    Single Image, all segmentations
    Author(s): Kaden Stillwagon

    Args:
        image_parameters (list): dict containing the parameters of every segmentation in the image
        condition (string): string specifying the condition to pick the parameters by

    Returns:
        top_condition_dict (dict): dictionary containing parameters values of the four highest metrics on the given condition for each segmentation mask in the image
    """
    four_highest_condition_metrics, metric_dictionary = four_highest_condition_metrics_single_image(image_parameters, condition)

    top_condition_dict = {}
    for metric in four_highest_condition_metrics:
        top_condition_dict[metric] = metric_dictionary[metric]

    return top_condition_dict


def find_parameter_values_single_image(image_parameters, parameter):
    """
    Returns a dictionary of the parameters values for a specific parameter for each segmentation mask in the image
    Single image, all segmentations
    Author(s): Kaden Stillwagon

    Args:
        image_parameters (list): dict containing the parameters of every segmentation in the image
        parameter (string): string specifying the parameter

    Returns:
        parameter_dict (dict): dictionary containing parameters values for the specified parameter for each segmentation mask in the image
    """
    parameter_dict = {
        parameter: []
    }
    
    if 'Principal Component' in parameter:
        pc_dict = get_pca_features_all_masks_single_image(image_parameters)
        parameter_dict[parameter] = pc_dict[parameter]
    else:
        for cell_parameters in image_parameters:
            parameter_dict[parameter].append(cell_parameters['Metrics'][parameter])

    return parameter_dict



#~~~~~~~~~~~~~~~~~~~~~~~~~
#    FINDING OUTLIERS
#~~~~~~~~~~~~~~~~~~~~~~~~~


def find_outliers(parameter_dict):
    """
    Finds the Cell Indices for each of the 3 chosen parameters in each image that are > 3 standard deviations away from the mean 
    Author(s): Kaden Stillwagon

    Args:
        parameter_dict (dict): dictionary containing parameters values for a specified parameter for each segmentation mask in each image (result of find_specific_condition_parameters_all_masks for example)

    Returns:
        top_condition_dict (list): list of lists containing the cell indices of outlier cells in each image in the image set
    """
    outliers_list = []
    for image in parameter_dict[list(parameter_dict.keys())[0]]:
        outliers_list.append(set())

    for metric in list(parameter_dict.keys()):
        for i in range(len(parameter_dict[metric])):
            image_metric_values = parameter_dict[metric][i]['Values']

            mean = np.mean(image_metric_values)
            std = np.std(image_metric_values)
            z_scores = (image_metric_values - mean) / std
            large_positive_z_score_indices = np.where(z_scores > 3)[0]
            large_negative_z_score_indices = np.where(z_scores < -3)[0]

            for indice in large_positive_z_score_indices:
                outliers_list[i].add(int(indice))
            for indice in large_negative_z_score_indices:
                outliers_list[i].add(int(indice))

    for i in range(len(parameter_dict[list(parameter_dict.keys())[0]])):
        outliers_list[i] = list(outliers_list[i])
    return outliers_list


def find_outliers_single_image(parameter_dict):
    """
    Finds the Cell Indices for each of the 4 chosen parameters in the image that are > 3 standard deviations away from the mean 
    Author(s): Kaden Stillwagon

    Args:
        parameter_dict (dict): dictionary containing parameters values for a specified parameter for each segmentation mask in the image (result of find_specific_condition_parameters_all_masks_single_image for example)

    Returns:
        top_condition_dict (list): list containing the cell indices of outlier cells in the image
    """
    outliers_list = set()
    for metric in parameter_dict.keys():
        mean = np.mean(parameter_dict[metric])
        std = np.std(parameter_dict[metric])
        z_scores = (parameter_dict[metric] - mean) / std
        large_positive_z_score_indices = np.where(z_scores > 3)[0]
        large_negative_z_score_indices = np.where(z_scores < -3)[0]

        for indice in large_negative_z_score_indices:
            outliers_list.add(int(indice))
        for indice in large_positive_z_score_indices:
            outliers_list.add(int(indice))

    outliers_list = list(outliers_list)

    return outliers_list



#~~~~~~~~~~~~~~~~~~~~~~~~~~
#    EXPORTING RESULTS
#~~~~~~~~~~~~~~~~~~~~~~~~~~

def generate_project_statistics(image_set_parameters):
    """
    Calculates the mean, median, STD, Range, and IQR for every parameter in every image and formats into an excel-style list to be exported to an excel sheet
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set

    Returns:
        top_condition_dict (list): list formated excel-style with mean, median, STD, Range, and IQR for every parameter in every image
    """
    project_statistics = []

    topRow = ['METRIC']
    statistics = ['Mean', 'Median', 'STD', 'Range', 'IQR']
    for stat in statistics:
        for image_parameters in image_set_parameters:
            topRow.append(f'{image_parameters["Date"]} ({stat})')

    project_statistics.append(topRow)


    image_parameter_dataset = {}
    for parameter_set in image_set_parameters:
        date = parameter_set['Date']

        parameter_dict = {}
        for metric in image_set_parameters[0]['Parameters'][0]['Metrics'].keys():
            parameter_dict[metric] = []

        image_cells_parameters = parameter_set['Parameters']
        for cell in image_cells_parameters:
            cell_parameters = cell['Metrics']
            for metric in cell_parameters.keys():
                parameter_dict[metric].append(cell_parameters[metric])

        image_parameter_dataset[date] = parameter_dict


    
    for metric in image_set_parameters[0]['Parameters'][0]['Metrics'].keys():
        parameter_row = [metric]
        # Mean Values
        for date in image_parameter_dataset.keys():
            mean = np.mean(image_parameter_dataset[date][metric])
            parameter_row.append(float(mean))

        # Median Values
        for date in image_parameter_dataset.keys():
            median = np.median(image_parameter_dataset[date][metric])
            parameter_row.append(float(median))
        
        # STD Values
        for date in image_parameter_dataset.keys():
            std = np.std(image_parameter_dataset[date][metric])
            parameter_row.append(float(std))

        # Range Values
        for date in image_parameter_dataset.keys():
            range = np.max(image_parameter_dataset[date][metric]) - np.min(image_parameter_dataset[date][metric])
            parameter_row.append(float(range))

        # IQR Values
        for date in image_parameter_dataset.keys():
            q75 = np.percentile(image_parameter_dataset[date][metric], 75)
            q25 = np.percentile(image_parameter_dataset[date][metric], 25)
            IQR = q75 - q25
            parameter_row.append(float(IQR))

        project_statistics.append(parameter_row)


    return project_statistics


def generate_project_histograms(image_set_parameters, project):
    """
    Creates histograms for every parameter in every image and saves to the project folder under Histograms
    DO NOT USE - NOT FUNCTIONAL
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set
        project (string): string specifying the project we are generating histograms for
    """
    image_parameter_dataset = {}
    for parameter_set in image_set_parameters:
        date = parameter_set['Date']

        parameter_dict = {}
        for metric in image_set_parameters[0]['Parameters'][0]['Metrics'].keys():
            parameter_dict[metric] = []

        image_cells_parameters = parameter_set['Parameters']
        for cell in image_cells_parameters:
            cell_parameters = cell['Metrics']
            for metric in cell_parameters.keys():
                parameter_dict[metric].append(cell_parameters[metric])

        image_parameter_dataset[date] = parameter_dict

    colors = ['Red', 'Yellow', 'Green', 'Blue']
    for metric in image_set_parameters[0]['Parameters'][0]['Metrics'].keys():
        index = 0
        for date in image_parameter_dataset.keys():
            plt.hist(image_parameter_dataset[date][metric], bins=30, alpha=0.5, label=date, color=colors[index])
            index += 1
        plt.xlabel(metric)
        plt.ylabel('Frequency')
        plt.legend(loc='upper right')
        label_string = f'projects/{project}/Histograms/{metric} Histogram'
        plt.savefig(bbox_inches='tight')
    


##################################
#              PCA
##################################


def remove_nan_values_from_image_set_parameters(image_set_parameters):
    """
    Removes cells with nan-valued parameters from image_set_parameters and returns as a new list
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set, as well as the average parameters

    Returns:
        image_set_parameters_no_nan (list): list containing the date and parameters of every segmentation in every image in the image set, as well as the average parameters, with all cells with nan values removed
    """
    image_set_parameters_no_nan = {
        'Average': [],
        'Individual': []
    }

    for i in range(len(image_set_parameters['Average'])):
        all_metrics_non_nan = True
        for metric in list(image_set_parameters['Average'][i]['Parameters'].keys()):
            if np.isnan(image_set_parameters['Average'][i]['Parameters'][metric]):
                all_metrics_non_nan = False
        
        if all_metrics_non_nan:
            image_set_parameters_no_nan['Average'].append({
                'Date': image_set_parameters['Average'][i]['Date'],
                'Parameters': image_set_parameters['Average'][i]['Parameters']
            })

    for i in range(len(image_set_parameters['Individual'])):
        curr_image_parameters = []
        for j in range(len(image_set_parameters['Individual'][i]['Parameters'])):
            all_metrics_non_nan = True
            for metric in list(image_set_parameters['Individual'][i]['Parameters'][j]['Metrics'].keys()):
                if np.isnan(image_set_parameters['Individual'][i]['Parameters'][j]['Metrics'][metric]):
                    all_metrics_non_nan = False
            
            if all_metrics_non_nan:
                curr_image_parameters.append(image_set_parameters['Individual'][i]['Parameters'][j])
        
        image_set_parameters_no_nan['Individual'].append({
            'Date': image_set_parameters['Individual'][i]['Date'],
            'Parameters': curr_image_parameters
        })
    
    return image_set_parameters_no_nan


def standardize_image_set_parameters(image_set_parameters):
    """
    Standardizes the parameters of every segmentation in every image by subtracting by the parameter mean and divinding by the parameter standard deviation
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set, as well as the average parameters

    Returns:
        image_set_parameters (list): list containing the date and standardized parameters of every segmentation in every image in the image set
        metric_all_values_standardized (dict): dict containing the a list of standardized values from every segmentation in every image for each parameter
    """
    individual_image_set_parameters = image_set_parameters['Individual']
    #print(individual_image_set_parameters[0]['Parameters'][0]['Metrics'])
    metric_all_values = {}
    for metric in list(individual_image_set_parameters[0]['Parameters'][0]['Metrics'].keys()):
        metric_values = []
        for i in range(len(individual_image_set_parameters)):
            for j in range(len(individual_image_set_parameters[i]['Parameters'])):
                metric_values.append(individual_image_set_parameters[i]['Parameters'][j]['Metrics'][metric])

        metric_all_values[metric] = metric_values
    
    metric_all_values_standardized = {}
    for metric in list(metric_all_values.keys()):
        metric_all_values[metric] = np.array(metric_all_values[metric])
        metric_mean = np.mean(metric_all_values[metric])
        metric_std = np.std(metric_all_values[metric])

        metric_all_values_standardized[metric] = (metric_all_values[metric] - metric_mean) / metric_std

        for i in range(len(image_set_parameters['Individual'])):
            for j in range(len(image_set_parameters['Individual'][i]['Parameters'])):
                image_set_parameters['Individual'][i]['Parameters'][j]['Metrics'][metric] = (image_set_parameters['Individual'][i]['Parameters'][j]['Metrics'][metric] - metric_mean) / metric_std
                

    return image_set_parameters, metric_all_values_standardized

def get_pca_features_all_masks(image_set_parameters):
    """
    Finds the first three principal components in the image_set and returns the projection of the image_set onto the three components
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in every image in the image set, as well as the average parameters

    Returns:
        pc_dict (dict): dict containing the date and projected parameters of every segmentation in every image in the image set onto the first three principal components
    """
    image_set_parameters = remove_nan_values_from_image_set_parameters(image_set_parameters)
    standardized_image_set_parameters, metric_all_values_standardized = standardize_image_set_parameters(image_set_parameters)

    standardized_metric_dataset = []
    for metric in list(metric_all_values_standardized.keys()):
        standardized_metric_dataset.append(metric_all_values_standardized[metric])

    covariance_matrix = np.cov(standardized_metric_dataset)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    pc_eigenvalues = eigenvalues[-3:]
    pc_eigenvectors = eigenvectors[-3:]

    eigenvalue_sum = np.sum(eigenvalues)
    pc_eigenvalues_sum = np.sum(pc_eigenvalues)
    # print(pc_eigenvalues_sum / eigenvalue_sum)
    # print(pc_eigenvectors)


    pc_dict = {}
    for i in range(1, 4):
        metric = f'Principal Component {i}'
        individual_cell_sequential_metrics = []
        for image_parameters in standardized_image_set_parameters['Individual']:

            individual_cell_sequential_metric_values = []
            for parameter_set in image_parameters['Parameters']:
                metric_list = []
                for key in list(parameter_set['Metrics'].keys()):
                    metric_list.append(parameter_set['Metrics'][key])
                
                pc_metric = np.dot(pc_eigenvectors[-i], np.array(metric_list))
                individual_cell_sequential_metric_values.append(pc_metric)

            individual_cell_sequential_metrics.append({
                'Date': image_parameters['Date'],
                'Values': individual_cell_sequential_metric_values,
            })

    

        sorted_individual_cell_sequential_metrics = list(sorted(individual_cell_sequential_metrics, key=lambda item: item['Date']))
        pc_dict[metric] = sorted_individual_cell_sequential_metrics

    return pc_dict


###############################
#      Average Masks PCA
###############################


def standardize_average_image_set_parameters(image_set_parameters):
    """
    Standardizes the average parmaeters in every image by subtracting by the average parameter mean and divinding by the average parameter standard deviation
    Average parameters, not all masks
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and average parameters of every image in the image set

    Returns:
        image_set_parameters (list): list containing the date and standardized average parameters of every image in the image set
        metric_all_values_standardized (dict): dict containing the a list of standardized values from every image for each average parameter
    """
    average_image_set_parameters = image_set_parameters['Average']
    #print(individual_image_set_parameters[0]['Parameters'][0]['Metrics'])
    metric_all_values = {}
    for metric in list(average_image_set_parameters[0]['Parameters'].keys()):
        metric_values = []
        for i in range(len(average_image_set_parameters)):
            metric_values.append(average_image_set_parameters[i]['Parameters'][metric])

        metric_all_values[metric] = metric_values
    
    metric_all_values_standardized = {}
    for metric in list(metric_all_values.keys()):
        metric_all_values[metric] = np.array(metric_all_values[metric])
        metric_mean = np.mean(metric_all_values[metric])
        metric_std = np.std(metric_all_values[metric])

        metric_all_values_standardized[metric] = (metric_all_values[metric] - metric_mean) / metric_std

        for i in range(len(image_set_parameters['Average'])):
            image_set_parameters['Average'][i]['Parameters'][metric] = (image_set_parameters['Average'][i]['Parameters'][metric] - metric_mean) / metric_std
                

    return image_set_parameters, metric_all_values_standardized


def get_pca_features_average_masks(image_set_parameters):
    """
    Finds the first three principal components in the image_set and returns the projection of the image_set onto the three components
    Average parameters, not all masks
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and average parameters of every image in the image set

    Returns:
        pc_dict (dict): dict containing the date and projected average parameters of every image in the image set onto the first three principal components
    """
    image_set_parameters = remove_nan_values_from_image_set_parameters(image_set_parameters)
    standardized_image_set_parameters, metric_all_values_standardized = standardize_average_image_set_parameters(image_set_parameters)

    standardized_metric_dataset = []
    for metric in list(metric_all_values_standardized.keys()):
        standardized_metric_dataset.append(metric_all_values_standardized[metric])

    covariance_matrix = np.cov(standardized_metric_dataset)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    pc_eigenvalues = eigenvalues[-3:]
    pc_eigenvectors = eigenvectors[-3:]


    pc_dict = {}
    for i in range(1, 4):
        metric = f'Principal Component {i}'
        individual_cell_sequential_metrics = []
        for image_parameters in standardized_image_set_parameters['Average']:
            metric_list = []
            for key in list(image_parameters['Parameters'].keys()):
                metric_list.append(image_parameters['Parameters'][key])
                
            pc_metric = np.dot(pc_eigenvectors[-i], np.array(metric_list))

            individual_cell_sequential_metrics.append({
                'Date': image_parameters['Date'],
                'Value': pc_metric,
            })

    

        sorted_individual_cell_sequential_metrics = list(sorted(individual_cell_sequential_metrics, key=lambda item: item['Date']))
        pc_dict[metric] = sorted_individual_cell_sequential_metrics

    return pc_dict


#################################
#       PCA Single Image
#################################
    

def remove_nan_values_from_image_set_parameters_single_image(image_set_parameters):
    """
    Removes cells with nan-valued parameters from image_set_parameters and returns as a new list
    Single image
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in the image

    Returns:
        image_set_parameters_no_nan (list): list containing the date and parameters of every segmentation in the image, with all cells with nan values removed
    """
    image_set_parameters_no_nan = []

    for i in range(len(image_set_parameters)):
        all_metrics_non_nan = True
        for metric in list(image_set_parameters[i]['Metrics'].keys()):
            if np.isnan(image_set_parameters[i]['Metrics'][metric]):
                all_metrics_non_nan = False
            
        if all_metrics_non_nan:
            image_set_parameters_no_nan.append(image_set_parameters[i])
        
    
    return image_set_parameters_no_nan


def standardize_image_set_parameters_single_image(image_set_parameters):
    """
    Standardizes the parameters of every segmentation in the image by subtracting by the parameter mean and divinding by the parameter standard deviation
    Single Image
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in the image

    Returns:
        image_set_parameters (list): list containing the date and standardized parameters of every segmentation in the image
        metric_all_values_standardized (dict): dict containing the a list of standardized values from every segmentation in the image for each parameter
    """
    metric_all_values = {}
    for metric in list(image_set_parameters[0]['Metrics'].keys()):
        metric_values = []
        for i in range(len(image_set_parameters)):
            metric_values.append(image_set_parameters[i]['Metrics'][metric])

        metric_all_values[metric] = metric_values
    
    metric_all_values_standardized = {}
    for metric in list(metric_all_values.keys()):
        metric_all_values[metric] = np.array(metric_all_values[metric])
        metric_mean = np.mean(metric_all_values[metric])
        metric_std = np.std(metric_all_values[metric])

        metric_all_values_standardized[metric] = (metric_all_values[metric] - metric_mean) / metric_std

        for i in range(len(image_set_parameters)):
            image_set_parameters[i]['Metrics'][metric] = (image_set_parameters[i]['Metrics'][metric] - metric_mean) / metric_std
                

    return image_set_parameters, metric_all_values_standardized



def get_pca_features_all_masks_single_image(image_set_parameters):
    """
    Finds the first three principal components in the image parameters and returns the projection of the image parameters onto the three components
    Single Image
    Author(s): Kaden Stillwagon

    Args:
        image_set_parameters (list): list containing the date and parameters of every segmentation in the image

    Returns:
        pc_dict (dict): dict containing the date and projected parameters of every segmentation in the image onto the first three principal components
    """
    image_parameters = remove_nan_values_from_image_set_parameters_single_image(image_parameters)
    standardized_image_set_parameters, metric_all_values_standardized = standardize_image_set_parameters_single_image(image_parameters)

    standardized_metric_dataset = []
    for metric in list(metric_all_values_standardized.keys()):
        standardized_metric_dataset.append(metric_all_values_standardized[metric])

    # print(np.array(standardized_metric_dataset).shape)
    covariance_matrix = np.cov(standardized_metric_dataset)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
    pc_eigenvalues = eigenvalues[-4:]
    pc_eigenvectors = eigenvectors[-4:]

    # print(eigenvalues)
    # eigenvalue_sum = np.sum(eigenvalues)
    # pc_eigenvalues_sum = np.sum(pc_eigenvalues)
    # print(pc_eigenvalues_sum / eigenvalue_sum)
    # print(pc_eigenvectors)



    pc_dict = {}
    for i in range(1, 5):
        metric = f'Principal Component {i}'
        individual_cell_sequential_metrics = []
        for cell_parameters in standardized_image_set_parameters:
            metric_list = []
            for key in list(cell_parameters['Metrics'].keys()):
                metric_list.append(cell_parameters['Metrics'][key])
                
            pc_metric = np.dot(pc_eigenvectors[-i], np.array(metric_list))
            individual_cell_sequential_metrics.append(pc_metric)


        pc_dict[metric] = individual_cell_sequential_metrics

    return pc_dict

