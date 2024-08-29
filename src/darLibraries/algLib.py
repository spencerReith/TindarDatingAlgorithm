'''
File: 'algLib.py'
Summer 2024
Spencer Reith

Description:
    Contains functions for querying a SQLite database, constructing and visualizing graphs,
    and analyzing data related to the swiping. It handles operations such as 
    fetching data from the database, building and visualizing graphs, inserting and updating data, 
    and calculating statistics. Some of the statistical algorithms are related to functions not showcased in this repo.
'''

## 'algLib.py' - contains several functions that relate to database querierying, graph visualization, editing, and analysis. These functions are relevant for our usage and analysis of the algorithm.
## Spencer Reith, Summer 2024


from classes.applicant import Applicant
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx
import scipy as sp

########################################################
### FUNCTIONS FOR DATABASE QUERERING & GRAPH CONSTRUCTION + VISUALIZATION
########################################################

def getNodesFromDB():
    # Connect to the SQLite database
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    # Fetch data from the table
    cursor.execute('SELECT * FROM applicant_pool;')
    rows = cursor.fetchall()
    # Create a dictionary to store the fetched data
    nodes = {}
    # store in dictionary as {userID:applicant}
    for row in rows:
        key = int(row[0])
        nodes[key] = Applicant(int(row[1]), row[2], row[3], row[4], row[5], row[6])
    # Close the connection
    conn.close()
    return nodes # return nodes

def getEdgesFromDB():
    # Connect to the SQLite database
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    # Fetch data from the table
    cursor.execute('SELECT * FROM interactions_table;')
    rows = cursor.fetchall()
    # Create a list to store the fetched data
    edges = []
    # store in dictionary as {userID:applicant}
    for row in rows:
        edge = row ## key by weight (at least for now)
        edges.append(edge) ## item is a list of [node a, node b]
    # Close the connection
    conn.close()
    return edges # return edges

def getStatisticsFromDB():
    # Connect to the SQLite database
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    # Fetch data from the table
    cursor.execute('SELECT * FROM statistics;')
    rows = cursor.fetchall()
    # Create a dictionary to store the fetched data
    statistics = {}
    # store in dictionary as {userID:(stat1, stat2, stat3)}
    for row in rows:
        key = int(row[0])
        statistics[key] = [row[1], row[2], row[3]]
    # Close the connection
    conn.close()
    return statistics # return nodes


def buildSelfID_GraphFromDB(selfID):
    ## initialize graph G
    G = nx.DiGraph()
    ##  select all nodes (getNodesFromDB)
    applicantDictionary = getNodesFromDB()
    for key, value in applicantDictionary.items():
        G.add_node(key, sex=value.getSex(), prefSex=value.getPrefSex())
    
    ##  select all edges ## NEED TO CHECK HERE: IS THE ORDER RIGHT FOR 0,1,2 being a,b,weight ?
    interactionsList = getEdgesFromDB()
    for interaction in interactionsList:
        ## if node a = self or node b = self, then interaction is from or to users
        if interaction[0] == selfID or interaction[1] == selfID:
            G.add_edge(interaction[0], interaction[1], weight=interaction[2])
    
    return G ##  return whole_G


def buildWholeGraphFromDB():
    ## initialize graph G
    G = nx.DiGraph()
    ##  select all nodes (getNodesFromDB)
    applicantDictionary = getNodesFromDB()
    for key, value in applicantDictionary.items():
        G.add_node(key, sex=value.getSex(), prefSex=value.getPrefSex())
    
    interactionsList = getEdgesFromDB()
    for interaction in interactionsList:
        G.add_edge(interaction[0], interaction[1], weight=interaction[2])
    
    return G ##  return graph selfID_G



########################################################
### FUNCTIONS FOR GRAPH/DATABASE INSERTION #############
########################################################

