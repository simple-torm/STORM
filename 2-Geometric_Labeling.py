"""
Created on Thu Oct 26 10:28:08 2023

@author: dhers

This code will analyze the positions according to geometric parameters
"""

#%% Import libraries

import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Circle

import random

#%% Lets define some useful functions

class Point:
    def __init__(self, df, table):
        
        x = df[table + '_x']
        y = df[table + '_y']

        self.positions = np.dstack((x, y))[0]

    @staticmethod
    def dist(p1, p2):
        return np.linalg.norm(p1.positions - p2.positions, axis=1)

class Vector:
    def __init__(self, p1, p2, normalize=True):
        self.positions = p2.positions - p1.positions

        self.norm = np.linalg.norm(self.positions, axis=1)

        if normalize:
            self.positions = self.positions / np.repeat(
                np.expand_dims(
                    self.norm,
                    axis=1
                ),
                2,
                axis=1
            )

    @staticmethod
    def angle(v1, v2):
        length = len(v1.positions)

        angle = np.zeros(length)

        for i in range(length):
            angle[i] = np.rad2deg(
                np.arccos(
                    np.dot(
                        v1.positions[i], v2.positions[i]
                    )
                )
            )

        return angle

#%% This function finds the files that we want to use and lists their path

def find_files(path_name, exp_name, group, folder):
    
    group_name = f"/{group}"
    
    folder_name = f"/{folder}"
    
    wanted_files_path = os.listdir(path_name + exp_name + group_name + folder_name)
    wanted_files = []
    
    for file in wanted_files_path:
        if f"_{folder}.csv" in file:
            wanted_files.append(path_name + exp_name + group_name + folder_name + "/" + file)
            
    wanted_files = sorted(wanted_files)
    
    return wanted_files

#%%

# At home:
path = r'C:/Users/dhers/Desktop/Videos_NOR/'

# In the lab:
# path = r'/home/usuario/Desktop/Santi D/Videos_NOR/' 

experiment = r'2024-02_Persistance'

Hab_position = find_files(path, experiment, "Hab", "position")
TR1_position = find_files(path, experiment, "TR1", "position")
TR2_position = find_files(path, experiment, "TR2", "position")
TS_position = find_files(path, experiment, "TS", "position")

all_position = Hab_position + TR1_position + TR2_position + TS_position

#%%

"""
Lets see an example of the geometric algorithm
"""

video = random.randint(1, len(TS_position)) # Select the number of the video you want to use

example = TS_position[video - 1]

# %%

"""
We extract the positions of both objects and all the bodyparts.
"""
def plot_position(file, maxDistance = 2.5, maxAngle = 45):
    
    # Read the .csv
    df = pd.read_csv(file)
    
    # Extract the filename without extension
    filename = os.path.splitext(os.path.basename(file))[0]
    
    """
    Extract positions of both objects and bodyparts
    """
    
    obj1 = Point(df, 'obj_1')
    obj2 = Point(df, 'obj_2')
    
    nose = Point(df, 'nose')
    head = Point(df, 'head')
    
    """
    We now filter the frames where the mouse's nose is close to each object
    """
    
    # Find distance from the nose to each object
    dist1 = Point.dist(nose, obj1)
    dist2 = Point.dist(nose, obj2)
    
    """
    Next, we filter the points where the mouse is looking at each object
    """
    
    # Compute normalized head-nose and head-object vectors
    head_nose = Vector(head, nose, normalize = True)
    head_obj1 = Vector(head, obj1, normalize = True)
    head_obj2 = Vector(head, obj2, normalize = True)
    
    # Find the angles between the head-nose and head-object vectors
    angle1 = Vector.angle(head_nose, head_obj1) # deg
    angle2 = Vector.angle(head_nose, head_obj2) # deg
    
    # Find points where the mouse is looking at the objects
    # Im asking the nose be closer to the aimed object to filter distant sighting
    towards1 = nose.positions[(angle1 < maxAngle) & (dist1 < 3 * maxDistance)]
    towards2 = nose.positions[(angle2 < maxAngle) & (dist2 < 3 * maxDistance)]

    """
    Finally, we can plot the points that match both conditions
    """
    
    # Highlight positions where the mouse is close to each object
    fig, ax = plt.subplots()
    
    # Plot the nose positions
    ax.plot(*nose.positions.T, ".", color = "grey", alpha = 0.2)
    
    # Plot the filtered points
    ax.plot(*towards1.T, ".", label = "Oriented towards 1", color = "blue", alpha = 0.5)
    ax.plot(*towards2.T, ".", label = "Oriented towards 2", color = "darkgreen", alpha = 0.5)
    
    # Plot the objects
    ax.plot(*obj1.positions[0], "o", lw = 20, label = "Object 1", color = "red")
    ax.plot(*obj2.positions[0], "o", lw = 20, label = "Object 2", color = "darkorange")
    
    # Plot the circles of distance criteria
    ax.add_artist(Circle(obj1.positions[0], maxDistance, color = "purple", alpha = 0.4))
    ax.add_artist(Circle(obj2.positions[0], maxDistance, color = "purple", alpha = 0.4))
    
    ax.axis('equal')
    ax.set_xlabel("Horizontal position (cm)")
    ax.set_ylabel("Vertical position (cm)")
    ax.legend(bbox_to_anchor = (0, 0, 1, 1), ncol=2, loc='upper left', fancybox=True, shadow=True)
    
    plt.title(f"Analysis of {filename}")
    plt.tight_layout()
    plt.show()

