import pandas as pd
import itertools
import openpyxl

# importing season total scores
response = False
while response == False:
    print('a) 2020/2021')
    print('b) 2021/2022')
    print('c) 2022/2023')
    print('d) 2023/2024')
    pickSeason = input("Pick the letter for your desired season: ")
    if pickSeason == 'a' or pickSeason == 'A':
        season = '2020to2021'
        response = True
    elif pickSeason == 'b' or pickSeason == 'B':
        season = '2021to2022'
        response = True
    elif pickSeason == 'c' or pickSeason == 'C':
        season = '2022to2023'
        response = True
    elif pickSeason == 'd' or pickSeason == 'D':
        season = '2023to2024'
        response = True
    else:
        print('Please choose a valid letter!')
        print()


csv = season + '\\cleaned_players.csv'
allPlayers = pd.read_csv(csv)
names = allPlayers.loc[:, ['first_name', 'second_name']]

# importing game week scores
gameWeek = False
while gameWeek == False:
    week = input("Enter the game week (1-38): ")
    if int(week) >= 1 and int(week) <= 38:
        gameWeek = True
    else:
        print('Pick a valid game week!')
        print()


csv2 = season + '/gw' + str(week) + '.csv'  

# pull out relevant values: 'name', 'position', 'team', total_points' from gameweek
gw = pd.read_csv(csv2)
gwGrouped = gw.loc[:, ['name', 'team', 'total_points']] 

# Merge duplicate names and scores for gameweek
gwRevised = gwGrouped.groupby(['name', 'team'], as_index=False)['total_points'].sum()

# combining 'first_name' and 'second_name' columns into 'name' column for season total df
names_str = []
for index, row in names.iterrows():
    names_str.append(row['first_name'] + ' ' + row['second_name'])


namesToFrame = {'name': names_str}
namesFrame = pd.DataFrame(namesToFrame)
otherThings = allPlayers.loc[:, ['total_points', 'element_type']]
playerFrame = pd.concat([namesFrame, otherThings], axis = 1)
positions = playerFrame.loc[:, 'element_type']

# helper function 1
def helper1(x):
    x.append({'name': playerFrame.loc[index, 'name'], 
    'position': playerFrame.loc[index, 'element_type'],
    'season_points': playerFrame.loc[index, 'total_points']})


# empty lists to fill in loop
dataForwards = []
dataMidfielders = []
dataDefenders = []
dataGoalkeepers = []

# loop sorts positions with "if position == ..." and uses the index of position to extract 
# corresponding elements of the playerFrame DataFrame ('name', 'position', 'total_points).
# The elements are placed together into one list element of data*Position*. 
for index, position in enumerate(positions):
    if position == 'FWD':
        helper1(dataForwards)
    elif position == 'MID':
        helper1(dataMidfielders)
    elif position == 'DEF':
        helper1(dataDefenders)
    else:
        helper1(dataGoalkeepers)


# helper function 2
def helper2(y, pos, num1, num2):
    # converting lists to DataFrames and ranking
    x = pd.DataFrame(columns=['name', 'position', 'season_points'])
    z = pd.concat([x, pd.DataFrame(y)], ignore_index=True)
    sortedPosition = z.sort_values(by='season_points', ascending=False, ignore_index=True)
    # Find top scores of positions and including players 
    # with equal point scores for the last available spot
    s1 = sortedPosition.iloc[num1]['season_points']
    s2 = sortedPosition.iloc[num2]['season_points']
    match_count = (sortedPosition['season_points'] == s1).sum()
    if match_count > 1 and s1 == s2:
        i = num2
        while s1 == s2:
            best = sortedPosition.head(i+1)
            i += 1
            s2 = sortedPosition.iloc[i]['season_points']
        return best
    else:
        best = sortedPosition.head(num2)
        return best


# Obtaining best positions data frames
unmergedForwards = helper2(dataForwards, 'Forwards', 2, 3)
unmergedMidfielders = helper2(dataMidfielders, 'Midfielders', 4, 5)
unmergedDefenders = helper2(dataDefenders, 'Defenders', 4, 5)
unmergedGoalkeepers = helper2(dataGoalkeepers, 'Goalkeepers', 1, 2)

