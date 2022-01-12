from LFPython import spec
import time
import matplotlib.pyplot as pl

spec = spec(experiment_name = 'HRS500MS_Pixis100_test', folder_name = 'measurement1')
#wait some time before starting the acquisition (this is just optional)
time.sleep(3)

#take 5 spectra in a row in standard mode
for i in range(5):
    x, wl, inten = spec.acquire()
    pl.plot(wl, inten, label = f'{i}')


pl.legend()
pl.show()

#to delete all the recorded data in the last used folder use:
spec.cleanup()
#to delete all the data except the averaged data use:
#spec.cleanup_rawdata()

#take 5 additional spectra but save them in a new folder without the time stamp
spec.update_folder_name(folder_name = 'measurement2', add_time = False)

for i in range(5):
    #save the spectra without the time stamp and with a custom name
    x, wl, inten = spec.acquire(file_name = f'meas{i}_test', add_time = False)
    pl.plot(wl, inten, label = f'{i}')

for i in range(5):
    #save the spectra with the time stamp and with a custom name
    x, wl, inten = spec.acquire(file_name = f'meas{i}_testwithtime', add_time = True)
    pl.plot(wl, inten, label = f'{i}')


pl.legend()
pl.show()

#delete all the data except for the averaged data
spec.cleanup_rawdata()



