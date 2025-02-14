# MARTA (Myocyte Automatic Retrieval and Tissue Analyzer)

This program algorithms are fully described in the next publication:

Oliver-Gelabert, A.; García-Mendívil, L.; Vallejo-Gil, J.M.; Fresneda-Roldán, P.C.; Andelová, K.; Fañanás-Mastral, J.; Vázquez-Sancho, M.; Matamala-Adell, M.; Sorribas-Berjón, F.; Ballester-Cuenca, C.; Tribulova, N.; Ordovás, L.; Raúl Diez, E.; Pueyo, E. Automatic Quantification of Cardiomyocyte Dimensions and Connexin 43 Lateralization in Fluorescence Images. *Biomolecules* **2020**, *10*, 1334.

DOI: https://doi.org/10.3390/biom10091334

### File Description:

* MARTA_win.exe is the program to run on Windows OS (tested in Windows 10 64-bit succesfully). Same as MARTA_v3.exe in [video demonstration](https://www.youtube.com/playlist?list=PLxAhyI5uMABUJHDdJXx7utR3qqDxmYjzf).
* MARTA_linux is the program to run on Linux OS (tested in Ubuntu 64-bit). How to download & run from command line (Linux):

> 1. git clone https://github.com/tonibois/MARTA
> 2. chmod 777 -R MARTA_linux
> 3. ./MARTA_linux

* a_c1.tif is a SERCA channel of sample a, pocessed together with a_c2.tif and a_c3.tif
* a_c2.tif is a CX43 channel of sample a, pocessed together with a_c1.tif and a_c3.tif
* a_c3.tif is WGA channel of sample a, pocessed together with a_c1.tif and a_c2.tif
* e.tif a MERGED image of two channels (F-Actin and Cx43)
* Parameters_e_default.png is a snapchot of the default parameters set to process image "e" when running main program MARTA_win.exe
![A test image](Parameters_e_default.png)

* Parameters_a.png is a snapchot of the parameter configuration that must be set to process "a" for automated mode processing (a_c1.tif, a_c2.tif and a_c3.tif)

### To run from source 

* It's mandatory to have installed python 3 and required python libraries (i.e. tkinter, OpenCV2, matplotlib, numpy, warnings...)
* From CLI on the path where the source file MARTA_source.py is located, just type "python MARTA_source.py"
