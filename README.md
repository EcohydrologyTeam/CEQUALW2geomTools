Pangeo Notebook Examples
====

Jupyter notebooks that demonstrate the workflows and code for discovering, accessing, analyzing, and visualizing data using the [Pangeo](https://pangeo.io/packages.html) & [HoloViz](https://holoviz.org) ecosystems of Anaconda-developed libraries, such as:
  - [Pandas](https://pandas.pydata.org),
  - [GeoPandas](http://geopandas.org/),
  - [Xarray](http://xarray.pydata.org/en/stable/) for multidimensional labeled data such as netCDF, and
  - [Intake](https://intake.readthedocs.io/en/latest/index.html) for finding, exploring, loading and disseminating data.


## Create Conda Environment for Pangeo Notebooks

1. **Create a conda environment** from the [environment_pangeo.yml](pangeo_notebook_examples/environment_pangeo.yml) in this folder, following one of these instructions:
  - Navigator: [Import the environment file using Anaconda Navigator](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-environments/#importing-an-environment).
  - Console: [Create an environment from an environment.yml file](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html?highlight=environment.yml#creating-an-environment-from-an-environment-yml-file) using the console, replacing `<path>/environment_pangeo.yml` with the full file pathway to the file in your local cloned repository.
  ```console
  conda env create --file <path>/environment.yml
  ```
  - NOTE: the environment name will be `pangeo`
2. **Activate that environment.**
  - Navigator: [Using an environment](https://docs.anaconda.com/anaconda/navigator/tutorials/manage-environments/).
  - Console: [Activate an environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html?#activating-an-environment).
  ```console
  conda activate pangeo
  ```
3. **Launch [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) (recommended) or [Jupyter Notebook](https://jupyter.readthedocs.io/en/latest/)**.
  - Navigator: [Launch](https://docs.anaconda.com/anaconda/navigator/)
  - Console: one of the below.
  ```console
  jupyter lab
  ```
  ```console
  jupyter notebook
  ```
