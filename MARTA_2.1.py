# coding: utf-8
import time as tm
import os
import sys
import cv2
import imutils
import numpy as np
import matplotlib.pyplot as plt
import warnings
import PIL
import pkg_resources.py2_warn
#import pkg_resources.py2_warn
from datetime import datetime, timezone
from tkinter import *
from tkinter.ttk import Progressbar
from tkinter import ttk
from tkinter.font import BOLD
from tkinter import simpledialog
from PIL import ImageTk, Image


class ToolTip(object):

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 57
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

       
class MyWindow:
    def __init__(self, win):
        self.master = win
        
        self.lbl1=Label(win, text='Number of images \n(1 or 3)')
        self.t1=Entry(win,textvariable=StringVar(window, value='3'), width=5, justify='center')
        self.lbl1.grid(column=4,row=0, sticky=E)
        self.t1.grid(column=5,row=0,sticky=W)
        CreateToolTip(self.t1, text = 'One merged input file (1) or three input files (3)')

        self.lbl2=Label(win, text='File label pattern \n(no ext)')
        self.t2=Entry(window,textvariable=StringVar(window, value='a'), width=5, justify='center')
        self.lbl2.grid(column=2,row=0, sticky=E)
        self.t2.grid(column=3,row=0, sticky=W)
        CreateToolTip(self.t2, text = 'Pattern filename with no extension.')

        self.lb_33=Label(win, text='Input extension', justify= RIGHT)
        self.t33=Entry(window,textvariable=StringVar(window, value='.tif'), width=5, justify='center')
        self.lb_33.grid(column=6,row=0, sticky=E)
        self.t33.grid(column=7,row=0, sticky=W)

        self.lb_34=Label(win, text='Output extension')
        self.t34=Entry(window,textvariable=StringVar(window, value='.tif'), width=5)
        self.lb_34.grid(column=6,row=1, sticky=E)
        self.t34.grid(column=7,row=1, sticky=W)

        self.lbl4=Label(win, text='scaling (units/pixel)')
        self.t4=Entry(window,textvariable=StringVar(window, value='0.21'), width=5, justify='center')
        self.lbl4.grid(column=4,row=1, sticky=E)
        self.t4.grid(column=5,row=1, sticky=W)


        self.selected = StringVar()

        rad1 = Radiobutton(window,text='Automatic', value='automatic', variable=self.selected)
        rad2 = Radiobutton(window,text='Supervised', value='supervised', variable=self.selected)

        self.selected.set("automatic")

        CreateToolTip(rad1, text = 'Select for full automated processing')
        CreateToolTip(rad2, text = 'Select for individual decision for all detections')
       
        btn2 = Button(window, text="Generate Automatic mask", font= "bold", command=self.run, height=2, width=25)
        btn3 = Button(window, text=" Generate Manual mask ", command=self.say_hi)
        btn10 = Button(window, text="         Exit         ", command=self.ex)
        previewCM = Button(window, text="Preview \nCardiomyocytes", bg="#10FF10", command=self.sercaORG, width=15)
        previewCx = Button(window, text="Preview \nConnexin 43", bg="#FFFFFF", command=self.cxORG, width=15)
        previewWGA = Button(window, text="Preview \nWGA", bg="#F08080", command=self.wgaORG, width=15)
        previewtres = Button(window, text="Preview cell masks", bg="#FFFFFF", command=self.sumar_canales, width=25)


        rad1.grid(column=0, row=1)
        rad2.grid(column=1, row=1)


        btn2.grid(column=6, row=26, columnspan=2, rowspan=2)
        btn3.grid(column=0,row=36, columnspan=2)
        btn10.grid(column=4, row=27)
        previewCM.grid(row=8, column=8)
        previewCx.grid(row=9, column=8)
        previewWGA.grid(row=10, column=8)
        previewtres.grid(row=11, column=6, columnspan=2)

        CreateToolTip(btn2, text = 'Click to run automated processing of input images with the parameter set.')
        CreateToolTip(btn3, text = 'Click to create a manual delineated mask of the input images. \n Double click to generate vertices. \n Press ESC to go to next subimage in case of split. \n The output will be labeled as pattern_mM (i.e. a_mM).')
        
        self.selcomb = StringVar()

        rad21 = Radiobutton(window,text='Add', value='addch', variable=self.selcomb)
        rad22 = Radiobutton(window,text='Independent', value='indepch', variable=self.selcomb)

        self.selcomb.set("addch")
        
        rad21.grid(column=0, row=2)
        rad22.grid(column=1, row=2)
        
        self.chk1_state = BooleanVar()
        self.chk1_state.set(False) 
        chk1 = Checkbutton(window, text='Input Mask', var=self.chk1_state)
        chk1.grid(column=0, row=3)

        CreateToolTip(chk1, text = 'Check to process a provided input mask (i.e a_mM.tif)')

        self.chk2_state = BooleanVar()
        self.chk2_state.set(False) 
        chk2 = Checkbutton(window, text='Equalize', var=self.chk2_state)
        chk2.grid(column=1, row=3)
        CreateToolTip(chk2, text = 'Check to make equalization of input files before processing.')

        self.chk3_state = BooleanVar()
        self.chk3_state.set(False)
        chk3 = Checkbutton(window, text='Evaluate', var=self.chk3_state)
        chk3.grid(column=2, row=3)
        CreateToolTip(chk3, text = 'Check to generate evaluation using manual delineated mask (i.e a_mM.tif) \n and input files (i.e. a_c1.tif, a_c2.tif, a_c3.tif).')

        lbl5=Label(win, text='Equalized \nbinary threshold')
        self.t5=Entry(window,textvariable=StringVar(window, value='70'), width=5)
        lbl5.grid(column=0,row=7, sticky=E)
        self.t5.grid(column=1,row=7, sticky=W)
        CreateToolTip(self.t5, text = '8-bit binary value for thresholding when equalization is used for channels c1 (cell) and c3 (intersticium) ')

        lbl5_2=Label(win, text='Binary threshold for c4')
        self.t5_2=Entry(window,textvariable=StringVar(window, value='254'), width=5)
        lbl5_2.grid(column=2,row=7, sticky=E)
        self.t5_2.grid(column=3,row=7, sticky=W)
        CreateToolTip(self.t5_2, text = '8-bit binary value for thresholding in c4 channel')

        lbl6=Label(win, text='Binary threshold \nfor c1 (CM)', bg="#10FF10")
        self.t6=Entry(window,textvariable=StringVar(window, value='7'), width=5)
        lbl6.grid(column=0,row=8, sticky=E)
        self.t6.grid(column=1,row=8, sticky=W)
        CreateToolTip(self.t6, text = '8-bit binary value for thresholding in c1 channel (Myocite fill, i.e. SERCA, F-actin,...)')

        lbl7=Label(win, text='Binary threshold \nfor c2 (CX)', bg="#FFFFFF")
        self.t7=Entry(window,textvariable=StringVar(window, value='12'), width=5)
        lbl7.grid(column=0,row=9, sticky=E)
        self.t7.grid(column=1,row=9, sticky=W)
        CreateToolTip(self.t7, text = '8-bit binary value for thresholding in c2 channel (CX43 for longitudinal CM delimitation)')

        lbl8=Label(win, text='Binary threshold \nfor c3 (INT)', bg="#F08080")
        self.t8=Entry(window,textvariable=StringVar(window, value='9'), width=5)
        lbl8.grid(column=0,row=10, sticky=E)
        self.t8.grid(column=1,row=10, sticky=W)
        CreateToolTip(self.t8, text = '8-bit binary value for thresholding in c3 channel (Intersticium fill, i.e. WGA)')

        lbl9=Label(win, text='Noise removal matrix rank \nin c1 (CM)', bg="#10FF10")
        self.t9=Entry(window,textvariable=StringVar(window, value='3'), width=5)
        lbl9.grid(column=2,row=8, sticky=E)
        self.t9.grid(column=3,row=8, sticky=W)     

        lbl_10=Label(win, text='Noise removal matrix rank \nin c2 (CX)', bg="#FFFFFF")
        self.t10=Entry(window,textvariable=StringVar(window, value='4'), width=5)
        lbl_10.grid(column=2,row=9, sticky=E)
        self.t10.grid(column=3,row=9, sticky=W)

        lb_11=Label(win, text='Noise removal matrix rank \nin c3 (INT)', bg="#F08080")
        self.t11=Entry(window,textvariable=StringVar(window, value='4'), width=5)
        lb_11.grid(column=2,row=10, sticky=E)
        self.t11.grid(column=3,row=10, sticky=W)

        lb_12=Label(win, text='Dilation matrix rank \nin c1 (CM)', bg="#10FF10")
        self.t12=Entry(window,textvariable=StringVar(window, value='5'), width=5)
        lb_12.grid(column=4,row=8, sticky=E)
        self.t12.grid(column=5,row=8, sticky=W)

        lb_13=Label(win, text='Dilation matrix rank \nin c2 (CX)', bg="#FFFFFF")
        self.t13=Entry(window,textvariable=StringVar(window, value='7'), width=5)
        lb_13.grid(column=4,row=9, sticky=E)
        self.t13.grid(column=5,row=9, sticky=W)

        lb_14=Label(win, text='Dilation matrix rank \nin c3 (INT)', bg="#F08080")
        self.t14=Entry(window,textvariable=StringVar(window, value='2'), width=5)
        lb_14.grid(column=4,row=10, sticky=E)
        self.t14.grid(column=5,row=10, sticky=W)

        lb_15=Label(win, text='Dilation iterations \nin c1 (CM)', bg="#10FF10")
        self.t15=Entry(window,textvariable=StringVar(window, value='3'), width=5)
        lb_15.grid(column=6,row=8, sticky=E)
        self.t15.grid(column=7,row=8, sticky=W)

        lb_16=Label(win, text='Dilation iterations \nin c2 (CX)', bg="#FFFFFF")
        self.t16=Entry(window,textvariable=StringVar(window, value='6'), width=5)
        lb_16.grid(column=6,row=9, sticky=E)
        self.t16.grid(column=7,row=9, sticky=W)

        lb_17=Label(win, text='Dilation iterations \nin c3 (INT)', bg="#F08080")
        self.t17=Entry(window,textvariable=StringVar(window, value='3'), width=5)
        lb_17.grid(column=6,row=10, sticky=E)
        self.t17.grid(column=7,row=10, sticky=W)

        lb_21=Label(win, text='First Filter \nminimum area (um**2)')
        self.t21=Entry(window,textvariable=StringVar(window, value='100'), width=5)
        lb_21.grid(column=0,row=11, sticky=E)
        self.t21.grid(column=1,row=11, sticky=W)

        lb_22=Label(win, text='First Filter \nminimum perimeter (um)')
        self.t22=Entry(window,textvariable=StringVar(window, value='40'), width=5)
        lb_22.grid(column=0,row=12, sticky=E)
        self.t22.grid(column=1,row=12, sticky=W)

        lb_23=Label(win, text='Second Filter \nL min (um)')
        self.t23=Entry(window,textvariable=StringVar(window, value='35'), width=5)
        lb_23.grid(column=0,row=13, sticky=E)
        self.t23.grid(column=1,row=13, sticky=W)

        lb_24=Label(win, text='Second Filter \nL max (um)')
        self.t24=Entry(window,textvariable=StringVar(window, value='200'), width=5)
        lb_24.grid(column=2,row=13, sticky=E)
        self.t24.grid(column=3,row=13, sticky=W)

        lb_25=Label(win, text='Second Filter \nW min (um)')
        self.t25=Entry(window,textvariable=StringVar(window, value='5'), width=5)
        lb_25.grid(column=0,row=14, sticky=E)
        self.t25.grid(column=1,row=14, sticky=W)

        lb_26=Label(win, text='Second Filter \nW max (um)')
        self.t26=Entry(window,textvariable=StringVar(window, value='50'), width=5)
        lb_26.grid(column=2,row=14, sticky=E)
        self.t26.grid(column=3,row=14, sticky=W)

        lb_27=Label(win, text='Second Filter \nR min')
        self.t27=Entry(window,textvariable=StringVar(window, value='1'), width=5)
        lb_27.grid(column=0,row=15, sticky=E)
        self.t27.grid(column=1,row=15, sticky=W)

        lb_270=Label(win, text='Padding scale factor')
        self.t270=Entry(window,textvariable=StringVar(window, value='1'), width=5)
        lb_270.grid(column=2,row=11, sticky=E)
        self.t270.grid(column=3,row=11, sticky=W)
        CreateToolTip(self.t270, text = '0 for no padding, 1 or 2 are recommended to compensate noise removal effects in automated mask generation')
        
        lb_28=Label(win, text='Gamma correction')
        self.t28=Entry(window,textvariable=StringVar(window, value='0.5'), width=5)
        lb_28.grid(column=0,row=16, sticky=E)
        self.t28.grid(column=1,row=16, sticky=W)
        CreateToolTip(self.t28, text = 'Set < 1 to obtain brighter merged output or > 1 to obtain darker merged image output')
         
        lb_29=Label(win, text='Big scale \nbar lenght (um)')
        self.t29=Entry(window,textvariable=StringVar(window, value='100'), width=5)
        lb_29.grid(column=0,row=17, sticky=E)
        self.t29.grid(column=1,row=17, sticky=W)
        CreateToolTip(self.t29, text = 'Set the lenght of scale bar for full image')

        lb_30=Label(win, text='Small scale \nbar lenght (um)')
        self.t30=Entry(window,textvariable=StringVar(window, value='20'), width=5)
        lb_30.grid(column=2,row=17, sticky=E)
        self.t30.grid(column=3,row=17, sticky=W)
        CreateToolTip(self.t30, text = 'Set the lenght of scale bar for individual retrieval images of detections')

        lb_31=Label(win, text='Small window \nsize (um)')
        self.t31=Entry(window,textvariable=StringVar(window, value='150'), width=5)
        lb_31.grid(column=0,row=18, sticky=E)
        self.t31.grid(column=1,row=18, sticky=W)
        CreateToolTip(self.t31, text = 'Set the size of the window for individual retrievals')
        
        lb_32=Label(win, text='Select \nCM ID plot')
        self.t32=Entry(window,textvariable=StringVar(window, value='all'), width=5)
        lb_32.grid(column=0,row=19, sticky=E)
        self.t32.grid(column=1,row=19, sticky=W)
        CreateToolTip(self.t32, text = 'Set a number to display only specific CM number on final output image. Set all to display all CMs')
        
        self.bo1_state = BooleanVar()
        self.bo1_state.set(False) 
        bo1 = Checkbutton(window, text='Plot \nID numbers', var=self.bo1_state)
        bo1.grid(column=0, row=20)
        CreateToolTip(bo1, text = 'Check to display ID numbers on final output')
        
        self.bo2_state = BooleanVar()
        self.bo2_state.set(True) 
        bo2 = Checkbutton(window, text='Histograms', var=self.bo2_state)
        bo2.grid(column=1, row=20)
        CreateToolTip(bo2, text = 'Check to generate histogram of detected CMs')
        
        self.bo3_state = BooleanVar()
        self.bo3_state.set(True) 
        bo3 = Checkbutton(window, text='Box Plots', var=self.bo3_state)
        bo3.grid(column=2, row=20)       
        CreateToolTip(bo3, text = 'Check to generate Box Plots of detected CMs')

        self.bo4_state = BooleanVar()
        self.bo4_state.set(True) 
        bo4 = Checkbutton(window, text='Merge', var=self.bo4_state)
        bo4.grid(column=3, row=20)
        CreateToolTip(bo4, text = 'Check to generate the binary merged output in a subfolder. \n For instance: out_quantif_timestamp/a_timestamp_merged_binarized.tif')

        self.bo5_state = BooleanVar()
        self.bo5_state.set(True) 
        bo5 = Checkbutton(window, text='Binary Channels', var=self.bo5_state)
        bo5.grid(column=2, row=22)
        CreateToolTip(bo5, text = 'Check to generate binarized output channels in a subfolder. \n For instance: out_quantif_timestamp/a_timestamp_c1_binarized.tif')
        
        self.bo6_state = BooleanVar()
        self.bo6_state.set(True) 
        bo6 = Checkbutton(window, text='CM Mask (Ma)', var=self.bo6_state)
        bo6.grid(column=0, row=21)
        CreateToolTip(bo6, text = 'Check to generate cell mask in a subfolder. \n For instance: out_quantif_timestamp/a_timestamp_mask.tif')

        self.bo7_state = BooleanVar()
        self.bo7_state.set(True)
        bo7 = Checkbutton(window, text='Retrievals \noverlapped', var=self.bo7_state)
        bo7.grid(column=1, row=21)
        CreateToolTip(bo7, text = 'Check to generate merged output with detections in a subfolder. \n For instance: out_quantif_timestamp/a_timestamp_combined_annotated.tif')
        
        self.bo8_state = BooleanVar()
        self.bo8_state.set(True)
        bo8 = Checkbutton(window, text='Tissue Mask', var=self.bo8_state)
        bo8.grid(column=2, row=21)
        CreateToolTip(bo8, text = 'Check to generate tissue mask in a subfolder. \n For instance: out_quantif_timestamp/a_timestamp_tissue_mask.tif')
        
        self.bo9_state = BooleanVar()
        self.bo9_state.set(True)
        bo9 = Checkbutton(window, text='Plot \nIndividual CMs', var=self.bo9_state)
        bo9.grid(column=3, row=21)
        CreateToolTip(bo9, text = 'Check to generate individual images for each detection in a subfolder inside main subfolder. \n For instance: out_quantif_timestamp/CMs/1.tif')
        
        lbl520=Label(win, text='                        ')
        lbl520.grid(column=0,row=24)
        lbl52=Label(win, text='Parameters for \nEVALUATION', bg="black", fg="white")
        lbl52.grid(column=0,row=25)
        # lbl521=Label(win, text='                        ')
        # lbl521.grid(column=0,row=26)
        
        lbl53=Label(win, text='Minimum \nIntersection value')
        self.t53=Entry(window,textvariable=StringVar(window, value='50'), width=5)
        lbl53.grid(column=0,row=26, sticky=E)
        self.t53.grid(column=1,row=26, sticky=W)

        lbl54=Label(win, text='Intersection \nmode (max/ref)')
        self.t54=Entry(window,textvariable=StringVar(window, value='ref'), width=5)
        lbl54.grid(column=0,row=27, sticky=E)
        self.t54.grid(column=1,row=27, sticky=W)

        # lbl520=Label(win, text='                                                ')
        # lbl520.grid(column=0,row=29)
        lbl52=Label(win, text='Parameters for \nManual Mask Generation', bg="black", fg="white")
        lbl52.grid(column=0,row=28)
        # lbl521=Label(win, text='                                                ')
        # lbl521.grid(column=0,row=29)
        
        lbl530=Label(win, text='Number of vertices \nof polygon')
        self.t530=Entry(window,textvariable=StringVar(window, value='8'), width=5)
        lbl530.grid(column=0,row=29, sticky=E)
        self.t530.grid(column=1,row=29, sticky=W)
        CreateToolTip(self.t530, text = 'Number of vertices for each feature. High number will be more accurate but slower manual delineation')
        
        lbl531=Label(win, text='X splits')
        self.t531=Entry(window,textvariable=StringVar(window, value='1'), width=5)
        lbl531.grid(column=0,row=30, sticky=E)
        self.t531.grid(column=1,row=30, sticky=W)
        CreateToolTip(self.t531, text = 'Number of splits in x direction to delineate CMs for big images. Press ESC to go to following split')

        lbl532=Label(win, text='Y splits')
        self.t532=Entry(window,textvariable=StringVar(window, value='1'), width=5)
        lbl532.grid(column=0,row=31, sticky=E)
        self.t532.grid(column=1,row=31, sticky=W)
        CreateToolTip(self.t532, text = 'Number of splits in y direction  CMs for big images. Press ESC to go to following split')
        
    def ex(self):
        sys.exit()

    def sercaORG(self):
        #serca = cv2.imread("a_c1.tif")
        global fname_c1
        idim=self.t2.get()
        inpf=self.t33.get()
        fname_c1=idim+'_c1'+inpf
        serca = cv2.imread(fname_c1)
        serca400 = imutils.resize(serca, width=285, height=280)
        sercapreview = cv2.cvtColor(serca400, cv2.COLOR_BGR2RGB)
        imserca= Image.fromarray(sercapreview)
        imgserca=ImageTk.PhotoImage(image=imserca)
        origserca = Label(window)
        origserca.configure(image=imgserca)
        origserca.image = imgserca
        origserca.grid(column=9, row=0, rowspan=10)
        imgc1 = cv2.imread(fname_c1, cv2.IMREAD_GRAYSCALE)
        tresh_c1=int(self.t6.get())
        dkremovec1=int(self.t9.get())
        dkrgrowc1=int(self.t12.get())
        iters_grow_c1=int(self.t15.get())
        
        kernel_noise_remove_c1=np.ones((dkremovec1, dkremovec1),np.uint8)
        kernel_grow_c1=np.ones((dkrgrowc1,dkrgrowc1),np.uint8)
        
        thresh1serca = cv2.threshold(imgc1,tresh_c1,255,cv2.THRESH_BINARY)[1]
        erserca=cv2.morphologyEx(thresh1serca, cv2.MORPH_OPEN, kernel_noise_remove_c1)
        gimgserca=cv2.dilate(erserca,kernel_grow_c1,iterations = iters_grow_c1)
        greyserca = np.copy(gimgserca)
        greyserca400 = imutils.resize(greyserca, width=285, height=280)
        gimserca= Image.fromarray(greyserca400)
        gimgserca=ImageTk.PhotoImage(image=gimserca)
        maskserca = Label(window)
        maskserca.configure(image=gimgserca)
        maskserca.image = gimgserca
        maskserca.grid(column=10, row=0, rowspan=10)
    
    def cxORG(self):
        #serca = cv2.imread("a_c1.tif")
        idim=self.t2.get()
        inpf=self.t33.get()
        fname_c2=idim+'_c2'+inpf
        connexinorig = cv2.imread(fname_c2)
        connexinorig400 = imutils.resize(connexinorig, width=285, height=280)
        cxpreview = cv2.cvtColor(connexinorig400, cv2.COLOR_BGR2RGB)
        imcx= Image.fromarray(cxpreview)
        imgcx=ImageTk.PhotoImage(image=imcx)
        origcx = Label(window)
        origcx.configure(image=imgcx)
        origcx.image = imgcx
        origcx.grid(column=9, row=10, rowspan=10)        
             
         # Process channel 4 (Binarized Connexin for quantification)  
 
        imgc2=cv2.imread(fname_c2,0)
        eqthrcx=int(self.t5_2.get())
        tresh_c2=int(self.t7.get())
        
        if(self.chk2_state.get()==True):
            equalize='y'
        else:
            equalize='n'
        
        if(equalize == 'y'):
            equ=cv2.equalizeHist(imgc2)
            ret,imgcxb2 = cv2.threshold(equ,eqthrcx,255,cv2.THRESH_BINARY)
            ret,threshcx = cv2.threshold(equ,eqthrcx,255,cv2.THRESH_BINARY)
        else:
            ret,threshcx = cv2.threshold(imgc2,tresh_c2,255,cv2.THRESH_BINARY)
            ret,imgcxb2 = cv2.threshold(cv2.equalizeHist(imgc2),eqthrcx,255,cv2.THRESH_BINARY)  
        
        gimgcx=np.copy(imgcxb2)
        greycx = np.copy(gimgcx)
        greycx400 = imutils.resize(greycx, width=285, height=280)
        gimcx= Image.fromarray(greycx400)
        gimgcx=ImageTk.PhotoImage(image=gimcx)
        maskcx = Label(window)
        maskcx.configure(image=gimgcx)
        maskcx.image = gimgcx
        maskcx.grid(column=10, row=10, rowspan=10)
    
    def wgaORG(self):
        #serca = cv2.imread("a_c1.tif")
        idim=self.t2.get()
        inpf=self.t33.get()
        fname_c3=idim+'_c3'+inpf
        wgaorig = cv2.imread(fname_c3)
        wgaorig400 = imutils.resize(wgaorig, width=285, height=280)
        wgapreview = cv2.cvtColor(wgaorig400, cv2.COLOR_BGR2RGB)
        imwga= Image.fromarray(wgapreview)
        imgwga=ImageTk.PhotoImage(image=imwga)
        origwga = Label(window)
        origwga.configure(image=imgwga)
        origwga.image = imgwga
        origwga.grid(column=9, row=20, rowspan=10)
        
        # Para mostrar la previsualización del canal de wga
        imgc3 = cv2.imread(fname_c3, cv2.IMREAD_GRAYSCALE)
        tresh_c3=int(self.t8.get())
        dkremovec3=int(self.t11.get())
        dkrgrowc3=int(self.t14.get())
        iters_grow_c3=int(self.t17.get())
        
        kernel_noise_remove_c3=np.ones((dkremovec3, dkremovec3),np.uint8)
        kernel_grow_c3=np.ones((dkrgrowc3,dkrgrowc3),np.uint8)
        
        thresh1wga = cv2.threshold(imgc3,tresh_c3,255,cv2.THRESH_BINARY)[1]
        erwga=cv2.morphologyEx(thresh1wga, cv2.MORPH_OPEN, kernel_noise_remove_c3)
        gimgwga=cv2.dilate(erwga,kernel_grow_c3,iterations = iters_grow_c3)
        greywga = np.copy(gimgwga)
        greywga400 = imutils.resize(greywga, width=285, height=280)
        gimwga= Image.fromarray(greywga400)
        gimgwga=ImageTk.PhotoImage(image=gimwga)
        maskwga = Label(window)
        maskwga.configure(image=gimgwga)
        maskwga.image = gimgwga
        maskwga.grid(column=10, row=20, rowspan=10)
    
    def sumar_canales(self):
        idim=self.t2.get()
        inpf=self.t33.get()
        fname_c1=idim+'_c1'+inpf
        imgc1 = cv2.imread(fname_c1, cv2.IMREAD_GRAYSCALE)
        tresh_c1=int(self.t6.get())
        dkremovec1=int(self.t9.get())
        dkrgrowc1=int(self.t12.get())
        iters_grow_c1=int(self.t15.get())
        
        kernel_noise_remove_c1=np.ones((dkremovec1, dkremovec1),np.uint8)
        kernel_grow_c1=np.ones((dkrgrowc1,dkrgrowc1),np.uint8)
        
        thresh1serca = cv2.threshold(imgc1,tresh_c1,255,cv2.THRESH_BINARY)[1]
        erserca=cv2.morphologyEx(thresh1serca, cv2.MORPH_OPEN, kernel_noise_remove_c1)
        gimgserca=cv2.dilate(erserca,kernel_grow_c1,iterations = iters_grow_c1)
        greyserca = np.copy(gimgserca)
        # greyserca400 = imutils.resize(greyserca, width=285, height=280)
        greenserca= cv2.cvtColor(greyserca, cv2.COLOR_GRAY2RGB)

        idim=self.t2.get()
        inpf=self.t33.get()
        fname_c2=idim+'_c2'+inpf
        imgc2 = cv2.imread(fname_c2, cv2.IMREAD_GRAYSCALE)
        tresh_c2=int(self.t7.get())
        dkremovec2=int(self.t10.get())
        dkrgrowc2=int(self.t13.get())
        iters_grow_c2=int(self.t16.get())
        
        kernel_noise_remove_c2=np.ones((dkremovec2, dkremovec2),np.uint8)
        kernel_grow_c2=np.ones((dkrgrowc2,dkrgrowc2),np.uint8)
        
        thresh1cx = cv2.threshold(imgc2,tresh_c2,255,cv2.THRESH_BINARY)[1]
        ercx=cv2.morphologyEx(thresh1cx, cv2.MORPH_OPEN, kernel_noise_remove_c2)
        gimgcx=cv2.dilate(ercx,kernel_grow_c2,iterations = iters_grow_c2)
        greycx = np.copy(gimgcx)
        # greycx400 = imutils.resize(greycx, width=285, height=280)

        idim=self.t2.get()
        inpf=self.t33.get()
        fname_c3=idim+'_c3'+inpf
        imgc3 = cv2.imread(fname_c3, cv2.IMREAD_GRAYSCALE)
        tresh_c3=int(self.t8.get())
        dkremovec3=int(self.t11.get())
        dkrgrowc3=int(self.t14.get())
        iters_grow_c3=int(self.t17.get())
        
        kernel_noise_remove_c3=np.ones((dkremovec3, dkremovec3),np.uint8)
        kernel_grow_c3=np.ones((dkrgrowc3,dkrgrowc3),np.uint8)
        
        thresh1wga = cv2.threshold(imgc3,tresh_c3,255,cv2.THRESH_BINARY)[1]
        erwga=cv2.morphologyEx(thresh1wga, cv2.MORPH_OPEN, kernel_noise_remove_c3)
        gimgwga=cv2.dilate(erwga,kernel_grow_c3,iterations = iters_grow_c3)
        greywga = np.copy(gimgwga)
        # greywga400 = imutils.resize(greywga, width=285, height=280)

        # sumaSercaWGA = cv2.add(greyserca, greywga)
        restarSercaWGA = cv2.subtract(greyserca, greywga)

        # sumarlostres = cv2.add(sumaSercaWGA, greycx)
        restarcx= cv2.subtract(restarSercaWGA, greycx)
        # sumarlostres400 = imutils.resize(sumarlostres, width=285, height=280)
        restarlostres400 = imutils.resize(restarcx, width=415, height=400)
        lostres = np.copy(restarlostres400)
        imlostres = Image.fromarray(lostres)
        imgtres = ImageTk.PhotoImage(image=imlostres)
        masktres = Label(window)
        masktres.configure(image=imgtres)
        masktres.image = imgtres
        masktres.grid(column=5, row=12, rowspan=14, columnspan=4)


    def say_hi(self):
        global cnt,drect,boxvv,numboxes,nvect
        cnt=0
        drect=[]
        box=[]
        
        # mouse callback function
        def draw_trpz(event,x,y,flags,param):
            global cnt,drect,boxvv,numboxes,nvect

            if event == cv2.EVENT_LBUTTONDBLCLK:
                print(x,y)
                drect.append([x,y])
                cnt=cnt+1
                vect=[]
                cv2.circle(subpic,(x,y),5,(255,255,255),-1)
                cv2.putText(subpic,str(cnt),(x+5,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                if(cnt==nvert):
                    cnt=0
                    numboxes=numboxes+1
                    for i in range(0,nvert,1):
                        vect.append(drect[i])
            
                    box.append([np.array([vect])])
                    cv2.drawContours(subpic,[np.array([vect])],-1,(255,255,255),3)
                    cv2.drawContours(sublack,[np.array([vect])],-1,(255,255,255),-1)
                    cv2.drawContours(sublack,[np.array([vect])],-1,(255,0,0),1)
                    print(drect)
                    drect=[]
        print('---------------------------------------------------------------------------------------------------------------')
        print('---------------------------  MANUAL MASK GENERATION    --------------------------------------------------------')
        print('---------------------------------------------------------------------------------------------------------------')
        # Start counting time seconds to evaluate total time spent by running the program
        t0= tm.localtime()
        
        # Assign args to program variables
        subdx=int(self.t531.get())
        subdy=int(self.t532.get())
        nvert=int(self.t530.get())      
        gamma=float(self.t28.get())
        Nim=int(self.t1.get())
        idim=self.t2.get()
        scale=float(self.t4.get())      
        inpf=self.t33.get() #".tif"
        outf=self.t34.get() #".png"      
  

        numboxes=0


        # Read and merge channels 
        if(Nim==3):
            fname_c3=idim+'_c3'+inpf
            fname_c2=idim+'_c2'+inpf
            fname_c1=idim+'_c1'+inpf
            # Overlap image:
            img1 = cv2.imread(fname_c1)
            img3 = cv2.imread(fname_c3)
            img2 = cv2.imread(fname_c2)
            comb=cv2.add(img1,img3)
            comb2=cv2.add(comb,img2)

            # Apply a gamma correction here
            lookUpTable = np.empty((1,256), np.uint8)
            for i in range(256):
                lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)

            img = cv2.LUT(comb2, lookUpTable)
        else:
            img = cv2.imread(idim+inpf)
            
        thresh, blackAndWhiteImage = cv2.threshold(img, 0, 0, cv2.THRESH_BINARY)
        cv2.imwrite("blackblack"+outf,blackAndWhiteImage)
        imblack = cv2.imread("blackblack"+outf)


        xs=np.shape(img)[0]
        ys=np.shape(img)[1]

        # definition of input image subdivision for each dymension (height, width) 
        dh=int(xs/subdx)
        dw=int(ys/subdy)

        x0=0
        y0=0

        for k in range(0,subdx,1):
            for j in range(0,subdy,1):
                subpic=np.copy(img[k*dh:(k+1)*dh,j*dw:(j+1)*dw])
                sublack=np.copy(imblack[k*dh:(k+1)*dh,j*dw:(j+1)*dw])
                
                cv2.namedWindow('image')
                cv2.setMouseCallback('image',draw_trpz)

                while(1):
                    rows, cols, _channels = map(int, subpic.shape)
                    cv2.imshow('image',subpic)            
                    #k = 
                    if cv2.waitKey(20) & 0xFF == 27:
                        break
  
                cv2.destroyAllWindows()
                
                img[k*dh:(k+1)*dh,j*dw:(j+1)*dw]=subpic
                imblack[k*dh:(k+1)*dh,j*dw:(j+1)*dw]=sublack
                
        cv2.imwrite(idim+'_mM.tif',imblack)
        cv2.imwrite(idim+'_mM_overlap.tif',img)


        print("************************************************************************************************************")
        print("************************************************************************************************************")
        t1 = tm.localtime()
        print("Job time (s) : ", np.round(t1 - t0,2)) 
        print("************************************************************************************************************")
        print("************************************************************************************************************") 

        
    def run(self):

        
        # Time initialization
        t0= tm.localtime()

        # Ignore warnings 
        warnings.filterwarnings('ignore')
        warnings.simplefilter('ignore')

        # Create a time dependent output folder filename format
        dirstr=str(round(tm.time()))
        distr=dirstr
        os.mkdir("out_quantif_"+dirstr)

        # Processing mode (supervised, automatic)

        procmode=self.selected.get()
        
        # Input images must be labelled as: idim_c1.tif (CM MARKER), idim_c2.tif (CX43 MARKER), idim_c3.tif (INTERSTICIUM MARKER)
        # Number of input channels (3 or 1)
        Nim=int(self.t1.get())
        # Filename input start pattern for biomarked channels
        idim=self.t2.get()
        # scale
        scale=float(self.t4.get())

        # Input mask (y/n). If y, an input mask labelled as idim_Mm.tif must be provided as input
        if(self.chk1_state.get()==True):
            Inpmask='y'
        else:
            Inpmask='n'
            
        if(self.chk2_state.get()==True):
            equalize='y'
        else:
            equalize='n'

        if(self.chk3_state.get()==True):
            evaluate='y'
        else:
            evaluate='n'
            
        # Mode of mask combination (addch/indepch):
        modecomb=self.selcomb.get() #'addch'

        # scale parameter (in micrometers/pixel)
        eqthr=int(self.t5.get())
        
        # Threshold set (if equalize = no):
        tresh_c1=int(self.t6.get())
        tresh_c2=int(self.t7.get())
        tresh_c3=int(self.t8.get())
        
        # Threshold equalization for c4 channel
        eqthrcx=int(self.t5_2.get())
        # Kernel window size for noise removal in c1 (parameter nr_c1)
        dkremovec1=int(self.t9.get())
        # kernel window size for dilate of c1 (parameter ng_c1)
        dkrgrowc1=int(self.t12.get())
        # Iterations for dilate in c2 (parameter ngit_c1)
        iters_grow_c1=int(self.t15.get())
        
        # Kernel window size for noise removal in c2 (parameter nr_c2)
        dkremovec2=int(self.t10.get())
        # kernel window size for dilate of c2 (parameter ng_c2)
        dkrgrowc2=int(self.t13.get())
        # Iterations for dilate in c2 (parameter ngit_c2)
        iters_grow_c2=int(self.t16.get())

        # Kernel window size for noise removal in c3 (parameter nr_c3)
        dkremovec3=int(self.t11.get())
        # kernel window size for dilate of c3 ((parameter ng_c3)
        dkrgrowc3=int(self.t14.get())
        # Iterations for dilate in c3 (parameter ngit_c3)
        iters_grow_c3=int(self.t17.get())
        
        # First filtered parameters
        # Minimum area of retrieved contour
        ff_areamin=int(self.t21.get()) #100 # squared micrometers
        # Minimum perimeter of retrieved contour
        ff_permin=int(self.t22.get()) #40   # micrometers
        # Second filtered parameters
        # Minimum lenght of CM 
        sf_lboxmin=int(self.t23.get()) #20 # micrometers
        # Maximum lenght of CM
        sf_lboxmax=int(self.t24.get()) #200 # micrometers
        # Minimum width of CM
        sf_wmin=int(self.t25.get()) #5      # micrometers
        # Maximum width of CM
        sf_wmax=int(self.t26.get()) #50     # micrometers
        # Minimum aspect ratio (Lenght/Width) of CM
        sf_rmin=float(self.t27.get()) #1    
        # Padding applied to cell enclosing rectangles as function of dilate parameters
        scpad=int(self.t270.get())
        pad= scpad*dkrgrowc2*iters_grow_c2
        # Select specific Cardiomyocite ID (all/ID number)
        select=self.t32.get()
        # Plot ID numbers (y/n)
        if(self.bo1_state.get()==True):
            plotidnumb='y'
        else:
            plotidnumb='n'
            
        # Font type in image annotations index
        font = cv2.FONT_HERSHEY_SIMPLEX
        # Gamma correction factor (improve brightness of merged image: >1 => darker than original)
        gamma=float(self.t28.get())
        # 0-3 (number of half-sized reductions for final overlaped image output, it's recommended 2 or 3 for large size input files)
        redfactor=0    
        # Font size
        fsize=2 
        # Contour width
        contwidth= 2
        # Window size for individual plots (um)
        wxsize=float(self.t31.get())/scale       
        # Plot scale bars
        scalebars='y'
        # lenght of scale bar (um)
        scalebarlen=float(self.t29.get())
        # mini scale bar (y/n)
        miniscbar='y'
        # mini scale bar lenght (um)
        minisbarlen=float(self.t30.get())
        
        # Graphical output (generate (y) or not (n)):
        if(self.bo2_state.get()==True):
            plothist='y'
        else:
            plothist='n'
            
        if(self.bo3_state.get()==True):
            plotboxplot='y'
        else:
            plotboxplot='n'

        plotdens='y'
        
        if(self.bo4_state.get()==True):
            plotcombin='y'
        else:
            plotcombin='n'

        if(self.bo5_state.get()==True):
            plotchbin='y'
        else:
            plotchbin='n'

        if(self.bo6_state.get()==True):
            plotmask='y'
        else:
            plotmask='n'

        if(self.bo7_state.get()==True):
            plotanot='y'
        else:
            plotanot='n'

        if(self.bo8_state.get()==True):
            plotissuemask='y'
        else:
            plotissuemask='n'

        if(self.bo9_state.get()==True):
            plotsepCMs='y'
        else:
            plotsepCMs='n'

        if (plotsepCMs=='y'):
            os.mkdir("out_quantif_"+dirstr+"/CMs/") 
        # Input format
        inpf=self.t33.get() #".tif"
        outf=self.t34.get() #".png"
        
        #***************************************  END OF PARAMETER SET ********************************************

        # define kernels in a proper way
        kernel_noise_remove_c2 = np.ones((dkremovec2,dkremovec2),np.uint8)
        kernel_grow_c2 =np.ones((dkrgrowc2,dkrgrowc2),np.uint8)

        kernel_noise_remove_c1=np.ones((dkremovec1,dkremovec1),np.uint8)
        kernel_grow_c1=np.ones((dkrgrowc1,dkrgrowc1),np.uint8)

        kernel_noise_remove_c3 = np.ones((dkremovec3,dkremovec3),np.uint8)
        kernel_grow_c3 =np.ones((dkrgrowc3,dkrgrowc3),np.uint8)

        # Selective color mask (greenchannel)
        up_mask_g=255
        dwn_mask_g=250   


        f3 = open("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_paramout.txt", 'w')
        f2 = open("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_data.csv", 'w')

        if(procmode=='supervised'):
            f2.write('ID,value,L(um),W(um),ang(degree),CxLat2,AreaBox(um2),Area(um2),perimeter(um),xc(pix),yc(pix),CXTOT\n')    
        else:
            f2.write('ID,L(um),W(um),ang(degree),CxLat2,AreaBox(um2),Area(um2),perimeter(um),xc(pix),yc(pix),CXTOT\n')

        # Set actual time variables
        now = datetime.now() 
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        time = now.strftime("%H:%M:%S")
        date_time = now.strftime("%Y%m%d_%H%M%S")

        
        # Start binarization
        if(Nim == 3):
            fname_c3=idim+'_c3'+inpf
            fname_c2=idim+'_c2'+inpf
            fname_c1=idim+'_c1'+inpf
        if(Nim==1):
            fname=idim+inpf
            neq = cv2.imread(fname,0)
            if(equalize == 'y'):
                img=cv2.equalizeHist(neq)
                tresh_c1=eqthr
                tresh_c2=254
            else:
                img=neq
                
            ret,backg = cv2.threshold(img,tresh_c1,255,cv2.THRESH_BINARY)
            ret,tiss  = cv2.threshold(img,tresh_c1,255,cv2.THRESH_BINARY_INV)
            ret,foreg = cv2.threshold(img,tresh_c2,255,cv2.THRESH_BINARY)
            thresh, blackAndWhiteImage = cv2.threshold(img, 0, 0, cv2.THRESH_BINARY)
            cv2.imwrite("blackback"+inpf,blackAndWhiteImage)
            imgback = cv2.imread("blackback"+inpf)
            imgfor = cv2.imread("blackback"+inpf)
            imgtis = cv2.imread("blackback"+inpf)
            imgback[:,:,2]=tiss
            imgback[:,:,1]=0
            imgback[:,:,0]=0
            imgfor[:,:,2]=foreg
            imgfor[:,:,1]=foreg
            imgfor[:,:,0]=foreg
            imgtis[:,:,2]=0
            imgtis[:,:,1]=backg
            imgtis[:,:,0]=0
            cv2.imwrite(idim+"_c3"+inpf, imgback)
            cv2.imwrite(idim+"_c1"+inpf, imgtis)
            cv2.imwrite(idim+"_c2"+inpf, imgfor)
            fname_c3=idim+'_c3'+inpf
            fname_c2=idim+'_c2'+inpf
            fname_c1=idim+'_c1'+inpf
            
        # Process channel 1 (Binarization+noise removal+growth)
        thresh, blackAndWhiteImage = cv2.threshold(cv2.imread(fname_c1,0), 0, 0, cv2.THRESH_BINARY)
        cv2.imwrite("blackback"+inpf,blackAndWhiteImage)
        imgc1 = cv2.imread(fname_c1,0)   

        if(equalize == 'y'):
            equ=cv2.equalizeHist(imgc1)
            ret,thresh1serca = cv2.threshold(equ,eqthr,255,cv2.THRESH_BINARY)
        else:
            ret,thresh1serca = cv2.threshold(imgc1,tresh_c1,255,cv2.THRESH_BINARY)

        erserca=cv2.morphologyEx(thresh1serca, cv2.MORPH_OPEN, kernel_noise_remove_c1)
        imgserca=cv2.dilate(erserca,kernel_grow_c1,iterations = iters_grow_c1)
        grayserca = np.copy(imgserca) #cv2.cvtColor(imgserca, cv2.COLOR_BGR2GRAY)

        # Process channel 2 (Binarization+noise removal+growth)  
        imgc2=cv2.imread(fname_c2,0)

        if(equalize == 'y'):
            equ=cv2.equalizeHist(imgc2)
            ret,imgcxb2 = cv2.threshold(equ,eqthrcx,255,cv2.THRESH_BINARY)
            ret,threshcx = cv2.threshold(equ,eqthrcx,255,cv2.THRESH_BINARY)
        else:
            ret,threshcx = cv2.threshold(imgc2,tresh_c2,255,cv2.THRESH_BINARY)
            ret,imgcxb2 = cv2.threshold(cv2.equalizeHist(imgc2),eqthrcx,255,cv2.THRESH_BINARY)

        ercx=cv2.morphologyEx(threshcx, cv2.MORPH_OPEN, kernel_noise_remove_c2)
        imgcx=cv2.dilate(ercx,kernel_grow_c2,iterations = iters_grow_c2)
        imgcxb=np.copy(imgc2)
        graycx = np.copy(imgc2) 

        # Process channel 3 (Binarization+noise removal+growth)
        imgc3 = cv2.imread(fname_c3,0)

        if(equalize == 'y'):
            equ=cv2.equalizeHist(imgc3)
            ret,thresh1 = cv2.threshold(equ,eqthr,255,cv2.THRESH_BINARY)
        else:
            ret,thresh1 = cv2.threshold(imgc3,tresh_c3,255,cv2.THRESH_BINARY)
            
        er=cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel_noise_remove_c3)
        imgwga=cv2.dilate(er,kernel_grow_c3,iterations = iters_grow_c3)
        graywga = np.copy(imgwga)#cv2.cvtColor(imgwga, cv2.COLOR_BGR2GRAY)

        # Write a black background image for mask combination
        thresh, blackAndWhiteImage = cv2.threshold(cv2.imread(fname_c2), 0, 0, cv2.THRESH_BINARY)
        cv2.imwrite("blackback"+outf,blackAndWhiteImage)

        # Define selective color cut: 100% green color
        lower = np.array([0,dwn_mask_g,0])
        upper = np.array([0,up_mask_g,0])

        # Channel combination 
        if(modecomb=='addch'):
            img3comb = cv2.imread("blackback"+outf)
            img3comb[:,:,2]=cv2.add(imgwga,imgcx)
            img3comb[:,:,1]=cv2.add(imgserca,imgcx)
            img3comb[:,:,0]=imgcx
        elif (modecomb=='indepch'):
            img3comb = cv2.imread("blackback"+outf)
            img3comb[:,:,2]=imgwga
            img3comb[:,:,1]=imgserca
            img3comb[:,:,0]=imgcx    

        # Mask Generation

        if(Inpmask=='n'):
            mask_green = cv2.inRange(img3comb, lower, upper)
        else:
            mask_green = cv2.imread(idim+'_Mm'+inpf,0)
                
        # Counting relative proportions of channels
        n_c2=np.count_nonzero(imgcxb2[:,:])
        n_c3=np.count_nonzero(imgwga[:,:])
        n_c1=np.count_nonzero(imgserca[:,:])
        inters=cv2.bitwise_and(graywga,grayserca)
        n_inters=np.count_nonzero(inters)

        cxex=n_c2/(n_c2+n_c1+n_c3-n_inters)*100
        c1ex=n_c1/(n_c2+n_c1+n_c3-n_inters)*100
        c3ex=n_c3/(n_c2+n_c1+n_c3-n_inters)*100
        intex=n_inters/(n_c1+n_c3-n_inters)*100

        # Tissue mask generation
        tissue = cv2.imread("blackback"+outf)
        tissue[:,:,0]=cv2.add(cv2.add(imgserca,imgwga),imgcx)
        tissue[:,:,1]=cv2.add(cv2.add(imgserca,imgwga),imgcx)
        tissue[:,:,2]=cv2.add(cv2.add(imgserca,imgwga),imgcx)

        # Overlap image:
        img1 = cv2.imread(fname_c1)
        img3 = cv2.imread(fname_c3)
        img2 = cv2.imread(fname_c2)
        comb=cv2.add(img1,img3)
        comb2=cv2.add(comb,img2)

        # Apply a gamma correction here
        lookUpTable = np.empty((1,256), np.uint8)
        for i in range(256):
            lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)

        origpic = cv2.LUT(comb2, lookUpTable)

        # Print outputs in screen     
        print("************************************************************************************************************")
        print("This ouput has been generated on " + day +"th of " + month + " of year " + year + ", at local time:  " + time)
        print("************************************************************************************************************")
        print("******************   MARTA (Myocite Automatic Retrieval and Tissue Analyzer)   *****************************")
        print("************************************************************************************************************")
        print("*********************            Source: A. Oliver et al (2020)       **************************************")
        print("Automatic  quantification  of  cardiomyocyte  dimensions  and  connexin43 lateralization in fluorescence images")
        print("************************************************************************************************************")
        print("***********************************  INPUT PARAMETERS ******************************************************")
        print("************************************************************************************************************")   
        print("Input file name:                                      ",idim)
        print("Input format:                                         ",inpf)
        print("Output format:                                        ",outf)
        print("Number of input files:                                ",Nim)
        print("Scale (40x=>0.25, 20x=> 0.50, 10x=> 1.0) :            ",np.round(scale,2)," um/pixel")
        print("Equalize inputs:                                      ",equalize)
        print("Processing mode:                                      ",procmode)
        print("Combine Channel mode:                                 ",modecomb)
        print("Direct input mask:                                    ",Inpmask)
        print("Box padding, h :                                      ",pad," pixels")
        if(scalebars=='y'):
            print("Scale bar lenght:                                     ",scalebarlen,' um')
        if(miniscbar=='y'):    
            print("Individual scale bar lenght:                          ",minisbarlen, ' um')
        print("************************************************************************************************************")

        if (equalize=='y'):
            print("Threshold binarization :                               ",eqthr) 
        else:
            print("Binary Threshold (c1) :                                ",tresh_c1) 
            print("Binary Threshold (c2) :                                ",tresh_c2)
            print("Binary Threshold (c3) :                                ",tresh_c3)
        print("************************************************************************************************************")
        print("Morphological Transform parameters of c1:                                                                   ")
        print("Kernel noise size   :                                   ",dkremovec1)
        print("Kernel growth size  :                                   ",dkrgrowc1)
        print("Iterations for growth size :                            ",iters_grow_c1)
        print("************************************************************************************************************")
        print("Morphological Transform parameters of c2: ")     
        print("Kernel noise size :                                     ",dkremovec2)
        print("Kernel growth size :                                    ",dkrgrowc2)
        print("Iterations for growth size :                            ",iters_grow_c2)
        print("************************************************************************************************************")
        print("Morphological Transform parameters of c3: ")    
        print("Kernel noise size :                                     ", dkremovec3)
        print("Kernel growth size :                                    ", dkrgrowc3)
        print("Iterations for growth size :                            ", iters_grow_c3)
        print("****************************** MORPHOLOGICAL CELL FILTERS **************************************************")
        print("Parameters used for first filtering:                                                                        ") 
        print("Minimum contour area :                                  ",ff_areamin," um2")
        print("Minimum contour perimeter :                             ",ff_permin," um")
        print("************************************************************************************************************")
        print("Parameters used for second filtering:                                                                       ") 
        print("Minimum box-cardiomyocite lenght :                      ",sf_lboxmin," um")
        print("Maximum box-cardiomyocite lenght :                      ",sf_lboxmax," um")
        print("Maximum box-cardiomyocite width  :                      ",sf_wmax," um")
        print("Minimum box-cardiomyocite width  :                      ",sf_wmin," um")
        print("Minimum Aspect Ratio of cardiomyocite (Lenght/Width) :  ",sf_rmin)
        print("************************************************************************************************************")
        print("Gamma correction value :                                ",gamma)
        print("Reduction factor of overlaped output :                  ",redfactor)
        print("************************************************************************************************************")
        print("***********************************  CHANNEL PROPERTIES ****************************************************")
        print("************************************************************************************************************")
        if(Nim == 3):
            print("RGB mean of c1:                                       ",round(cv2.mean(cv2.imread(fname_c1,0))[0],2))
            print("RGB mean of c2:                                       ",round(cv2.mean(cv2.imread(fname_c2,0))[0],2))
            print("RGB mean of c3:                                       ",round(cv2.mean(cv2.imread(fname_c3,0))[0],2))
        elif(Nim==1):
            print("RGB mean of input:                                    ",round(cv2.mean(cv2.imread(fname,0))[0],2))    
            
        print("************************************************************************************************************")
        print("***************************  RELATIVE PROPORTIONS OF BIOMARKERS ********************************************")
        print("************************************************************************************************************")
        print("Percentage of c2 respect to c3 and c1 (CXEX in %):   ", round(n_c2/(n_c2+n_c3+n_c1-n_inters)*100,2))
        print("Percentage of c3 respect to c3 and c1 (INEX in %):   ", round((n_c3-n_inters)/(n_c2+n_c3+n_c1-n_inters)*100,2))
        print("Percentage of c1 respect to c3 and c1 (CMEX in %):   ", round((n_c1)/(n_c2+n_c3+n_c1-n_inters)*100,2))
        print("************************************************************************************************************")
        print("************************************************************************************************************")
        print("Intersection between c1 and c3 (%):                  ", round(n_inters/(n_c3+n_c1-n_inters)*100,2))
        print('Tissue area from pixel count (mm2) :                 ', round(np.count_nonzero(tissue[:,:,0]==255)*scale*scale/1000000,5))
        # Contour search (cv2.RETR_EXTERNAL, cv2.RETR_LIST, cv2.RETR_TREE,...)
        contours2, hierarchy = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Create the background for contours
        img_contours = cv2.imread("blackback"+inpf)
        supmask = cv2.imread("blackback"+inpf)
        # variable initialization
        distm=0.1
        boxc=[]
        angv=[]
        Lboxv=[]
        Wboxv=[]
        Aboxv=[]
        CXLATV=[]
        cardiomdet=0
        yminc=0
        ymaxc=np.shape(img_contours)[0]
        xminc=0
        xmaxc=np.shape(img_contours)[1]

        
        # Loop over contours. CM search:
        for j in range(0,len(contours2)-1,1):        

        # Computation of contour area and perimeter using OpenCV libraries
            area = cv2.contourArea(contours2[j])*scale**2
            perimeter = cv2.arcLength(contours2[j],True)*scale
            
        # First filter:
            if (perimeter > ff_permin) & (area > ff_areamin): 

        # Enclosing filtered contours in minimum area rectangles        
                rect = cv2.minAreaRect(contours2[j])
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                boxc.append(box)
                
        # Axis lenght stimation        
                d01box=((box[0][0]-box[1][0])**2+(box[0][1]-box[1][1])**2)**0.5
                d12box=((box[1][0]-box[2][0])**2+(box[1][1]-box[2][1])**2)**0.5

        # lenght and widths
                Lbox=np.maximum(d01box,d12box)*scale
                Wbox=np.minimum(d01box,d12box)*scale
                
        # Second filter applied        
                if (Lbox > sf_lboxmin) & (Lbox < sf_lboxmax) & (Lbox/Wbox > sf_rmin) & (Wbox < sf_wmax) & (Wbox > sf_wmin):
        #  CM counter       
                    cardiomdet=cardiomdet+1
            
        #  Box partition coordinates            
                    if np.minimum(d01box,d12box) == d01box:
                        x0=box[0][0]
                        x1=box[1][0]
                        y0=box[0][1]
                        y1=box[1][1]
                        x2=box[2][0]
                        y2=box[2][1]
                        x3=box[3][0]
                        y3=box[3][1]
                        x4=int(round((x0+x1)/2))
                        y4=int(round((y0+y1)/2))
                        x5=int(round((x1+x2)/2))
                        y5=int(round((y1+y2)/2))
                        x6=int(round((x2+x3)/2))
                        y6=int(round((y2+y3)/2))
                        x7=int(round((x3+x0)/2))
                        y7=int(round((y3+y0)/2))
                        x8=int(round((x4+x0)/2))
                        y8=int(round((y4+y0)/2))
                        x9=int(round((x4+x1)/2))
                        y9=int(round((y4+y1)/2))        
                        x10=int(round((x5+x1)/2))
                        y10=int(round((y5+y1)/2))
                        x11=int(round((x5+x2)/2))
                        y11=int(round((y5+y2)/2))
                        x12=int(round((x6+x2)/2))
                        y12=int(round((y6+y2)/2))
                        x13=int(round((x6+x3)/2))
                        y13=int(round((y6+y3)/2))
                        x14=int(round((x7+x3)/2))
                        y14=int(round((y7+y3)/2))
                        x15=int(round((x7+x0)/2))
                        y15=int(round((y7+y0)/2))        
                    else:
                        x0=box[1][0]
                        x1=box[2][0]
                        y0=box[1][1]
                        y1=box[2][1]
                        x2=box[3][0]
                        y2=box[3][1]
                        x3=box[0][0]
                        y3=box[0][1]
                        x4=int(round((x0+x1)/2))
                        y4=int(round((y0+y1)/2))
                        x5=int(round((x1+x2)/2))
                        y5=int(round((y1+y2)/2))
                        x6=int(round((x2+x3)/2))
                        y6=int(round((y2+y3)/2))
                        x7=int(round((x3+x0)/2))
                        y7=int(round((y3+y0)/2))
                        x8=int(round((x4+x0)/2))
                        y8=int(round((y4+y0)/2))
                        x9=int(round((x4+x1)/2))
                        y9=int(round((y4+y1)/2))        
                        x10=int(round((x5+x1)/2))
                        y10=int(round((y5+y1)/2))
                        x11=int(round((x5+x2)/2))
                        y11=int(round((y5+y2)/2))
                        x12=int(round((x6+x2)/2))
                        y12=int(round((y6+y2)/2))
                        x13=int(round((x6+x3)/2))
                        y13=int(round((y6+y3)/2))
                        x14=int(round((x7+x3)/2))
                        y14=int(round((y7+y3)/2))
                        x15=int(round((x7+x0)/2))
                        y15=int(round((y7+y0)/2)) 

        # Application of a padding to the rectangle 

                    d13=((x0-x2)**2+(y0-y2)**2)**0.5
                    d24=((x1-x3)**2+(y1-y3)**2)**0.5
                    
                    xn1=np.copy(x0)
                    xn2=np.copy(x1)
                    xn3=np.copy(x2)
                    xn4=np.copy(x3)
                                        
                    yn1=np.copy(y0)
                    yn2=np.copy(y1)
                    yn3=np.copy(y2)
                    yn4=np.copy(y3)
                                                                       
                    x0=xn1-int(round(pad*(xn3-xn1)/d13))
                    x1=xn2-int(round(pad*(xn4-xn2)/d24))
                    y0=yn1-int(round(pad*(yn3-yn1)/d13))
                    y1=yn2-int(round(pad*(yn4-yn2)/d24))
                                        
                    x2=xn3+int(round(pad*(xn3-xn1)/d13))
                    y2=yn3+int(round(pad*(yn3-yn1)/d13))
                    x3=xn4+int(round(pad*(xn4-xn2)/d24))
                    y3=yn4+int(round(pad*(yn4-yn2)/d24))
                    
        # Computing lenght of paded rectangle (extended in long axis direction)
                    expbox1=((x0-x1)**2+(y0-y1)**2)**0.5
                    expbox2=((x1-x2)**2+(y1-y2)**2)**0.5
                    
        # Computing the coordinates range of the box             
                    xmaxb=np.max((x0,x1,x2,x3))
                    ymaxb=np.max((y0,y1,y2,y3))
                    xminb=np.min((x0,x1,x2,x3))
                    yminb=np.min((y0,y1,y2,y3))
                    
        # Split CM box into 4 equal parts            
                    rec1=np.array([[x0,y0],[x1,y1],[x10,y10],[x15,y15]])
                    rec2=np.array([[x15,y15],[x10,y10],[x5,y5],[x7,y7]])
                    rec3=np.array([[x7,y7],[x5,y5],[x11,y11],[x14,y14]])
                    rec4=np.array([[x14,y14],[x11,y11],[x2,y2],[x3,y3]])  


        # Draw a background image 
                    thresh, blackAndWhiteImage = cv2.threshold(cv2.imread(fname_c1,0), 0, 0, cv2.THRESH_BINARY)
                    cv2.imwrite("blacksub"+outf,blackAndWhiteImage)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    
        # Compute an intersection between c2 channel and partitioned rectangles
                    r0fig=cv2.drawContours(imgblack,[rec1],0,(255,255,255),-1)
                    int0=cv2.bitwise_and(r0fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp0=np.count_nonzero(int0)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r1fig=cv2.drawContours(imgblack,[rec2],0,(255,255,255),-1)
                    int1=cv2.bitwise_and(r1fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp1=np.count_nonzero(int1)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r2fig=cv2.drawContours(imgblack,[rec3],0,(255,255,255),-1)
                    int2=cv2.bitwise_and(r2fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp2=np.count_nonzero(int2)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r3fig=cv2.drawContours(imgblack,[rec4],0,(255,255,255),-1)
                    int3=cv2.bitwise_and(r3fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp3=np.count_nonzero(int3)
                    
        # Compute the proportions of c2 relative to each compartment          
                    p0=nwp0/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p1=nwp1/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p2=nwp2/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p3=nwp3/(nwp0+nwp1+nwp2+nwp3+0.001)*100  
                    
        # Compute the lenghts and widths of CMs (lenghts as average of extended and non extended rectangle)
                    Lbox0=np.maximum(d01box,d12box)*scale
                    Lbox1=np.maximum(expbox1,expbox2)*scale
                    Lbox=(Lbox0+Lbox1)*0.5
                    Wbox=np.minimum(d01box,d12box)*scale
                    Abox=Lbox*Wbox
        # Compute angles of orientation of retrieved CM respect to vertical image axis
                    if(d01box>d12box):
                        ang=np.arccos((box[0][1]-box[1][1])*scale/Lbox)*180/np.pi
                        sgang=-1#(box[0][1]-box[1][1])
                    else:
                        ang=np.arccos((box[1][1]-box[2][1])*scale/Lbox)*180/np.pi
                        sgang=1#(box[0][1]-box[1][1])

        # In supervised mode revise
                    if(procmode=='supervised'):
                        ctdx=int(round((box[0][0]+box[1][0]+box[2][0]+box[3][0])/4))    
                        ctdy=int(round((box[0][1]+box[1][1]+box[2][1]+box[3][1])/4))
                        
                        xminw=ctdx-wxsize/2
                        yminw=ctdy-wxsize/2
                        xmaxw=ctdx+wxsize/2
                        ymaxw=ctdy+wxsize/2
                       
                        if(Nim==3):
                            origpic = cv2.LUT(comb2, lookUpTable)
                        else:
                            origpic = cv2.imread(fname)
                        
                        if(xminw<0):
                            xminw=0
                        if(yminw<0):
                            yminw=0
                        if(xmaxw>np.shape(origpic)[1]):
                            xmaxw=np.shape(origpic)[1]
                        if(ymaxw>np.shape(origpic)[0]):
                            ymaxw=np.shape(origpic)[0]
                    
                        cv2.drawContours(origpic,[box],0,(0,255,255),2)   
                        cv2.drawContours(origpic,[contours2[j]],0,(255,0,255),2)
                        
                        # Definition of mini scale bars for individual retrieval
                        xmsc0=xmaxw-10-int(minisbarlen/scale)
                        ymsc0=ymaxw-10
                        xmsc1=xmaxw-10
                        ymsc1=ymaxw-10
                        xmsc2=xmaxw-10
                        ymsc2=ymaxw-20
                        xmsc3=xmaxw-10-int(minisbarlen/scale)
                        ymsc3=ymaxw-20
                        mscbar=np.array([[int(xmsc0),int(ymsc0)],[int(xmsc1),int(ymsc1)],[int(xmsc2),int(ymsc2)],[int(xmsc3),int(ymsc3)]])
                        
                        if (miniscbar=='y'):
                            cv2.drawContours(origpic,[mscbar],-1,(255,255,255),-1)
                        cv2.imshow('CM detected',origpic[int(yminw):int(ymaxw),int(xminw):int(xmaxw)])

                        window.withdraw()
                        
                        # the input dialog
                        
                        USER_INP = simpledialog.askstring(title="MARTA",prompt="Write y in the dialog to save detection or any other comment to not save\n Then, press OK to continue to the next or cancel to exit")
                        cv2.destroyAllWindows() 
                        value = USER_INP 
                        
                        f2.write(str(cardiomdet)+','+str(value)+','+str(round(Lbox,2))+','+str(round(Wbox,2))+','+str(round(ang,2))+','+str(round((p1+p2)*100/(p0+p3+p1+p2+0.001),2))+','+str(round(Abox,2))+','+str(round(area,2))+','+str(round(perimeter,2))+','+str(round((x2+x1)*0.5,2))+','+str(round((y2+y1)*0.5,2))+','+str(round((nwp0+nwp1+nwp2+nwp3)*100*scale*scale/Abox,2))+'\n')  
                        if(plotsepCMs=='y'):
                            if (miniscbar=='y'):
                                cv2.drawContours(origpic,[mscbar],-1,(255,255,255),-1)
                            cv2.imwrite("out_quantif_"+dirstr+"/CMs/"+str(cardiomdet)+"_"+value+outf,origpic[int(yminw):int(ymaxw),int(xminw):int(xmaxw)])

                        if(value=='y'):

                        # Store variables in lists              
                            angv.append(ang*sgang)
                            Lboxv.append(Lbox)
                            Wboxv.append(Wbox)
                            Aboxv.append(Abox)         
                            CXLATV.append((p1+p2)*100/(p0+p3+p1+p2+0.001))
                            cv2.drawContours(supmask, [box], -1, (255, 255, 255), -1)
                            
                        if(select=="all") & (value=='y'):
                            cv2.drawContours(img_contours,[rec1],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours,[rec2],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours,[rec3],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours,[rec4],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours, contours2[j], -1, (255, 0, 255), contwidth*2)                
                        else:
                            if(str(cardiomdet)==select):
                                cv2.drawContours(img_contours,[rec1],0,(255,0,0),contwidth)
                                cv2.drawContours(img_contours,[rec2],0,(255,0,0),contwidth)
                                cv2.drawContours(img_contours,[rec3],0,(255,0,0),contwidth)
                                cv2.drawContours(img_contours,[rec4],0,(255,0,0),contwidth)    
                                cv2.drawContours(img_contours, contours2[j], -1, (255, 0, 255), contwidth)
                                yminc=yminb
                                ymaxc=ymaxb
                                xminc=xminb
                                xmaxc=xmaxb
                                 
        # Plot ID numbers at center of rectangle if specified in parameters
                        x1=int(round((box[0][0]+box[1][0])/2))
                        x2=int(round((box[2][0]+box[3][0])/2))
                        y1=int(round((box[0][1]+box[1][1])/2))
                        y2=int(round((box[2][1]+box[3][1])/2))
                    
                        if(plotidnumb=="y"):
                            cv2.putText(img_contours, str(cardiomdet), (int(round((x2+x1)*0.5)+5),int(round((y2+y1)*0.5))), font, fsize, (255, 100, 100), contwidth, cv2.LINE_AA)                    
                            
                    else:
                        f2.write(str(cardiomdet)+','+str(round(Lbox,2))+','+str(round(Wbox,2))+','+str(round(ang,2))+','+str(round((p1+p2)*100/(p0+p3+p1+p2+0.001),2))+','+str(round(Abox,2))+','+str(round(area,2))+','+str(round(perimeter,2))+','+str(round((x2+x1)*0.5,2))+','+str(round((y2+y1)*0.5,2))+','+str(round((nwp0+nwp1+nwp2+nwp3)/scale*scale/Abox,2))+'\n')  
                        angv.append(ang*sgang)
                        Lboxv.append(Lbox)
                        Wboxv.append(Wbox)
                        Aboxv.append(Abox)         
                        CXLATV.append((p1+p2)*100/(p0+p3+p1+p2+0.001))                

                        ctdx=int(round((box[0][0]+box[1][0]+box[2][0]+box[3][0])/4))    
                        ctdy=int(round((box[0][1]+box[1][1]+box[2][1]+box[3][1])/4))
                        
                        xminw=ctdx-wxsize/2
                        yminw=ctdy-wxsize/2
                        xmaxw=ctdx+wxsize/2
                        ymaxw=ctdy+wxsize/2
                        if(xminw<0):
                            xminw=0
                        if(yminw<0):
                            yminw=0
                        if(xmaxw>np.shape(origpic)[1]):
                            xmaxw=np.shape(origpic)[1]
                        if(ymaxw>np.shape(origpic)[0]):
                            ymaxw=np.shape(origpic)[0]
                            
                        conn = cv2.imread(fname_c2)   
                        if(plotsepCMs=='y'):
                            if(Nim==3):
                                origpic = cv2.LUT(comb2, lookUpTable)
                                connexin = cv2.LUT(conn, lookUpTable)
                            else:
                                origpic = cv2.imread(fname)
                                connexin = cv2.imread(fname_c2)
                            #cv2.drawContours(origpic,[box],0,(0,0,255),1)   
                            cv2.drawContours(origpic,[contours2[j]],0,(255,0,255),contwidth)
                            cv2.drawContours(origpic,[rec1],0,(255,0,0),contwidth)
                            cv2.drawContours(origpic,[rec2],0,(255,0,0),contwidth)
                            cv2.drawContours(origpic,[rec3],0,(255,0,0),contwidth)
                            cv2.drawContours(origpic,[rec4],0,(255,0,0),contwidth)                         

                            
                            cv2.drawContours(connexin,[rec1],0,(255,0,0),contwidth)
                            cv2.drawContours(connexin,[rec2],0,(255,0,0),contwidth)
                            cv2.drawContours(connexin,[rec3],0,(255,0,0),contwidth)
                            cv2.drawContours(connexin,[rec4],0,(255,0,0),contwidth)
                            #cv2.drawContours(img_contours,[box],0,(0,255,255),contwidth)
                            cv2.drawContours(connexin, contours2[j], -1, (255, 0, 255), contwidth)                     
                            if (miniscbar=='y'):
                                xmsc0=xmaxw-10-int(minisbarlen/scale)
                                ymsc0=ymaxw-10
                                xmsc1=xmaxw-10
                                ymsc1=ymaxw-10
                                xmsc2=xmaxw-10
                                ymsc2=ymaxw-20
                                xmsc3=xmaxw-10-int(minisbarlen/scale)
                                ymsc3=ymaxw-20
                                mscbar=np.array([[int(xmsc0),int(ymsc0)],[int(xmsc1),int(ymsc1)],[int(xmsc2),int(ymsc2)],[int(xmsc3),int(ymsc3)]])                        
                                cv2.drawContours(origpic,[mscbar],-1,(255,255,255),-1)
           
                            cv2.imwrite("out_quantif_"+dirstr+"/CMs/"+str(cardiomdet)+outf,origpic[int(yminw):int(ymaxw),int(xminw):int(xmaxw)])
                            cv2.imwrite("out_quantif_"+dirstr+"/CMs/"+str(cardiomdet)+'_c2'+outf,connexin[int(yminw):int(ymaxw),int(xminw):int(xmaxw)])
        # Draw all the contours or ID specified             
                        if(select=="all"):
                            cv2.drawContours(img_contours,[rec1],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours,[rec2],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours,[rec3],0,(255,0,0),contwidth)
                            cv2.drawContours(img_contours,[rec4],0,(255,0,0),contwidth)
                            #cv2.drawContours(img_contours,[box],0,(0,255,255),contwidth)
                            cv2.drawContours(img_contours, contours2[j], -1, (255, 0, 255), contwidth)

                        else:
                            if(str(cardiomdet)==select):
                                cv2.drawContours(img_contours,[rec1],0,(255,0,0),contwidth)
                                cv2.drawContours(img_contours,[rec2],0,(255,0,0),contwidth)
                                cv2.drawContours(img_contours,[rec3],0,(255,0,0),contwidth)
                                cv2.drawContours(img_contours,[rec4],0,(255,0,0),contwidth)    
                                cv2.drawContours(img_contours, contours2[j], -1, (255, 0, 255), contwidth)
                                yminc=yminb
                                ymaxc=ymaxb
                                xminc=xminb
                                xmaxc=xmaxb
                                 
        # Plot ID numbers at center of rectangle if specified in parameters
                        x1=int(round((box[0][0]+box[1][0])/2))
                        x2=int(round((box[2][0]+box[3][0])/2))
                        y1=int(round((box[0][1]+box[1][1])/2))
                        y2=int(round((box[2][1]+box[3][1])/2))
                    
                        if(plotidnumb=="y"):
                            cv2.putText(img_contours, str(cardiomdet), (int(round((x2+x1)*0.5)+5),int(round((y2+y1)*0.5))), font, fsize, (255, 100, 100), contwidth, cv2.LINE_AA)                    
                            
        # END OF THE LOOP

        # Compute stats of the parameters
        cxlatm=np.mean(CXLATV)
        lboxm=np.mean(Lboxv)
        wboxm=np.mean(Wboxv)
        angm=np.mean(angv)

        # Define scale bars
        xsc0=np.shape(img3comb)[1]-100-int(scalebarlen/scale)
        ysc0=np.shape(img3comb)[0]-50
        xsc1=np.shape(img3comb)[1]-100
        ysc1=np.shape(img3comb)[0]-50
        xsc2=np.shape(img3comb)[1]-100
        ysc2=np.shape(img3comb)[0]-100
        xsc3=np.shape(img3comb)[1]-100-int(scalebarlen/scale)
        ysc3=np.shape(img3comb)[0]-100
        scbar=np.array([[xsc0,ysc0],[xsc1,ysc1],[xsc2,ysc2],[xsc3,ysc3]])

        # Statistical analysis plots
        if plothist == 'y' :
        # create a figure 
            fig = plt.figure() 
        # define subplots 
            plt1 = fig.add_subplot(221) 
            plt2 = fig.add_subplot(222) 
            plt3 = fig.add_subplot(223) 
            plt4 = fig.add_subplot(224) 
            plt1.hist(CXLATV, bins=10) 
            plt1.set_title('CXLAT(%)') 
            plt2.hist(Lboxv, bins=10) 
            plt2.set_title('L(um)') 
            plt3.hist(Wboxv, bins=10)  
            plt3.set_title('W(um)') 
            plt4.hist(angv, bins=10) 
            plt4.set_title('Angle(deg)') 
        # Space between subplots 
            fig.subplots_adjust(hspace=.5,wspace=0.5) 
            plt.savefig("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_histplot.png",dpi=200)
            
        if plotboxplot == 'y' :
        # create a figure 
            fig2 = plt.figure() 
        # define subplots 
            plt5 = fig2.add_subplot(221) 
            plt6 = fig2.add_subplot(222) 
            plt7 = fig2.add_subplot(223) 
            plt8 = fig2.add_subplot(224) 
            plt5.boxplot(CXLATV) 
            plt5.set_title('CXLAT(%)') 
            plt6.boxplot(Lboxv)  
            plt6.set_title('L(um)') 
            plt7.boxplot(Wboxv)    
            plt7.set_title('W(um)') 
            plt8.boxplot(angv)  
            plt8.set_title('Angle(deg)') 
        # Space between subplots 
            fig2.subplots_adjust(hspace=.5,wspace=0.5) 
            plt.savefig("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_boxsplot.png",dpi=200)

        # write outputs in separated files: Binarized channels and cell mask
        if plotcombin == 'y' :
            if(scalebars=='y'):
                cv2.drawContours(img3comb,[scbar],-1,(255,255,255),-1)
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_merged_binarized"+outf, img3comb[yminc:ymaxc,xminc:xmaxc])
        if plotchbin  == 'y' :
            img=cv2.imread("blacksub"+outf) 
            if(Nim==3):
                img= imgserca
            else:
                img= imgserca
            if(scalebars=='y'):
                cv2.drawContours(img,[scbar],-1,(255,255,255),-1)
                cv2.drawContours(imgcx,[scbar],-1,(255,255,255),-1)
                cv2.drawContours(imgcxb2,[scbar],-1,(255,255,255),-1)

            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_c1_binarized"+outf, img[yminc:ymaxc,xminc:xmaxc])
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_c2_binarized"+outf, imgcx[yminc:ymaxc,xminc:xmaxc])
            img=cv2.imread("blacksub"+outf) 
            if(Nim==3):
                img= imgwga
            else:
                img= imgwga
            if(scalebars=='y'):
                cv2.drawContours(img,[scbar],-1,(255,255,255),-1)    

            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_c3_binarized"+outf, img[yminc:ymaxc,xminc:xmaxc])    
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_c4_binarized"+outf, imgcxb2[yminc:ymaxc,xminc:xmaxc])      
        if plotmask == 'y' : 
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_cell_mask_nb"+outf, mask_green[yminc:ymaxc,xminc:xmaxc])
            if(scalebars=='y'):
                cv2.drawContours(mask_green,[scbar],-1,(255,255,255),-1)
                cv2.drawContours(supmask,[scbar],-1,(255,255,255),-1)          
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_cell_mask"+outf, mask_green[yminc:ymaxc,xminc:xmaxc])
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_superv_cell_mask"+outf, supmask[yminc:ymaxc,xminc:xmaxc])
            
        if plotissuemask == 'y':
            if(scalebars=='y'):
                cv2.drawContours(tissue,[scbar],-1,(255,255,255),-1)    
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_tissue_mask"+outf, tissue)
            
        anotat=np.copy(img_contours)
        # combine the 3 channel original merged background to the contours found by the algorithm
        if(Nim == 3):
            imgserca = cv2.imread(fname_c1)
            imgwga = cv2.imread(fname_c3)
            imgcx = cv2.imread(fname_c2)
            comb=cv2.add(imgserca,imgwga)
            comb2=cv2.add(comb,imgcx)
        #    comb3=cv2.add(cv2.imread(fname_c2,0),anotat)
            # Apply a gamma correction here
            lookUpTable = np.empty((1,256), np.uint8)
            for i in range(256):
                lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)

            result = cv2.LUT(comb2, lookUpTable)
            com3=cv2.add(result,img_contours)
            

        if(Nim == 1):
            comb2=cv2.imread(fname)
            imgcxb3=cv2.imread(fname_c2)
            comb3=cv2.add(imgcxb3,anotat)
            com3=cv2.add(comb2,img_contours)

        imgresize = imutils.resize(com3, width=415, height=400)
        imgrescop = np.copy(imgresize)
        imgarr = Image.fromarray(imgrescop)
                            
        imgphoto = ImageTk.PhotoImage(image=imgarr)
        winim = Label(window)
        winim.configure(image=imgphoto)
        winim.image = imgphoto
        winim.grid(column=12, row=8, rowspan=20, columnspan=20)
        
        # make a reduction of output file  
        if(redfactor == 1) & (plotanot == 'y') :
            reduc = cv2.pyrDown(com3)
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_combined_annotated"+outf, reduc[yminc:ymaxc,xminc:xmaxc])
        elif(redfactor == 2)& (plotanot == 'y') :
            reduc = cv2.pyrDown(cv2.pyrDown(com3))
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_combined_annotated"+outf, reduc[yminc:ymaxc,xminc:xmaxc])
        elif(redfactor == 3)& (plotanot == 'y') :
            reduc = cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(com3)))
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_combined_annotated"+outf, reduc[yminc:ymaxc,xminc:xmaxc])
        else:
            if (plotanot == 'y') :
                if(scalebars=='y'):
                    cv2.drawContours(com3,[scbar],-1,(255,255,255),-1)  
                cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_combined_annotated"+outf, com3[yminc:ymaxc,xminc:xmaxc])

        f3.write("************************************************************************************************************\n")
        f3.write("This ouput has been generated on "+day+"th of "+month+" of year "+year+", at local time: "+time+'\n')
        f3.write("************************************************************************************************************\n")  
        f3.write("******************   MARTA (Myocite Automatic Retrieval and Tissue Analyzer)   *****************************\n")
        f3.write("************************************************************************************************************\n")  
        f3.write("*********************            Source: A. Oliver et al (2020)       **************************************\n")
        f3.write("************************************************************************************************************\n")         
        f3.write("Automatic  quantification  of  cardiomyocyte  dimensions  and  connexin43 lateralization in fluorescence images\n")
        f3.write("************************************************************************************************************\n")          
        f3.write("***********************************  INPUT PARAMETERS ******************************************************\n")
        f3.write("************************************************************************************************************\n")   
        f3.write("Input file name:                                      "+str(idim)+"\n")
        f3.write("Number of input files:                                "+str(Nim)+"\n")
        f3.write("Scale (40x=>0.25, 20x=> 0.50, 10x=> 1.0) :            "+str(np.round(scale,2))+"um/pixel"+"\n")
        f3.write("Equalize inputs:                                      "+str(equalize)+"\n")
        f3.write("Processing mode:                                      "+procmode+"\n")
        f3.write("Combine Channel mode:                                 "+modecomb+"\n")
        f3.write("Direct input mask:                                    "+Inpmask+"\n")
        f3.write("Box padding, h :                                      "+str(pad)+" pixels"+"\n")
        if(scalebars=='y'):
            f3.write("Scale bar lenght:                                     "+str(scalebarlen)+' um'+"\n")
        if(miniscbar=='y'):    
            f3.write("Individual scale bar lenght:                          "+str(minisbarlen)+' um'+"\n")
        f3.write("***********************************************************************************************************\n")

        if (equalize=='y'):
            f3.write("Threshold binarization :                               "+str(eqthr)+"\n") 
        else:
            f3.write("Binary Threshold (c1) :                                "+str(tresh_c1)+"\n") 
            f3.write("Binary Threshold (c2) :                                "+str(tresh_c2)+"\n")
            f3.write("Binary Threshold (c3) :                                "+str(tresh_c3)+"\n")
        f3.write("************************************************************************************************************\n")
        f3.write("Morphological Transform parameters of c1:                            "+"\n")
        f3.write("Kernel noise size   :                                   "+str(dkremovec1)+"\n")
        f3.write("Kernel growth size  :                                   "+str(dkrgrowc1)+"\n")
        f3.write("Iterations for growth size :                            "+str(iters_grow_c1)+"\n")
        f3.write("************************************************************************************************************\n")
        f3.write("Morphological Transform parameters of c2: "+"\n")     
        f3.write("Kernel noise size :                                     "+str(dkremovec2)+"\n")
        f3.write("Kernel growth size :                                    "+str(dkrgrowc2)+"\n")
        f3.write("Iterations for growth size :                            "+str(iters_grow_c2)+"\n")
        f3.write("************************************************************************************************************\n")
        f3.write("Morphological Transform parameters of c3: "+"\n")    
        f3.write("Kernel noise size :                                     "+str(dkremovec3)+"\n")
        f3.write("Kernel growth size :                                    "+str(dkrgrowc3)+"\n")
        f3.write("Iterations for growth size :                            "+str(iters_grow_c3)+"\n")
        f3.write("****************************** MORPHOLOGICAL CELL FILTERS *************************************************\n")
        f3.write("Parameters used for first filtering:                                                                       \n") 
        f3.write("Minimum contour area :                                  "+str(ff_areamin)+" um2"+"\n")
        f3.write("Minimum contour perimeter :                             "+str(ff_permin)+" um"+"\n")
        f3.write("***********************************************************************************************************\n")
        f3.write("Parameters used for second filtering:                                                                      \n") 
        f3.write("Minimum box-cardiomyocite lenght :                      "+str(sf_lboxmin)+" um\n")
        f3.write("Maximum box-cardiomyocite lenght :                      "+str(sf_lboxmax)+" um\n")
        f3.write("Maximum box-cardiomyocite width  :                      "+str(sf_wmax)+" um\n")
        f3.write("Minimum box-cardiomyocite width  :                      "+str(sf_wmin)+" um\n")
        f3.write("Minimum Aspect Ratio of cardiomyocite (Lenght/Width) :  "+str(sf_rmin)+"\n")
        f3.write("************************************************************************************************************"+"\n")
        f3.write("Gamma correction value :                                "+str(gamma)+'\n')
        f3.write("Reduction factor of overlaped output :                  "+str(redfactor)+'\n')
        f3.write("***********************************************************************************************************\n")
        f3.write("***********************************  CHANNEL PROPERTIES ***************************************************\n")
        f3.write("***********************************************************************************************************\n")
        if(Nim == 3):
            f3.write("RGB mean of c1:                                       "+str(round(cv2.mean(cv2.imread(fname_c1,0))[0],2))+'\n')
            f3.write("RGB mean of c2:                                       "+str(round(cv2.mean(cv2.imread(fname_c2,0))[0],2))+'\n')
            f3.write("RGB mean of c3:                                       "+str(round(cv2.mean(cv2.imread(fname_c3,0))[0],2))+'\n')
        elif(Nim==1):
            f3.write("RGB mean of input:                                    "+str(round(cv2.mean(cv2.imread(fname,0))[0],2))+'\n')    
            
        f3.write("************************************************************************************************************"+'\n')
        f3.write("***************************  RELATIVE PROPORTIONS OF BIOMARKERS ********************************************"+'\n')
        f3.write("************************************************************************************************************"+'\n')
        f3.write("Percentage of c2 respect to c3 and c1 (CXEX in %):   "+str(round(n_c2/(n_c2+n_c3+n_c1-n_inters)*100,2))+'\n')
        f3.write("Percentage of c3 respect to c3 and c1 (INEX in %):   "+str(round((n_c3-n_inters)/(n_c2+n_c3+n_c1-n_inters)*100,2))+'\n')
        f3.write("Percentage of c1 respect to c3 and c1 (CMEX in %):   "+str(round((n_c1)/(n_c2+n_c3+n_c1-n_inters)*100,2))+'\n')
        f3.write("************************************************************************************************************"+'\n')
        f3.write("************************************************************************************************************"+'\n')
        f3.write("Intersection between c1 and c3 (%):                  "+str(round(n_inters/(n_c3+n_c1-n_inters)*100,2))+'\n')
        f3.write('Tissue area from pixel count (mm2) :                 '+str(round(np.count_nonzero(tissue[:,:,0]==255)*scale*scale/1000000,5))+'\n')
        f3.write("***************************  RESULTS STATISTICAL ANALYSIS **************************************************"+'\n')
        f3.write("Number of detected cardiomyocites:                   "+str(cardiomdet)+'\n')
        f3.write("Percentage of Cx43 Lateral (%):                      "+str(round(cxlatm,2))+"+/-"+str(round(np.std(CXLATV),2))+'\n')
        f3.write("Average Lenght of CMs found (um):                    "+str(round(lboxm,2))+"+/-"+str(round(np.std(Lboxv),2))+'\n')
        f3.write("Average Width of CMs (um):                           "+str(round(wboxm,2))+"+/-"+str(round(np.std(Wboxv),2))+'\n')
        f3.write("Average angle of CMs (degree):                       "+str(round(angm,2))+"+/-"+str(round(np.std(angv),2))+'\n')
        # f3.write("***************************  RESULTS COMPUTING TIME ********************************************************"+'\n')
        t1 = tm.localtime()
        # f3.write("Total time of execution (s) :                        "+str(round(t1 - t0,2))+'\n') 
        # f3.write("***********************************************************************************************************"+'\n')
        f3.write("************************************************************************************************************\n")          
        f3.write("***********************************  CREDITS ***************************************************************\n")
        f3.write("************************************************************************************************************\n")  
        f3.write("Antonio Oliver Gelabert  (ORCID : http://orcid.org/0000-0001-8571-2733)                                     \n")        
        f3.write("Laura Garcia Mendivil    (ORCID : http://orcid.org/0000-0002-2954-1068)                                     \n")
        f3.write("Laura Ordovas            (ORCID : http://orcid.org/0000-0003-3982-1263)                                     \n")
        f3.write("Emiliano Raul Diez       (ORCID : http://orcid.org/0000-0001-5163-3703)                                     \n")
        f3.write("Eshter Pueyo             (ORCID : http://orcid.org/0000-0002-1960-407X)                                     \n")
        f3.write("************************************************************************************************************\n")         
        f3.write("Funding  :                                                                                                  \n")
        f3.write("************************************************************************************************************\n")
        f3.write("MODELAGE (ERC-StG 638284)                                                                                   \n")
        f3.write("************************************************************************************************************\n")
        
        print("***************************  RESULTS STATISTICAL ANALYSIS **************************************************")
        print("Number of detected cardiomyocites:                   ", cardiomdet)
        print("Percentage of Cx43 Lateral (%):                      ", round(cxlatm,2),"+/-",round(np.std(CXLATV),2))
        print("Average Lenght of CMs found (um):                    ", round(lboxm,2),"+/-",round(np.std(Lboxv),2))
        print("Average Width of CMs (um):                           ", round(wboxm,2),"+/-",round(np.std(Wboxv),2))
        print("Average angle of CMs (degree):                       ",round(angm,2),"+/-",round(np.std(angv),2))
        # print("***************************  RESULTS COMPUTING TIME ********************************************************")
        # print("Total time of execution (s) :                        ", str(round(t1 - t0,2))) 
        print("************************************************************************************************************")

        f3.close()
        f2.close()

        if(evaluate=='y'):
            fname_manual=idim+"_mM"+inpf
            if(procmode == 'supervised'):
                fname_auto="out_quantif_"+dirstr+"/"+idim+"_"+distr+"_superv_cell_mask"+outf
            else:
                fname_auto="out_quantif_"+dirstr+"/"+idim+"_"+distr+"_cell_mask_nb"+outf

            mininters=float(self.t53.get())
            modeval=self.t54.get()    
            amin=ff_areamin
            amax=99999999.
            lmin=sf_lboxmin
            lmax=sf_lboxmax
            wmin=sf_wmin
            wmax=sf_wmax
            permin=ff_permin
            f = open("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_evaluation_output.txt", 'w')
            f4 = open("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_autocoinc_data.txt", 'w')
            f4.write('ID,L(um),W(um),ang(degree),CxLat2,AreaBox(um2),Max Intersection\n')
            f5 = open("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_manucoinc_data.txt", 'w')
            f5.write('ID,L(um),W(um),ang(degree),CxLat2,AreaBox(um2),Max Intersection,CXTOT\n')
            print("************************************************************************************************************")
            print("This ouput has been generated on " + day +"th of " + month + " of year " + year + ", at local time:  " + time)
            print("************************************************************************************************************")
            print("******************   MARTA (Myocite Automatic Retrieval and Tissue Analyzer)   *****************************")
            print("************************************************************************************************************")
            print("*****************        2-MASK INTERSECTION-OBJECT EVALUATION     *****************************************")
            print("************************************************************************************************************")
            f.write("************************************************************************************************************\n")
            f.write("This ouput has been generated on " + day +"th of " + month + " of year " + year + ", at local time:  " + time+"\n")
            f.write("************************************************************************************************************\n")
            f.write("******************   MARTA (Myocite Automatic Retrieval and Tissue Analyzer)   *****************************\n") 
            f.write("************************************************************************************************************\n")
            f.write("*****************        2-MASK INTERSECTION-OBJECT EVALUATION     *****************************************\n")
            f.write("************************************************************************************************************\n")    
            iman = cv2.imread(fname_manual,0)
            imaut= cv2.imread(fname_auto,0)
            retm,binthrman = cv2.threshold(iman,200,255,cv2.THRESH_BINARY)
            retm,binthraut = cv2.threshold(imaut,200,255,cv2.THRESH_BINARY)
            contman, hierarchy = cv2.findContours(binthrman, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contauto, hierarchy = cv2.findContours(binthraut, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            lcnt=len(contman)
            Lboxv=[]
            Wboxv=[]
            boxc=[]
            Aboxv=[]
            areamanv=[]
            permanv=[]

            
            thresh, blackAndWhiteImage = cv2.threshold(iman, 0, 0, cv2.THRESH_BINARY)
            cv2.imwrite("blackback.tif",blackAndWhiteImage)
            img_contours = cv2.imread("blackback.tif")
            img_boxman= cv2.imread("blackback.tif")

            for j in range(0,len(contman)-1,1):
                areaman = cv2.contourArea(contman[j])*scale**2
                areamanv.append(areaman)
                perman = cv2.arcLength(contman[j],True)*scale
                permanv.append(perman)
                rect = cv2.minAreaRect(contman[j])
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                d01box=((box[0][0]-box[1][0])**2+(box[0][1]-box[1][1])**2)**0.5
                d12box=((box[1][0]-box[2][0])**2+(box[1][1]-box[2][1])**2)**0.5
                    
                Abox=d01box*d12box*scale**2
                Lbox=np.maximum(d01box,d12box)*scale
                Wbox=np.minimum(d01box,d12box)*scale
                if(Lbox > lmin) & (Lbox < lmax) & (areaman < amax) &(areaman> amin) &(perman>permin) &(Wbox<wmax)&(Wbox>wmin):
                    Lboxv.append(Lbox)
                    Aboxv.append(Abox)
                    Wboxv.append(Wbox)
                    boxc.append(box)
                    cv2.drawContours(img_contours, [box], 0, (255,0,0), 2)
                    cv2.drawContours(img_contours, contman[j], -1, (255, 255, 255), 2)
                    cv2.drawContours(img_boxman, [box], 0, (255,0,0), 2)
                    
            Lboxva=[]
            Wboxva=[]
            boxca=[]
            Aboxva=[]
            areautova=[]
            perautova=[]
            thresh, blackAndWhiteImage = cv2.threshold(iman, 0, 0, cv2.THRESH_BINARY)
            cv2.imwrite("blackback.tif",blackAndWhiteImage)
            img_contaut = cv2.imread("blackback.tif")
            img_boxauto= cv2.imread("blackback.tif")

            for j in range(0,len(contauto)-1,1):
                areauto = cv2.contourArea(contauto[j])*scale**2
                areautova.append(areauto)
                perauto = cv2.arcLength(contauto[j],True)*scale
                perautova.append(perauto)
                recta = cv2.minAreaRect(contauto[j])
                boxa = cv2.boxPoints(recta)
                boxa = np.int0(boxa)

                d01boxa=((boxa[0][0]-boxa[1][0])**2+(boxa[0][1]-boxa[1][1])**2)**0.5
                d12boxa=((boxa[1][0]-boxa[2][0])**2+(boxa[1][1]-boxa[2][1])**2)**0.5
                    
                Aboxa=d01boxa*d12boxa*scale**2
                Lboxa=np.maximum(d01boxa,d12boxa)*scale
                Wboxa=np.minimum(d01boxa,d12boxa)*scale
                if(Lboxa > lmin) & (Lboxa < lmax) & (areauto < amax) &(areauto> amin) &(perauto>permin) &(Wboxa<wmax)&(Wboxa>wmin):
                    Lboxva.append(Lboxa)
                    Wboxva.append(Wboxa)
                    boxca.append(boxa)
                    Aboxva.append(Aboxa)
                    cv2.drawContours(img_contours, [boxa], 0, (0,0,255), 2)
                    cv2.drawContours(img_contours, contauto[j], -1, (0, 255, 0), 1)
                    cv2.drawContours(img_boxauto, [boxa], 0, (0,0,255), -1)

            print("*********************************** INPUT PARAMETERS *****************************************************")
            print("**********************************************************************************************************")
            print('Scale:                                                   ',scale,' pixels/um')
            print('Filter of minimum Lenght:                                ',lmin,' um')
            print('Filter of maximum Lenght                                 ',lmax,' um')
            print('Filter of minimum area:                                  ',amin,' um')
            print('Filter of maximum area:                                  ',amax,' um')
            print('Filter of minimum perimeter:                             ',permin,' um')
            print('Filter of maximum width :                                ',wmax,' um')
            print('Filter of minimum width :                                ',wmin,' um')
            print("**********************************************************************************************************")
            print("*********************************** OUTPUTS : NON-FILTERED CONTOURS **************************************")
            print("**********************************************************************************************************")
            print('Total number of manual contours:                         ',len(contman))
            print('Total number of automatic contours:                      ',len(contauto))
            print('Average area of manual contoured features:               ',round(np.mean(areamanv),2),"+/-",round(np.std(areamanv),2),' um**2')
            print('Average area of automatic contoured features:            ',round(np.mean(areautova),2),"+/-",round(np.std(areautova),2),' um**2')
            print('Average perimeter of manual contoured features:          ',round(np.mean(permanv),2),"+/-",round(np.std(permanv),2),' um')
            print('Average perimeter of automatic contoured features:       ',round(np.mean(perautova),2),"+/-",round(np.std(perautova),2),' um')
            print("**********************************************************************************************************")
            print("*********************************** OUTPUTS : FILTERED CONTOURS ******************************************")
            print("**********************************************************************************************************")
            print('Filtered number of manual contours:                      ',len(Lboxv))
            print('Filtered number of automatic contours:                   ',len(Lboxva))
            print('Average lenght of filtered manual contoured features:    ',round(np.mean(Lboxv),2),"+/-",round(np.std(Lboxv),2),' um')
            print('Average lenght of filtered automatic contoured features: ',round(np.mean(Lboxva),2),"+/-",round(np.std(Lboxva),2),' um')
            print('Average Width of filtered manual contoured features:     ',round(np.mean(Wboxv),2),"+/-",round(np.std(Wboxv),2),' um')
            print('Average Width of filtered automatic contoured features:  ',round(np.mean(Wboxva),2),"+/-",round(np.std(Wboxva),2),' um')
            print('Average area of filtered manual box features:            ',round(np.mean(Aboxv),2),"+/-",round(np.std(Aboxv),2),' um**2')
            print('Average area of filtered automatic box features:         ',round(np.mean(Aboxva),2),"+/-",round(np.std(Aboxva),2),' um**2')
            print("**********************************************************************************************************")

            f.write("*********************************** INPUT PARAMETERS *****************************************************\n")
            f.write("**********************************************************************************************************\n")
            f.write('Scale:                                                 '+str(scale)+' pixels/um \n')
            f.write('Filter of minimum Lenght:                              '+str(lmin)+' um \n')
            f.write('Filter of maximum Lenght:                              '+str(lmax)+' um \n')
            f.write('Filter of minimum Width:                               '+str(wmin)+' um \n')
            f.write('Filter of maximum Width:                               '+str(wmax)+' um \n')
            f.write('Filter of minimum perimeter:                           '+str(permin)+' um \n')
            f.write('Filter of minimum area:                                '+str(amin)+' um**2 \n')
            f.write('Filter of maximum area:                                '+str(amax)+' um**2 \n')
            f.write("**********************************************************************************************************\n")
            f.write("*********************************** OUTPUTS : NON-FILTERED CONTOURS **************************************\n")
            f.write("**********************************************************************************************************\n")
            f.write('Total number of manual contours:                        '+str(len(contman))+'\n')
            f.write('Total number of automatic contours:                     '+str(len(contauto))+'\n')
            f.write('Average area of manual contoured features:              '+str(round(np.mean(areamanv),2))+"+/-"+str(round(np.std(areamanv),2))+' um**2 \n')
            f.write('Average area of automatic contoured features:           '+str(round(np.mean(areautova),2))+"+/-"+str(round(np.std(areautova),2))+' um**2 \n')
            f.write('Average perimeter of manual contoured features:         '+str(round(np.mean(permanv),2))+"+/-"+str(round(np.std(permanv),2))+'um \n')
            f.write('Average perimeter of automatic contoured features:      '+str(round(np.mean(perautova),2))+"+/-"+str(round(np.std(perautova),2))+' um \n')
            f.write("**********************************************************************************************************\n")
            f.write("*********************************** OUTPUTS : FILTERED CONTOURS ******************************************\n")
            f.write("**********************************************************************************************************\n")
            f.write('Filtered number of manual contours:                      '+str(len(Lboxv))+'  \n')
            f.write('Filtered number of automatic contours:                   '+str(len(Lboxva))+' \n')
            f.write('Average lenght of filtered manual contoured features:    '+str(round(np.mean(Lboxv),2))+"+/-"+str(round(np.std(Lboxv),2))+' um \n')
            f.write('Average lenght of filtered automatic contoured features: '+str(round(np.mean(Lboxva),2))+"+/-"+str(round(np.std(Lboxva),2))+' um \n')
            f.write('Average Width of filtered manual contoured features:     '+str(round(np.mean(Wboxv),2))+"+/-"+str(round(np.std(Wboxv),2))+' um \n')
            f.write('Average Width of filtered automatic contoured features:  '+str(round(np.mean(Wboxva),2))+"+/-"+str(round(np.std(Wboxva),2))+' um \n')
            f.write('Average area of filtered manual box features:            '+str(round(np.mean(Aboxv),2))+"+/-"+str(round(np.std(Aboxv),2))+' um**2 \n')
            f.write('Average area of filtered automatic box features:         '+str(round(np.mean(Aboxva),2))+"+/-"+str(round(np.std(Aboxva),2))+' um**2 \n')
            f.write("**********************************************************************************************************\n")

            if(scalebars=='y'):
                cv2.drawContours(img_contours,[scbar],-1,(255,255,255),-1)      
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_Mm_Ma_cont"+outf,img_contours)

            redb=[]
            greenb=[]
            relint=[]

            for i in range(0,len(boxc)-1,1):
                imexample = cv2.imread("blackback.tif",0)
                example=boxc[i];
                areaexample=cv2.contourArea(example)

                xmin=np.min((example[0][0],example[1][0],example[2][0],example[3][0]))
                xmax=np.max((example[0][0],example[1][0],example[2][0],example[3][0]))
                ymin=np.min((example[0][1],example[1][1],example[2][1],example[3][1]))
                ymax=np.max((example[0][1],example[1][1],example[2][1],example[3][1]))

                cv2.drawContours(imexample, [example], 0, (255,0,0), -1)

                intersec=[]
                for j in range(0,len(boxca)-1,1):
                    imloop = cv2.imread("blackback.tif",0)
                    boxcap=boxca[j]
                    areaboxcap=cv2.contourArea(boxcap)
                    
                    xmin2=np.min((boxcap[0][0],boxcap[1][0],boxcap[2][0],boxcap[3][0]))
                    xmax2=np.max((boxcap[0][0],boxcap[1][0],boxcap[2][0],boxcap[3][0]))
                    ymin2=np.min((boxcap[0][1],boxcap[1][1],boxcap[2][1],boxcap[3][1]))
                    ymax2=np.max((boxcap[0][1],boxcap[1][1],boxcap[2][1],boxcap[3][1]))

                    xmin3=np.min((xmin,xmin2))
                    xmax3=np.max((xmax,xmax2))
                    ymin3=np.min((ymin,ymin2))
                    ymax3=np.max((ymax,ymax2))

                    autsubr3=imloop[ymin3:ymax3,xmin3:xmax3]
                    mansubr3=imexample[ymin3:ymax3,xmin3:xmax3]
                    mansubr=imexample[ymin:ymax,xmin:xmax]
                    autosubr2=imloop[ymin2:ymax2,xmin2:xmax2]
                    
                    cv2.drawContours(imloop, [boxcap], 0, (255,0,0), -1)
                           
                    intsec=cv2.bitwise_and(autsubr3,mansubr3)
                    area1=np.count_nonzero(cv2.bitwise_and(mansubr, mansubr))
                    area2=np.count_nonzero(cv2.bitwise_and(autosubr2,autosubr2))
                    if(modeval=='max'):
                        intersec.append(np.count_nonzero(intsec)/np.max((area1,area2))*100)
                    else:
                        intersec.append(np.count_nonzero(intsec)/(area2+0.00001)*100)
                        
                boxmaxint_index=np.argmax(intersec)
                boxmaxint=boxca[boxmaxint_index]

                if(np.max(intersec)>mininters):
                    relint.append(np.max(intersec))
                    greenb.append(boxmaxint)
                    box=boxmaxint
                    d01box=((box[0][0]-box[1][0])**2+(box[0][1]-box[1][1])**2)**0.5
                    d12box=((box[1][0]-box[2][0])**2+(box[1][1]-box[2][1])**2)**0.5
                    if np.minimum(d01box,d12box) == d01box:
                        x0=box[0][0]
                        x1=box[1][0]
                        y0=box[0][1]
                        y1=box[1][1]
                        x2=box[2][0]
                        y2=box[2][1]
                        x3=box[3][0]
                        y3=box[3][1]
                        x4=int(round((x0+x1)/2))
                        y4=int(round((y0+y1)/2))
                        x5=int(round((x1+x2)/2))
                        y5=int(round((y1+y2)/2))
                        x6=int(round((x2+x3)/2))
                        y6=int(round((y2+y3)/2))
                        x7=int(round((x3+x0)/2))
                        y7=int(round((y3+y0)/2))
                        x8=int(round((x4+x0)/2))
                        y8=int(round((y4+y0)/2))
                        x9=int(round((x4+x1)/2))
                        y9=int(round((y4+y1)/2))        
                        x10=int(round((x5+x1)/2))
                        y10=int(round((y5+y1)/2))
                        x11=int(round((x5+x2)/2))
                        y11=int(round((y5+y2)/2))
                        x12=int(round((x6+x2)/2))
                        y12=int(round((y6+y2)/2))
                        x13=int(round((x6+x3)/2))
                        y13=int(round((y6+y3)/2))
                        x14=int(round((x7+x3)/2))
                        y14=int(round((y7+y3)/2))
                        x15=int(round((x7+x0)/2))
                        y15=int(round((y7+y0)/2))        
                    else:
                        x0=box[1][0]
                        x1=box[2][0]
                        y0=box[1][1]
                        y1=box[2][1]
                        x2=box[3][0]
                        y2=box[3][1]
                        x3=box[0][0]
                        y3=box[0][1]
                        x4=int(round((x0+x1)/2))
                        y4=int(round((y0+y1)/2))
                        x5=int(round((x1+x2)/2))
                        y5=int(round((y1+y2)/2))
                        x6=int(round((x2+x3)/2))
                        y6=int(round((y2+y3)/2))
                        x7=int(round((x3+x0)/2))
                        y7=int(round((y3+y0)/2))
                        x8=int(round((x4+x0)/2))
                        y8=int(round((y4+y0)/2))
                        x9=int(round((x4+x1)/2))
                        y9=int(round((y4+y1)/2))        
                        x10=int(round((x5+x1)/2))
                        y10=int(round((y5+y1)/2))
                        x11=int(round((x5+x2)/2))
                        y11=int(round((y5+y2)/2))
                        x12=int(round((x6+x2)/2))
                        y12=int(round((y6+y2)/2))
                        x13=int(round((x6+x3)/2))
                        y13=int(round((y6+y3)/2))
                        x14=int(round((x7+x3)/2))
                        y14=int(round((y7+y3)/2))
                        x15=int(round((x7+x0)/2))
                        y15=int(round((y7+y0)/2)) 

        # Application of a padding to the rectangle 

                    d13=((x0-x2)**2+(y0-y2)**2)**0.5
                    d24=((x1-x3)**2+(y1-y3)**2)**0.5
                    
                    xn1=np.copy(x0)
                    xn2=np.copy(x1)
                    xn3=np.copy(x2)
                    xn4=np.copy(x3)
                                        
                    yn1=np.copy(y0)
                    yn2=np.copy(y1)
                    yn3=np.copy(y2)
                    yn4=np.copy(y3)
                                                                       
                    x0=xn1-int(round(pad*(xn3-xn1)/d13))
                    x1=xn2-int(round(pad*(xn4-xn2)/d24))
                    y0=yn1-int(round(pad*(yn3-yn1)/d13))
                    y1=yn2-int(round(pad*(yn4-yn2)/d24))
                                        
                    x2=xn3+int(round(pad*(xn3-xn1)/d13))
                    y2=yn3+int(round(pad*(yn3-yn1)/d13))
                    x3=xn4+int(round(pad*(xn4-xn2)/d24))
                    y3=yn4+int(round(pad*(yn4-yn2)/d24))
                    
        # Computing lenght of paded rectangle (extended in long axis direction)
                    expbox1=((x0-x1)**2+(y0-y1)**2)**0.5
                    expbox2=((x1-x2)**2+(y1-y2)**2)**0.5
                    
        # Computing the coordinates range of the box             
                    xmaxb=np.max((x0,x1,x2,x3))
                    ymaxb=np.max((y0,y1,y2,y3))
                    xminb=np.min((x0,x1,x2,x3))
                    yminb=np.min((y0,y1,y2,y3))
                    
        # Split CM box into 4 equal parts            
                    rec1=np.array([[x0,y0],[x1,y1],[x10,y10],[x15,y15]])
                    rec2=np.array([[x15,y15],[x10,y10],[x5,y5],[x7,y7]])
                    rec3=np.array([[x7,y7],[x5,y5],[x11,y11],[x14,y14]])
                    rec4=np.array([[x14,y14],[x11,y11],[x2,y2],[x3,y3]])  


        # Draw a background image 
                    thresh, blackAndWhiteImage = cv2.threshold(cv2.imread(fname_c1,0), 0, 0, cv2.THRESH_BINARY)
                    cv2.imwrite("blacksub"+outf,blackAndWhiteImage)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    
        # Compute an intersection between c2 channel and partitioned rectangles
                    r0fig=cv2.drawContours(imgblack,[rec1],0,(255,255,255),-1)
                    int0=cv2.bitwise_and(r0fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp0=np.count_nonzero(int0)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r1fig=cv2.drawContours(imgblack,[rec2],0,(255,255,255),-1)
                    int1=cv2.bitwise_and(r1fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp1=np.count_nonzero(int1)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r2fig=cv2.drawContours(imgblack,[rec3],0,(255,255,255),-1)
                    int2=cv2.bitwise_and(r2fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp2=np.count_nonzero(int2)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r3fig=cv2.drawContours(imgblack,[rec4],0,(255,255,255),-1)
                    int3=cv2.bitwise_and(r3fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp3=np.count_nonzero(int3)
                    
        # Compute the proportions of c2 relative to each compartment          
                    p0=nwp0/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p1=nwp1/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p2=nwp2/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p3=nwp3/(nwp0+nwp1+nwp2+nwp3+0.001)*100  
                    
        # Compute the lenghts and widths of CMs (lenghts as average of extended and non extended rectangle)
                    Lbox0=np.maximum(d01box,d12box)*scale
                    Lbox1=np.maximum(expbox1,expbox2)*scale
                    Lbox=(Lbox0+Lbox1)*0.5
                    Wbox=np.minimum(d01box,d12box)*scale
                    Abox=Lbox*Wbox
                    f4.write(str(round(Lbox,2))+','+str(round(Wbox,2))+','+str(round((p1+p2)*100/(p0+p3+p1+p2+0.001),2))+','+str(round(Abox,2))+','+str(round(area,2))+','+str(round(perimeter,2))+','+str(round(np.max(intersec)))+'\n')

                    box=example
                    d01box=((box[0][0]-box[1][0])**2+(box[0][1]-box[1][1])**2)**0.5
                    d12box=((box[1][0]-box[2][0])**2+(box[1][1]-box[2][1])**2)**0.5
                    if np.minimum(d01box,d12box) == d01box:
                        x0=box[0][0]
                        x1=box[1][0]
                        y0=box[0][1]
                        y1=box[1][1]
                        x2=box[2][0]
                        y2=box[2][1]
                        x3=box[3][0]
                        y3=box[3][1]
                        x4=int(round((x0+x1)/2))
                        y4=int(round((y0+y1)/2))
                        x5=int(round((x1+x2)/2))
                        y5=int(round((y1+y2)/2))
                        x6=int(round((x2+x3)/2))
                        y6=int(round((y2+y3)/2))
                        x7=int(round((x3+x0)/2))
                        y7=int(round((y3+y0)/2))
                        x8=int(round((x4+x0)/2))
                        y8=int(round((y4+y0)/2))
                        x9=int(round((x4+x1)/2))
                        y9=int(round((y4+y1)/2))        
                        x10=int(round((x5+x1)/2))
                        y10=int(round((y5+y1)/2))
                        x11=int(round((x5+x2)/2))
                        y11=int(round((y5+y2)/2))
                        x12=int(round((x6+x2)/2))
                        y12=int(round((y6+y2)/2))
                        x13=int(round((x6+x3)/2))
                        y13=int(round((y6+y3)/2))
                        x14=int(round((x7+x3)/2))
                        y14=int(round((y7+y3)/2))
                        x15=int(round((x7+x0)/2))
                        y15=int(round((y7+y0)/2))        
                    else:
                        x0=box[1][0]
                        x1=box[2][0]
                        y0=box[1][1]
                        y1=box[2][1]
                        x2=box[3][0]
                        y2=box[3][1]
                        x3=box[0][0]
                        y3=box[0][1]
                        x4=int(round((x0+x1)/2))
                        y4=int(round((y0+y1)/2))
                        x5=int(round((x1+x2)/2))
                        y5=int(round((y1+y2)/2))
                        x6=int(round((x2+x3)/2))
                        y6=int(round((y2+y3)/2))
                        x7=int(round((x3+x0)/2))
                        y7=int(round((y3+y0)/2))
                        x8=int(round((x4+x0)/2))
                        y8=int(round((y4+y0)/2))
                        x9=int(round((x4+x1)/2))
                        y9=int(round((y4+y1)/2))        
                        x10=int(round((x5+x1)/2))
                        y10=int(round((y5+y1)/2))
                        x11=int(round((x5+x2)/2))
                        y11=int(round((y5+y2)/2))
                        x12=int(round((x6+x2)/2))
                        y12=int(round((y6+y2)/2))
                        x13=int(round((x6+x3)/2))
                        y13=int(round((y6+y3)/2))
                        x14=int(round((x7+x3)/2))
                        y14=int(round((y7+y3)/2))
                        x15=int(round((x7+x0)/2))
                        y15=int(round((y7+y0)/2)) 

        # Application of a padding to the rectangle 

                    d13=((x0-x2)**2+(y0-y2)**2)**0.5
                    d24=((x1-x3)**2+(y1-y3)**2)**0.5
                    
                    xn1=np.copy(x0)
                    xn2=np.copy(x1)
                    xn3=np.copy(x2)
                    xn4=np.copy(x3)
                                        
                    yn1=np.copy(y0)
                    yn2=np.copy(y1)
                    yn3=np.copy(y2)
                    yn4=np.copy(y3)
                                                                       
                    x0=xn1-int(round(pad*(xn3-xn1)/d13))
                    x1=xn2-int(round(pad*(xn4-xn2)/d24))
                    y0=yn1-int(round(pad*(yn3-yn1)/d13))
                    y1=yn2-int(round(pad*(yn4-yn2)/d24))
                                        
                    x2=xn3+int(round(pad*(xn3-xn1)/d13))
                    y2=yn3+int(round(pad*(yn3-yn1)/d13))
                    x3=xn4+int(round(pad*(xn4-xn2)/d24))
                    y3=yn4+int(round(pad*(yn4-yn2)/d24))
                    
        # Computing lenght of paded rectangle (extended in long axis direction)
                    expbox1=((x0-x1)**2+(y0-y1)**2)**0.5
                    expbox2=((x1-x2)**2+(y1-y2)**2)**0.5
                    
        # Computing the coordinates range of the box             
                    xmaxb=np.max((x0,x1,x2,x3))
                    ymaxb=np.max((y0,y1,y2,y3))
                    xminb=np.min((x0,x1,x2,x3))
                    yminb=np.min((y0,y1,y2,y3))
                    
        # Split CM box into 4 equal parts            
                    rec1=np.array([[x0,y0],[x1,y1],[x10,y10],[x15,y15]])
                    rec2=np.array([[x15,y15],[x10,y10],[x5,y5],[x7,y7]])
                    rec3=np.array([[x7,y7],[x5,y5],[x11,y11],[x14,y14]])
                    rec4=np.array([[x14,y14],[x11,y11],[x2,y2],[x3,y3]])  


        # Draw a background image 
                    thresh, blackAndWhiteImage = cv2.threshold(cv2.imread(fname_c1,0), 0, 0, cv2.THRESH_BINARY)
                    cv2.imwrite("blacksub"+outf,blackAndWhiteImage)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    
        # Compute an intersection between c2 channel and partitioned rectangles
                    r0fig=cv2.drawContours(imgblack,[rec1],0,(255,255,255),-1)
                    int0=cv2.bitwise_and(r0fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp0=np.count_nonzero(int0)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r1fig=cv2.drawContours(imgblack,[rec2],0,(255,255,255),-1)
                    int1=cv2.bitwise_and(r1fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp1=np.count_nonzero(int1)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r2fig=cv2.drawContours(imgblack,[rec3],0,(255,255,255),-1)
                    int2=cv2.bitwise_and(r2fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp2=np.count_nonzero(int2)
                    imgblack = cv2.imread("blacksub"+outf,0)
                    r3fig=cv2.drawContours(imgblack,[rec4],0,(255,255,255),-1)
                    int3=cv2.bitwise_and(r3fig[yminb:ymaxb,xminb:xmaxb],imgcxb2[yminb:ymaxb,xminb:xmaxb])
                    nwp3=np.count_nonzero(int3)
                    
        # Compute the proportions of c2 relative to each compartment          
                    p0=nwp0/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p1=nwp1/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p2=nwp2/(nwp0+nwp1+nwp2+nwp3+0.001)*100
                    p3=nwp3/(nwp0+nwp1+nwp2+nwp3+0.001)*100  
                    
        # Compute the lenghts and widths of CMs (lenghts as average of extended and non extended rectangle)
                    Lbox0=np.maximum(d01box,d12box)*scale
                    Lbox1=np.maximum(expbox1,expbox2)*scale
                    Lbox=(Lbox0+Lbox1)*0.5
                    Wbox=np.minimum(d01box,d12box)*scale
                    Abox=Lbox*Wbox
                    f5.write(str(round(Lbox,2))+','+str(round(Wbox,2))+','+str(round((p1+p2)*100/(p0+p3+p1+p2+0.001),2))+','+str(round(Abox,2))+','+str(round(area,2))+','+str(round(perimeter,2))+','+str(round(np.max(intersec)))+'\n')                                 
                else:
                    redb.append(boxmaxint)
                    
            for j in range(0,len(greenb),1):
                cv2.drawContours(img_boxman, [greenb[j]], 0, (0,0,255), 2)

            if(scalebars=='y'):
                cv2.drawContours(img_boxman,[scbar],-1,(255,255,255),-1)      
            cv2.imwrite("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_MaxAnd"+outf,img_boxman)
            print("******************************* STATISTICAL PARAMETERS OF MAX-INTERSECTION *******************************")
            print("**********************************************************************************************************")
            print('Minimum intersection (%):                                  ',round(np.min(relint),1))
            print("Percentile 10,20,30,40,60,70,80,90:                        ",round(np.percentile(relint,10),1),round(np.percentile(relint,20),1),round(np.percentile(relint,30),1),round(np.percentile(relint,40),1),round(np.percentile(relint,60),1),round(np.percentile(relint,70),1),round(np.percentile(relint,80),1),round(np.percentile(relint,90),1))
            print('Maximum intersection (%):                                  ',round(np.max(relint),1))
            print('Average intersection (%):                                  ',round(np.mean(relint),1),"+/-",round(np.std(relint),1))
            print("median:                                                    ",round(np.median(relint),1))
            print("**********************************************************************************************************")
            print("**********************************************************************************************************")

            f.write("******************************* STATISTICAL PARAMETERS OF MAX-INTERSECTION *******************************\n")
            f.write("**********************************************************************************************************\n")
            f.write('Minimum intersection (%):                              '+str(round(np.min(relint),1))+'\n')
            f.write("Percentile 10,20,30,40,60,70,80,90:                    "+str(round(np.percentile(relint,10),1))+','+str(round(np.percentile(relint,20),1))+','+str(round(np.percentile(relint,30),1))+','+str(round(np.percentile(relint,40),1))+','+str(round(np.percentile(relint,60),1))+','+str(round(np.percentile(relint,70),1))+','+str(round(np.percentile(relint,80),1))+','+str(round(np.percentile(relint,90),1))+'\n')
            f.write('Maximum intersection (%):                              '+str(round(np.max(relint),1))+'\n')
            f.write('Average intersection (%):                              '+str(round(np.mean(relint),1))+"+/-"+str(round(np.std(relint),1))+'\n')
            f.write("**********************************************************************************************************\n") 
            f.write("******************************* STATISTICAL PERCENTILE LIST **********************************************\n")
            f.write("**********************************************************************************************************\n")
            # COMPUTING PERCENTILE PLOTS
            percentlist=[]
            xdata=[]
            for i in range(0,100,1):
                percentlist.append(np.percentile(relint,i))
                xdata.append(i)
                f.write(str(i)+","+str(round(np.percentile(relint,i),1))+'\n')
            auc = np.trapz(percentlist,xdata)
            auc/100
 
            plt.figure(figsize=(15, 10))
            plt.plot(xdata,percentlist);
            # Add title and axis names

            plt.ylabel('Pc(k)', fontsize=18, family="serif")
            plt.xlabel('k' , fontsize=18, family="serif")
            plt.text(90, 0, "AUC="+str(round(auc/10000,1)), family="serif", fontsize=18,bbox=dict(facecolor='red', alpha=0.5));
            plt.tick_params(direction='in', length=5, width=3, grid_alpha=0.5, labelsize=18)
            plt.savefig("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_percentileplot"+outf)

            nb50=0
            nb60=0
            nb70=0
            nb80=0

            for j in range(0,len(relint),1):
                if(relint[j]>50):
                    nb50=nb50+1
                if(relint[j]>60):
                    nb60=nb60+1
                if(relint[j]>70):
                    nb70=nb70+1
                if(relint[j]>80):
                    nb80=nb80+1
            f.write("**********************************************************************************************************\n")
            f.write("**********************************************************************************************************\n")
            f.write("AUC percentile curve:                                    "+str(round(auc/100,1))+'\n')
            f.write('Number of cases with > 50% of intersection:              '+str(nb50)+'('+str(round(nb50/len(relint)*100,1))+' %)'+'\n')
            f.write('Number of cases with > 60% of intersection:              '+str(nb60)+'('+str(round(nb60/len(relint)*100,1))+' %)'+'\n')
            f.write('Number of cases with > 70% of intersection:              '+str(nb70)+'('+str(round(nb70/len(relint)*100,1))+' %)'+'\n')
            f.write('Number of cases with > 80% of intersection:              '+str(nb80)+'('+str(round(nb80/len(relint)*100,1))+' %)'+'\n')
            f.write("**********************************************************************************************************\n")
            f.write("**********************************************************************************************************\n")

            # Statistical analysis plots
            fig = plt.figure() 
            # define subplots 
            plt1 = fig.add_subplot(221) 
            plt2 = fig.add_subplot(222) 
            plt3 = fig.add_subplot(223) 
            plt4 = fig.add_subplot(224)
            plt1.hist(relint, bins=10) 
            plt1.set_title('Intersection') 
            plt2.hist(Aboxv,alpha=0.5, label='manual')
            plt2.hist(Aboxva,alpha=0.5, label='auto')
            plt2.set_title('Area')
            plt2.legend(loc='best',prop={'size': 6})
            plt3.hist(Lboxv,alpha=0.5, label='manual')
            plt3.hist(Lboxva,alpha=0.5, label='auto')
            plt3.set_title('Lenght')
            plt3.legend(loc='best',prop={'size': 6})
            plt4.hist(Wboxv,alpha=0.5, label='manual')
            plt4.hist(Wboxva,alpha=0.5, label='auto')
            plt4.set_title('Width')
            plt4.legend(loc='best',prop={'size': 6})
            # Space between subplots 
            fig.subplots_adjust(hspace=.5,wspace=0.5) 
            plt.savefig("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_evalhistplot"+outf,dpi=200)

            # create a figure 
            fig2 = plt.figure() 
            # define subplots 
            plt5 = fig2.add_subplot(221) 
            plt6 = fig2.add_subplot(222) 
            plt7 = fig2.add_subplot(223) 
            plt8 = fig2.add_subplot(224) 
            plt5.boxplot(relint,patch_artist=True,labels=['I(%)']) 
            plt5.set_title('Intersection') 
            plt6.boxplot([Aboxv,Aboxva],patch_artist=True,labels=['Manual','Auto'])
            plt6.set_title('Area') 
            plt7.boxplot([Lboxv,Lboxva],patch_artist=True,labels=['Manual','Auto'])
            plt7.set_title('Lenght') 
            plt8.boxplot([Wboxv,Wboxva],patch_artist=True,labels=['Manual','Auto'])
            plt8.set_title('Width')
            
            # Space between subplots 
            fig2.subplots_adjust(hspace=.5,wspace=0.5) 
            plt.savefig("out_quantif_"+dirstr+"/"+idim+"_"+distr+"_evalboxplot"+outf,dpi=200)

            t1 = tm.localtime()

            print("***************************  RESULTS COMPUTING TIME ****************************************")
            print("Total time of execution (s) : ",                           str(round(t1 - t0,2))) 
            print("********************************************************************************************")

            f.write("**********************************************************************************************************\n")
            f.write("Total time of execution (s) :                            "+str(round(t1 - t0,2))+'\n') 
            f.write("**********************************************************************************************************\n")
            f.close()
            f4.close()
            f5.close()

            return
        else:
            return
    
window=Tk()
mywin=MyWindow(window)
window.title('Myocite Automatic Retrieval and Tissue Analysis (MARTA) with preview')
window.geometry("1680x1100+10+10")
window.mainloop()
