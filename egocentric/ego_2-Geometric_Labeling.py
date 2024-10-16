"""
Created on Wed Aug 28 11:49:30 2024

@author: Santiago D'hers

Use:
    - This script will create the geolabels and calculate the distance traveled

Requirements:
    - The position.csv files processed by 1-Manage_H5.py
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
    
    files_path = os.path.join(path_name, exp_name, group, folder)
    files = os.listdir(files_path)
    wanted_files = []
    
    for file in files:
        if f"_{folder}.csv" in file:
            wanted_files.append(os.path.join(files_path, file))
            
    wanted_files = sorted(wanted_files)
    
    return wanted_files

#%%

# State your path:
path = r'C:/Users/dhers/OneDrive - UBA/workshop'
experiment = r'2023-05_TeNOR'

Hab_position = find_files(path, experiment, "Hab", "position")
TR1_position = find_files(path, experiment, "TR1", "position")
TR2_position = find_files(path, experiment, "TR2", "position")
TS_position = find_files(path, experiment, "TS", "position")

all_position = Hab_position + TR1_position + TR2_position + TS_position

#%% Lets see an example of the geometric algorithm

video = random.randint(1, len(TS_position)) # Select the number of the video you want to use
example = TS_position[video - 1]

#%%

# Define the rotation function
def rotate_points(df, angle):
    # Create the rotation matrix
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])
    
    # Apply the rotation to all coordinates
    for col in df.columns:
        if '_x' in col:
            y_col = col.replace('_x', '_y')
            xy_coords = np.vstack((df[col], df[y_col])).T
            rotated_coords = xy_coords @ rotation_matrix
            df[col], df[y_col] = rotated_coords[:, 0], rotated_coords[:, 1]

    return df

def recenter_points(df):
    # Subtract the nose_x and nose_y for each row from the corresponding '_x' and '_y' columns
    for col in df.columns:
        if 'nose' not in col:
            if '_x' in col:
                df[col] = df[col] - df['nose_x']
            elif '_y' in col:
                df[col] = df[col] - df['nose_y']
    
    # Set nose coordinates to (0, 0)
    df['nose_x'] = 0
    df['nose_y'] = 0

    return df

#%%

def rotate_and_recenter(df):
    
    # Define the neck and head points
    nose = Point(df, 'nose')
    head = Point(df, 'head')
    
    # Calculate the vector from neck to head
    vector_nose_head = Vector(nose, head)
    
    # The target vector is vertical, i.e., (0, -1), so we use the y-axis unit vector
    vertical_vector = np.array([0, -1])
    
    # Calculate the angles to rotate the neck-head vector to align with the vertical axis
    # Assuming all vectors are normalized, we calculate the rotation angle in radians
    angles = np.arccos(np.clip(np.dot(vector_nose_head.positions, vertical_vector), -1.0, 1.0))
    
    # Check the direction of rotation by using the cross product
    # Negative angles will be corrected by multiplying by -1
    cross_product = np.cross(vector_nose_head.positions, np.tile(vertical_vector, (len(angles), 1)))
    
    # Correct the sign of the angles based on the cross product
    angles = np.where(cross_product > 0, -angles, angles)
    
    # Apply rotation for each frame
    for i, angle in enumerate(angles):
        df.iloc[i] = rotate_points(df.iloc[[i]].copy(), angle)
        
    recentered = recenter_points(df)
    
    return recentered

#%%

example_df = pd.read_csv(example)

rotated_df = rotate_and_recenter(example_df)

#%%

# Select a random row index
random_row = random.randint(0, len(rotated_df) - 1)

# Define the body parts you're plotting
body_parts = ['nose', 'L_ear', 'R_ear', 'head', 'neck', 'body', 'tail_1', 'tail_2', 'tail_3', 'obj_1', 'obj_2']

# Create a plot
plt.figure(figsize=(6, 6))

# Plot each body part at the selected row
for part in body_parts:
    plt.plot(rotated_df.loc[random_row, f'{part}_x'], rotated_df.loc[random_row, f'{part}_y'], 'o', label=part)

# Setting up the plot
plt.title(f'Mouse Body Parts at Frame {random_row}')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()

#%%

# We extract the positions of both objects and all the bodyparts.

def plot_position(df, maxDistance = 2.5, maxAngle = 45):
    
    # Remove the rows where the mouse is still not in the video
    df.dropna(inplace=True)

    # Extract positions of both objects and bodyparts
    
    obj1 = Point(df, 'obj_1')
    obj2 = Point(df, 'obj_2')
    
    nose = Point(df, 'nose')
    head = Point(df, 'head')
    
    # We now filter the frames where the mouse's nose is close to each object
    
    # Find distance from the nose to each object
    dist1 = Point.dist(nose, obj1)
    dist2 = Point.dist(nose, obj2)
    
    # Next, we filter the points where the mouse is looking at each object
    
    # Compute normalized head-nose and head-object vectors
    head_nose = Vector(head, nose, normalize = True)
    head_obj1 = Vector(head, obj1, normalize = True)
    head_obj2 = Vector(head, obj2, normalize = True)
    
    # Find the angles between the head-nose and head-object vectors
    angle1 = Vector.angle(head_nose, head_obj1) # deg
    angle2 = Vector.angle(head_nose, head_obj2) # deg
    
    # Find points where the mouse is looking at the objects
    # Im asking the nose be closer to the aimed object to filter distant sighting
    towards1 = obj1.positions[(angle1 < maxAngle) & (dist1 < dist2)]
    towards2 = obj2.positions[(angle2 < maxAngle) & (dist2 < dist1)]

    # Finally, we can plot the points that match both conditions
    
    # Highlight positions where the mouse is close to each object
    fig, ax = plt.subplots()
    
    # Plot the nose positions
    ax.plot(*obj1.positions.T, ".", color = "grey", alpha = 0.2)
    ax.plot(*obj2.positions.T, ".", color = "grey", alpha = 0.2)
    
    # Plot the filtered points
    ax.plot(*towards1.T, ".", label = "Oriented towards 1", color = "brown", alpha = 0.4)
    ax.plot(*towards2.T, ".", label = "Oriented towards 2", color = "teal", alpha = 0.4)
    
    ax.axis('equal')
    ax.set_xlabel("Horizontal position (cm)")
    ax.set_ylabel("Vertical position (cm)")
    ax.legend(bbox_to_anchor = (0, 0, 1, 1), ncol=2, loc='upper left', fancybox=True, shadow=True, framealpha=1.0)

    plt.title("Nose coordinates during object exploration")
    plt.tight_layout()
    plt.show()

#%%

plot_position(rotated_df, maxDistance = 2.5, maxAngle = 45)

#%% Now we define the function that creates the geometric labels for all _position.csv files in a folder

def create_geolabels(files, maxDistance = 2.5, maxAngle = 45, nan_to_0 = False):
    
    for file in files:
        
        # Determine the output file path
        input_dir, input_filename = os.path.split(file)
        parent_dir = os.path.dirname(input_dir)
        
        # Read the file
        position = pd.read_csv(file)
        
        # Remove the rows where the mouse is still not in the video, excluding the first 4 columns (the object)
        original_rows = position.shape[0]
        position.dropna(subset = position.columns[4:], inplace=True)
        position.reset_index(drop=True, inplace=True)
        rows_removed = original_rows - position.shape[0]
    
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
        
        if "Hab" not in file:
            
            # Create the geolabels dataframe
            geolabels = pd.DataFrame(np.zeros((position.shape[0], 2)), columns=["Left", "Right"]) 
            
            for i in range(position.shape[0]):
                
                # Check if mouse is exploring object 1
                if dist1[i] < maxDistance and angle1[i] < maxAngle:
                    geolabels.loc[i, "Left"] = 1
        
                # Check if mouse is exploring object 2
                elif dist2[i] < maxDistance and angle2[i] < maxAngle:
                    geolabels.loc[i, "Right"] = 1

            geolabels['Left'] = geolabels['Left'].astype(int)
            geolabels['Right'] = geolabels['Right'].astype(int)
            
            # Add rows filled with zeros at the beginning of geolabels
            zeros_rows = pd.DataFrame(np.nan, index=np.arange(rows_removed), columns=geolabels.columns)
            geolabels = pd.concat([zeros_rows, geolabels]).reset_index(drop=True)
            
            # Insert a new column with the frame number at the beginning of the DataFrame
            geolabels.insert(0, "Frame", geolabels.index + 1)
            
            if nan_to_0:
                # Fill any remaining nan with 0
                geolabels.fillna(0, inplace=True)
            
            # Create a filename for the output CSV file
            output_filename_geolabels = input_filename.replace('_position.csv', '_geolabels.csv')
            output_folder_geolabels = os.path.join(parent_dir + '/geolabels')
            os.makedirs(output_folder_geolabels, exist_ok = True)
            output_path_geolabels = os.path.join(output_folder_geolabels, output_filename_geolabels)
            geolabels.to_csv(output_path_geolabels, index=False)
            
            print(f"Saved geolabels to {output_filename_geolabels}")
        
        # Create the distances dataframe
        distances = pd.DataFrame(np.zeros((position.shape[0], 2)), columns=["nose_dist", "body_dist"])
        
        # Calculate the Euclidean distance between consecutive nose positions
        distances['nose_dist'] = (((position['nose_x'].diff())**2 + (position['nose_y'].diff())**2)**0.5) / 100
        distances['body_dist'] = (((position['body_x'].diff())**2 + (position['body_y'].diff())**2)**0.5) / 100
        
        # Add rows filled with zeros at the beginning of distances
        zeros_rows = pd.DataFrame(np.nan, index=np.arange(rows_removed), columns=distances.columns)
        distances = pd.concat([zeros_rows, distances]).reset_index(drop=True)
        
        # Insert a new column with the frame number at the beginning of the DataFrame
        distances.insert(0, "Frame", distances.index + 1)

        
        if nan_to_0:
            # Fill any remaining nan with 0
            distances.fillna(0, inplace=True)
        
        output_filename_distances = input_filename.replace('_position.csv', '_distances.csv')
        output_folder_distances = os.path.join(parent_dir + '/distances')
        os.makedirs(output_folder_distances, exist_ok = True)
        output_path_distances = os.path.join(output_folder_distances, output_filename_distances)
        distances.to_csv(output_path_distances, index=False)
            
        print(f"Saved distances to {output_filename_distances}")

#%%

create_geolabels(all_position)

#%%

# The end
