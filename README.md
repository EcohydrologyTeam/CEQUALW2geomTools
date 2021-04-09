CE-QUAL-W2 Preliminary Segmentation Notebook Example
====

Jupyter notebook that creates a preliminary W2 segmentation from a centerline shape file.
The current notebook is: [JNB_transect_and_polygons_Checks.ipynb](CEQUALW2geomTools/JNB_transect_and_polygons_Checks.ipynb)


## Create Conda Environment for W2 Notebooks

1. **Create a conda environment** from the [environment_w2_jnb.yml](CEQUALW2geomTools/environment_w2_jnb.yml) in this folder, following one of these instructions:
  - Navigator: [Import the environment file using Anaconda Navigator](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-environments/#importing-an-environment).
  - Console: [Create an environment from an environment.yml file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html?highlight=environment.yml#creating-an-environment-from-an-environment-yml-file) using the console, replacing `<path>/environment_w2_jnb.yml` with the full file pathway to the file in your local cloned repository.
  ```console
  conda env create --file <path>/environment.yml
  ```
  - NOTE: the environment name will be `w2_jnb`
2. **Activate that environment.**
  - Navigator: [Using an environment](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-environments/).
  - Console: [Activate an environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html?#activating-an-environment).
  ```console
  conda activate w2_jnb
  ```
3. **Launch [Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/)**.
  - Navigator: [Launch](https://docs.anaconda.com/anaconda/navigator/)
  - Console: one of the below.
  ```console
  jupyter notebook
  ```
