# GoCalc\
## Go (board game) AI\
\
Trying to bring visualization and human understanding to AI.\
Primary external libraries used:  kivy, tensorflow, keras, numpy, pandas, and matplotlib.\
\
Most recent pic/vid of work-in-progress (older pics/vids below):\
(demo of game board interface, 2021-01-03)\
![](readme_vid01.gif)\
\
Basic layout of user interface is constructed.  Each horizontal panel will represent a prediction model.\
Each prediction model panel will have a display section and an interface section.  The displays are for\
board related visuals.  The interfaces are for the options that each model provides.\
\
First model under construction is influence_model.  The purpose is to give each empty position on the\
board a score representing which color will likely claim that empty position as a point.\
\
Long term plans is to include a dashboard for more detailed statistical analysis of the models and their\
calculations.\
\
## past pics/vids...\
\
(calculating stone influence per empty position in each predicted move, 2020-12-31)\
![](readme_pic01.PNG)\