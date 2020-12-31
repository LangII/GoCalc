# GoCalc

Go (board game) AI



Trying to bring visualization and human understanding to AI.
Primary external libraries used:  kivy, tensorflow, keras, numpy, pandas, and matplotlib.



![Screenshot](readme_pic01.PNG)
(calculating stone influence per empty position in each predicted move)



First model under construction is influence_model.  The purpose is to give each empty position on the
board a score representing which color will likely claim that empty position as a point.