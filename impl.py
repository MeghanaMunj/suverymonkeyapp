__author__ = ''

import os

import const
import json
import  logging as log
import sdk.const as sdkconst
from sdk.const import COMMON_CONFIG_FIELDS, \
    COMMON_IDENTITY_FIELDS, NAME, VALUE
from const import CONFIG_FIELDS, IDENTITY_FIELDS
from threep.base import ThreePBase
from sdk.utils import get_key_value_label, make_kv_list

# Insert your import statements here
from runtime_import.libs.suverymonkeyapp.util import surveymonkeyDataYielder
import urllib
import urllib2
import surveymonkeydatafetch
import requests
# End of import statements


class surveymonkeyManager(ThreePBase):
    """
    This is main class using which Mammoth framework interacts with third party API
    plugin (referred as API hereinafter). Various responsibilities of this class
    is to manage/update identities, ds_configs and few more interfaces to handle API logic

    """

    def __init__(self, storage_handle, api_config):
        
        self.config_file = "/".join([os.path.dirname(__file__), const.CONFIG_FILE])
        super(surveymonkeyManager, self).__init__(storage_handle, api_config)


    def get_identity_spec(self, auth_spec):
        """
           This function is called to render the form on the authentication screen. It provides the render specification to
        the frontend.

        In the simplest case just return the provided auth_spec parameter.
        """
        SM_API_BASE = "https://api.surveymonkey.net"
        ACCESS_TOKEN_ENDPOINT = "/oauth/authorize"
        REDIRECT_URI = "https://redirect.mammoth.io/redirect/oauth2"
        '''
        #user id - megmunj@gmail.com
        client_id = "oExDyiCTQOKf-oYOzXzE0w"
        client_secret = "231452587066024730312549141434044897569"
        '''
        #user id - devmammoth 
        client_id = "uZ96HzyISGWErTw4wyyUfw"
        client_secret = "81506191360428165871720130634287353605"
        
        
        url_params = urllib.urlencode({
            'redirect_uri': REDIRECT_URI,
            'client_id': client_id,
            'response_type': 'code'})        
        oauth_url = SM_API_BASE + ACCESS_TOKEN_ENDPOINT + '?' + url_params
        oauth_save_url = "http://localhost:6346/sandbox?integration_key=surveymonkey"
        auth_spec["AUTH_URL"] = oauth_url + "&state=" + urllib2.quote(oauth_save_url)
        
        return auth_spec
        
        

    def get_identity_config_for_storage(self, params=None):
        """
        :param params: dict, required to generate identity_config dict object for storage
        :return: newly created identity_config. The value obtained in params is
        a dictionary that should contain following keys:
        
        """
        config = {
            const.IDENTITY_FIELDS.NAME: params.get(const.IDENTITY_FIELDS.NAME),
            #sdkconst.COMMON_IDENTITY_FIELDS.NAME: params.get(const.IDENTITY_FIELDS.NAME, 'untitled'),
        }
        client_id = "uZ96HzyISGWErTw4wyyUfw"
        client_secret = "81506191360428165871720130634287353605"
        lv_auth_code = params.get("code")
        SM_API_BASE = "https://api.surveymonkey.net"
        ACCESS_TOKEN_ENDPOINT = "/oauth/token"
        oauth_save_url = "http://localhost:6346/sandbox?integration_key=surveymonkey"
        REDIRECT_URI = "https://redirect.mammoth.io/redirect/oauth2"
        REDIRECT_URI = REDIRECT_URI + "&state=" + urllib2.quote(oauth_save_url)
        #REDIRECT_URI = "http://http://127.0.0.1"
        
        data = {
            "client_secret": client_secret,
            "code": lv_auth_code,
            "redirect_uri": "https://redirect.mammoth.io/redirect/oauth2",
            "client_id": client_id,
            "grant_type": "authorization_code",
        }

        access_token_uri = SM_API_BASE + ACCESS_TOKEN_ENDPOINT 
        
        access_token_response = requests.post(access_token_uri, data=data)
        
        access_json = access_token_response.json()
        print("**********Access tocken response",access_token_response)
        access_json = access_token_response.json()
        print("***************access token response json*************",access_json)    
        if 'access_token' in access_json:
            lv_access_token =  access_json['access_token']
        else:
            lv_access_token = None
        print("Access token is ---------------------",lv_access_token)
        print("********PARAMS are *****************", params)
        print("Common identity fields are ************",COMMON_IDENTITY_FIELDS)
        
        print("++++++++++++++++++++++++++++authorization code ->",params.get("code"))
        
        # create an identity dictionary and store this with the storage handle.
        identity_config = { "auth_code" : lv_auth_code,
                            "access_token" : lv_access_token
        }
        print('Config Name ---------------------------------------')
        if params.get(COMMON_IDENTITY_FIELDS.NAME):
            identity_config[COMMON_IDENTITY_FIELDS.NAME] = params.get(
                COMMON_IDENTITY_FIELDS.NAME)
        else:

            lv_smapi = surveymonkeydatafetch.ApiService(lv_access_token)
            lt_user = lv_smapi.get_user()
            if lt_user.get('status') == 0:
                print('User information is as follows --------------------')
                print(lt_user)
                identity_config[sdkconst.COMMON_IDENTITY_FIELDS.NAME] = lt_user.get('username') + ' - ' + lt_user.get('email')  
            else:
                identity_config[sdkconst.COMMON_IDENTITY_FIELDS.NAME] = "unspecified_name"
        print("Identity config -------",identity_config)
        
        return identity_config

    def validate_identity_config(self, identity_config):
        """
            :param identity_config:
            :return: True/False: whether the given identity_config is valid or not
        """
        
        print("inside validate method --------*****************************",identity_config)
        if "access_token" in identity_config:
            lv_smapi = surveymonkeydatafetch.ApiService(identity_config.get("access_token"))
            lv_flag = lv_smapi.validate_api()
            print("*****************validate results ************",lv_flag)
            return lv_flag
        else:
            return False

    def format_identities_list(self, identity_list):
        """
        :param identity_list: all the existing identities, in the
        following format:
            {
                IDENTITY_KEY_1: identity_config_1,
                IDENTITY_KEY_2: identity_config_2,
                ...
            }
        :return:Returns extracted list of  all identities, in the following format:
          [
            {
                name: DISPLAY_NAME_FOR_IDENTITY_1
                value: IDENTITY_KEY_1
            },
            {
                name: DISPLAY_NAME_FOR_IDENTITY_2
                value: IDENTITY_KEY_2
            },
            ...

          ]
        """
        # using make_kv_list method here, You can use your own logic.

        formatted_list = make_kv_list(identity_list, sdkconst.FIELD_IDS.VALUE,
                                       sdkconst.FIELD_IDS.NAME)
        return formatted_list


    def delete_identity(self, identity_config):
        """
            put all the logic here you need before identity deletion and
            if identity can be deleted, return True else False
            returning true will delete the identity from the system.

            :param identity_config: identity
            :return:
        """
        return True

    def get_ds_config_spec(self, ds_config_spec,
                           identity_config, params=None):
        """
            :param ds_config_spec: ds_config_spec from json spec.
            :param identity_config: corresponding identity object for which
                ds_config_spec are being returned
            :param params: additional parameters if any
            :return:  ds_config_spec.
            Any dynamic changes to ds_config_spec, if required, should be made here.
        """
        items = []
        if "access_token" in identity_config:
            lv_smapi = surveymonkeydatafetch.ApiService(identity_config.get("access_token"))
            lw_surveys = lv_smapi.get_surveys_with_response()
            print("Surveys ----------------------------------------------",lw_surveys )
            if lw_surveys['status'] != 0:
                return ds_config_spec
            else:
                for lw_sur in lw_surveys['data']:
                    items.append({"selectable": False,
                                  'selected': True,
                                  "name": lw_sur.get('title'),
                                  'value': lw_sur.get('id')
                                  })
            print("setting the config value +++++++++++")

            print('Items Survey ----', items)
            ds_config_spec['ux']['attributes']['surveys']['items'] = items
            items = []
            items.append({"selectable": False,
                                  'selected': True,
                                  "name": 'Questions',
                                  'value': 'Q'
                                  })
        
            items.append({"selectable": False,
                                  'selected': True,
                                          "name": 'Response',
                                          'value': 'R'
                                          })
            ds_config_spec['ux']['attributes']['download']['items'] = items
            print("Value of DS config-------",ds_config_spec['ux']['attributes']['download']['items'])
        return ds_config_spec

    def get_ds_config_for_storage(self, params=None):
        """
        :param params: dict, required to generate ds_config dict object for storage
        :return: newly created ds_config. The value obtained in params is
        a dictionary that should contain following keys:
             surveys,
             name,
        
        """

        ds_config = {
            CONFIG_FIELDS.SURVEYS: params.get(CONFIG_FIELDS.SURVEYS),
            CONFIG_FIELDS.download: params.get(CONFIG_FIELDS.download)
        }

        return ds_config

    def format_ds_configs_list(self, ds_config_list, params=None):
        """
            :param ds_config_list: all the existing ds_configs, in the
            following format:
                {
                    CONFIG_KEY_1: ds_config_1,
                    CONFIG_KEY_2: ds_config_2,
                    ...
                }
            :param params: Additional parameters, if any.
            :return:Returns extracted list of  all ds_configs, in the following format:
              [
                {
                    name: DISPLAY_NAME_FOR_CONFIG_1
                    value: CONFIG_KEY_1
                },
                {
                    name: DISPLAY_NAME_FOR_CONFIG_2
                    value: CONFIG_KEY_2
                },
                ...
        """

        formatted_list = make_kv_list(ds_config_list, sdkconst.VALUE, sdkconst.NAME)
        return formatted_list


    def is_connection_valid(self, identity_config, ds_config=None):
        """
            :param identity_key:
            :param ds_config_key:
            :return: Checks weather the connection specified by provided identity_key and ds_config_key is valid or not. Returns True if valid,
                     False if invalid
        """
        return True

    def sanitize_identity(self, identity):
        """
            update identity object with some dynamic information you need to fetch
            everytime from server. for e.g. access_token in case of OAUTH
            :param identity:
            :return:
        """
        return identity

    def validate_ds_config(self, identity_config, ds_config):
        """
            :param identity_config: identity object
            :param ds_config: ds_config object
            :return: dict object with a mandatory key "is_valid",
            whether the given ds_config is valid or not
        """
        return {'is_valid':True}

    def get_data(self, identity_key, config_key, start_date=None,
                 end_date=None,
                 batch_id=None, storage_handle=None, api_config=None):
        """

        :param self:
        :param identity_key:
        :param config_key:
        :param start_date:
        :param end_date:
        :param batch_id: TODO - replace it with a dict
        :param storage_handle:
        :param api_config:
        :return: instance of DataYielder class defined in util.py
        """
        return surveymonkeyDataYielder(storage_handle,
                    api_config,
                    identity_key,
                    config_key,
                    start_date, end_date, batch_id=batch_id)

    def get_display_info(self, identity_config, ds_config):
        """
            :param self:
            :param identity_config:
            :param ds_config:
            :return: dict object containing user facing information extracted from
             the given identity_config and ds_config.
        """
        pass

    def sanitize_ds_config(self, ds_config):
        """
            :param ds_config:
            :return:

            update ds_config object with some dynamic information you need to update
            every time from server.
        """
        return ds_config

    def augment_ds_config_spec(self, identity_config, params):
        """
            :param params: dict object containing subset ds_config parameters
            :param identity_config:
            :return: dict in the form : {field_key:{property_key:property_value}}
            this method is used to update/augment ds_config_spec with some dynamic
            information based on inputs received
        """
        return {}

    def update_ds_config(self, ds_config, params):
        """
            :param ds_config:
            :param params: dict object containing information required to update ds_config object
            :return: updated ds_config dict
        """
        return ds_config

    def if_identity_exists(self, existing_identities, new_identity):
        """
            :param existing_identities: dict of existing identities
            :param new_identity: new identity dict
            :return: True/False if the new_identity exists already
            in  existing_identities

        """
        return False

    def get_data_sample(self, identity_config, ds_config):
        """
            :param identity_config:
            :param ds_config:
            :return: data sample in the following format:
            {
                "metadata": [],
                "rows": []
            }

            metadata : metadata as a list of dictionaries in the following format
                {
                    'internal_name': UNIQUE COLUMN IDENTIFIER,
                    'display_name': COLUMN HEADER,
                    'type': COLUMN DATATYPE -  TEXT/DATE/NUMERIC
               }

        """
        return {}

    def list_profiles(self, identity_config):
        """
            :param identity_config: for which profiles have to be returned

            :return:Returns list of  all profiles for a given identity_config,
            in the following format:
              [
                {
                    name: DISPLAY_NAME_FOR_PROFILE_1
                    value: PROFILE_IDENTIFIER_1
                },
                {
                    name: DISPLAY_NAME_FOR_PROFILE_2
                    value: PROFILE_IDENTIFIER_2
                },
                ...

              ]
        """
        return []

    def delete_ds_config(self, identity_config, ds_config):
        """
            :param identity_config:
            :param ds_config:
            :return: delete status

            put all the pre deletion logic here for ds_config and
            if ds_config can be deleted, return True else False
            returning true will delete the ds_config from the system
        """
        return True