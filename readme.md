# biteen-utilities
A repository for common coding tasks in the Biteen Lab.   
## Methods:
### biteen_io.py:
Reading, writing, and converting between different file types. 
* convert .nd2 to .tif
* convert .nd2 to .npy
* extract ROIs from cellpose .npy into 2d numpy array
* convert cellpose .npy to .mat (SMALL-LABS format)
* convert SMALL-LABS output (*_fits.mat, *_guesses.mat) to pandas DataFrame
* convert SMALL-LABS output (*_fits.mat, *_guesses.mat) to .csv
* convert pandas DataFrame to SMALL-LABS format .mat
* convert SMALL-LABS output to Spot-On format
* convert pandas DataFrame to Spot-On format

### biteen_pandas.py:
Working with tabular data stored in pandas DataFrames.
* calculate individual step data from localizations
* filter localization data by number of localizations in each track
* calculate median step size for each track

### biteen_plots.py
Plotting single-molecule data.
* Plot localizations overlayed on image data, e.g. phase contrast
* Plot trajectories overlayed on image data, e.g. phase contrast

## Future
* dpsp
* drift correction with RCC
* registration
* using napari
* MSD
* using NOBIAS output