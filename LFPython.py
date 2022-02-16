import shutil
import clr
import os, glob, string
import time
from datetime import datetime
import sys
import numpy as np
import pandas as pd
#print('import sys')
clr.AddReference('System.IO')
clr.AddReference('System.Threading')
clr.AddReference('System.Collections')
from System.IO import *
from System.Threading import AutoResetEvent
from System import String
from System.Collections.Generic import List
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')
clr.AddReference('PrincetonInstruments.LightField.Automation')
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import SpectrometerSettings
from PrincetonInstruments.LightField.AddIns import DeviceType
from PrincetonInstruments.LightField.AddIns import ExperimentSettings


acquireCompleted = AutoResetEvent(False)
def experiment_completed(sender, event_args):
        acquireCompleted.Set()

class spec():
    def __init__(self, experiment_name : str, folder_name : str = 'temp', add_time: bool = True, init_folder_path = None):
        """
        This class aims to serve as an interface between data acquisition in lightfield and python. Spectra can be acquired, saved as files and returned in python. Spectra are saved to a folder which always contains a timestamp and a folder name which can be chosen by the user.
        Spectra are saved in this folder (as csv and spe) and also saved with a timestamp and an ascending measurement counter starting from 0.

        Prerequisites: - A lightfield experiment; all the settings such as exposure time, ROI are set in the lightfield software
        - In lightfield one MUST chose to save the spectra in the CSV-FORMAT
        
        :param: experiment_name: string: name of the lightfield experiment that one wants to use (requires a camera)
        :param: folder_name: string: name of the folder where the spectra are saved
        :param: add_time: bool: If true a timestamp is added to the front of the folder name
        :param: init_folder_path:  If not None, the spectra will be saved to this given **path** (so using this argument one has to make sure that the
        path works for the given operating system and so on)
        """           
        auto = Automation(True, List[String]())
        self.experiment = auto.LightFieldApplication.Experiment        

        self.experiment.Load(experiment_name) #This is the name of the 'experiment'/device combination created in Lightfield
        self.experiment.ExperimentCompleted += experiment_completed
        if init_folder_path is None:
            cur_dir = os.path.abspath(os.path.dirname(__file__))
            if add_time:
                timestamp=datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
                self.folder = os.path.join(cur_dir, f'{timestamp}__{folder_name}')
            else:
                self.folder = os.path.join(cur_dir, f'{folder_name}')

            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            else:
                print('Folder already exists; choose different folder name')

            self.experiment.SetValue(ExperimentSettings.FileNameGenerationDirectory, self.folder)
        else:
            self.folder = init_folder_path
            self.experiment.SetValue(ExperimentSettings.FileNameGenerationDirectory, self.folder)

        self.xpixels = None
        self.wlengths = None
        self.intens = None

        self.intens_uptodate = False
        self.iter = 0

    def update_folder_name(self, folder_name: str, add_time: bool = True):
        '''
        This method updates the name of the folder in which the acquired spectrums are saved 
        and resets the measurement counter to 0 ()

        :param: folder_name: string: name of the folder
        :param: add_time: bool: If true a timestamp is added to the front of the folder name

        :return: returns the  absolute path to the folder
        '''
        cur_dir = os.path.abspath(os.path.dirname(__file__))
        if add_time:
            timestamp=datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
            self.folder = os.path.join(cur_dir, f'{timestamp}__{folder_name}')
        else:
            self.folder = os.path.join(cur_dir, f'{folder_name}')

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        else:
            print('Folder already exists; choose different folder name')

        self.experiment.SetValue(ExperimentSettings.FileNameGenerationDirectory, self.folder)

        self.iter = 0

        return self.folder

    def acquire(self, save_averaged_data = True, file_name: str = None, add_time: bool = True):
        '''
        This method acquires a spectrum via lightfield and loads the wavelengths and intensities from the saved file.
        Consecutive acquisations are labelled with numbers starting from 0 (measurement counter) and a timestamp in the default setting.
        Alternatively one can choose a custom file_name; in this case one has to be cautious to choose a new file name for every acquisition.

        :param: save_averaged_data: bool: If True, the averaged data (frames and columns are averaged) is saved to a csv file
        :param: file_name: str: If given, the data will be saved with this file name with the option to add a time stamp to the front.
        :param: add_time: bool: If file_name is given and add_time is True, a time stamp will be added to the front of the custom file_name

        :return: returns the x-pixel, wavelength and intensity data from the acquired spectrum. The data is averaged over the acquired frames and pixel-columns.
        '''
        timestamp=datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
        if file_name is not None:
            if add_time:
                file_name = f'{timestamp}__{file_name}'
        elif file_name is None:
            file_name = f'{timestamp}__{self.iter}'        
        
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationBaseFileName,file_name)
        self.experiment.Acquire()
        acquireCompleted.WaitOne()
               
        #load in last acquired data and save it to self.wlenghts and self.intens
        data = np.loadtxt(os.path.join(self.folder, f'{file_name}.csv'), delimiter = ',')
        #load into pandas to average over the frames and columns
        data = pd.DataFrame(data)

        #group by pixels -> we average over the individual frames and columns
        data_xpixels = data.groupby(1)[4].mean()
        self.xpixels = data_xpixels.keys().to_numpy()
        self.intens = data_xpixels.to_numpy()

        #group by wavelengths
        data_wlengths = data.groupby(3)[4].mean()
        self.wlengths = data_wlengths.keys().to_numpy()

        self.intens_uptodate = True        

        if save_averaged_data:
            np.savetxt(os.path.join(self.folder, f'{file_name}_av.csv'), np.column_stack([self.xpixels, self.wlengths, self.intens]), delimiter=',')
        self.iter += 1
        return (self.xpixels, self.wlengths, self.intens)
    
    def xpixels(self):
        '''
        This method returns the x-pixel indides of the spectrum

        :return: returns the x-pixel indices of the spectrum
        '''
        if self.xpixels is None:
            self.acquire()
            return self.xpixels
        else:
            return self.xpixels

    def wavelengths(self):
        '''
        This method returns the wavelengths of the spectrum

        :return: returns the wavelengths of the spectrum
        '''
        if self.wlengths is None:
            self.acquire()
            return self.wlengths
        else:
            return self.wlengths

    def intensities(self):
        '''
        This method returns the intensities of the last measured spectrum.

        :return: returns the intensities of the spectrum
        '''
        if self.intens_uptodate is False:
            self.acquire()
            return self.intens
        else:
            self.intens_uptodate = False
            return self.intens

    def set_exposure(self, timeinms):
        '''
        This method sets the exposure time for the acquisition in lightfield

        :return: exposure time
        '''
        self.experiment.SetValue(CameraSettings.ShutterTimingExposureTime,timeinms)
        return timeinms

    def cleanup(self):
        '''
        This method deletes the last measurement folder. In order to continue measuring use update_folder_name to create a new folder.
        Otherwise the program will crash, since Lightfield will try to save the acquired spectra in a non-existing folder.
        '''

        shutil.rmtree(self.folder)

    def cleanup_rawdata(self):
        '''
        This method deletes everything in the last measurement folder except for the averaged csv data
        (this saves a lot of space)
        '''

        for file in os.listdir(self.folder):
            if file[-6:] != 'av.csv':
                os.remove(os.path.join(self.folder, file))
