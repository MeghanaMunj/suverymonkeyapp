# encoding: utf-8
import logging
import const
import sdk.const as sdkconst
from threep.base import DataYielder
import csv
import surveymonkeydatafetch

log = logging


class surveymonkeyDataYielder(DataYielder):
    def __init__(self, *args, **kwargs):
        self.knowledge = None
        self.batchId = kwargs.get(sdkconst.KEYWORDS.BATCH_ID)
        del kwargs[sdkconst.KEYWORDS.BATCH_ID]
        super(surveymonkeyDataYielder, self).__init__(*args, **kwargs)

    def get_format_spec(self):
        """
            :return: format spec as a dictionary in the following format:
                {
                    UNIQUE_COLUMN_IDENTIFIER_1: FORMAT_SPEC for column1,
                    UNIQUE_COLUMN_IDENTIFIER_2: FORMAT_SPEC for column2
                    ...
                }
                FORMAT_SPEC examples:
                 for a DATE type column format could be : '%d-%b-%Y', so, it's entry
                 in the spec would look like:
                        COLUMN_IDENTIFIER: '%d-%b-%Y'

            """
        return {}

    def get_data_as_csv(self, file_path):
        """
            :param file_path: file path where csv results has to be saved
            :return: dict object mentioning csv download status, success/failure
            TODO: return dict format to be standardized
        """
        print('*****************DS config data *******************')
        print(self.ds_config)
        print(self.identity_config)
        lv_smapi = surveymonkeydatafetch.ApiService(self.identity_config.get("access_token"))
        lv_client = lv_smapi.get_client()
        lv_survey = surveymonkeydatafetch.SurveyDetails(lv_client,self.ds_config.get('surveys'))
        lv_survey.get_header_for_survey()
        lv_download = self.ds_config.get('download')
        if lv_download == 'Q':
            lv_survey.download_questions_veritcal_format(file_path)

                
        else:
            lv_survey.get_bulk_response()
            lv_survey.download_survey_response_vertical_format(file_path)
            
        return {}

    def _setup(self):
        """
            one time computations required to pull data from third party service.
            Apart from basic variable initialization done in __init__ method of
            same class, all other datapull readiness logic should be here
       """
        #['surveyid','rid','qid','qheading','qfamily','choice_id','choice_text','text']
        ds_config_key = self.config_key
        identity_key = self.identity_key
        self.identity_config = self.storage_handle.get(sdkconst.NAMESPACES.IDENTITIES,
                                                       identity_key)

        self.ds_config = self.storage_handle.get(identity_key, ds_config_key)

        lv_download = self.ds_config.get('download')
        if lv_download == 'Q':
            self.knowledge = [{
            'internal_name': 'surveyid',
            'display_name': 'Survey ID',
            'type': 'TEXT'
            },
            {
                'internal_name': 'qid',
                'display_name': 'Question ID',
                'type': 'TEXT'
            },
            {
                'internal_name': 'qheading',
                'display_name': 'Question Heading',
                'type': 'TEXT'
            },
            {
                'internal_name': 'qfamily',
                'display_name': 'Question Family',
                'type': 'TEXT'
            },
            {
                'internal_name': 'choice_id',
                'display_name': 'Choice ID',
                'type': 'TEXT'
            },
            {
                'internal_name': 'choice_text',
                'display_name': 'Choice Text',
                'type': 'TEXT'
            }            
            ]
        else:
            self.knowledge = [{
            'internal_name': 'surveyid',
            'display_name': 'Survey ID',
            'type': 'TEXT'
            },
            {
                'internal_name': 'rid',
                'display_name': 'Response ID',
                'type': 'TEXT'
            },
            {
                'internal_name': 'qid',
                'display_name': 'Question ID',
                'type': 'TEXT'
            },
            {
                'internal_name': 'qheading',
                'display_name': 'Question Heading',
                'type': 'TEXT'
            },
            {
                'internal_name': 'qfamily',
                'display_name': 'Question Family',
                'type': 'TEXT'
            },
            {
                'internal_name': 'choice_id',
                'display_name': 'Choice ID',
                'type': 'TEXT'
            },
            {
                'internal_name': 'choice_text',
                'display_name': 'Choice Text',
                'type': 'TEXT'
            },
            {
                'internal_name': 'text',
                'display_name': 'Text Answer',
                'type': 'TEXT'
            }            
            ]
        
            
        

    def reset(self):
        """
            use this method to reset parameters, if needed, before pulling data.
            For e.g., in case, you are using cursors to pull, you may need to reset
            cursor object after sampling rows for metadata computation
            """
        pass

    def describe(self):
        """
            :return: metadata as a list of dictionaries in the following format
                {
                    'internal_name': UNIQUE COLUMN IDENTIFIER,
                    'display_name': COLUMN HEADER,
                    'type': COLUMN DATATYPE -  TEXT/DATE/NUMERIC
               }
        """
        return {}
