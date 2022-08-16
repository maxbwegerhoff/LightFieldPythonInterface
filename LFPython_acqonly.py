import shutil
import clr
import os, glob, string
import time
from datetime import datetime
import sys
import numpy as np
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
        This class aims to serve as an interface between data acquisition in lightfield and python. Spectra can be acquired and saved as files. 
        However the acquired spectrum is not immediately available in python (in contrast to LFPython.py).
        Spectra are saved to a folder which always contains a timestamp and a folder name which can be chosen by the user.
        Spectra are saved in this folder and also saved with a timestamp and an ascending measurement counter starting from 0.

        Prerequisites: - A lightfield experiment; all the settings such as exposure time, ROI are set in the lightfield software
        
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

        self.spedata = None

        self.intens_uptodate = False
        self.iter = 0

    def update_folder_name(self, folder_name: str = None, add_time: bool = True, folder_path: str = None):
        '''
        This method updates the name of the folder in which the acquired spectrums are saved 
        and resets the measurement counter to 0 ()

        :param: folder_name: string: name of the folder
        :param: add_time: bool: If true a timestamp is added to the front of the folder name

        :return: returns the  absolute path to the folder
        '''
        if folder_path is not None:
            self.folder = folder_path
        else:
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

    def acquire(self, file_name: str = None, add_time: bool = True):
        '''
        This method acquires a spectrum via lightfield.
        Consecutive acquisations are labelled with numbers starting from 0 (measurement counter) and a timestamp in the default setting.
        Alternatively one can choose a custom file_name; in this case one has to be cautious to choose a new file name for every acquisition.

        :param: file_name: str: If given, the data will be saved with this file name with the option to add a time stamp to the front.
        :param: add_time: bool: If file_name is given and add_time is True, a time stamp will be added to the front of the custom file_name

        :return: None, the acquired spectrum is not immediately available in python
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
        self.iter += 1
        #self.spedata = spe.SpeFile(os.path.join(self.folder, f'{file_name}.spe'))
        
        return None

    def set_exposure(self, timeinms):
        '''
        This method sets the exposure time for the acquisition in lightfield

        :return: exposure time
        '''
        self.experiment.SetValue(CameraSettings.ShutterTimingExposureTime,timeinms)
        return timeinms

    def set_exposures_per_frame(self, num: int, method: str = 'Sum'):
        '''
        This method sets the number of exposures that are summed up or averaged for each frame

        Possible values for method are 'Sum' and 'Average'

        :return: exposure time
        '''
        if num > 1:
            self.experiment.SetValue(ExperimentSettings.OnlineProcessingFrameCombinationMethod,method)
        self.experiment.SetValue(ExperimentSettings.OnlineProcessingFrameCombinationFramesCombined,num)
        
        return num

    def set_number_of_frames(self, num_frames):
        '''
        This method sets the number of frames to be acquired in lightfield

        :return: number of frames
        '''
        self.experiment.SetValue(ExperimentSettings.AcquisitionFramesToStore, num_frames)

        return num_frames

    def get_framerate(self):

        return self.experiment.GetValue(CameraSettings.AcquisitionFrameRate)