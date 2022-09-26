#! /usr/bin/python3
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as 
# shown at https://oss.oracle.com/licenses/upl/

import requests
import json
import yaml
import os, sys
import socket
import platform
import logging
import time, datetime

from pprint import pprint

from urllib3.connection import HTTPConnection
from urllib3.connectionpool import HTTPConnectionPool
from requests.adapters import HTTPAdapter

# Importing the URIs needed to connect to the Oracle Solaris RAD/REST API
from sstore_uri_list import *

# Define config files
working_dir = '/opt/sstore_scraper'
server_config_file = 'etc/server_info.yaml'
sstore_list_file = 'etc/sstore_list.yaml'

# Classes that convert the requests API to a local RAD/REST connection
class radConnection(HTTPConnection):
    def __init__(self):
        super().__init__("localhost")

    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect("/system/volatile/rad/radsocket-http")

class radConnectionPool(HTTPConnectionPool):
    def __init__(self):
        super().__init__("localhost")

    def _new_conn(self):
        return radConnection()

class radAdapter(HTTPAdapter):
    def get_connection(self, url, proxies=None):
        return radConnectionPool()

# Function to convert an SSID in to a simpler string
def ssid_converter(ssid, item_name=''):
    ssid_name_list_raw = ssid.split('//:')[1:]
    # logging.debug((ssid_name_list_raw, item_name))
    ssid_name_list = []
    for item in ssid_name_list_raw:
        if item.split('.')[0] == 'part':
            # ssid_name_list += [item_name]
            pass
        elif item.split('.')[1].startswith('convert'):
            logging.debug(f'{item} has a convert operation, skipping')
            pass
        else:
            ssid_name_list += item.split('.')[-1:]
    return '_'.join(ssid_name_list)

