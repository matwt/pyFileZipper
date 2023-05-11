import os
import zipfile

from os import listdir
from os.path import isfile, join, exists
import threading
from time import sleep
import time

# from tkinter import Tk     # from tkinter import Tk for Python 3.x
import tkinter as tk
from tkinter import *
from tkinter import simpledialog
from tkinter import filedialog
from tkinter import messagebox
import multiprocessing

markus = 15
gPath = ""
folder_path = ""

def setPath(path):
    global gPath
    gPath = path


# dunno how this works
def divide_chunks(l, chunkSize):
    # using list comprehension
    final = [l[i:i + chunkSize] for i in range(0, len(l), chunkSize)]
    return final

# zipes the given file
def zipFile(path, file):
    
    try:
        # zipping file at this compression level took about 2 milliseconds on my laptop (not run in container) - Markus
        with zipfile.ZipFile(str(path + "/" + changeTozipExt(file)), mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.write(str(path + "/" + file), arcname=file)
            # print("Zipped file: " + file)

    except Exception as e:
        print(e)


# zipes the given file
def unzipFile(path, file):
    try:
        # zipping file at this compression level took about 2 milliseconds on my laptop (not run in container) - Markus
        with zipfile.ZipFile(str(path + "/" + file), mode='r') as zf:
            zf.extractall(str(path + "/"))
            print("Unzipped file: " + file)

    except Exception as e:
        print(e)

def deleteFilesInFolder(path, files:list):
    for file in files:
        try:
            os.remove(str(path + "/" + file))
            print("deleted " + file)
        except:
            print("could not remove " + str(path + "/" + file))

def changeTozipExt(file:str) -> str:
    newfile = os.path.splitext(file)[0]
    return str(newfile + ".zip")


def getFilesInDirectory(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    return onlyfiles

def getFilesInCurrentDirectory():
    onlyfiles = [f for f in listdir('.') if isfile(f)]
    return onlyfiles

def getDirsInDirectory(path):
    onlydirs = [d for d in listdir(path) if os.path.isdir(join(path, d))]
    return onlydirs

# function that takes a lits of files and returns a list of only the files with a .csv extention
def getcsvFiles(files:list) -> list:
    csvList = []
    for item in files:
        end = len(item)
        if (item[end-3:end] == 'csv'):
            csvList.append(item)
    return csvList


# function that takes a lits of files and returns a list of only the files with a .csv extention
def getzipFiles(files:list) -> list:
    zipList = []
    for item in files:
        end = len(item)
        if (item[end-3:end] == 'zip'):
            zipList.append(item)
    return zipList

# function that takes a lits of files/dirs and returns a list of only the folders
def getFolders(files:list) -> list:
    global folder_path
    foldList = []
    for item in files:
        d = os.path.join(folder_path, item)
        if os.path.isdir(d):
            foldList.append(item)
    return foldList

def zipFilesInFolder(files, threadNo):
    global folder_path
    for file in files:
        zipFile(folder_path, file)
    print("* [Thread: " + threadNo + "] Done Zipping")
    print("* [Thread: " + threadNo + "] Deleting zipped files")
    deleteFilesInFolder(folder_path, files)

    print("* [Thread: " + threadNo + "] Done!")

    # messagebox.showinfo(title="Zipping info", message="Zipping finnished")

def zipFilesInFolder(files):
    global folder_path
    for file in files:
        zipFile(folder_path, file)
        print("thread " + threading.current_thread().name + " zipped file")

    print("* Done Zipping")
    print("* Deleting zipped files")
    deleteFilesInFolder(folder_path, files)

    print("* Done!")


def helloThread(nr):
    print("Hello! I am thread " + str(nr))

def zipFilesCommand():
    global folder_path
    files = getFilesInDirectory(str(folder_path + '/'))
    files = getcsvFiles(files)
    if (len(files) < 1):
        print("empty list")
        return

    cpuCount = multiprocessing.cpu_count()

    nrThreads = simpledialog.askinteger("threads", prompt="How many threads will you use? (1-20), Recomended: " + str(cpuCount), minvalue=1, maxvalue=20)
    if (nrThreads == None): return

    # if we have more threads than files
    if (len(files) < nrThreads):
        nrThreads = len(files)
        print("more threads then files, reducing nr threads")
    
    nrFilesPerThread = int((len(files)-1) / nrThreads) + 1
    print("nr files per thread: " + str(nrFilesPerThread))

    filesForThreads = divide_chunks(files, nrFilesPerThread)
    print(filesForThreads)
    for item in filesForThreads:
        if (filesForThreads.count(item) > 1): print("DUPLICATE")
    # filesForThreads
    # return

    threadList = list()
    StartTimer = time.perf_counter()

    for i in range(nrThreads):
        t = threading.Thread(target=lambda: zipFilesInFolder(filesForThreads[i]), name=str(i))
        # t = threading.Thread(target=lambda: helloThread(i), name=str(i))
        t.start()
        print(t.name)
        print(str("Thread nr: " + str(i) + " started"))
        threadList.append(t)

    taskDone = False
    win = wait("Zipping files, please wait")
    root.after(1, win.deiconify)
    root.withdraw()

    while not taskDone:
        sleep(200/1000)
        finishedThreads = list()
        for thread in threadList:
            if not thread.is_alive():
                print(str("thread " + str(thread.name) + ": has finnished"))
                finishedThreads.append(thread)

        # remove finished threads
        for thread in finishedThreads:
            # print("removed thread")
            threadList.remove(thread)

        if (len(threadList) == 0):
            # print("list empty")
            taskDone = True
    
    stopTimer = time.perf_counter()
    totalTime = stopTimer - StartTimer

    print("total time: " + str(totalTime))
    
    # print("out of loop")
    root.after(1, win.destroy)
    root.after(1, root.deiconify)
    messagebox.showinfo(title="Zipping info", message="Zipping finnished in: " + str(totalTime))
    print("* Done Zipping!")


def unzipFilesInFolder():
    global folder_path
    global root
    files = getFilesInDirectory(str(folder_path + '/'))
    files = getzipFiles(files)
    win = wait("Un-zipping files, please wait")
    root.after(1, win.deiconify)
    root.withdraw()

    StartTimer = time.perf_counter()
    
    for file in files:
        unzipFile(folder_path, file)

    stopTimer = time.perf_counter()
    totalTime = stopTimer - StartTimer

    root.after(1, win.destroy)
    root.after(1, root.deiconify)

    print("* Done unzipping in: " + str(totalTime))
    print("* Deleting old files")
    deleteFilesInFolder(folder_path, files)
    print("* Done!")

    messagebox.showinfo(title="Un-Zipping info", message="Unzipping finnished in: " + str(totalTime))


def unzipFoldersInFolder():
    global folder_path
    global root
    folders = getDirsInDirectory(str(folder_path + '/'))
    #folders = getFolders(files)

    folder_path_temp = folder_path
    for folder_path_local in folders:
        folder_path = folder_path_temp + '/' + folder_path_local
        unzipFilesInFolder()
    folder_path = folder_path_temp


def wait(message):
    global root
    # global buttonBrowse
    # global buttonUnZip
    # global buttonZip

    win = Toplevel(root)
    # win.anchor(CENTER)
    win.transient()
    # win.positionfrom(root)
    # win.geometry("200x100")
    win.title('Wait')
    Label(win, text=str(message), font=("Arial", 20)).pack()
    x = root.winfo_x()
    y = root.winfo_y()
    win.geometry("+%d+%d" %(x,y))
    # Keep the toplevel window in front of the root window
    # win.wm_transient(root)
    # Label(win, text=str(message), font=("Arial", 20)).place(relx=0.5, rely=0.5, anchor= CENTER)

    # winLab = Label(win, text=str(message), font=("Arial", 20))
    # winLab.eval('tk::PlaceWindow . center')
    # winLab.pack()
    root.update()

    # Label(win, text=message).pack()
    return win

def main():
    # application_window = tk.Tk()
    # application_window.title = "File Zipper"
    global folderLabel
    global buttonZip
    global buttonUnZip
    global buttonUnZipFold
    global root

    root = tk.Tk()
    root.geometry('300x200')
    root.title('File Zipper')
    root.config(bg='white')
    root.eval('tk::PlaceWindow . center')
    # folder_path.set("No folder selected")

    # frame1 = Frame(root, bg='white')
    # frame1.pack(expand=True, fill=BOTH)

    # title = Text(root)
    # title.insert(INSERT, "hello world")

    # Create label

    header = Label(root, text = "File Zipper")
    header.config(font =("Courier", 14))

    # folder = Label(root, textvariable=folder_path)
    folderLabel = Label(root, text="no folder selected", wraplength=180)
    # folderLabel.place(relx=0.5, rely=0.5, anchor=CENTER)
    # if(folder_path == ""):
    #     folder.config(text="No folder selected")
    # else:
    #     folder.config(text=str(folder_path))

    buttonBrowse = Button(root, text='Choose folder', command=browse_button)
    # buttonBrowse.place(x=100, y=150)
    buttonZip = Button(root, text="Zip files in folder", command=zipFilesCommand, state=DISABLED)
    buttonUnZipFold = Button(root, text="Un-Zip folders and files in folder", command=unzipFoldersInFolder, state=DISABLED)
    buttonUnZip = Button(root, text="Un-Zip files in folder", command=unzipFilesInFolder, state=DISABLED)
    # buttonZip.place(x=20, y=20)

    
    header.pack()
    folderLabel.pack()
    # buttonBrowse.pack()
    buttonBrowse.place(relx=0.5, rely=0.5, anchor=CENTER)
    # buttonZip.pack()
    buttonZip.place(relx=0.3, rely=0.7, anchor=CENTER)
    buttonUnZip.place(relx=0.7, rely=0.7, anchor=CENTER)
    buttonUnZipFold.place(relx=0.5, rely=0.9, anchor=CENTER)
    # title.pack()
    root.mainloop()


def open_file():
   file = filedialog.askopenfile(mode='r', filetypes=[('Python Files', '*.py')])
   if file:
      content = file.read()
      file.close()
      print("%d characters in this file" % len(content))

def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    # global root
    global folderLabel
    global folder_path
    global buttonZip
    global buttonUnZip

    filename = filedialog.askdirectory()
    if (filename != ""):
        folder_path = filename
        folderLabel.config(text=folder_path)
        buttonZip.config(state=ACTIVE)
        buttonUnZip.config(state=ACTIVE)
        buttonUnZipFold.config(state=ACTIVE)
    
    # folder_path.set(filename)
    print(filename)

main()