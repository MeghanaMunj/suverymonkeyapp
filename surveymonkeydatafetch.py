import requests
import json
import csv 
HOST = "https://api.surveymonkey.net"
class SurveyResponse(object):
   def __init__(self,i_response,i_data=None):
      self.lt_qandans = {}
      print('Response is -----------', i_response)
      self.responseid = i_response.get('id')
      for lw_pages in i_response.get('pages'):
         for lw_question in lw_pages.get('questions'):
            #print('Question with answer is ---------------------------')
            #print(lw_question)
            lt_answers = lw_question.get('answers')
            lt_choice = []
            lv_othertext = ""
            lv_text = ""
            lv_choiceflag = False
            lv_otherflag = False
            lv_textflag = False
            lv_questionid = lw_question.get('id')
            #make the response lean and only fetch the choice id , other text or normal question text answer 
            self.lt_qandans[lv_questionid] = {}
            for lw_answer in lt_answers:
               #if answer has choice id then 
               if 'choice_id' in lw_answer:
                  lt_choice.append(lw_answer.get('choice_id'))
                  lv_choiceflag = True
               #if the answer has other option selected    
               if 'other_id' in lw_answer:
                  lv_othertext = lw_answer.get('text')
                  lv_otherflag = True
               #else if the option is text answer    
               elif 'text' in lw_answer:
                  lv_text = lw_answer.get('text')
                  lv_textflag = True
            if lv_choiceflag:
               #if its choice then it will be an list other wise it will will be plain text 
               self.lt_qandans[lv_questionid]['choice'] = lt_choice
            if lv_otherflag:
               self.lt_qandans[lv_questionid]['other'] = lv_othertext
            if lv_textflag:
               self.lt_qandans[lv_questionid]['text'] = lv_text
      print('Question ids and Asnwers to it are ------------------------------')
      print(self.lt_qandans)

