------------------------------------------------------------------------------
Capgemini Hackathon
------------------------------------------------------------------------------

This is Siddharth Nishtala's solution to the Capgemini Data Science Hackathon.
Find out more about it on:

https://techchallenge.in.capgemini.com/techchallenge/data-science

------------------------------------------------------------------------------
Instructions to run the project
------------------------------------------------------------------------------
1. Install the dependencies - NumPy, Pandas and Keras.
2. Change directory to '/CapgeminiHackathon/src'.
3. Run the 'main.py' script in the src folder (Python 3).

------------------------------------------------------------------------------
Results
------------------------------------------------------------------------------
All the variables are printed on the console before the simulation begins.

The number of billable resources and benched resources are then printed on the console.

The following metrics for the model are calculated using a test data set and printed.
TESTING ACCURACY:
                ACCURACY = (NUMBER OF CORRECTLY PREDICTED JOBS * 100) / TOTAL NUMBER OF JOBS

TESTING OPTIMISM:
                OPTIMISM = (NUMBER OF PREDICTED JOBS * 100) / NUMBER OF JOBS

The details and analysis of each of the 12 months is then printed on the console. These monthly results are also printed in a .csv format in the 'results' folder as 'Details - Year.csv' and 'Analysis - Year.csv'.
The skill sets of each employee that is billable, benched, resigning or that are to be hired are saved as files in the 'results' folder. This is done month-wise.

The final results that summarise the complete simulation are then printed on the console.

Two sets of metrics are provided for assessing 'Total Business Captured':

JAN - DEC : The assumption is that no new hires join the company in January and February as no information is given about the same. As hiring takes 2 months, first set of new hires join in March.
MAR - DEC : These represent the statistics after the new hires start joining the company. These new hires will go on to replace resigning billable employees and new demand.