# Class that handles the connection to RAD/REST, the conversion of the data,
# and the export in various formats
class StatsStoreScraper:
    def __init__(self, destination='splunk'):
        # Loading connection data
        server_list_filename = f'{working_dir}/{server_config_file}'

        if server_list_filename:
            with open(server_list_filename, 'r') as f:
                self.server_connection_info = yaml.safe_load(f)
                logging.info(self.server_connection_info)
        # Warn if the file doesn't exist and exit
        else:
            logging.info(f'missing the {server_list_filename} file')
            exit()

        if list(self.server_connection_info['destination'].keys())[0] == 'splunk':
            # setting the destination of the data
            self.destination = 'splunk'
            # loading system info info the data template
            system_info = platform.uname()
            self.server_connection_info['destination']['splunk']['data_template']['host'] = system_info.node
            self.server_connection_info['destination']['splunk']['data_template']['fields']['os'] = f'Oracle Solaris {system_info.version}'
            self.server_connection_info['destination']['splunk']['data_template']['fields']['version'] = system_info.version
            self.server_connection_info['destination']['splunk']['data_template']['fields']['arch'] = system_info.machine
            self.server_connection_info['destination']['splunk']['data_template']['fields']['processor'] = system_info.processor.upper()
        else:
            logging.info(f'unsupported destination type in {server_list_filename}')
            exit()

        # Loading in SSID lists
        sstore_stats_filename = f'{working_dir}/{sstore_list_file}'

        if sstore_stats_filename:
            with open(sstore_stats_filename, 'r') as f:
                sstore_stats = yaml.safe_load(f)
                logging.debug(sstore_stats)
        
            # Converting SSID lists to a single list
            sstore_id_list = []
            for key in sstore_stats.keys():
                sstore_id_list.extend(sstore_stats[key])
            
            sstore_id_list = list(set(sstore_id_list))
        # Warn if the file doesn't exist
        else:
            logging.info(f'missing the {sstore_stats_filename} file')
            sstore_id_list = []

        # Load the JSON template needed for the StatsStore RAD/REST module from sstore_uri_list.py
        self.json_body = json_body_template
        # Add the SSIDs to the JSON template
        self.json_body['ssids'] = sstore_id_list

        logging.info('Initialized StatsStore Scraper')

        if os.fork():
            sys.exit()

    # Function to connect to Oracle Solaris RAD/REST
    def read_list(self, request_type, server_connection_info, rad_rest_uri, payload=None):

        return_dict = {}
        for server in server_connection_info['servers'].keys():
            return_dict[server] = {}

            # Check if using a local or remote connection
            if server_connection_info['servers'][server]['server_port'] == 'local':
                logging.info('Using local RAD connection to get StatsStore data')

                # Create query url to be used
                query_url = f"http://rad/{rad_rest_uri}"

                with requests.Session() as session:
                    session.mount("http://rad/", radAdapter())
                    response = session.request(request_type, query_url, json=payload)

                return_dict[server] = {'status_code': response.status_code, 'text': json.loads(response.text)}
            
            # Using the remote connection
            else:
                logging.info('Using remote RAD/REST connection to get StatsStore data')
                # Create query url to be used
                query_url = f"https://{server}:{server_connection_info['servers'][server]['server_port']}/{rad_rest_uri}"

                ### Need to add a check if the SSL cert and key are present

                # Get the cert/key location
                query_certs = tuple(map(server_connection_info['servers'][server].get, ['ssl_cert', 'ssl_key']))

                # Make the request
                try:
                    response = requests.request(request_type, query_url, json=payload, cert=query_certs, verify=server_connection_info['servers'][server]['cert_location'])
                    return_dict[server] = {'status_code': response.status_code, 'text': json.loads(response.text)}
                except:
                    ### Need to improve the exception handling
                    return_dict[server] = {'status_code': 400, 'text': {"status": "failed", "payload": []}}

        return return_dict

    # Function to convert StatsStore response to dict with only data
    def convert_list(self, sstore_list):
        return_dict = {}

        # For each server go through their responses and filter out the data
        for server in sstore_list.keys():
            if sstore_list[server]['status_code'] == 200:
                return_dict[server] = {}
                for number_1, item_1 in enumerate(sstore_list[server]['text']['payload']['records']):

                    # Check that only one datapoint being asked
                    if len(item_1['points']) > 1:
                        logging.info('Error: points array longer than 1')
                    else:
                        ssid_name = ssid_converter(item_1['ssid'])
                        # Regular single point
                        if (item_1['points'][0]['point_value']['value']['type'] == 'REAL') or (item_1['points'][0]['point_value']['value']['type'] == 'NUMBER'):
                            return_dict[server][ssid_name] = {}

                            for number_2, item_2 in enumerate(item_1['points']):
                                if item_2['point_type'] == 'VALUE_POINT':
                                    return_dict[server][ssid_name]['timestamp'] = item_2['point_value']['ts']
                                    value_type =item_2['point_value']['value']['type'].lower()
                                    return_dict[server][ssid_name]['value'] = item_2['point_value']['value'][value_type]
                                else:
                                    return_dict[server][ssid_name]['value'] = 'not a value_point'
                            # logging.debug(return_dict)

                        # Dictionary with multiple points
                        elif item_1['points'][0]['point_value']['value']['type'] == 'DICTIONARY':
                            return_dict[server][ssid_name] = {}

                            for number_2, item_2 in enumerate(item_1['points']):
                                if item_2['point_type'] == 'VALUE_POINT':
                                    for item_3 in item_2['point_value']['value']['dictionary']:
                                        return_dict[server][ssid_name]['timestamp'] = item_2['point_value']['ts']
                                        value_type = item_2['point_value']['value']['dictionary'][item_3]['type'].lower()
                                        return_dict[server][ssid_name][item_3] = item_2['point_value']['value']['dictionary'][item_3][value_type]
                                else:
                                    return_dict[server][ssid_name]['value'] = 'not a value_point'
                            # logging.debug(return_dict)
                        
                        # Catching stats with no data in them
                        elif item_1['points'][0]['point_value']['value']['type'] == 'NO_DATA':
                            logging.debug(f"The SSID: {ssid_name} on {server} is giving {item_1['points'][0]['point_value']['value']}")
                            pass
                        
                        # Something it can't work with
                        else:
                            return_dict[server][ssid_name] = {}
                            return_dict[server][ssid_name]['value'] = f"{item_1['points'][0]['point_value']['value']['type']}: this is neither a real or a dictionary"
                            logging.debug(f"{ssid_name} on {server} contains {item_1['points'][0]['point_value']['value']['type']}: this is neither a real or a dictionary")
            # Warn if the connection to a server failed
            else:
                logging.info(f'no connection with server {server}, no data to filter')

        return return_dict

    # Function to get the stats and convert them in one step
    def get_stats(self):
        # Reading StatstStore data from host(s)
        sstore_list = self.read_list('PUT', self.server_connection_info, f'{sstore_data_uri}_rad_method/read', self.json_body)
        sstore_converted_dict = self.convert_list(sstore_list)
        return sstore_converted_dict

    # Function to print the result into an destination specific format
    def print_list(self, sstore_converted_dict):
        for server in sstore_converted_dict.keys():
            # Check if the destination is Splunk
            if self.destination == 'splunk':
                value_list = {}
                # Convert the value names to fit the Splunk format
                for item in sstore_converted_dict[server].keys():
                    for key in sstore_converted_dict[server][item].keys():
                        if key != 'timestamp':
                            if key == 'value':
                                value_list[f'metric_name:{item}'] = sstore_converted_dict[server][item][key]
                            else:
                                value_list[f'metric_name:{item}_{key}'] = sstore_converted_dict[server][item][key]

                # Load the Splunk specific output template
                connect_data = self.server_connection_info['destination']['splunk']
                splunk_data = connect_data['data_template']
                ### Look at adding the timestamp
                # Add the recent data
                splunk_data['fields'].update(value_list)

                # Send the data to Splunk if this is defined
                ### Need a better way to check the endpoint and also add a way to print to the console/a file for debug
                if connect_data['server_endpoint']:
                    request_url = f"{connect_data['request_transport']}{connect_data['server_endpoint']}{connect_data['request_uri']}"
                    logging.info(f"sending data to {request_url}")
                    logging.debug(connect_data['headers'])
                    ### Add ability to set the verification and collect connection errors
                    response = requests.request(connect_data['request_type'], request_url, json=splunk_data, headers=connect_data['headers'], verify=False)
                    logging.debug(response.text)
                else:
                    logging.info('No server_endpoint was set.')

            # The destination set is not supported
            else:
                pprint('The destination is not supported')
            ### Add other destination types to this function

    # Function to gather the stats in a continuous loop
    ### Add a way to only run this once
    def run_stats_loop(self):
        while True:
            sstore_converted_dict = self.get_stats()
            self.print_list(sstore_converted_dict)
            time.sleep(self.server_connection_info['agent']['interval'])

def main():
    # Setting logging level to debug
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.captureWarnings(True)

    logging.info('starting up')
    # Reading StatstStore data from host(s)
    my_scraper = StatsStoreScraper()
    
    logging.info('starting loop')
    my_scraper.run_stats_loop()
    
if __name__ == '__main__':
    main()
