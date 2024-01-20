Steps to run program:
1.  Install python 3.11.7 and add to the environment path
2.  Go to the root folder of the repository
3.  Install the dependencies
```
python3 -m pip install -r requirements.txt
```

4.  Set up the folder with the data from RI. In this example, the folder is RI_Data.
5.  Locate the execution date and the user you want to analyse.
6.  Run the main program. The arguments of the program are (You can check running "python3 main.py --h"):
    -   (Required) user : The user you want to analyse
    -   (Required) date : The date of the analysis
    -   (Optional) read_oculus : 0 if your data is on the device 1 if your data is on the Oculus Quest Storage
    -   (Optional) directory : Define the directory with the RI Data

Example of an execution with user: default ; date: 20231226_204637 ; read_oculus : 0 ; directory : RI_Data

```
python3 .\Scripts\main.py --user default --date 20231226_204637 --read_oculus 0 --directory RI_Data
```

This will generate a new folder Output_fatigue with the results for the analysis.