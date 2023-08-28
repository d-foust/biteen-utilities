# biteen-utilities
A repository for common coding tasks in the Biteen Lab.  
## Methods:
### biteen_io.py:
Reading, writing, and converting between different file types.
* convert .nd2 to .tif
* convert .nd2 to .npy
* convert cellpose .npy to .mat (SMALL-LABS format)
* read cellpose .npy
* convert SMALL-LABS output (*_fits.mat, *_guesses.mat) to pandas DataFrame
* convert SMALL-LABS output (*_fits.mat, *_guesses.mat) to .csv
* convert pandas DataFrame to SMALL-LABS format .mat

### biteen_pandas.py:
Working with tabular data stored in pandas DataFrames. 
* 

### biteen_plots.py
Plotting single-molecule data.
* Plotting trajectories overlayed on image data, e.g. phase contrast, segmented regions of interest