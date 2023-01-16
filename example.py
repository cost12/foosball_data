#https://towardsdatascience.com/generate-sports-rankings-with-data-science-4dd1979571da

# Importing packages
import numpy as np
import pandas as pd

# Reading 'teams' and 'scores' data
teams = pd.read_csv('teams.txt', header = None)
num_of_teams = len(teams.index)
data = pd.read_csv('scores.txt', header = None)

# Initializing Colley Matrix 'c'and vector 'b'
c = np.zeros([num_of_teams, num_of_teams])
b = np.zeros(num_of_teams)

# Iterating through rows and populating Colley matrix values
for index, row in data.iterrows():
    t1 = row[2]
    t2 = row[5]
        
    c[(t1-1)][(t1-1)] += 1 # Updating diagonal element
    c[(t2-1)][(t2-1)] += 1 # Updating diagonal element
    c[(t1-1)][(t2-1)] -= 1 # Updating off - diagonal element
    c[(t2-1)][(t1-1)] -= 1 # Updating off - diagonal element
    
    # Updating vecotr b based on result of each game
    if row[4] > row[7]:
        b[(t1-1)] += 1
        b[(t2-1)] -= 1
    elif row[4] < row[7]:
        b[(t1-1)] -= 1
        b[(t2-1)] += 1

# Adding 2 to diagonal elements (total number of games) of Colley matrix
diag = c.diagonal() + 2
np.fill_diagonal(c, diag)
# Dividing by 2 and adding one to vector b
for i, value in enumerate(b):
    b[i] = b[i] / 2
    b[i] += 1

# Solving N variable linear equation
r = np.linalg.solve(c, b)

# Displaying ranking for top 4 teams
top_teams = r.argsort()[-4:][::-1]
for i in top_teams:
    print (str(r[i]) + " " + str(teams.iloc[i][1]))