# merging frames to get game week points
bestGoalkeepers = pd.merge(unmergedGoalkeepers.loc[:, ['name', 'position']], gwRevised, on=['name'], how='inner')
bestGoalkeepers = bestGoalkeepers.sort_values(by='total_points', ascending=False, ignore_index=True)
bestDefenders = pd.merge(unmergedDefenders.loc[:, ['name', 'position']], gwRevised, on=['name'], how='inner')
bestDefenders = bestDefenders.sort_values(by='total_points', ascending=False, ignore_index=True)
bestMidfielders = pd.merge(unmergedMidfielders.loc[:, ['name', 'position']], gwRevised, on=['name'], how='inner')
bestMidfielders = bestMidfielders.sort_values(by='total_points', ascending=False, ignore_index=True)
bestForwards = pd.merge(unmergedForwards.loc[:, ['name', 'position']], gwRevised, on=['name'], how='inner')
bestForwards = bestForwards.sort_values(by='total_points', ascending=False, ignore_index=True)

# adding position and points to names for later use
bestForwards['name'] += ' (' + bestForwards['position'].astype(str) + ') (' + bestForwards['total_points'].astype(str) + ')'
bestMidfielders['name'] += ' (' + bestMidfielders['position'].astype(str) + ') (' + bestMidfielders['total_points'].astype(str) + ')'
bestDefenders['name'] += ' (' + bestDefenders['position'].astype(str) + ') (' + bestDefenders['total_points'].astype(str) + ')'
bestGoalkeepers['name'] += ' (' + bestGoalkeepers['position'].astype(str) + ') (' + bestGoalkeepers['total_points'].astype(str) + ')'

# Player counts for possible formations
goalkeeper = bestGoalkeepers.iloc[0]['total_points']
threeDef = bestDefenders.loc[[0, 1, 2], 'total_points'].sum()
fourDef = bestDefenders.loc[[0, 1, 2, 3], 'total_points'].sum()
fiveDef = bestDefenders.loc[[0, 1, 2, 3, 4], 'total_points'].sum()
twoMid = bestMidfielders.loc[[0, 1], 'total_points'].sum()
threeMid = bestMidfielders.loc[[0, 1, 2], 'total_points'].sum()
fourMid = bestMidfielders.loc[[0, 1, 2, 3], 'total_points'].sum()
fiveMid = bestMidfielders.loc[[0, 1, 2, 3, 4], 'total_points'].sum()
oneFwd = bestForwards.iloc[0]['total_points']
twoFwd = bestForwards.loc[[0, 1], 'total_points'].sum()
threeFwd = bestForwards.loc[[0, 1, 2], 'total_points'].sum()

# Formations
# 1-3-4-3, 1-3-5-2, 1-4-3-3, 1-4-4-2, 1-4-5-1, 1-5-4-1, 1-5-3-2, 1-5-2-3
three43 = int(goalkeeper) + int(threeDef) + int(fourMid) + int(threeFwd)
three52 = int(goalkeeper) + int(threeDef) + int(fiveMid) + int(twoFwd)
four33 = int(goalkeeper) + int(fourDef) + int(threeMid) + int(threeFwd)
four42 = int(goalkeeper) + int(fourDef) + int(fourMid) + int(twoFwd)
four51 = int(goalkeeper) + int(fourDef) + int(fiveMid) + int(oneFwd)
five41 = int(goalkeeper) + int(fiveDef) + int(fourMid) + int(oneFwd)
five32 = int(goalkeeper) + int(fiveDef) + int(threeMid) + int(twoFwd)
five23 = int(goalkeeper) + int(fiveDef) + int(twoMid) + int(threeFwd)

# Formations Table
formationsTable = pd.DataFrame({'Formations': ['1-3-4-3', '1-3-5-2', '1-4-3-3', 
                                               '1-4-4-2', '1-4-5-1', '1-5-4-1', 
                                               '1-5-3-2', '1-5-2-3'], 'Sums': 
                                               [three43, three52, four33, four42, 
                                                four51, five41, five32, five23]})


# Ranking Formations
sortedFormations = formationsTable.sort_values(by='Sums', ascending=False, ignore_index=True)

# Checking for formations with duplicate sums
sForm1 = sortedFormations.iloc[0]['Sums']
sForm2 = sortedFormations.iloc[1]['Sums']
match_countForm = (sortedFormations['Sums'] == sForm1).sum()

# In the event the next formation has the same sum as the first
# this loop will run to make a sub-DataFrame of duplicates
if match_countForm > 1:
    i = 1
    while sForm1 == sForm2:
        bestFormations = sortedFormations.head(i+1)
        i += 1
        sForm2 = sortedFormations.iloc[i]['Sums']
else:
    bestFormations = sortedFormations.head(1)


# turns data frame into list
def makeList(x):
    list = x.tolist()
    return list


