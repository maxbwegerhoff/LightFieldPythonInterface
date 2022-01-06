from LFPython import spec
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