def createApplicantTable():
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS applicant_pool (
        key INTEGER PRIMARY KEY,
        userID INTEGER,
        name TEXT,
        email TEXT,
        classYear INTEGER,
        sex CHAR(1),
        prefSex CHAR(1)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

def createEdgeTable():
    ## assumes that the interaction is going FROM user a TO user b.
    ## so, [1,2,9] represents user 1 blacklisting user 2.
    ## also, primary key is somewhat arbitrary in this case. We can change later as we see fit.
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS interactions_table (
        a_userID INTEGER,
        b_userID INTEGER,
        weight INTEGER,
        UNIQUE(a_userID, b_userID)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()


## Run createReferralsTable
def createReferralsTable():
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS referrals_table (
        originator_ID INTEGER,
        a_userID INTEGER,
        b_userID INTEGER,
        UNIQUE(a_userID, b_userID)
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()


## Run addApplicantToDB
def addApplicantToDB(a):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    INSERT INTO applicant_pool (key, userID, name, email, classYear, sex, prefSex)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, (a.getUserId(), a.getUserId(), a.getName(), a.getEmail(), a.getClassYear(), a.getSex(), a.getPrefSex()))
    conn.commit()
    conn.close()

## Run addInteractionToDB
def addInteractionToDB(a_userID, b_userID, weight):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    INSERT OR REPLACE INTO interactions_table (a_userID, b_userID, weight)
    VALUES (?, ?, ?);
    '''
    cursor.execute(query, (a_userID, b_userID, weight))
    conn.commit()
    conn.close()


## Run addInteractionToGraph
def addInteractionToGraph(G, a_userID, b_userID, edge_weight):
    G.add_edge(a_userID, b_userID, weight=edge_weight)

## Run addInteraction(selfID, otherID, weight)
## ->  A: add to the database at the same time you add to the database, and you don't have to re-make the graph from the database. this is probably best.
## ->  B: add to the database, and every time you go to draw a queue, you need to build a new graph and then draw a queue. That's really not best.
def addInteraction(G, a_userID, b_userID, edge_weight):
    addInteractionToDB(a_userID, b_userID, edge_weight)
    addInteractionToGraph(G, a_userID, b_userID, edge_weight)


########################################################
### FUNCTIONS FOR GRAPH VISUALIZATION ##################
########################################################

def visualizeGraph(G):
    nx.draw(G, with_labels=True)
    plt.show()

########################################################
### FUNCTIONS FOR GRAPH ANALYSIS #######################
########################################################

## Run createApplicantTable
def createStatisticsTable():
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    CREATE TABLE IF NOT EXISTS statistics (
        userID INTEGER PRIMARY KEY,
        offerReceptionRate FLOAT,
        offerBestowalRate FLOAT,
        tindarIndex FLOAT
    );
    '''
    cursor.execute(query)
    conn.commit()
    conn.close()

##  Run calcOfferReceptionRate
def calcOfferReceptionRate(G, selfID):
    in_edges_list = list(G.in_edges(selfID, data=True))
    offers = 0
    swipes = 0
    for edge in in_edges_list:
        if edge[2]['weight'] == 1:
            offers+=1
            swipes+=1
        if edge[2]['weight'] == 0:
            swipes+=1
        else:
            continue
    ## if applicant has not recieved any swipes, leave rate as None
    if swipes == 0:
        rate = None
    else:
        rate = offers/swipes
    return rate


## Run calcOfferBestowalRate
def calcOfferBestowalRate(G, selfID):
    out_edges_list = list(G.out_edges(selfID, data=True))
    offers = 0
    swipes = 0
    for edge in out_edges_list:
        if edge[2]['weight'] == 1:
            offers+=1
            swipes+=1
        if edge[2]['weight'] == 0:
            swipes+=1
        else:
            continue
    ## if applicant has not swiped on anyone yet, leave rate as None
    if swipes == 0:
        rate = None
    else:
        rate = offers/swipes
    return rate

# Run calcTindarIndex
def calcTindarIndex(GPA, ricePurityScore):
    scaledGPA = 0
    if GPA < 3:
        scaledGPA = .1
    else:
        scaledGPA = GPA - 2.9
    tindarIndex = (scaledGPA * ricePurityScore) / 1.1

    return tindarIndex

def addTindarIndexToDB(userID, tindarIndex):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    INSERT INTO statistics (userID, tindarIndex)
    VALUES (?, ?);
    '''
    cursor.execute(query, (userID, tindarIndex))
    conn.commit()
    conn.close()

def fetchTindarIndex(userID):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    SELECT tindarIndex FROM statistics WHERE userID = ?;
    '''
    tindarIndex = cursor.execute(query, (userID,)).fetchone()[0]
    conn.commit()
    conn.close()
    ## return tindarIndex
    return tindarIndex


    

## Run calcApplicantStatistics
def calcApplicantStatistics(G, selfID):
    offerReceptionRate = calcOfferReceptionRate(G, selfID)
    offerBestowalRate = calcOfferBestowalRate(G, selfID)
    ## insert data into table
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    UPDATE statistics SET offerReceptionRate = ?, offerBestowalRate = ? WHERE userID = ?
    '''
    cursor.execute(query, (offerReceptionRate, offerBestowalRate, selfID))
    conn.commit()
    conn.close()


def calcStatistics(G):
    ID_list = list(G.nodes())
    for ID in ID_list:
        calcApplicantStatistics(G, ID)

## Run writeApplicantStatistics(filepath)
def writeApplicantStatistics():
    header = "\n\nStatistics Breakdown.\nTindar.\n\nThis file breaks-down several key metrics of the applicant pool.\n"
    # with open(filepath, 'w') as file:
    #     file.write(header)
    statistics = getStatisticsFromDB()
    print(header)
    print(statistics) ## for now, I'll add functions later
    ## now we'd want to analyze these stats
    ## lots of ways to do it... some ideas
    ## sort database by highest to lowest offerReceptionRate
    ## sort database by highest to lowest offerBestowalRate
    ## histogram of tindarIndex es
    ## tindarIndex versus offerReceptionRate
    ## tindarIndex versus offerBestowalRate
    ## offerReceptionRate versus offerBestowalRate



##  read applicant statistics from databse table
##  maybe store them in a dictionary {id:(stat1, stat2)}
##  print them into a txt file in table format (probably more useful to read than a CVV)

########################################################
### FUNCTIONS RELATING TO REFERRALS ####################
########################################################

def getApplicantFromDB(userID):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    SELECT * FROM applicant_pool WHERE userID = ?;
    '''
    row = cursor.execute(query, (userID,)).fetchone()
    a = Applicant(row[1], row[2], row[3], row[4], row[5], row[6])
    conn.commit()
    conn.close()
    ## return tindarIndex
    return a

def sexBasedCompatabilityCheck(a_userID, b_userID):
    applicantA = getApplicantFromDB(a_userID)
    applicantB = getApplicantFromDB(b_userID)
    a_sex = applicantA.getSex()
    a_pref = applicantA.getPrefSex()
    b_sex = applicantB.getSex()
    b_pref = applicantB.getPrefSex()

    if (a_pref == b_sex) or (b_sex == 'b'):
        if (a_sex == b_pref) or (b_pref == 'b'):
            return True
    return False

def getEdgeWeight(a, b):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    SELECT * FROM interactions_table WHERE a_userID = ? AND b_userID = ?;
    '''
    result = cursor.execute(query, (a, b)).fetchone()
    ## If edge does not exist, return 'DNE'
    if result == None:
        conn.close()
        return 'None'
    else:
        edge_weight = result[2]
    conn.close()
    ## return edge_weight
    return edge_weight

def addReferralToDB(self_ID, a, b):
    conn = sqlite3.connect('../main.db')
    cursor = conn.cursor()
    query = '''
    INSERT INTO referrals_table (self_ID, a_userID, b_userID)
    VALUES (?, ?, ?);
    '''
    cursor.execute(query, (self_ID, a, b))
    conn.commit()
    conn.close()

def attemptReferral(self_ID, a, b):
    if sexBasedCompatabilityCheck(a, b) == False:
        return("COMPATABILITY FAILURE")
    else:
        ab_edgeWeight = getEdgeWeight(a, b)
        ba_edgeWeight = getEdgeWeight(b, a)
        if ab_edgeWeight == ba_edgeWeight == 1:
            return("TYPE-1 FAILURE")
        if ab_edgeWeight == 9 or ba_edgeWeight == 9:
            return("TYPE-9 FAILURE")
        if ab_edgeWeight == 14 or ba_edgeWeight == 14:
            return("TYPE-14 FAILURE")
        if ab_edgeWeight == 0 or ba_edgeWeight == 0:
            addReferralToDB(a,b)
            return("TYPE-0 FAILURE")
        if ab_edgeWeight == 1 and ba_edgeWeight == 'None':
            addInteractionToDB(b, a, 14)
            addReferralToDB(self_ID, a,b)
            return("1-None Success")
        if ab_edgeWeight == 'None' and ba_edgeWeight == 1:
            addInteractionToDB(a, b, 14)
            addReferralToDB(self_ID, a,b)
            return("None-1 Success")
        if ab_edgeWeight == ba_edgeWeight == 'None':
            addInteractionToDB(a, b, 14)
            addInteractionToDB(b, a, 14)
            addReferralToDB(self_ID, a,b)
            return("None-None Success")

## If 'a' wants to reneg on 'b', then we replace a & b's old interaction with a blacklist
def renegInDatabase(a_userID, b_userID):
    addInteractionToDB(a_userID, b_userID, 9)