# helper function 3
def helper3(altComb, x, y, z, ind):  # x is empty position list, y is topplayer list, z is position string
    for permutation in altComb:
        variation = z + ' Variation'
        x.append(variation)
        if ind == True:
            pass
        else:
            for player in y:
                x.append(player)
        for player in permutation:
            x.append(player)
    return x


# helper function 4
def helper4(altComb, x, y, z, ind):  # x is empty position list, y is topplayer list, z is position string
    for permutation in altComb:
        variation = z + ' Variation'
        x.append(variation)
        if ind == True:
            pass
        else:
            for player in y:
                x.append(player)
        x.append(permutation)
    return x


# This variable is used as a marker in the following loop. It provides
# the number of players in each DataFrame. 
maxPlayers = [len(bestGoalkeepers), len(bestDefenders), len(bestMidfielders), len(bestForwards)]
formationsList = []

# best goalkeeper(s)
if bestGoalkeepers.iloc[0]['total_points'] > bestGoalkeepers.iloc[1]['total_points']:
    goalkeepersFinal_list = bestGoalkeepers.loc[0, 'name']
else:
    goalkeepersFinal_list = []
    duplicateGoalkeepers = makeList(bestGoalkeepers.loc[:, 'name'])
    for player in duplicateGoalkeepers:
        goalkeepersFinal_list.append('Goalkeeper Variation')
        goalkeepersFinal_list.append(player)


# loop for variation lists: defs, mids, fwds
for formation in bestFormations.loc[:, 'Formations']:
    i = 2 # skipping goalkeeps because there are always 2, never one
    while i < 8:
        if int(formation[i]) == maxPlayers[int(i/2)]:  #1
            if i == 2:
                defendersFinal_list = makeList(bestDefenders.loc[:, 'name'])
            elif i == 4:
                midfieldersFinal_list = makeList(bestMidfielders.loc[:, 'name'])
            else:
                forwardsFinal_list = makeList(bestForwards.loc[:, 'name'])
            i += 2
        else:
            positions = [bestGoalkeepers, bestDefenders, bestMidfielders, bestForwards] 
            posLen = int(formation[i])
            currentPosition = positions[int(i/2)]
            if currentPosition.iloc[posLen-1]['total_points'] != currentPosition.iloc[posLen]['total_points']:  # if last not equal to next
                if i == 2:
                    defendersFinal = bestDefenders.head(posLen)
                    defendersFinal_list = makeList(defendersFinal.loc[:, 'name'])
                elif i == 4:
                    midfieldersFinal = bestMidfielders.head(posLen)
                    midfieldersFinal_list = makeList(midfieldersFinal.loc[:, 'name'])
                else:
                    forwardsFinal = bestForwards.head(posLen)
                    forwardsFinal_list = makeList(forwardsFinal.loc[:, 'name'])
                i += 2
            else:
                altPlayers = currentPosition.iloc[posLen-1]['name']
                altPlayers_list = [altPlayers]
                k = posLen-2
                while currentPosition.iloc[posLen-1]['total_points'] == currentPosition.iloc[k]['total_points'] and k >= 0:
                    currentPlayer = currentPosition.iloc[k]['name']
                    altPlayers_list.append(currentPlayer)
                    k -= 1
                    if k < 0:
                        break
                j = posLen
                maxValue = maxPlayers[int(i/2)]
                while currentPosition.iloc[posLen-1]['total_points'] == currentPosition.iloc[j]['total_points'] and j >= 0:
                    currentPlayer = currentPosition.iloc[j]['name']
                    altPlayers_list.append(currentPlayer)
                    j += 1
                    if j > int(maxValue)-1:
                        break
                if k+1 == 0:
                    topSpots_list = altPlayers_list
                    spotsAvailable = posLen
                    majorDuplicator = True
                else:
                    topSpots = currentPosition.head(k+1)
                    spotsAvailable = posLen - len(topSpots)
                    topSpots_list = makeList(topSpots.loc[:,'name'])
                    majorDuplicator = False
                if spotsAvailable < 2:
                    altComb = altPlayers_list
                    if i == 2:
                        defendersFinal_list = []
                        helper4(altComb, defendersFinal_list, topSpots_list, 'Defenders', majorDuplicator)
                    elif i == 4:
                        midfieldersFinal_list = []
                        helper4(altComb, midfieldersFinal_list, topSpots_list, 'Midfielders', majorDuplicator)
                    else:
                        forwardsFinal_list = []
                        helper4(altComb, forwardsFinal_list, topSpots_list, 'Forwards', majorDuplicator)
                else:
                    altComb = list(itertools.combinations(altPlayers_list, spotsAvailable))   
                    if i == 2:
                        defendersFinal_list = []
                        helper3(altComb, defendersFinal_list, topSpots_list, 'Defenders', majorDuplicator)
                    elif i == 4:
                        midfieldersFinal_list = []
                        helper3(altComb, midfieldersFinal_list, topSpots_list, 'Midfielders', majorDuplicator)
                    else:
                        forwardsFinal_list = []
                        helper3(altComb, forwardsFinal_list, topSpots_list, 'Forwards', majorDuplicator)
                i += 2
    formationsList.append('Formation')
    formationsList.append('Goalkeepers')
    formationsList.append(goalkeepersFinal_list)
    formationsList.append('Defenders')
    formationsList.append(defendersFinal_list)
    formationsList.append('Midfielders')
    formationsList.append(midfieldersFinal_list)
    formationsList.append('Forwards')
    formationsList.append(forwardsFinal_list)


