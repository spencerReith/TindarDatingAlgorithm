## 'algLibTest.py' – testing functions in the algLib (algorithm library)
import darLibraries.algLib as algLib
import sqlite3
import random
import algorithm
from darLibraries.applicantDictAssembler import getApplicantDict

### honestly, this thing is pretty slow running with 20,000 interactions. I don't know why that is.
### I might need to re-design parts of the algorithm.
### More or less, I might need to quit the whole networkx concept, and go right from the database
### AKA, I'll be finding predecessores directly from interactions_table->b_userID==selfID
### Selecting that whole row would let me see the edge weight. It might be worth it to do that. I don't know.

## LOAD IN SAMPLE SERIES OF APPLICANTS INTO AN APPLICANT DICTIONARY
### maybe just import this from applicantDictAssembler.py, and retrieve the dictionary immediately
# def getApplicantDict():

#     applicants_mf = 'textFiles/applicants_mf.csv'
#     applicants_mb = 'textFiles/applicants_mb.csv'
#     applicants_mm = 'textFiles/applicants_mm.csv'
#     applicants_fm = 'textFiles/new_applicants_fm.csv'
#     applicants_fb = 'textFiles/applicants_fb.csv'
#     applicants_ff = 'textFiles/applicants_ff.csv'



#     filePathList = [applicants_mf, applicants_mb, applicants_mm, applicants_fm, applicants_fb, applicants_ff]
#     applicantDict = {}

#     for filePath in filePathList:
#         with open(filePath, newline='') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 if len(row) == 6:
#                     applicantDict[row[0]] = Applicant(row[0], row[1], row[2], row[3], row[4], row[5])
#                 else:
#                     print(row)


#     return applicantDict


conn = sqlite3.connect('../main.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS applicant_pool;')
cursor.execute('DROP TABLE IF EXISTS interactions_table;')
cursor.execute('DROP TABLE IF EXISTS statistics;')
conn.commit()
conn.close()




## NOT to be confused with getNodesFromDB() which returns an applicant dictionary
## This function is just meant to load the mock users from CVV files into an applicant dictionary
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
    ### AS ANNOYING AS IT IS, THE TEST WOULD BE A LOT MORE REALISTIC IF I MADE THE INTERACTIONS MORE REALISTIC... I KNOW ITS STILL GOOD, BUT, IF IM GONNA SHOW IT TO JOBS MAYBE ITS WORTH IT TO MAKE THE INTERACITONS MORE REALISTIC, BUT ALSO IT WOULD BE A PAIN IN THE ASS... I DONT KNOW
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
        ## check... ## ALSO CHECK changing of interactions table in algLib and Here
        for b_userID in selfQueue:
            swipe_choice = random.randint(0, 1)
            algLib.addInteraction(selfID_Graph, selfID, b_userID, swipe_choice)
    algLib.visualizeGraph(selfID_Graph) ###CHECH NEED TO CHECK HERE

algLib.visualizeGraph(wholeGraph)

algLib.calcStatistics(wholeGraph)
