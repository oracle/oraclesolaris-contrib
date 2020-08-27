#!/usr/bin/env python
# coding: utf-8

# # Notebook for Working With Oracle Solaris Compliance Through its REST API
# 
# This Jupyter Notebook is aimed at showing how you can use the REST interface in Oracle Solaris to work with its Compliance framework. The REST API is layered on top of the Oracle Solaris Remote Administration Deamon (RAD), and gives access to all the RAD modules through REST. This notebook is using Python to run all the tasks. </br></br>
# In this notebook we'll show how to connect to the REST interface and how to perform the various tasks you can do through REST.
# 
# > *Note 1* — You'll need to enable the `svc:/system/rad:remote` service to be able to remotely connect. </br> 
# > *Note 2* — If the server doesn't have a certification signed by a public CA pull in `/etc/certs/localhost/host-ca/hostca.crt` from your server. </br> 
# > *Note 3* — The user you use to connect to the system will need to have either the `Compliance Assessor` or `Compliance Reporter` profiles set to be able perform these tasks. </br>
# > *Note 4* — This notebook was written with Python 3.7
# 
# Here are the steps on what to do.
# 
# ## Imports and Setting Variables
# 
# First to import all the Python libraries:

# In[ ]:


import requests
import json
import base64
import os
import time
import pandas as pd


# Turning off warnings thrown by Python:

# In[ ]:


import warnings
warnings.filterwarnings('ignore')


# Next pull in the variables needed for this notebook.
# 
# Defining variables:

# In[ ]:


config_filename = 'base_login_root_wel.json'

base_authentication_uri = 'api/authentication/1.0/Session/'
base_compliance_uri = 'api/com.oracle.solaris.rad.compliance_mgr/1.0/'
compliance_assessment_uri = '{}Assessment/'.format(base_compliance_uri)


# The system specific information is located in a JSON file and is structured like this: </br>
# 
# ```json
# {
#     "server_name": "<ip address>",
#     "server_port": "<RAD Remote port>",
#     "cert_location": "<path_to_cert>",
#     "config_json": {
#         "username": "<username>",
#         "password": "<password>",
#         "scheme": "pam",
#         "preserve": true,
#         "timeout": -1
#     }
# }
# ``` 
# 
# If you don't want to use a certificate set `"cert_location": false` instead of the location of the cert file. If your server has a certificate signed by a public CA set `"cert_location": true`.
# 
# Loading this system specific information:

# In[ ]:


if config_filename:
    with open(config_filename, 'r') as f:
        server_connection_info = json.load(f)
        
server_connection_info['server_name']


# ---
# ## Base Functions
# 
# Next we define the base functions used to make the connection with the REST interface. The first is to establish a session, the second is for the regular GET, PUT, POST, and DELETE tasks.
# 
# > *Note* — This needs to be extended to correctly use the Certs
# 
# The function to establish a session:

# In[ ]:


def rad_rest_login(session_name, server_connection_info, base_authentication_uri):
    login_url = 'https://{0}:{1}/{2}'.format(*list(map(server_connection_info.get, ['server_name', 'server_port'])), base_authentication_uri)
    print("Logging in with this URL: " + login_url)

    try:
        response = session_name.post(login_url, json = server_connection_info['config_json'], verify = server_connection_info['cert_location'])
    except:
        print('no connection')
        response = 'empty'
    
    return response


# The function to run regular requests:

# In[ ]:


def rad_rest_request(request_type, session_name, server_connection_info, rad_rest_uri, payload = None):
    
    # Create a list of variables
    query_vars = list(map(server_connection_info.get, ['server_name', 'server_port']))
    query_vars.append(rad_rest_uri)

    # Create query url to be used
    query_url = 'https://{0}:{1}/{2}'.format(*query_vars)

    response = session_name.request(request_type, query_url, json = payload)
    
    return response


# ---
# The following section now shows the various commands you can run. First it'll explore the `Assessment/` part of the API, this handles all the things related to the assessments, their info, creation, deletion, etc.
# 
# ## Logging in and setting up a session
# 
# First establish the session and bring in the necessary credentials. Note we're printing the results to give a better insight on what's coming back, we won't be doing this for every request just a few to give you a feel:

# In[ ]:


s = requests.Session()

login_answer = rad_rest_login(s, server_connection_info, base_authentication_uri)

# printing the answers coming back to show the proces.
print(login_answer.status_code)
print(login_answer.text)


# ---
# ## Getting a list of all the current reports on the system
# 
# Now to get a list of all the current reports on the system, first we query the generic URI which gives back a list of `href` objects. These are the individual report URIs which we can use to get more information about the reports and even to fetch the reports. This is assuming there are already some reports on the system.</br></br>
# First we fetch the list of reports:

# In[ ]:


query_answer = rad_rest_request('GET', s, server_connection_info, compliance_assessment_uri)
query_text = json.loads(query_answer.text)

print(query_answer.status_code, '\n')
print(query_text)


# ---
# Now we have the report URI's we can use these to fetch more information about each URI. This next code runs through the list, pulls out the URI and then uses `/metadata` appended to the end to get extra information about the reports. We've added a `for` loop to iterate through each element in the response and print them out nicely:

