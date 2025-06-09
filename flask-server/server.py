from flask import Flask, request, send_file, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from datetime import timedelta
from parameters_main import create_metric_dataset_for_single_image
import json
from parameter_tracking import *
from PIL import Image
import base64
import io
from cell_parameter_metrics import *
import server_utils
import pandas as pd
import numpy as np
from tqdm import tqdm

app = Flask(__name__, static_folder="dist", static_url_path="")
CORS(app, origins=["http://localhost:5173"])

print("✅ Flask app loaded")

# Serve Frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')  # for SPA routing

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    Getting Project Data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route("/get_projects_data") 
def get_projects_data():
    """
    Flask endpoint that returns the cover images paths, titles, and descriptions of each of the projects to the React website
    Author(s): Kaden Stillwagon

    Returns:
        (dict): dict containing the cover images paths, titles, and descriptions of each of the projects
    """
    projects_data_file = open('projects/projects_data.json')
    projects_data = json.load(projects_data_file)

    project_titles = []
    project_descriptions = []
    project_cover_images = []

    for project in projects_data:
        project_cover_images.append(project['Cover Image'])
        project_titles.append(project['Title'])
        project_descriptions.append(project['Description'])

    return {'Project Images': project_cover_images, 'Project Titles': project_titles, 'Project Descriptions': project_descriptions}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Getting Images
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@app.route("/get_cover_image", methods=["POST"])
def get_cover_image():
    """
    Flask endpoint that returns the cover image for the specified project to the React website
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project to return the cover image for

    Returns:
        (file): png of the cover image for the specified project
    """
    project = request.values['Project']

    projects_data_file = open('projects/projects_data.json')
    projects_data = json.load(projects_data_file)

    cover_image_path = ''

    for project_data in projects_data:
        if project_data['Title'] == project:
            cover_image_path = project_data['Cover Image']

    if cover_image_path == 'None':
        return {'cover_image': cover_image_path}
    else:
        return send_file(cover_image_path, as_attachment=True)


@app.route("/get_specific_image", methods=["POST"])
def get_specific_image():
    """
    Flask endpoint that returns a specific image from the specified project at the specified date
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Date (string): string specifying the date of the image to return

    Returns:
        (file): png of the image from the specified project at the specified date
    """
    project = request.values['Project']
    date = request.values['Date']

    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != ".DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Captured'] == date:
                return send_file(f'projects/{project}/cell_images/{image_folder}/image_input.png', as_attachment=True)

    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != "..DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Uploaded'] == date:
                return send_file(f'projects/{project}/cell_images/{image_folder}/image_input.png', as_attachment=True)


@app.route("/get_segmented_cell_image", methods=["POST"])
def get_segmented_cell_image():
    """
    Flask endpoint that returns the image of a specific segmentation from the specified project at the specified date
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Date (string): string specifying the date of the image
        Segmentation Index (string): string-integer specifying the index cell to return an image of

    Returns:
        (file): png of the cell at the specified index from the specified project at the specified date
    """
    project = request.values['Project']
    date = request.values['Date']
    segmentation_index = int(request.values['Segmentation Index'])

    target_image_folder = None
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != ".DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Captured'] == date:
                target_image_folder = image_folder

    if (target_image_folder == None):
        for image_folder in os.listdir(f'projects/{project}/cell_images'):
            if image_folder != "..DS_Store":
                image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
                image_data = json.load(image_data_file)

                if image_data['Datetime Uploaded'] == date:
                    target_image_folder = image_folder


    f = open(f'projects/{project}/cell_images/{target_image_folder}/parameters.json')
    image_parameters = json.load(f)['Full Dataset']
    print(date)
    print(len(image_parameters))
    cell_index = image_parameters[segmentation_index]['Cell Index']

    image = get_sample_image(project=project, image_date=target_image_folder)
    segmentations = get_sample_segmentation(project=project, image_date=target_image_folder)

    cell_mask = get_cell_mask(project=project, image_date=target_image_folder, cell=cell_index, seg_out=segmentations)
    masked_image = get_mask_pixel_intensities(image, cell_mask)
    cropped_image_array = crop_to_mask(masked_image)

    cropped_image = Image.fromarray(cropped_image_array.astype('uint8'))
    cropped_image_io = io.BytesIO()
    cropped_image.save(cropped_image_io, 'PNG')
    cropped_image_io.seek(0)

    return send_file(cropped_image_io, download_name="segmentation", mimetype='image/PNG', as_attachment=True)


