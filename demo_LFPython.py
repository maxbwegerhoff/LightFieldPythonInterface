from LFPython import spec
import time
import matplotlib.pyplot as pl

spec = spec(experiment_name = 'HRS500MS_Pixis100_test', folder_name = 'measurement1')
#wait some time before starting the acquisition (this is just optional)
time.sleep(3)

#take 5 spectra in a row
for i in range(5):
    x, wl, inten = spec.acquire()
    pl.plot(wl, inten, label = f'{i}')


pl.legend()
pl.show()

#to delete all the recorded data in the last used folder use:
#spec.cleanup()
#to delete all the data except the averaged data use:
#spec.cleanup_rawdata()

#take 5 additional spectra but save them in a new folder
spec.update_folder_name(folder_name = 'measurement2')

for i in range(5):
    x, wl, inten = spec.acquire()
    pl.plot(wl, inten, label = f'{i}')


pl.legend()
pl.show()