# helper function 5
# (len(nestedList) - count(pos + 'Variation'))/count(pos +'Variation') = number players
def helper5(formationsList, i, pos, posList):
    a = len(formationsList[i])
    b = formationsList[i].count(pos + ' Variation')
    if b == 0:
        posList.append(formationsList[i])
    else:
        c = int((a-b)/b)  # number of player for given position
        d = 1
        e = c+1
        f = int(a)+1
        while e < f:
            posList.append(formationsList[i][d:e])
            d += c+1
            e += c+1


# separting into nested lists for later permutations
permGoalkeepers = []
permDefenders = []
permMidfielders = []
permForwards = []
i = 2
j = 2
k = 4
l = 6
m = 8
while i < len(formationsList):
    if i == j:
        permGoalkeepers.append('Formation')
        helper5(formationsList, i, 'Goalkeeper', permGoalkeepers)
        j += 9
        i += 2
    elif i == k:
        permDefenders.append('Formation')
        helper5(formationsList, i, 'Defenders', permDefenders)
        k += 9
        i += 2
    elif i == l:
        permMidfielders.append('Formation')
        helper5(formationsList, i, 'Midfielders', permMidfielders)
        l += 9 
        i += 2
    else:
        permForwards.append('Formation')
        helper5(formationsList, i, 'Forwards', permForwards)
        m += 9
        i += 3


# helper function 6
def helper6(x,y):
    for index, player in enumerate(x):
        if player == 'Formation':
            y.append(index)
        else:
            pass


formLocDef = []
formLocMid = []
formLocFwd = []
helper6(permDefenders, formLocDef)
helper6(permMidfielders, formLocMid)
helper6(permForwards, formLocFwd)


del permGoalkeepers[0]
finalList = ['Formation']
newI = 1
newJ = 1
newK = 1
locI = 1
locJ = 1
locK = 1

for gplayer in permGoalkeepers:
    if gplayer == 'Formation':
        finalList.append('Formation')
        newI = formLocDef[locI] + 1
        newJ = formLocMid[locJ] + 1
        newK = formLocFwd[locK] + 1
        locI += 1
        locJ += 1
        locK += 1
    else:
        i = newI
        while i < len(permDefenders) and permDefenders[i] != 'Formation':
            j = newJ
            while j < len(permMidfielders) and permMidfielders[j] != 'Formation':
                k = newK
                while k < len(permForwards) and permForwards[k] != 'Formation':
                    finalList.append('Variation')
                    finalList.append(gplayer)
                    finalList.append(permDefenders[i])
                    finalList.append(permMidfielders[j])
                    finalList.append(permForwards[k])
                    k += 1
                j += 1
            i += 1


# un-nest list
def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list 


finalListDenest = flatten_list(finalList)

# converting list to DataFrame
finalListdf = pd.DataFrame()
i = 0  # formation loop
j = 1  # variation loop
k = 0  # team loop

for element in finalListDenest:
    if element == 'Formation':
        formName = 'Formation ' + str(i+1)
        finalListdf[formName] = [bestFormations.iloc[i,0], 'Score = ' + str(bestFormations.iloc[i,1]), '', '', '', '', '', '', '', '', '']
        j = 1
        i += 1
    elif element == 'Variation':
        varName = 'Variation ' + str(j) + ' (F' + str(i) + ')'
        finalListdf[varName] = ['', '', '', '', '', '', '', '', '', '', ''] 
        k = 0
        j += 1
    else:
        finalListdf.loc[k, varName] = element
        k += 1

print()
print(finalListdf)

finalListdf.to_csv(season + '\\Top Squad TofW\\' + 'gw' + str(week) + 'bestLineups.csv', index = False)
print()
print('"gw' + str(week) + 'bestLineups.csv" has been saved to ".../' + season + '/Top Squad TofW"')
print()
