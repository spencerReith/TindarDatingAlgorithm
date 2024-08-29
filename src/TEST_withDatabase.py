## 'algLibTest.py' – testing functions in the algLib (algorithm library)
import darLibraries.algLib as algLib
import sqlite3
import random
import algorithm
from darLibraries.applicantDictAssembler import getApplicantDict


conn = sqlite3.connect('../main.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS applicant_pool;')
cursor.execute('DROP TABLE IF EXISTS interactions_table;')
cursor.execute('DROP TABLE IF EXISTS statistics;')
conn.commit()
conn.close()




applicantDict = getApplicantDict()



algLib.createApplicantTable()
algLib.createEdgeTable()
algLib.createStatisticsTable()

for applicantKey in applicantDict:
    algLib.addApplicantToDB(applicantDict[applicantKey])
    GPA = random.randint(290,400) / 100
    ricePurityScore = random.randint(1,100)
    tindarIndex = algLib.calcTindarIndex(GPA, ricePurityScore)
    algLib.addTindarIndexToDB(applicantKey, tindarIndex)

for i in range(8000):
    interaction = 0
    random_userIDs = random.sample(list(applicantDict.keys()), 2)
    random_number = random.randint(0,10)
    if 0 <= random_number <= 2:
        interaction = 0
    elif 3 <= random_number <= 8:
        interaction = 1
    else:
        interaction = 9
    algLib.addInteractionToDB(random_userIDs[0], random_userIDs[1], interaction)

wholeGraph = algLib.buildWholeGraphFromDB()

string_selfID_sample = random.sample(list(applicantDict.keys()), 5)
## convert userID's to integers
int_selfID_sample = []
for element in string_selfID_sample:
    int_selfID_sample.append(int(element))

print("random_selfID_sample: ", int_selfID_sample)
for selfID in int_selfID_sample:
    selfID_Graph = algLib.buildSelfID_GraphFromDB(selfID)
    # algLib.visualizeGraph(selfID_Graph)
    print("\nselfID: ", selfID)
    selfQueue = []
    for q in range(5):
        selfQueue = algorithm.getCompositeQueue(selfID_Graph, selfID, 8)
        print("Queue: ", selfQueue)
        for b_userID in selfQueue:
            swipe_choice = random.randint(0, 1)
            algLib.addInteraction(selfID_Graph, selfID, b_userID, swipe_choice)
    algLib.visualizeGraph(selfID_Graph)

algLib.visualizeGraph(wholeGraph)

algLib.calcStatistics(wholeGraph)
