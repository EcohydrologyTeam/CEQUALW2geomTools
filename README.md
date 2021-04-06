#CE-QUAL-W2 Preliminary Segmentation Notebook Example
Jupyter notebooks that creates a preliminary W2 segmentation from a centerline shape file.

The current notebook is: JNB_transect_and_polygons_Checks.ipynb

##Create Conda Environment for Pangeo Notebooks
Create a conda environment from the environment_w2_jnb.yml in this folder, following one of these instructions:
Navigator: Import the environment file using Anaconda Navigator.
Console: Create an environment from an environment.yml file using the console, replacing <path>/environment_w2_jnb.yml with the full file pathway to the file in your local cloned repository.
conda env create --file <path>/environment.yml
NOTE: the environment name will be w2_jnb
##Activate that environment.
Navigator: Using an environment.
Console: Activate an environment.
conda activate w2_jnb
Launch Jupyter Notebook.
Navigator: Launch
Console:
jupyter notebook