class SurveyDetails(object):
   def __init__(self,i_client,i_id,i_data=None):
      #set the client and href
      self.client = i_client
      lv_url = "https://api.surveymonkey.net/v3/surveys/%s" % (i_id)
      self.href = lv_url      
      lt_params = i_data if i_data is not None else {}
      #read the specific survey
      lv_response = self.client.get(self.href,json = lt_params)
      #get the survey details in json format
      lt_surveydetails = lv_response.json() 
      # get response count
      self.response_count = lt_surveydetails.get('response_count')
      #short description
      self.title = lt_surveydetails.get('title')
      #page count
      self.page_count = lt_surveydetails.get('page_count')
      self.question_count = lt_surveydetails.get('question_count')
      #survey id
      self.surveyid = lt_surveydetails.get('id')
      #get all the pages 
      lv_pageurl = lv_url + '/pages'
      lv_responsepage = self.client.get(lv_pageurl,json = lt_params)
      lt_pages = lv_responsepage.json()
      #print('*********************************Pages************')
      #print(lt_pages)
      self.lt_pages = []
      self.lt_pages = lt_pages.get('data')
      '''     
   #This method is now commented as there are many api calls made by it.   
   def get_responses(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      lv_url = self.href + '/responses/'
      self.lt_responses = []
      self.response_count = 0
      lt_json = self.get_json(lv_url,lt_params)      
      if lt_json['status'] != 0:
         return {
                     "status": 1,
                           "errmsg": "Did not receive a valid response "}
      self.lt_responses = lt_json['data']['data']
      self.response_count = lt_json['data']['total']
      print('_________Responses List are as follows ---------------------',self.title)
      print(self.lt_responses)
      return {}   '''
   def download_survey_response_vertical_format(self,i_filepath):   
      #field names list
      lt_qfname = ['surveyid','rid','qid','qheading','qfamily','choice_id','choice_text','text']
      lw_row = {}
      #open response file for each survey 
      with open(i_filepath, 'w') as outfile:
         writer = csv.DictWriter(outfile,fieldnames=lt_qfname)
         #add the header 
         writer.writeheader()
     
     
         for lw_response in self.lt_response:
            
            i = 0
            #for each question in the response
            for lw_question in self.lt_questions:
               lw_row = {}
               lw_row['surveyid'] = self.surveyid
               lw_row['rid'] = lw_response.responseid               
               lv_questionid = lw_question.get('id')
               if lv_questionid in lw_response.lt_qandans:
                  lw_qdetail = self.lt_qdetail[i]
                  lw_row['qid'] = lv_questionid
                  lw_row['qheading'] = lw_question.get('heading')
                  lw_row['qfamily'] = lw_qdetail.get('family')
                  #if the question has choices option 
                  if lw_qdetail.get('family') != 'open_ended':
                     #get all options available for that question id
                     lt_options = self.qcolumn.get(lv_questionid)
                     #for each option 
                     for lw_options in lt_options:
                        #if option is other 
                        if lw_options[0] == 'other' :
                           if 'other' in lw_response.lt_qandans.get(lv_questionid):                     
                              #if its other then take the value from other text box                             
                              lw_file = lw_row
                              lw_file['choice_id'] = 'other'
                              lw_file['choice_text'] = lw_response.lt_qandans.get(lv_questionid).get('other')
                              lw_file['text'] = ''
                              writer.writerow(lw_file)
                        else:
                           #if option is choice 
                           if 'choice' in lw_response.lt_qandans.get(lv_questionid):
                              #if that choice is selected then 
                              if lw_options[0] in lw_response.lt_qandans.get(lv_questionid).get('choice'):
                                    #if its choice then select the text for the choice
                                    lw_file = lw_row
                                    lw_file['choice_id'] = lw_options[0]  
                                    lw_file['choice_text'] = lw_options[1]
                                    lw_file['text'] = ''
                                    writer.writerow(lw_file)
                                    
                  else:
                     #if simple text answer then take text value
                     if lv_questionid in lw_response.lt_qandans:
                        #in this case the choice id will be blank 
                        lw_row['choice_id'] = ''
                        lw_row['choice_text'] = ''
                        lw_row['text'] = lw_response.lt_qandans.get(lv_questionid).get('text')
                        writer.writerow(lw_row)
                        
                     
               i = i + 1
                     
   # Download the questions and their details in vertical format            
   def download_questions_veritcal_format(self,i_filepath):
      
      
      lt_qfname = ['surveyid','qid','qheading','qfamily','choice_id','choice_text']
      with open(i_filepath, 'w') as outfile:
         writer = csv.DictWriter(outfile,fieldnames=lt_qfname)
         writer.writeheader()
       
         i = 0
         #for each question 
         for lw_question in self.lt_questions:
            lw_row = {}
            lv_questionid = lw_question.get('id')
            lw_row['surveyid'] = self.surveyid
            lw_row['qid'] = lv_questionid
            lw_row['qheading'] = lw_question.get('heading')
            lw_qdetail = self.lt_qdetail[i]
            lw_row['qfamily'] = lw_qdetail.get('family')
            #if its choice question then get the choice details 
            if lw_qdetail.get('family') != 'open_ended':
               j = 0
               lw_file = lw_row 
               #list of 2 elements 
               # 1st element - will hold all choice id
               # 2nd element - its corresponding text in each entry
               lw_qcolarray = []
               #if answers are there 
               if 'choices' in lw_qdetail.get('answers'):
                  #get the choices
                  lt_choices = lw_qdetail.get('answers').get('choices')
                  lv_lenchoice = len(lt_choices) 
                  while j < lv_lenchoice:
                     #the first choice text
                     lw_file['choice_id'] = lt_choices[j].get('id')
                     lw_file['choice_text'] = lt_choices[j].get('text')
                     writer.writerow(lw_file)
                     
                     print('Choice entry -------->', lw_file) 
                     j = j + 1
               #if other option is there in possible answers       
               if "other" in lw_qdetail.get('answers'):
                  #get the other text 
                  lv_othertext = lw_qdetail.get('answers').get('other').get('text')
                  lw_file['choice_id'] = 'other'
                  lw_file['choice_text'] = lv_othertext
                  writer.writerow(lw_file)
                  
                  print('Other Entry ----------->', lw_file)
                  
            else:
               lw_row['choice_id'] = ''
               lw_row['choice_text'] = ''
               writer.writerow(lw_row)
               
            i = i + 1
         
            
      
   #Using the survey details create the header for the file
   #it will create attribute header which will be first row of the file
   #it will create attribut answers which will be second row of the file
   def get_header_for_survey(self,i_data=None):
         #get the questions url and the id       
         self.get_questions()
         
         #get the question details - this will fetch the question text
         self.get_question_details()
         # dictionary to hold the questions and the choices in the sequence 
         self.qcolumn = {}

         #print('Length of the Question details is ------',len(self.lt_qdetail))
         i = 1
         #this will be the first row of the csv file with questions followed by blank for number of choices if any
         self.header = []
         # this will be second row of the csv file with choices. If there are no choice it will be blank
         self.answers = []
         for lw_question in self.lt_questions:
            #question text
            self.header.append(lw_question.get('heading'))
            #start with the first question details
            lw_qdetail = self.lt_qdetail[i-1]
            #if its not open_ended means its multichoice
            if lw_qdetail.get('family') != 'open_ended':
               j = 1
               #list of 2 elements 
               # 1st element - will hold all choice id
               # 2nd element - its corresponding text in each entry
               lw_qcolarray = []
               #if answers are there 
               if 'answers' in lw_qdetail:
                  #get the choices
                  lt_choices = lw_qdetail.get('answers').get('choices')
                  lv_lenchoice = len(lt_choices)
                  #the first choice text
                  self.answers.append(lt_choices[0].get('text'))
                  lw_qcolarray.append([lt_choices[0].get('id') , lt_choices[0].get('text')])
                  #for every choice 
                  while j < lv_lenchoice:
                     #get all the answers in the second row of the file
                     self.answers.append(lt_choices[j].get('text'))
                     #get the choice id and its text in list
                     lw_qcolarray.append([lt_choices[j].get('id') , lt_choices[j].get('text')])
                     #from second column of each question the header line will be blank
                     self.header.append("")
                     j = j + 1
               #if other option is there in possible answers       
               if "other" in lw_qdetail.get('answers'):
                     #get the other text 
                     lv_othertext = lw_qdetail.get('answers').get('other').get('text')
                     #corresponding value will be there in second row of the file
                     self.answers.append(lv_othertext)
                     #header row will be blank since other is also option
                     self.header.append("")
                     # in this case the choice id will be selected as 'other' 
                     # and its text will be stored
                     lw_qcolarray.append(['other', lv_othertext])
               #at end add entry of the question in ditionary with the list of choices and its text
               self.qcolumn[lw_question.get('id')] = lw_qcolarray
            else:
               self.answers.append("")               
            i = i + 1
         '''print('Header for the question is as follows%%%%%%%$$$$$$$$$$$$$$$$$$$$$')   
         print(self.header)
         print('Multiple choice sub header is *********************')
         print(self.answers)'''
         print('Question ids with their options -----------')
         print(self.qcolumn)
         
         return {}
   def get_response_formatted(self):
      self.lt_download = []
      #for each Response
      for lw_response in self.lt_response:
         lt_row = []
         #for each question in the response
         for lw_questions in self.lt_questions:
            lv_questionid = lw_questions.get('id')
            #Multi choice answer
            if  lv_questionid in self.qcolumn:
               #get all options available for that question id
               lt_options = self.qcolumn.get(lv_questionid)
               #for each option check if its selected in the aswers
               print('Question is ----',lv_questionid)
               print('Options are ------',lt_options)
               for lw_options in lt_options:
                  #if the answers for that question is fetched by the response bulk method 
                  if lv_questionid in lw_response.lt_qandans:
                     print('Response Question and asnwers are ------------------------')
                     print(lw_response.lt_qandans)
                     if lw_options[0] == 'other' :
                        if 'other' in lw_response.lt_qandans.get(lv_questionid):                     
                           #if its other then take the value from other text box                             
                           lt_row.append(lw_response.lt_qandans.get(lv_questionid).get('other'))
                        else:
                           lt_row.append("")
                     else:
                        #there is assumption that there are only two values other and choice in case of multichoice 
                        if 'choice' in lw_response.lt_qandans[lw_questions['id']]:
                           if lw_options[0] in lw_response.lt_qandans.get(lv_questionid).get('choice'):
                              #if its choice then select the text for the choice
                              lt_row.append(lw_options[1])      
                           else:
                              # if not selected then send blank
                              lt_row.append("")
                        else:
                           # if the particular option is not selected then add blank
                           lt_row.append("")
                  else:
                     lt_row.append("")
            else:
               #if simple text answer then take text value
               if lv_questionid in lw_response.lt_qandans:
                  lt_row.append(lw_response.lt_qandans.get(lv_questionid).get('text'))
               else:
                  lt_row.append("")
         self.lt_download.append(lt_row)
      print('The response details are as follows in columns ****************************')
      print(self.lt_download)
   def get_bulk_response(self,i_data=None):
      self.lt_response = []
      lt_params = i_data if i_data is not None else {}
      lv_url = self.href + '/responses/bulk'
      lv_page = 1
      lv_responseread = 0
      lt_data = []
      while lv_responseread < self.response_count:
         lt_json = self.get_json(lv_url,lt_params)
         print('_________Bulk  Responses are as follows ---------------------')
         print(lt_json)
         if lt_json.get('status') != 0:
            return lt_json
         self.per_page = lt_json.get('data').get('per_page')
         lt_data = lt_data + lt_json.get('data').get('data')
         lv_url = ''
         lv_url = lt_json.get('data').get('links').get('next')
         print('Next Links are -----------------',lv_url)
         
         lv_responseread = lv_responseread + self.per_page
         lv_page = lv_page + 1
         print('-------------------------Data to be analysed--------------------------------------------------')
         print(lt_data)
      for lw_data in lt_data:
         self.lt_response.append(SurveyResponse(lw_data))
      return {}
   def get_questions(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      self.lt_questions = []
      #within every page of the response there are questions - get their details 
      for lw_page in self.lt_pages:
         lv_url = lw_page.get('href') + '/questions'
         print('URL for questions is ----',lv_url)
         lv_response = self.client.get(lv_url,json = lt_params)
         if lv_response.status_code <> 200:
            return {
                     "status": 1,
                          "errmsg": "Did not receive a valid response "}
         lt_json = lv_response.json()
         print(lw_page.get('title') , ' --- Page data is -----------------------')
         print(lt_json.get('data'))
         #for lw_json in lt_json:
         self.lt_questions = self.lt_questions + lt_json.get('data')
      return {}
   def get_json(self,i_url,i_data=None):
      #This method returns the data in json format
      lt_params = i_data if i_data is not None else {}
      lv_response = self.client.get(i_url,json = lt_params)
      if lv_response.status_code <> 200:
         return {
                 "status": 1,
                  "errmsg": "Did not receive a valid response "}
             
      lt_json = lv_response.json()      
      return { 'status': 0, 'data':lt_json}      
   def get_question_details(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      self.lt_qdetail = []
      lt_json = []
      for lw_quest in self.lt_questions:
         print('***********Question details - Question***************')
         print(lw_quest)
         
         lv_url = lw_quest.get('href')
         print('URL for questions details is ----',lv_url)
         lv_response = self.client.get(lv_url,json = lt_params)
         if lv_response.status_code <> 200:
            return {
                     "status": 1,
                          "errmsg": "Did not receive a valid response "}
         lt_json = lv_response.json()
         print('------------------Question Detail is -----------------')
         print(lt_json)
         self.lt_qdetail.append(lt_json)
      return {}
      
class ApiService(object):
   def __init__(self, access_token):
      #initiate the session and update the headers
      self.client = requests.Session()
      self.client.headers.update({
        "Authorization": "Bearer %s" % access_token,
      "Content-Type": "application/json"
      })
   def validate_api(self,i_data=None):
      #validate the status of the api
      # the method will return True if there are any surveys with response
      lt_status = self.get_surveys_with_response(i_data)
      if lt_status.get('status') != 0:
         return False
      else:
         return True
   def get_client(self):
      #Returns the client attribute
      return self.client
   def get_user(self):
      lv_url = "https://api.surveymonkey.net/v3/users/me" 
      lv_response = self.client.get(lv_url)
      if lv_response.status_code <> 200:
         return {
                 "status": 1,
                  "errmsg": "Did not receive a valid response "}
      else:
         lt_json = lv_response.json()
         return { "status":0, 
                  "username": lt_json.get("username"), 
                  "email": lt_json.get("email") }
   def get_json(self,i_url,i_data=None):
      #This method returns the data in json format
      lt_params = i_data if i_data is not None else {}
      lv_response = self.client.get(i_url,json = lt_params)
      if lv_response.status_code <> 200:
         return {
                 "status": 1,
                  "errmsg": "Did not receive a valid response "}
             
      lt_json = lv_response.json()      
      return { 'status': 0, 'data':lt_json}
      
   def get_data(self,i_url,i_data=None):
      #This method returns the status, survey list and the per_page attribute
      lt_params = i_data if i_data is not None else {}
      lv_response = self.client.get(i_url,json = lt_params)
      if lv_response.status_code <> 200:
         return {
                 "status": 1,
                  "errmsg": "Did not receive a valid response "}
             
      lt_json = lv_response.json()      
      lt_data = lt_json.get('data')
      lv_perpage = lt_json.get('per_page')
      return { 'status': 0, 'data':lt_data, 'per_page':lt_json['per_page']}
               
   def get_surveys_with_response(self,i_data=None):
      #This method returns the surveys with responses
      lt_survey_withresp = []
      #get the surveys
      lt_surveys = self.get_surveys(i_data)
      #if error then exit
      if lt_surveys.get('status') != 0:
         return {'status': 1, 'errmsg':'Did not get valid survey data'}
      lv_found = False
      #for each survey
      print('Surveys found ----------------------------------------')
      print(lt_surveys.get('data'))
      lt_survey_withresp=[]
      '''
      ##This to be used when the response_count field is not updated
      for lw_survey in lt_surveys['data']:
         # only select those survey whose reponse_count is > 0
         lv_resurl = lw_survey['href']+'/responses'
         lt_responejson = self.get_json(lv_resurl)
         print('Survey Response json ^^^^^^^^^^^^^^^',lt_responejson)
         if lt_responejson['data']['total'] > 0:
            lt_survey_withresp.append(lw_survey)
            lv_found = True
      '''
      for lw_survey in lt_surveys.get('data'):
         # only select those survey whose reponse_count is > 0
         lv_resurl = lw_survey.get('href')    
         lt_json = self.get_json(lv_resurl)
         print('Survey Json ^^^^^^^^^^^^^^^',lt_json)
         if lt_json.get('data').get('response_count') > 0:
            lt_survey_withresp.append(lw_survey)
            lv_found = True
      if lv_found:
         print('Survey with response are &&&&&&&&&&&&&&&&&&&&&&&&',lt_survey_withresp)
         return {'status': 0, 'data': lt_survey_withresp}
      else:
         return {'status': 1, 'errmsg': 'Did not get any Survey with response'}
   #This method fetches all the surveys   
   def get_surveys(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      lv_url = HOST + "/v3/surveys"
      #if page parameter is passed then get the result for that page
      if "page" in lt_params:
         lt_result = self.get_data(lv_url,lt_params)
         return lt_result
      else:
         #grab all the pages
         lv_current_page = 1
         #initialize the survey array
         lt_survey = []
         while True:
            #pass the page parameter
            lt_params["page"] = lv_current_page
            #get the data for that page
            lv_pageurl = lv_url + '?page=' + str(lv_current_page)
            lt_result = self.get_data(lv_pageurl)
            print('Survey output for page -----',lv_current_page)
            print(lt_result)
            if lt_result.get('status') !=0:
               return lt_result
            #append the survey entries to the final array
            for lw_survey in lt_result.get('data'):
               lt_survey.append(lw_survey)
            #if the surveys in page are same as per page then continue to next page else exit
            if len(lt_result.get('data')) == lt_result.get('per_page'):
               lv_current_page = lv_current_page + 1
            else:
               break
         return { "status": 0, "data": lt_survey}
      
     