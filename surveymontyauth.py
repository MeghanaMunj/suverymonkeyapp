#!/usr/bin/env python
import surveymonkeydatafetch
import urllib
import argparse
import webbrowser
import requests
import urllib2
import os
import time
import json
from furl import furl
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import csv

lv_path = "C:\\output\\chromedriver.exe"
os.environ["webdriver.chrome.driver"] = lv_path

#lv_path = "C:\\output\\IEDriverServer.exe"
#os.environ["webdriver.ie.driver"] = lv_path


SM_API_BASE = "https://api.surveymonkey.net"
AUTH_CODE_ENDPOINT = "/oauth/authorize"
ACCESS_TOKEN_ENDPOINT = "/oauth/token"
REDIRECT_URI = "http://127.0.0.1"
HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8000

api_key = "testing"

'''
#user id - megmunj
client_id = 'tqNnSkU9RJ-YEfWN0g_z5g'
client_secret = '41988752743902965171575396807070453910'
'''
#user id - devmammoth
client_id = 'iTrVyTsOTrmnfNCOUaThNA'
client_secret = "111213644395006718153390869016200438262 "

def exchange_code_for_token(auth_code, client_secret, client_id, redirect_uri):
    oauth_save_url = "http://127.0.0.1"
    data = {
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": oauth_save_url,
        "client_id": client_id,
        "grant_type": "authorization_code"
    }
    
    access_token_uri = SM_API_BASE + ACCESS_TOKEN_ENDPOINT 
    access_token_response = requests.post(access_token_uri, data=data)
    print("**********Access tocken response",access_token_response)
    access_json = access_token_response.json()
    print("***************access token response json*************",access_json)
    if 'access_token' in access_json:
        return access_json['access_token']
    else:
        print access_json
        return None
def oauth_dialog(client_id, redirect_uri):
    """ Construct the oauth_dialog_url.
    """
    url_params = urllib.urlencode({
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'response_type': 'code'})

    auth_dialog_url = SM_API_BASE + AUTH_CODE_ENDPOINT + '?' + url_params
    oauth_save_url = "http://127.0.0.1"
    auth_dialog_url = auth_dialog_url 
    print "\nThe auth dialog url was " + auth_dialog_url + "\n"
    return auth_dialog_url


# Bootstrap script to call into main
if __name__ == "__main__":
    #client_id = "oExDyiCTQOKf-oYOzXzE0w"
    #client_secret = "231452587066024730312549141434044897569"
    '''
    #user id megmunj
    client_id = 'tqNnSkU9RJ-YEfWN0g_z5g'
    client_secret = '41988752743902965171575396807070453910'     
    '''
    #user id - devmammoth
    client_id = 'iTrVyTsOTrmnfNCOUaThNA'
    client_secret = "111213644395006718153390869016200438262"
    
    # Load oauth dialog and take user input
    REDIRECT_URI = oauth_dialog( client_id, REDIRECT_URI)
    time.sleep(1)
    browser = webdriver.Chrome(lv_path)
    browser.get(REDIRECT_URI)
    
    browser.implicitly_wait(30000000)
    browser.maximize_window()
    for lw_username in browser.find_elements_by_id('username'):
        lw_username.send_keys('devmammoth')
    for lw_pass in browser.find_elements_by_id('password'):
        lw_pass.send_keys('meghana104')

    for lw_button in browser.find_elements_by_css_selector('#sign_in_form > fieldset > button'):
        lw_button.click()     
    browser.implicitly_wait(300000)
    for lw_submit in browser.find_elements_by_id('submit-oauth'):
        lw_submit.click()
    browser.implicitly_wait(300000)
    print(browser.current_url)
    browser.implicitly_wait(3000000)

    i = 5000
    x = 1
    while x < i:
        x = x + 1
        browser.implicitly_wait(300)
    lv_url = browser.current_url
    lt_args = furl(lv_url)
    lv_code = lt_args.args['code']
    print('Code is ---',lv_code)
    lv_strcode = str(lv_code)
    print('String Code is ---',lv_strcode)
    lv_codeauth = exchange_code_for_token(lv_code, client_secret, client_id, REDIRECT_URI)
    
    #**************************************************************
    print(lv_codeauth)
    #************************************************************

    s = requests.Session()
    s.headers.update({
        "Authorization": "Bearer %s" % lv_codeauth,
      "Content-Type": "application/json"
    })
    payload = {

    }
    url = "https://api.surveymonkey.net/v3/surveys" 
    
    #lv_response = s.get(url, json=payload)
    #print(lv_response)
    #print("Status of the response is -----", lv_response.status_code)
    #print(lv_response.json())
    #lt_json = lv_response.json()
    #lv_total = lt_json['total']
    '''if lv_total < 1:
        print("Total is less than 1. ---",lv_total)
    else:
        print("Total is greater than 1 ----",lv_total)'''
    #lt_data = lt_json['data']
    #print('**************data**************')
    #print(lt_data)
    #print('*************************class code****************')
    
    
    lv_surveymonkey = surveymonkeydatafetch.ApiService(lv_codeauth)
    #lt_result = lv_surveymonkey.get_surveys()
    print('Result of the class*************************')
    #print(lt_result)
    '''
    i = 1
    for lw_data in lt_result['data']:
        lt_surveydetails = lv_surveymonkey.get_json(lw_data['href'])
        print("Survey Details - ", i,'----',lt_surveydetails)
        i = i + 1'''
    print('Get surveys with response only *************************')
    lt_respresult = lv_surveymonkey.get_surveys_with_response()
    print(lt_respresult)
    
    print('Get Survey responses **************************************')
    i = 1
    for lw_survey in lt_respresult['data']:
        print('lw_survey ----',lw_survey)
        
        print('Survey Link is -------',lw_survey['href'])
        #if lw_survey['id'] != '119516433':
        #    continue
        
        lv_survey = surveymonkeydatafetch.SurveyDetails(lv_surveymonkey.client,lw_survey['id'])
        '''
        lt_error = lv_survey.get_questions()
        if "status" in lt_error:
            print('Error in fetching the questions')
        print('Questions for the survey are ------',lw_survey['id'])
        lt_error = lv_survey.get_question_details()
        if "status" in lt_error:
            print('Error in fetching the questions')'''
        lt_error = lv_survey.get_bulk_response()
        if "status" in lt_error:
           print('Error in fetching the Buld Response')
        
        lt_error = lv_survey.get_header_for_survey()
        if "status" in lt_error:
            print('Error in fetching the Survey Header')
        #lv_survey.get_response_formatted()
        lv_survey.download_questions_veritcal_format()
        lv_survey.download_survey_response_vertical_format()
        '''lt_error = lv_survey.get_responses()
        if "status" in lt_error:
            print('Error in fetching the response questions')
        for lw_response in lv_survey.lt_responses:
            lv_response = surveymonkeydatafetch.SurveyResponse(lv_surveymonkey.client,lw_response['href'])
        '''
        '''
        with open('testcol.csv','wb') as lv_file:
            wr = csv.writer(lv_file,quoting=csv.QUOTE_ALL)
            wr.writerow(lv_survey.header)
            wr.writerow(lv_survey.answers)
            for lw_download in lv_survey.lt_download:
                wr.writerow(lw_download)
        
                '''