@app.route("/get_whole_image_with_highlighted_segmentation", methods=["POST"])
def get_whole_image_with_highlighted_segmentation():
    """
    Flask endpoint that returns an image from the specified project at the specified date, with the specified cell highlighted
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Date (string): string specifying the date of the image
        Segmentation Index (string): string-integer specifying the index cell to return an image of

    Returns:
        (file): png of the image from the specified project at the specified date, with the specified cell highlighted
    """
    project = request.values['Project']
    date = request.values['Date']
    segmentation_index = int(request.values['Segmentation Index'])

    target_image_folder = None
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != ".DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Captured'] == date:
                target_image_folder = image_folder

    if (target_image_folder == None):
        for image_folder in os.listdir(f'projects/{project}/cell_images'):
            if image_folder != "..DS_Store":
                image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
                image_data = json.load(image_data_file)

                if image_data['Datetime Uploaded'] == date:
                    target_image_folder = image_folder


    f = open(f'projects/{project}/cell_images/{target_image_folder}/parameters.json')
    image_parameters = json.load(f)['Full Dataset']
    print(date)
    print(len(image_parameters))
    cell_index = image_parameters[segmentation_index]['Cell Index']

    image = get_sample_image(project=project, image_date=target_image_folder)
    segmentations = get_sample_segmentation(project=project, image_date=target_image_folder)

    cell_mask = get_cell_mask(project=project, image_date=target_image_folder, cell=cell_index, seg_out=segmentations)
    #masked_image_array = get_mask_pixel_intensities(image, cell_mask)
    highlighted_mask_image_array = get_highlighted_mask(image, cell_mask)
    #cropped_image_array = crop_to_mask(masked_image_array)

    highlighted_mask_image = Image.fromarray(highlighted_mask_image_array.astype('uint8'), 'RGB')
    highlighted_mask_image_io = io.BytesIO()
    highlighted_mask_image.save(highlighted_mask_image_io, 'PNG')
    highlighted_mask_image_io.seek(0)

    return send_file(highlighted_mask_image_io, download_name="segmentation", mimetype='image/PNG', as_attachment=True)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    Uploading New Data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route("/upload_image", methods=["POST"])
def upload_image():
    """
    Flask endpoint that takes in an image, segmentation csv, and date, calculates the segmentation metrics, and adds the specified project's folder
    Author(s): Kaden Stillwagon

    Args:
        image (file): png of the image to be added to the project
        segmentation_csv (file): csv containing the image's segmentations
        date-time (string): string specifying the date and time when the image was taken
        Project (string): string specifying the name of the project

    Returns:
        (dict): dict containing a boolean success marker
    """
    image = request.files.get('image')
    image_filename = image.filename

    segmentation_csv = request.files.get('segmentation_csv')
    segmentation_csv_filename = segmentation_csv.filename

    image_date = request.values.get('date-time')
    if len(image_date) == 0:
        image_date = None

    project = request.values['Project']

    print(image_filename)
    print(segmentation_csv_filename)
    print(image_date)
    print(project)


    curr_date_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    os.mkdir(f'projects/{project}/cell_images/{curr_date_time}')
    image.save(f'projects/{project}/cell_images/{curr_date_time}/image_input.png')
    segmentation_csv.save(f'projects/{project}/cell_images/{curr_date_time}/segmentation_output.csv')

    meta_data = {
        'Datetime Captured': image_date,
        'Datetime Uploaded': curr_date_time
    }

    with open(f'projects/{project}/cell_images/{curr_date_time}/meta_data.json', 'w') as f:
        json.dump(meta_data, f)

    projects_data_file = open('projects/projects_data.json')
    projects_data = json.load(projects_data_file)

    for i in range(len(projects_data)):
        if projects_data[i]['Title'] == project:
            image_folders = os.listdir(f'projects/{project}/cell_images')

            projects_data[i]['Cover Image'] = f'projects/{project}/cell_images/{image_folders[0]}/image_input.png'

    with open('projects/projects_data.json', 'w') as f:
        json.dump(projects_data, f)

    dataset, mean_dataset = create_metric_dataset_for_single_image(project, curr_date_time)
    image_data = {
        "Average Data": mean_dataset,
        "Full Dataset": dataset
    }
    with open(f'projects/{project}/cell_images/{curr_date_time}/parameters.json', 'w') as f:
        json.dump(image_data, f)

    return {"success": True}