#%%

plot_position(example, maxDistance = 2.5, maxAngle = 45)

#%%

"""
Now we define the function that creates the geometric labels for all _position.csv files in a folder
"""

def create_geolabels(files, maxDistance = 2.5, maxAngle = 45):
    
    for file in files:
    
        position = pd.read_csv(file)
    
        # Extract positions of both objects and bodyparts
        obj1 = Point(position, 'obj_1')
        obj2 = Point(position, 'obj_2')
        nose = Point(position, 'nose')
        head = Point(position, 'head')
    
        # Calculate distances
        dist1 = Point.dist(nose, obj1)
        dist2 = Point.dist(nose, obj2)
    
        # Calculate angles
        head_nose = Vector(head, nose, normalize=True)
        head_obj1 = Vector(head, obj1, normalize=True)
        head_obj2 = Vector(head, obj2, normalize=True)
    
        angle1 = Vector.angle(head_nose, head_obj1)
        angle2 = Vector.angle(head_nose, head_obj2)
    
        geolabels = pd.DataFrame(np.zeros((len(dist1), 3)), columns=["Frame", "Left", "Right"]) 
        
        distances = pd.DataFrame(np.zeros((len(dist1), 3)), columns=["Frame", "nose_dist", "body_dist"])
        
        for i in range(len(dist1)):
            
            geolabels["Frame"][i] = i+1
            
            distances["Frame"][i] = i+1
            
            # Check if mouse is exploring object 1
            if dist1[i] < maxDistance and angle1[i] < maxAngle:
                geolabels["Left"][i] = 1
    
            # Check if mouse is exploring object 2
            elif dist2[i] < maxDistance and angle2[i] < maxAngle:
                geolabels["Right"][i] = 1
    
        geolabels['Frame'] = geolabels['Frame'].astype(int)
        geolabels['Left'] = geolabels['Left'].astype(int)
        geolabels['Right'] = geolabels['Right'].astype(int)
        
        # Calculate the Euclidean distance between consecutive nose positions
        distances['nose_dist'] = ((position['nose_x'].diff())**2 + (position['nose_y'].diff())**2)**0.5
        distances['body_dist'] = ((position['body_x'].diff())**2 + (position['body_y'].diff())**2)**0.5
        
        # Replace NaN values with 0
        distances = distances.fillna(0)
    
        # Determine the output file path
        input_dir, input_filename = os.path.split(file)
        parent_dir = os.path.dirname(input_dir)
    
        # Create a filename for the output CSV file
        output_filename_geolabels = input_filename.replace('_position.csv', '_geolabels.csv')
        output_folder_geolabels = os.path.join(parent_dir + '/geolabels')
        os.makedirs(output_folder_geolabels, exist_ok = True)
        output_path_geolabels = os.path.join(output_folder_geolabels, output_filename_geolabels)
        geolabels.to_csv(output_path_geolabels, index=False)
        
        output_filename_distances = input_filename.replace('_position.csv', '_distances.csv')
        output_folder_distances = os.path.join(parent_dir + '/distances')
        os.makedirs(output_folder_distances, exist_ok = True)
        output_path_distances = os.path.join(output_folder_distances, output_filename_distances)
        distances.to_csv(output_path_distances, index=False)        
            
        print(f"Processed {input_filename} and saved results to {output_filename_geolabels}")

#%%

create_geolabels(all_position, maxDistance = 2.5, maxAngle = 45)
