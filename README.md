# LightFieldPythonInterface

## Step 1: Create an experiment in Lightfield with your desired settings

Example: I created an experiment called "HRS500_Pixis100_test". Such an experiment must exist for the interface to work. In this experiment one can adjust all the settings as needed beforehand.

<img src="screenshots/prerequisites__example_saved_experiment.png">

![](/pictures/prerequisites__example_saved_experiment.png)

However, for the interface to work correctly one must use the following settings in the Export Data tab:

<img src="screenshots/prerequisites__export_data_settings.png">

and in the save data file tab:

<img src="screenshots/prerequisites__save_data_file_settings.jpg">

## Step 2: Acquire spectra through python

Everything else is handled by the python class. For a demo of the class have a look/try the demo: demo_lfautom.py

```python

from lfautom import spec
import time
import matplotlib.pyplot as pl

spec = spec(experiment_name = 'HRS500MS_Pixis100_test', folder_name = 'test')
#wait some time before starting the acquisition (this is just optional)
time.sleep(10)

#take 5 spectra in a row
for i in range(5):
    x, wl, inten = spec.acquire()
    pl.plot(x, inten, label = f'{i}')


pl.legend()
pl.show()

#to delete all the recorded data in the last used folder use:
#spec.cleanup()

#to delete all the data except the averaged data use:
#spec.cleanup_rawdata()
```

The most important commands are:
```python
spec = spec(experiment_name = 'HRS500MS_Pixis100_test', folder_name = 'test')
```
to initialize the class based on the lightfield experiment. The data is then saved in a folder which contains a time stamp and the ```python folder_name```.

Calling

```python
spec.acquire()
```
acquires a spectrum and returns the pixel indices + corresponding wavelengths and intensities.