@app.route("/upload_many_images", methods=["POST"])
def upload_many_images():
    """
    Flask endpoint that takes in an lists of images, names, and annotation (segmentations), calculates the segmentation metrics for each, and adds each the specified project's folder
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        images (file): npy file containing the images
        names (file): npy file containing the image names
        annotations (file): npy file containing the segmentations

    Returns:
        (dict): dict containing a boolean success marker
    """
    project = request.values['Project']
    images = request.files.get('images')
    names = request.files.get('names')
    annotations = request.files.get('annotations')

    images = np.load(images)
    names = np.load(names)
    annotations = np.load(annotations)

    img_datetimes = server_utils.convert_image_names_to_datetimes(names)
    
    index_stopped = 0 # RESET TO 0 (note: add +1 to the actual index if starting from 0)
    # Death 1: 4-20 (Need 5, 7-15, 18-20)
    # indices_needed = [14, 15, 18, 19, 20]
    # Death 2: 219-END(287) (Need all)
    last_timestamp = datetime.strptime("0001-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    min_second_diff = 15
    for i in tqdm(range(index_stopped, len(img_datetimes))): #len(img_datetimes)
        print(f'\n~~~~Image {i+1}/{len(img_datetimes)}~~~~\n')

        image_date = img_datetimes[i]
        image_date_time = datetime.strptime(image_date, "%Y-%m-%dT%H:%M:%S")
        #Only collect image parameters if taken at least min_second_diff seconds after last image in dataset - NOT USED
        # time_diff = image_date_time - last_timestamp

        last_timestamp = image_date_time
        curr_date_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        image = Image.fromarray(images[i])
        segmentation_df = pd.DataFrame(annotations[i])

        os.mkdir(f'projects/{project}/cell_images/{curr_date_time}')
        image.save(f'projects/{project}/cell_images/{curr_date_time}/image_input.png')
        segmentation_df.to_csv(f'projects/{project}/cell_images/{curr_date_time}/segmentation_output.csv', header=False, index=False)

        meta_data = {
            'Datetime Captured': image_date,
            'Datetime Uploaded': curr_date_time
        }

        with open(f'projects/{project}/cell_images/{curr_date_time}/meta_data.json', 'w') as f:
            json.dump(meta_data, f)

        projects_data_file = open('projects/projects_data.json')
        projects_data = json.load(projects_data_file)

        for i in range(len(projects_data)):
            if projects_data[i]['Title'] == project:
                image_folders = os.listdir(f'projects/{project}/cell_images')

                projects_data[i]['Cover Image'] = f'projects/{project}/cell_images/{image_folders[0]}/image_input.png'

        with open('projects/projects_data.json', 'w') as f:
            json.dump(projects_data, f)

        dataset, mean_dataset = create_metric_dataset_for_single_image(project, curr_date_time)
        image_data = {
            "Average Data": mean_dataset,
            "Full Dataset": dataset
        }
        with open(f'projects/{project}/cell_images/{curr_date_time}/parameters.json', 'w') as f:
            json.dump(image_data, f)

    return {"success": True}




@app.route("/add_new_project", methods=["POST"])
def add_new_project():
    """
    Flask endpoint that takes in a project title and description, creates a new project, and adds to the projects folder
    Author(s): Kaden Stillwagon

    Args:
        Title (string): string specifying the name of the project
        Description (file): string descriping the project

    Returns:
        (dict): dict containing a boolean success marker
    """
    project_title = request.values['Title']
    project_description = request.values['Description']
    if project_description == 'undefined':
        project_description = 'No Description'

    print(project_title)
    print(project_description)

    curr_date_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    new_project_data = {
        'Title': project_title,
        'Description': project_description,
        'Cover Image': 'None',
        'Datetime Created': curr_date_time
    }

    f = open('projects/projects_data.json')
    projects_data = json.load(f)

    projects_data.append(new_project_data)

    with open(f'projects/projects_data.json', 'w') as f:
        json.dump(projects_data, f)

    os.mkdir(f'projects/{project_title}')
    os.mkdir(f'projects/{project_title}/cell_images')

    return {"success": True}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    Metrics with Specific Condition
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@app.route("/get_metrics_with_specific_condition_to_plot", methods=["POST"]) 
def get_metrics_with_specific_condition_to_plot():
    """
    Flask endpoint that returns the average metrics for the top three parameters for a specified condition
    Average Parameters
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Condition (string): string specifying the condition to pick the parameters by

    Returns:
        (dict): dict containing the dictionary of average metrics for the top parameters and a boolean success marker
    """
    project = request.values.get('Project')
    condition = request.values.get('Condition')

    project_images_parameters = []
    #print(os.listdir(f'projects/{project}/cell_images'))
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)['Average Data']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters.append({
                'Date': image_date,
                'Parameters': image_parameters
            })

    if len(project_images_parameters) > 0:
        top_condition_dict = find_specific_condition_parameters(image_set_parameters=project_images_parameters, condition=condition)
        return {"Success": True, "Parameter Dictionary": top_condition_dict}
    else:
        return {'Success': False}


