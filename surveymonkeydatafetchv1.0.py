import requests
import json

HOST = "https://api.surveymonkey.net"
class SurveyResponse(object):
   def __init__(self,i_client,i_href,i_data=None):
      self.client = i_client
      self.href = i_href + '/details'
      lt_params = i_data if i_data is not None else {}
      #read the specific response details
      lv_response = self.client.get(self.href,json = lt_params)
      #get the respnse details in the json format
      lt_responsedetails = lv_response.json()
      #print('Response details for ', self.href,'--------------------------')
      #print(lt_responsedetails)
      self.lt_qandans = {}
      for lw_pages in lt_responsedetails['pages']:
         for lw_question in lw_pages['questions']:
            #print('Question with answer is ---------------------------')
            #print(lw_question)
            self.lt_qandans[lw_question['id']] = lw_question['answers']
      print('Question ids and Asnwers to it are ------------------------------')
      print(self.lt_qandans)
   #def get_answers(self,i_qid):
      #for lw_qandans in self.lt_qandans:
         #self.
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
      self.analyze_url = lt_surveydetails['analyze_url']
      self.summary_url = lt_surveydetails['summary_url']
      self.question_count = lt_surveydetails['question_count']
      #survey id
      self.responseid = lt_surveydetails['id']
      lv_pageurl = lv_url + '/pages'
      lv_responsepage = self.client.get(lv_pageurl,json = lt_params)
      lt_pages = lv_responsepage.json()
      print('*********************************Pages************')
      print(lt_pages)
      self.lt_pages = []
      self.lt_pages = lt_pages['data']
         
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
      return {}   
   def get_header_for_survey(self,i_data=None):
   
         self.get_questions()
         self.get_question_details()
         self.qcolumn = {}

         #print('Length of the Question details is ------',len(self.lt_qdetail))
         i = 1
         self.header = []
         self.answers = []
         for lw_question in self.lt_questions:
            
            lv_fieldname = 'Q' + str(i)
            #self.header[lv_fieldname] = lw_question['heading']
            self.header.append(lw_question['heading'])
            print('Question details -----',i,'-----',self.lt_qdetail[i-1])
            lw_qdetail = self.lt_qdetail[i-1]
            if lw_qdetail['family'] != 'open_ended':
               j = 1
               
               lw_qcolarray = []
               if 'answers' in lw_qdetail:
                  lt_choices = lw_qdetail['answers']['choices']
                  lv_lenchoice = len(lt_choices)
                  self.answers.append(lt_choices[0]['text'])
                  lw_qcolarray.append(lt_choices[0]['text'])
                  while j < lv_lenchoice:
                     lv_fnamechoice = lv_fieldname + '-' + str(j+1)
                     self.answers.append(lt_choices[j]['text'])
                     lw_qcolarray.append(lt_choices[j]['text'])                     
                     self.header.append("")
                     j = j + 1
               if "other" in lw_qdetail['answers']:
                     lv_othertext = lw_qdetail['answers']['other']['text']
                     print('Others Text is -------------------------',lv_othertext)
                     self.answers.append(lv_othertext)
                     self.header.append("")
                     lw_qcolarray.append(lv_othertext) 
               self.qcolumn[lw_question['id']] = lw_qcolarray
            else:
               self.answers.append("")
               #self.answers[lv_fieldname] = ""
               
            i = i + 1
         print('Header for the question is as follows%%%%%%%$$$$$$$$$$$$$$$$$$$$$')   
         print(self.header)
         print('Multiple choice sub header is *********************')
         print(self.answers)
         print('Question ids with their options -----------')
         print(self.qcolumn)
         
         return {}
   def get_bulk_response(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      lv_url = self.href + '/responses/bulk'
      lt_json = self.get_json(lv_url,lt_params)
      print('_________Bulk  Responses are as follows ---------------------')
      print(lt_json)
      return lt_json
   def get_questions(self,i_data=None):
      lt_params = i_data if i_data is not None else {}
      self.lt_questions = []
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
            lv_found = True'''
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
      
     