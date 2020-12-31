# GoCalc

Go (board game) AI

Trying to bring visualization and human understanding to AI.
Primary external libraries used:  kivy, tensorflow, keras, numpy, pandas, and matplotlib.

Most recent pic/vid of work-in-progress:
(calculating stone influence per empty position in each predicted move, 2020-12-31)
![Screenshot](readme_pic01.PNG)

First model under construction is influence_model.  The purpose is to give each empty position on the
board a score representing which color will likely claim that empty position as a point.