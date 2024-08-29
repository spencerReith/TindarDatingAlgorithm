from classes.applicant import Applicant
import sqlite3
import csv


def getApplicantDict():

    applicants_mf = '../textFiles/applicants_mf.csv'
    applicants_mb = '../textFiles/applicants_mb.csv'
    applicants_mm = '../textFiles/applicants_mm.csv'
    applicants_fm = '../textFiles/applicants_fm.csv'
    applicants_fb = '../textFiles/applicants_fb.csv'
    applicants_ff = '../textFiles/applicants_ff.csv'



    filePathList = [applicants_mf, applicants_mb, applicants_mm, applicants_fm, applicants_fb, applicants_ff]
    applicantDict = {}

    for filePath in filePathList:
        with open(filePath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 6:
                    applicantDict[row[0]] = Applicant(row[0], row[1], row[2], row[3], row[4], row[5])
                else:
                    # print(row)
                    continue


    return applicantDict

applicantDict = getApplicantDict()


# conn = sqlite3.connect('main.db')
# cursor = conn.cursor()

# create_table_query = '''
# CREATE TABLE IF NOT EXISTS applicant_pool (
#     key TEXT PRIMARY KEY,
#     userID TEXT,
#     name TEXT,
#     email TEXT,
#     classYear TEXT,
#     sex TEXT,
#     prefSex TEXT
# );
# '''
# cursor.execute(create_table_query)

# for key, value in applicantDict.items():
#     cursor.execute('INSERT INTO applicant_pool (key, userID, name, email, classYear, sex, prefSex) VALUES (?, ?, ?, ?, ?, ?, ?)', (key, value.getUserId(), value.getName(), value.getEmail(), value.getClassYear(), value.getSex(), value.getPrefSex()))

# conn.commit()
