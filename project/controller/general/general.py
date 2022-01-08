import time

from functools import wraps
from flask import flash

from flask import render_template, redirect, url_for, session, request

def calculateTime(myDict):	
    dateNow = int(time.time())	
    for key, comment in myDict:	
        if comment.updated_date != None:	
            timePast = dateNow - comment.updated_date	
            days = timePast // 86400	
            hours = timePast // 3600 % 24	
            minutes = timePast // 60 % 60	
            seconds = timePast % 60	
            if days:	
                comment.updated_date = str(days) + " days ago"	
                continue	
            if hours:	
                comment.updated_date = str(hours) + " hours ago"	
                continue	
            if minutes:	
                comment.updated_date = str(minutes) + " minutes ago"	
                continue	
            if seconds:	
                comment.updated_date = str(seconds) + " seconds ago"	
                continue

