import requests
import json
import csv 
HOST = "https://api.surveymonkey.net"
class SurveyResponse(object):
   def __init__(self,i_response,i_data=None):
      self.lt_qandans = {}
      self.responseid = i_response['id']
      for lw_pages in i_response['pages']:
         for lw_question in lw_pages['questions']:
            #print('Question with answer is ---------------------------')
            #print(lw_question)
            lt_answers = lw_question['answers']
            lt_choice = []
            lv_othertext = ""
            lv_text = ""
            lv_choiceflag = False
            lv_otherflag = False
            lv_textflag = False
            #make the response lean and only fetch the choice id , other text or normal question text answer 
            self.lt_qandans[lw_question['id']] = {}
            for lw_answer in lt_answers:
               #if answer has choice id then 
               if 'choice_id' in lw_answer:
                  lt_choice.append(lw_answer['choice_id'])
                  lv_choiceflag = True
               #if the answer has other option selected    
               if 'other_id' in lw_answer:
                  lv_othertext = lw_answer['text']
                  lv_otherflag = True
               #else if the option is text answer    
               elif 'text' in lw_answer:
                  lv_text = lw_answer['text']
                  lv_textflag = True
            if lv_choiceflag:
               #if its choice then it will be an list other wise it will will be plain text 
               self.lt_qandans[lw_question['id']]['choice'] = lt_choice
            if lv_otherflag:
               self.lt_qandans[lw_question['id']]['other'] = lv_othertext
            if lv_textflag:
               self.lt_qandans[lw_question['id']]['text'] = lv_text
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
      self.response_count = lt_surveydetails['response_count']
      #short description
      self.title = lt_surveydetails['title']
      #page count
      self.page_count = lt_surveydetails['page_count']
      self.question_count = lt_surveydetails['question_count']
      #survey id
      self.surveyid = lt_surveydetails['id']
      #get all the pages 
      lv_pageurl = lv_url + '/pages'
      lv_responsepage = self.client.get(lv_pageurl,json = lt_params)
      lt_pages = lv_responsepage.json()
      #print('*********************************Pages************')
      #print(lt_pages)
      self.lt_pages = []
      self.lt_pages = lt_pages['data']
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
   def download_survey_response_vertical_format(self):   
      #field names list
      lt_qfname = ['surveyid','rid','qid','qheading','qfamily','choice_id','choice_text','text']
      lw_row = {}
      #open response file for each survey 
      with open('respfile'+self.surveyid+'.csv', 'w') as outfile:
         writer = csv.DictWriter(outfile,fieldnames=lt_qfname)
         #add the header 
         writer.writeheader()
         for lw_response in self.lt_response:
            lw_row['surveyid'] = self.surveyid
            lw_row['rid'] = lw_response.responseid
            i = 0
            #for each question in the response
            for lw_question in self.lt_questions:
               if lw_question['id'] in lw_response.lt_qandans:
                  lw_qdetail = self.lt_qdetail[i]
                  lw_row['qid'] = lw_question['id']
                  lw_row['qheading'] = lw_question['heading']
                  lw_row['qfamily'] = lw_qdetail['family']
                  #if the question has choices option 
                  if lw_qdetail['family'] != 'open_ended':
                     #get all options available for that question id
                     lt_options = self.qcolumn[lw_question['id']]
                     #for each option 
                     for lw_options in lt_options:
                        #if option is other 
                        if lw_options[0] == 'other' :
                           if 'other' in lw_response.lt_qandans[lw_question['id']]:                     
                              #if its other then take the value from other text box                             
                              lw_file = lw_row
                              lw_file['choice_id'] = 'other'
                              lw_file['choice_text'] = lw_response.lt_qandans[lw_question['id']]['other']
                              lw_file['text'] = ''
                              writer.writerow(lw_file)
                        else:
                           #if option is choice 
                           if 'choice' in lw_response.lt_qandans[lw_question['id']]:
                              #if that choice is selected then 
                              if lw_options[0] in lw_response.lt_qandans[lw_question['id']]['choice']:
                                    #if its choice then select the text for the choice
                                    lw_file = lw_row
                                    lw_file['choice_id'] = lw_options[0]  
                                    lw_file['choice_text'] = lw_options[1]
                                    lw_file['text'] = ''
                                    writer.writerow(lw_file)
                  else:
                     #if simple text answer then take text value
                     if lw_question['id'] in lw_response.lt_qandans:
                        #in this case the choice id will be blank 
                        lw_row['choice_id'] = ''
                        lw_row['choice_text'] = ''
                        lw_row['text'] = lw_response.lt_qandans[lw_question['id']]['text']
                        writer.writerow(lw_row)
                     
               i = i + 1
                     
   # Download the questions and their details in vertical format            
   def download_questions_veritcal_format(self):
      
      
      lt_qfname = ['surveyid','qid','qheading','qfamily','choice_id','choice_text']
      with open('qfile'+self.surveyid+'.csv', 'w') as outfile:
         writer = csv.DictWriter(outfile,fieldnames=lt_qfname)
         writer.writeheader()
         i = 0
         #for each question 
         for lw_question in self.lt_questions:
            lw_row = {}
            lw_row['surveyid'] = self.surveyid
            lw_row['qid'] = lw_question['id']
            lw_row['qheading'] = lw_question['heading']
            lw_qdetail = self.lt_qdetail[i]
            lw_row['qfamily'] = lw_qdetail['family']
            #if its choice question then get the choice details 
            if lw_qdetail['family'] != 'open_ended':
               j = 0
               lw_file = lw_row 
               #list of 2 elements 
               # 1st element - will hold all choice id
               # 2nd element - its corresponding text in each entry
               lw_qcolarray = []
               #if answers are there 
               if 'choices' in lw_qdetail['answers']:
                  #get the choices
                  lt_choices = lw_qdetail['answers']['choices']
                  lv_lenchoice = len(lt_choices) 
                  while j < lv_lenchoice:
                     #the first choice text
                     lw_file['choice_id'] = lt_choices[j]['id']
                     lw_file['choice_text'] = lt_choices[j]['text']
                     writer.writerow(lw_file)
                      
                     j = j + 1
               #if other option is there in possible answers       
               if "other" in lw_qdetail['answers']:
                  #get the other text 
                  lv_othertext = lw_qdetail['answers']['other']['text']
                  lw_file['choice_id'] = 'other'
                  lw_file['choice_text'] = lv_othertext
                  writer.writerow(lw_file)
                  
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
            self.header.append(lw_question['heading'])
            #start with the first question details
            lw_qdetail = self.lt_qdetail[i-1]
            #if its not open_ended means its multichoice
            if lw_qdetail['family'] != 'open_ended':
               j = 1
               #list of 2 elements 
               # 1st element - will hold all choice id
               # 2nd element - its corresponding text in each entry
               lw_qcolarray = []
               #if answers are there 
               if 'answers' in lw_qdetail:
                  #get the choices
                  lt_choices = lw_qdetail['answers']['choices']
                  lv_lenchoice = len(lt_choices)
                  #the first choice text
                  self.answers.append(lt_choices[0]['text'])
                  lw_qcolarray.append([lt_choices[0]['id'] , lt_choices[0]['text']])
                  #for every choice 
                  while j < lv_lenchoice:
                     #get all the answers in the second row of the file
                     self.answers.append(lt_choices[j]['text'])
                     #get the choice id and its text in list
                     lw_qcolarray.append([lt_choices[j]['id'] , lt_choices[j]['text']])
                     #from second column of each question the header line will be blank
                     self.header.append("")
                     j = j + 1
               #if other option is there in possible answers       
               if "other" in lw_qdetail['answers']:
                     #get the other text 
                     lv_othertext = lw_qdetail['answers']['other']['text']
                     #corresponding value will be there in second row of the file
                     self.answers.append(lv_othertext)
                     #header row will be blank since other is also option
                     self.header.append("")
                     # in this case the choice id will be selected as 'other' 
                     # and its text will be stored
                     lw_qcolarray.append(['other', lv_othertext])
               #at end add entry of the question in ditionary with the list of choices and its text
               self.qcolumn[lw_question['id']] = lw_qcolarray
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
            #Multi choice answer
            if lw_questions['id'] in self.qcolumn:
               #get all options available for that question id
               lt_options = self.qcolumn[lw_questions['id']]
               #for each option check if its selected in the aswers
               print('Question is ----',lw_questions['id'])
               print('Options are ------',lt_options)
               for lw_options in lt_options:
                  #if the answers for that question is fetched by the response bulk method 
                  if lw_questions['id'] in lw_response.lt_qandans:
                     print('Response Question and asnwers are ------------------------')
                     print(lw_response.lt_qandans)
                     if lw_options[0] == 'other' :
                        if 'other' in lw_response.lt_qandans[lw_questions['id']]:                     
                           #if its other then take the value from other text box                             
                           lt_row.append(lw_response.lt_qandans[lw_questions['id']]['other'])
                        else:
                           lt_row.append("")
                     else:
                        #there is assumption that there are only two values other and choice in case of multichoice 
                        if 'choice' in lw_response.lt_qandans[lw_questions['id']]:
                           if lw_options[0] in lw_response.lt_qandans[lw_questions['id']]['choice']:
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
               if lw_questions['id'] in lw_response.lt_qandans:
                  lt_row.append(lw_response.lt_qandans[lw_questions['id']]['text'])
               else:
                  lt_row.append("")
         self.lt_download.append(lt_row)
      print('The response details are as follows in columns ****************************')
      print(self.lt_download)
   def get_bulk_response(self,i_data=None):
      self.lt_response = []
      lt_params = i_data if i_data is not None else {}
      lv_url = self.href + '/responses/bulk'
      lt_json = self.get_json(lv_url,lt_params)
      print('_________Bulk  Responses are as follows ---------------------')
      print(lt_json)
      if lt_json['status'] != 0:
         return lt_json
      lv_count = lt_json['data']['total']
      for lw_data in lt_json['data']['data']:
          self.lt_response.append(SurveyResponse(lw_data))
          
      return {}
   def get_questions(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      self.lt_questions = []
      #within every page of the response there are questions - get their details 
      for lw_page in self.lt_pages:
         lv_url = lw_page['href'] + '/questions'
         print('URL for questions is ----',lv_url)
         lv_response = self.client.get(lv_url,json = lt_params)
         if lv_response.status_code <> 200:
            return {
                     "status": 1,
                          "errmsg": "Did not receive a valid response "}
         lt_json = lv_response.json()
         print(lw_page['title'] , ' --- Page data is -----------------------')
         print(lt_json['data'])
         #for lw_json in lt_json:
         self.lt_questions = self.lt_questions + lt_json['data']     
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
         
         lv_url = lw_quest['href'] 
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
      if lt_status['status'] != 0:
         return False
      else:
         return True
   def get_client(self,):
      #Returns the client attribute
      return self.client
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
      lt_data = lt_json['data']
      lv_perpage = lt_json['per_page']
      return { 'status': 0, 'data':lt_data, 'per_page':lt_json['per_page']}
               
   def get_surveys_with_response(self,i_data=None):
      #This method returns the surveys with responses
      lt_survey_withresp = []
      #get the surveys
      lt_surveys = self.get_surveys(i_data)
      #if error then exit
      if lt_surveys['status'] != 0:
         return {'status': 1, 'errmsg':'Did not get valid survey data'}
      lv_found = False
      #for each survey
      print('Surveys found ----------------------------------------')
      print(lt_surveys['data'])
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
      for lw_survey in lt_surveys['data']:
         # only select those survey whose reponse_count is > 0
         lv_resurl = lw_survey['href']      
         lt_json = self.get_json(lv_resurl)
         print('Survey Json ^^^^^^^^^^^^^^^',lt_json)
         if lt_json['data']['response_count'] > 0:
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
            lt_result = self.get_data(lv_url,lt_params)
            if lt_result['status'] !=0:
               return lt_result
            #append the survey entries to the final array
            for lw_survey in lt_result['data']:
               lt_survey.append(lw_survey)
            #if the surveys in page are same as per page then continue to next page else exit
            if len(lt_result['data']) == lt_result['per_page']:
               lv_current_page = lv_current_page + 1
            else:
               break
         return { "status": 0, "data": lt_survey}
      
     