# In[ ]:


for element in query_text['payload']:
    print('Getting metadata for: {}'.format(element['href'].split('/')[-1]))
    element_answer = rad_rest_request('GET', s, server_connection_info, '{}{}/metadata'.format(compliance_assessment_uri, element['href'].split('/')[-1]))
    element_text = json.loads(element_answer.text)
    
print('\nPrinting full metadata for: {}'.format(element['href'].split('/')[-1]))   
for key, item in element_text['payload'].items():
    print(key, ':', item)
print()


# ---
# This does the same but now pulls the data into a Pandas dataframe:

# In[ ]:


query_df = pd.DataFrame()
for element in query_text['payload']:
    element_answer = rad_rest_request('GET', s, server_connection_info, '{}{}/metadata'.format(compliance_assessment_uri, element['href'].split('/')[-1]))
    query_series = pd.read_json(element_answer.text)
    query_df = query_df.append(query_series['payload'], ignore_index = True) 


# In[ ]:


query_df


# Once you pull this data into Pandas it becomes very easy to find and select specific assessments by their characteristics, especially at scale.
# 
# For example if you just want to find the assessments that contain `'solaris.Baseline'` in their name you filter it this way:

# In[ ]:


query_df[query_df['Name'].str.contains('solaris.Baseline')]


# This you could use any value in the table to search on or sort the data with.
# 
# ---
# Next we use one of the reports — the one that happens to be the first in the list — and use the `/contents` method to fetch the full report for this assessment. The full report contains `report.html`, `state`, `log`, and `results.xccdf.xml` as individual elements, we first have to decode it from the `base64` encoding it's in and can then safe the file to disk. For connvenience we've created a subdirectory named after the assessment's UUID:

# In[ ]:


test_assessment = query_text['payload'][0]['href'].split('/')[-1]
print('getting the report for {}:'.format(test_assessment))
report_answer = rad_rest_request('GET', s, server_connection_info, '{}{}/contents'.format(compliance_assessment_uri, test_assessment))
report_text = json.loads(report_answer.text)

assessment_path = 'assessments/{}'.format(test_assessment)
os.makedirs(assessment_path, exist_ok = True)

for key in report_text['payload']:
    print('Saving {}'.format(key))
    file_name = '{}/{}'.format(assessment_path, key)
    with open(file_name, 'wb') as file:
        file.write(base64.b64decode(report_text['payload'][key]))


# This an easy way of pulling across the reports you're looking for over REST.
# 
# ---
# 
# ## Starting a new assessment
# 
# This section shows how to kick off a new compliance assessment. 
# 
# * first this happens with a `POST` command to create the assessment 
# * we pull in the UUID of the new assessment
# * then we check if it was created successfully
# * and then there’s a `PUT` command to set it’s state to `“AS_RUNNING”`
# * once this has been set the compliance assessment will start and we can track it's progress
# 
# ---
# 
# In case we want to use the current datetime in the assessment name we create a function that can generate it:

# In[ ]:


def get_time_stamp():
    time_zone = timezone(timedelta(hours = -7))
    return datetime.now(tz = time_zone).strftime('%Y-%m-%d,%H:%M')


# Generating a dict with the benchmark, profile, and name for the assessment:

# In[ ]:


benchmark = 'solaris'
profile = 'Baseline'

# the option to choose the assessment name
name = 'my_assess_2'
# name = '{}.{}.{}'.format(benchmark, profile, get_time_stamp())

json_body = {'benchmark': benchmark , 'profile' : profile, 'name': name}
json_body


# ---
# Now we use a `POST` command to create the assessment. In return we receive the `href` reference for the newly created assessment.

# In[ ]:


post_response = rad_rest_request('POST', s, server_connection_info, compliance_assessment_uri, json_body)
post_response_text = json.loads(post_response.text)
post_response_uri = post_response_text['payload']['href'][1:]

print(post_response.status_code)
print(post_response_text)
print(post_response_uri)


# ---
# We can now fetch the assessment UUID by using this `href` reference. We want to do this because the reference is temporary where the UUID is fixed.

# In[ ]:


request_uuid = json.loads(rad_rest_request('GET', s, server_connection_info, '{}/uuid'.format(post_response_uri)).text)
print(request_uuid)

post_response_uuid = '{}{}'.format(compliance_assessment_uri, request_uuid['payload'])
print(post_response_uuid)


# ---
# Once we have the tthe assessment UUID we can check it's current state, this should be `"As_CREATING"`:

# In[ ]:


get_state = rad_rest_request('GET', s, server_connection_info, '{}/state'.format(post_response_uuid))

print(json.loads(get_state.text))


# ---
# To now start the assessment we set it's state to `"AS_RUNNING"`. Note this is to the same `/state` URI, but this time instead of using `GET` we're using `PUT`:

# In[ ]:


json_body_running = {"value": 'AS_RUNNING'}

put_response = rad_rest_request('PUT', s, server_connection_info, '{}/state'.format(post_response_uuid), json_body_running)
print(put_response.status_code)
print(json.loads(put_response.text))


