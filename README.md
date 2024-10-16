# STORM - Simple Tracker for Object Recognition Memory

![STORM Logo](images/0-storm_logo.jpg)

**STORM** is a tool for tracking object recognition memory in mice 🐭. It allows users to track and analyze memory performance through the exploration of objects.

</div>

### Features

- post-DeepLabCut data processing to avoid dissapearing bodyparts and glitching
- Geometric labeling through distance and angle of aproach
- Automatic labeling using a trained AI model able to detect of temporal sequences of behaviour
- Comparing labels in a visual and simple way

### Future steps

- Learn to apply further DeepLabCut analysis:
  - Multianimal tracking for social memories
  - Apply detection of moving objects for dinamic maze designs

# Pipeline

- DeepLabCut analyzes video files and returns a .H5 file with the position of the mouse's bodyparts (along with two objects, in the case of object exploration). What we do next is up to us!

## Manage_H5

- It is important to filter from the file the frames where the mouse is not in the video
- Points that have a low likelihood assigned by DLC are filtered and data is processed by filters
- Also, it is convenient to scale the video from pixels to cm
- Return: We obtain .csv files with the scaled positions of the mice

![Example Manage_H5](images/1-Manage_H5.png)

## Geometric_Labeling

- One way of finding out when the mouse is exploring an object is to use a geometric criteria:
  - If the mouse is close to the object (distance < 2.5 cm)
  - If the mouse is oriented towards the object (angle < 45°)

![Example Geolabels](images/2-Geometric_Labeling.png)

## Automatic_Labeling

- Another way of finding out when the mouse is exploring is to train an artificial neural network with manually labeled data:

![Example Autolabels](images/3a-Create_Models.png)

Using TensorFlow, we were able to train a simple model that is able to clasify a mouse's position into exploration

![Example Autolabels_2](images/3a-Create_Models_simple.png)

We also trained a more complex LSTM network that is aware of frame sequences, and performs better as exploration is time dependant
It trains based on our own manual labeling, so it acquires the criteria of the user.

## Compare_Labels

- Once we have the manual, geometric and automatic labels, we can compare the performance of each on an example video:

![Example compare_1](images/4-Compare_Labels_line.png)

Using a polar graph, we can see for each position the angle of approach and distance in which the mice is exploring the objects
- For a single video:

![Example compare_1](images/4-Compare_Labels_polar.png)

- Or for many videos together:

![Example compare_2](images/4-Compare_Labels_polar_all.png)

#### Since the automatic method learns to detect exploration unrestricted by the angle and distance to the object, it tends to be more accurate (Although, let's face it... I chose the best numbers I've ever gotten for the picture)

![Example compare_3](images/4-Compare_Labels_result.png)

## Seize_Labels

- We can use the best labels to evauate the performance of a mouse during the different sessions:

![Example seize_1](images/5-Seize_Labels_example.png)

- And finally, we can find differences in the exploration of objects for a group of trained mice (which was the obective all along):

![Example seize_2](images/5-Seize_Labels_experiment.png)

# In conclusion
- This project, although already in use, is a work in progress that could someday improve the way we analyze object exploration videos.
- If you wish to contact us, please do so: simple.torm@gmail.com

#### Thanks for exploring us!

![Final_gif](images/mouse_exploring.gif)