@app.route("/get_metrics_with_specific_condition_to_plot_all_cell_masks", methods=["POST"]) 
def get_metrics_with_specific_condition_to_plot_all_cell_masks():
    """
    Flask endpoint that returns the metrics for the top three parameters for all cell masks for a specified condition
    All Parameters
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Condition (string): string specifying the condition to pick the parameters by

    Returns:
        (dict): dict containing the dictionary of metrics for the top parameters for all cell masks, a list of outlier cell indices for each image, and a boolean success marker
    """
    project = request.values.get('Project')
    condition = request.values.get('Condition')

    project_images_parameters = {
        'Average': [],
        'Individual': []
    }
    #print(os.listdir(f'projects/{project}/cell_images'))
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)
            average_parameters = image_parameters['Average Data']
            individual_cell_parameters = image_parameters['Full Dataset']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters['Average'].append({
                'Date': image_date,
                'Parameters': average_parameters
            })

            project_images_parameters['Individual'].append({
                'Date': image_date,
                'Parameters': individual_cell_parameters
            })

    if len(project_images_parameters['Average']) > 0:
        top_condition_dict = find_specific_condition_parameters_all_masks(image_set_parameters=project_images_parameters, condition=condition)

        outliers_list = find_outliers(top_condition_dict)

        return {"Success": True, "Parameter Dictionary": top_condition_dict, "Outliers": outliers_list}
    else: 
        return {"Success": False}



