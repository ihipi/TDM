from tdm import gui
import multiprocessing

if __name__ == '__main__':
    m = multiprocessing.Process(target=gui.start, name= 'principal')
    m.start()
    m.join()