# ---
# The assessment should now be running we can check this with this loop. Currently the status isn't refreshed for the running session so we start a new session and run the loop:

# In[ ]:


while True:
    s = requests.Session()
    login_again = rad_rest_login(s, server_connection_info, base_authentication_uri)
    
    my_list = rad_rest_request('GET', s, server_connection_info, '{}/metadata'.format(post_response_uuid))
    my_text = json.loads(my_list.text)
    print(my_text['payload']['Status'])
    if my_text['payload']['Status'] != 'Running':
        print('done')
        break
    time.sleep(30)


# ---
# ## Deleting an assessment
# 
# This section shows how to delete an assessment. 
# 
# First we take the UUID of the report we just created:

# In[ ]:


assessment_uuid = request_uuid['payload']


# Then we run the `DELETE` commannd:

# In[ ]:


delete_response = rad_rest_request('DELETE', s, server_connection_info, '{}{}'.format(compliance_assessment_uri, assessment_uuid))

print(delete_response.status_code)
print(json.loads(delete_response.text))


# ---
# ## Benchmarks
# 
# The next sections will go into the `Benchmark/` part of the REST API.
# 
# First we set the new URI for this part of the API:

# In[ ]:


compliance_benchmark_uri = '{}Benchmark/'.format(base_compliance_uri)
compliance_benchmark_uri


# ---
# The following command will allow you to get the available benchmarks on the system.

# In[ ]:


benchmark_get = rad_rest_request('GET', s, server_connection_info, '{}'.format(compliance_benchmark_uri))
benchmark_list = json.loads(benchmark_get.text)

print(benchmark_get.status_code)
print(benchmark_list)


# ---
# Next we explore the information linked to these benchmarks: `/name`, `/title`, `/profiles`

# In[ ]:


for benchmark_uri in benchmark_list['payload']:
    print(benchmark_uri['href'])
    benchmark_name = json.loads(rad_rest_request('GET', s, server_connection_info, '{}/name'.format(benchmark_uri['href'])).text)
    print(benchmark_name)
    benchmark_title = json.loads(rad_rest_request('GET', s, server_connection_info, '{}/title'.format(benchmark_uri['href'])).text)
    print(benchmark_title)
    benchmark_profiles = json.loads(rad_rest_request('GET', s, server_connection_info, '{}/profiles'.format(benchmark_uri['href'])).text)
    print(benchmark_profiles)


# ---
# 
# ## Tailoring
# 
# The `Tailoring/` API is closely related to the `Benchmark/` API. With this API you can find out if there are tailorings on the system and if so what they  are called and how they are tailored. I.e. which rules are set for this tailoring. Incidentally you can also use this API to find the way the predefined profiles are set.
# 
# First we set the tailoring URI:

# In[ ]:


compliance_tailoring_uri = '{}Tailoring/'.format(base_compliance_uri)
compliance_tailoring_uri


# ---
# Then we get the list of available tailorings:

# In[ ]:


tailoring_get = rad_rest_request('GET', s, server_connection_info, '{}'.format(compliance_tailoring_uri))

print(tailoring_get.status_code)
tailoring_list = json.loads(tailoring_get.text)
print(tailoring_list)


# ---
# We can now use this to get the full list of rules asigned to this tailoring:

# In[ ]:


tailoring_dfs = {}

for tailoring in tailoring_list['payload']:
    print(tailoring['href'])
    json_tailoring = {'tailoring': tailoring['href']}
    tailoring_description = json.loads(rad_rest_request('PUT', s, server_connection_info, 
                                                        '{}{}/_rad_method/get_descriptions'.format(compliance_benchmark_uri, 'solaris'), 
                                                        json_tailoring).text)
#     print(tailoring_description)
    tailoring_dfs[tailoring['href'].split('/')[-1]] = pd.DataFrame(tailoring_description['payload'])


# ---
# 
# Because there can be multiple tailorings on the system, I've put the dataframes inside a dict:

# In[ ]:


tailoring_dfs.keys()


# In[ ]:


tailoring_dfs['mysite'].head()


# ---
# Finally we can also use this API to get the list of rules set for the built-in profiles:

# In[ ]:


profile_description = json.loads(rad_rest_request('PUT', s, server_connection_info, 
                                                  '{}{}/_rad_method/get_descriptions'.format(compliance_benchmark_uri, 'solaris'), 
                                                  {'tailoring': 'Baseline'}).text)

profile_df = pd.DataFrame(profile_description['payload'])
#     print(rule['ruleid'], rule['title'], rule['description'])


# In[ ]:


profile_df


# In[ ]:


for cell in profile_df[profile_df['description'].str.contains('oscv', case = False)]['description']:
    print(cell)


# ---
# Things missing are:
# 
# * ways to set/upload a tailoring
# * a way to find out against which benchmark the tailoring is set
# * ways to download the compliance summary reports, this will only pull in `report.html`, `log`, `state`, and `results.xccdf.xml`.

# ---
# ---
# ## Main
# 
# We're skipping this section for now. This is to be able to run this more automated in the future.

# In[ ]:


def main():
    pass


# In[ ]:


# if __name__ == '__main__':
#     main()


# In[ ]:





# In[ ]:




