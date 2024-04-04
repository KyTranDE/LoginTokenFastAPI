from database.mysql import MySql
import datetime

def date2idx(date, sport_name):
    #  check date format yyyy-mm-dd
    date = datetime.datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
    db = MySql()
    result = db.query("select `idx` from `{}_date2index` where `date_play` = '{}'".format(sport_name, date), False)
    # db.close()
    return result[0][0]