@app.route("/get_metrics_with_specific_condition_to_plot_all_cell_masks_single_image", methods=["POST"]) 
def get_metrics_with_specific_condition_to_plot_all_cell_masks_single_image():
    """
    Flask endpoint that returns the metrics for the top four parameters for all cell masks in a single image for a specified condition
    All Parameters, Single Image
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Condition (string): string specifying the condition to pick the parameters by
        Date (string): string specifying the date of the image

    Returns:
        (dict): dict containing the dictionary of metrics for the top parameters for all cell masks in the single image, a list of outlier cell indices for the image, and a boolean success marker
    """
    project = request.values.get('Project')
    condition = request.values.get('Condition')
    date = request.values.get('Date')

    target_image_folder = None
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != ".DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Captured'] == date:
                target_image_folder = image_folder

    if (target_image_folder == None):
        for image_folder in os.listdir(f'projects/{project}/cell_images'):
            if image_folder != "..DS_Store":
                image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
                image_data = json.load(image_data_file)

                if image_data['Datetime Uploaded'] == date:
                    target_image_folder = image_folder

    f = open(f'projects/{project}/cell_images/{target_image_folder}/parameters.json')
    image_parameters = json.load(f)
    project_image_parameters = image_parameters['Full Dataset']


    top_condition_dict = find_specific_condition_parameters_all_masks_single_image(image_parameters=project_image_parameters, condition=condition)

    outliers_list = find_outliers_single_image(top_condition_dict)

    return {"Success": True, "Parameter Dictionary": top_condition_dict, "Outliers": outliers_list}



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    Metrics with Specific Parameter
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route("/get_specific_metrics_to_plot", methods=["POST"]) 
def get_specific_metrics_to_plot():
    """
    Flask endpoint that returns the average metrics for the specified parameter
    Average Parameters
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Parameter (string): string specifying the parameter

    Returns:
        (dict): dict containing the dictionary of average metrics for the specified parameter and a boolean success marker
    """
    project = request.values.get('Project')
    parameter = request.values.get('Parameter')

    project_images_parameters = {
        'Average': [],
        'Individual': []
    }
    #print(os.listdir(f'projects/{project}/cell_images'))
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)
            average_parameters = image_parameters['Average Data']
            individual_cell_parameters = image_parameters['Full Dataset']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters['Average'].append({
                'Date': image_date,
                'Parameters': average_parameters
            })

            project_images_parameters['Individual'].append({
                'Date': image_date,
                'Parameters': individual_cell_parameters
            })

    if len(project_images_parameters) > 0:
        parameter_dict = find_parameter_values(image_set_parameters=project_images_parameters, parameter=parameter)
        return {"Success": True, "Parameter Dictionary": parameter_dict}
    else:
        return {'Success': False}


@app.route("/get_specific_metrics_to_plot_all_cell_masks", methods=["POST"]) 
def get_specific_metrics_to_plot_all_cell_masks():
    """
    Flask endpoint that returns the metrics for the specified parameter for all cell masks
    All Parameters
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Parameter (string): string specifying the parameter

    Returns:
        (dict): dict containing the dictionary of metrics for the specified parameter for all cell masks, a list of outlier cell indices for each image, and a boolean success marker
    """
    project = request.values.get('Project')
    parameter = request.values.get('Parameter')
    otherParameterOne = request.values.get('Other Parameter One')
    otherParameterTwo = request.values.get('Other Parameter Two')

    project_images_parameters = {
        'Average': [],
        'Individual': []
    }
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)
            average_parameters = image_parameters['Average Data']
            individual_cell_parameters = image_parameters['Full Dataset']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters['Average'].append({
                'Date': image_date,
                'Parameters': average_parameters
            })

            project_images_parameters['Individual'].append({
                'Date': image_date,
                'Parameters': individual_cell_parameters
            })


    if len(project_images_parameters) > 0:
        parameter_dict = find_parameter_values_all_masks(image_set_parameters=project_images_parameters, parameter=parameter)
        parameter_dict_other_one = find_parameter_values_all_masks(image_set_parameters=project_images_parameters, parameter=otherParameterOne)
        parameter_dict_other_two = find_parameter_values_all_masks(image_set_parameters=project_images_parameters, parameter=otherParameterTwo)

        outliers_list = find_outliers({
            parameter: parameter_dict[parameter],
            otherParameterOne: parameter_dict_other_one[otherParameterOne],
            otherParameterTwo: parameter_dict_other_two[otherParameterTwo]
        })

        return {"Success": True, "Parameter Dictionary": parameter_dict, "Outliers": outliers_list}
    else: 
        return {"Success": False}

    
