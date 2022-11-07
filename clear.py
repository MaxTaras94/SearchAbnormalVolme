import os
import shutil
import time



def remove_contents(path):
    for root, dirs, files in os.walk(path):
      for file in files:
        print(f'Удаля файл {file}')
        os.remove(file)
        time.sleep(1)
if __name__ == "__main__": 
    remove_contents(r'logs back')