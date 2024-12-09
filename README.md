<div align="center">
  
# RAINSTORM
### Real & Artificial Intelligence Networks – Simple Tracker for Object Recognition Memory

![RAINSTORM Logo](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/logo.png)

</div>

**RAINSTORM** is a tool for scoring object recognition memory in mice 🐭. It allows users to automate the analysis of recognition memory performance through training of artificial neural networks.

### Features

- A Frame by Frame behavioral labeling tool that can be used both to score manually and train an artificial neural network
- Post-DeepLabCut data processing to avoid dissapearing bodyparts and glitching
- Geometric labeling of exploration through distance and angle of aproach
- Geometric labeling of freezing through immobility detection
- Automatic labeling of exploration using a trained AI model able to detect temporal sequences of behaviour
- Comparing labels in a visual and simple way

### Future steps

- Multianimal labeling for social memories
- Apply detection of moving objects for dinamic maze designs

# Installation

- Download & Install Miniconda (or Anaconda) - https://docs.anaconda.com/miniconda/install/
- Download or clone this RAINSTORM repository into your computer
- In the Miniconda Prompt, navigate to where the repository was stored and run: conda env create -f rainstorm_venv.yml
- - This will create a conda environment where the rainstorm package is installed, and we will use it to run the jupyter notebooks

# Pipeline

- DeepLabCut analyzes video files and returns a .H5 file with the position of the mouse's bodyparts (along with two objects, in the case of object exploration). What we do next is up to us!

## Manage_H5

- It is important to filter from the position file the frames where the mouse is not in the video
- Points that have a low likelihood assigned by DLC are filtered and data is smoothed
- Also, it is convenient to scale the video from pixels to cm
- Return: We obtain .csv files with the correct, scaled positions of the mice

![Example Manage_H5](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/1-Manage_H5.png)

## Geometric_Labeling

- One way of finding out when the mouse is exploring an object is to use a geometric criteria:
  - If the mouse is close to the object (distance < 2.5 cm)
  - If the mouse is oriented towards the object (angle < 45°)

![Example Geolabels](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/2-Geometric_Labeling.png)

## Automatic_Labeling

- Another way of finding out when the mouse is exploring is to train an artificial neural network with manually labeled data:

![Example Autolabels](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/3a-Create_Models.png)

Using TensorFlow, we were able to train models that are able to clasify a mouse's position into exploration

![Example Autolabels_2](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/3a-Create_Models_simple.png)

Among the models, we trained a more complex LSTM network that is aware of frame sequences, and performs better as exploration is time dependant.
It trains based on our own manual labeling, so it acquires the criteria of the users.

## Compare_Labels

- Once we have the manual, geometric and automatic labels, we can compare the performance of each on an example video:

![Example compare_1](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/4-Compare_Labels_line.png)

Using a polar graph, we can see for each position the angle of approach and distance in which the mice is exploring the objects
- For a single video:

![Example compare_1](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/4-Compare_Labels_polar.png)

- Or for many videos together:

![Example compare_2](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/4-Compare_Labels_polar_all.png)

#### Since the automatic method learns to detect exploration unrestricted by the angle and distance to the object, it tends to be more accurate (Although, let's be honest... I chose to show you the best numbers I've ever gotten).

![Example compare_3](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/4-Compare_Labels_result.png)

## Seize_Labels

- We can use the best labels to evauate the performance of a mouse during the different sessions:

![Example seize_1](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/5-Seize_Labels_example.png)

- And finally, we can find differences in the exploration of objects for a group of trained mice (which was the obective all along):

![Example seize_2](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/5-Seize_Labels_experiment.png)

# In conclusion
- This project, although already in use, is a work in progress that could significantly improve the way we analyze object exploration videos.
- If you wish to contact us, please do so: dhers.santiago@gmail.com
- © 2024. This project is openly licensed under the MIT License.

#### Thanks for exploring us!

![Final_gif](https://github.com/sdhers/RAINSTORM/blob/main/docs/images/mouse_exploring.gif)