@app.route("/get_specific_metrics_to_plot_single_image", methods=["POST"]) 
def get_specific_metrics_to_plot_single_image():
    """
    Flask endpoint that returns the metrics for the specified parameter for all cell masks in a single image
    All Parameters, Single Image
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Date (string): string specifying the date of the image
        Parameter (string): string specifying the parameter

    Returns:
        (dict): dict containing the dictionary of metrics for the specified parameter for all cell masks in the single image, a list of outlier cell indices for the image, and a boolean success marker
    """
    project = request.values.get('Project')
    date = request.values.get('Date')
    parameter = request.values.get('Parameter')
    otherParameterOne = request.values.get('Other Parameter One')
    otherParameterTwo = request.values.get('Other Parameter Two')
    otherParameterThree = request.values.get('Other Parameter Three')

    target_image_folder = None
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != ".DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Captured'] == date:
                target_image_folder = image_folder

    if (target_image_folder == None):
        for image_folder in os.listdir(f'projects/{project}/cell_images'):
            if image_folder != "..DS_Store":
                image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
                image_data = json.load(image_data_file)

                if image_data['Datetime Uploaded'] == date:
                    target_image_folder = image_folder

    f = open(f'projects/{project}/cell_images/{target_image_folder}/parameters.json')
    image_parameters = json.load(f)
    project_image_parameters = image_parameters['Full Dataset']

    parameter_dict = find_parameter_values_single_image(image_parameters=project_image_parameters, parameter=parameter)
    parameter_dict_other_one = find_parameter_values_single_image(image_parameters=project_image_parameters, parameter=otherParameterOne)
    parameter_dict_other_two = find_parameter_values_single_image(image_parameters=project_image_parameters, parameter=otherParameterTwo)
    parameter_dict_other_three = find_parameter_values_single_image(image_parameters=project_image_parameters, parameter=otherParameterThree)

    outliers_list = find_outliers_single_image({
        parameter: parameter_dict[parameter],
        otherParameterOne: parameter_dict_other_one[otherParameterOne],
        otherParameterTwo: parameter_dict_other_two[otherParameterTwo],
        otherParameterThree: parameter_dict_other_three[otherParameterThree]
    })

    return {"Success": True, "Parameter Dictionary": parameter_dict, "Outliers": outliers_list}


#~~~~~~~~~~~~~~~~~~~~~~~~
#    Exporting Data
#~~~~~~~~~~~~~~~~~~~~~~~~


@app.route("/get_project_data_to_export", methods=["POST"]) 
def get_project_data_to_export():
    """
    Flask endpoint that returns project statistics in an excel-style list
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project

    Returns:
        (dict): dict containing project statistics for a specified project
    """
    project = request.values.get('Project')

    project_images_parameters = []
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)['Full Dataset']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters.append({
                'Date': image_date,
                'Parameters': image_parameters
            })


    project_statistics = generate_project_statistics(image_set_parameters=project_images_parameters)
    #generate_project_histograms(image_set_parameters=project_images_parameters, project=project)

    return {"Success": True, "Data": project_statistics}




#~~~~~~~~~~~~~~~~~~~~~~~~
#          PCA
#~~~~~~~~~~~~~~~~~~~~~~~~


@app.route("/get_pca_metrics_all_cell_masks", methods=["POST"]) 
def get_pca_metrics_all_cell_masks():
    """
    Flask endpoint that returns the PCA metrics for all cell masks in the project images
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project

    Returns:
        (dict): dict containing the dictionary of PCA metrics for all cell masks in the project images, a list of outlier cell indices for each image, and a boolean success marker
    """
    project = request.values.get('Project')

    project_images_parameters = {
        'Average': [],
        'Individual': []
    }
    #print(os.listdir(f'projects/{project}/cell_images'))
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)
            average_parameters = image_parameters['Average Data']
            individual_cell_parameters = image_parameters['Full Dataset']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters['Average'].append({
                'Date': image_date,
                'Parameters': average_parameters
            })

            project_images_parameters['Individual'].append({
                'Date': image_date,
                'Parameters': individual_cell_parameters
            })

    if len(project_images_parameters['Average']) > 0:
        pc_dict = get_pca_features_all_masks(image_set_parameters=project_images_parameters)

        outliers_list = find_outliers(pc_dict)

        return {"Success": True, "Parameter Dictionary": pc_dict, "Outliers": outliers_list}
    else: 
        return {"Success": False}
    

@app.route("/get_pca_metrics_average_cell_masks", methods=["POST"]) 
def get_pca_metrics_average_cell_masks():
    """
    Flask endpoint that returns the aveage PCA metrics for the images in the project
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project

    Returns:
        (dict): dict containing the dictionary of average PCA metrics for the images in the project and a boolean success marker
    """
    project = request.values.get('Project')

    project_images_parameters = {
        'Average': [],
        'Individual': []
    }
    #print(os.listdir(f'projects/{project}/cell_images'))
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != '.DS_Store':
            f = open(f'projects/{project}/cell_images/{image_folder}/parameters.json')
            image_parameters = json.load(f)
            average_parameters = image_parameters['Average Data']
            individual_cell_parameters = image_parameters['Full Dataset']

            f = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_meta_data = json.load(f)

            image_date = image_meta_data['Datetime Captured']
            if image_date == 'None':
                image_date = image_meta_data['Datetime Uploaded']

            project_images_parameters['Average'].append({
                'Date': image_date,
                'Parameters': average_parameters
            })

            project_images_parameters['Individual'].append({
                'Date': image_date,
                'Parameters': individual_cell_parameters
            })

    if len(project_images_parameters['Average']) > 0:
        pc_dict = get_pca_features_average_masks(image_set_parameters=project_images_parameters)

        return {"Success": True, "Parameter Dictionary": pc_dict}
    else: 
        return {"Success": False}
    

@app.route("/get_pca_metrics_all_cell_masks_single_image", methods=["POST"]) 
def get_pca_metrics_all_cell_masks_single_image():
    """
    Flask endpoint that returns the PCA metrics for all cell masks in a single image
    Author(s): Kaden Stillwagon

    Args:
        Project (string): string specifying the name of the project
        Date (string): string specifying the date of the image

    Returns:
        (dict): dict containing the dictionary of PCA metrics for all cell masks in a single image, a list of outlier cell indices for the image, and a boolean success marker
    """
    project = request.values.get('Project')
    date = request.values.get('Date')

    target_image_folder = None
    for image_folder in os.listdir(f'projects/{project}/cell_images'):
        if image_folder != ".DS_Store":
            image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
            image_data = json.load(image_data_file)

            if image_data['Datetime Captured'] == date:
                target_image_folder = image_folder

    if (target_image_folder == None):
        for image_folder in os.listdir(f'projects/{project}/cell_images'):
            if image_folder != "..DS_Store":
                image_data_file = open(f'projects/{project}/cell_images/{image_folder}/meta_data.json')
                image_data = json.load(image_data_file)

                if image_data['Datetime Uploaded'] == date:
                    target_image_folder = image_folder

    f = open(f'projects/{project}/cell_images/{target_image_folder}/parameters.json')
    image_parameters = json.load(f)
    project_image_parameters = image_parameters['Full Dataset']


    pc_dict = get_pca_features_all_masks_single_image(image_set_parameters=project_image_parameters)

    outliers_list = find_outliers_single_image(pc_dict)

    return {"Success": True, "Parameter Dictionary": pc_dict, "Outliers": outliers_list}

# Serve Frontend
@app.route("/<path:path>")
def serve_react(path="index.html"):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(port=8000, debug=True)


