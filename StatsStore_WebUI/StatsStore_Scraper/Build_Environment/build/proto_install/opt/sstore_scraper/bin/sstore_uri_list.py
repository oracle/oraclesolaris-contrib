# List of statsStore URIs
# v1.0 based on Oracle Solaris 11.4 SRU33 
# Need to add a way to learn if there are newer versions of the base URIs
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as 
# shown at https://oss.oracle.com/licenses/upl/

# StatsStore URIs
base_sstore_uri = 'api/com.oracle.solaris.rad.sstore/1.0/'
sstore_configuration_uri = f'{base_sstore_uri}Configuration/'
sstore_data_uri = f'{base_sstore_uri}Data/'
sstore_info_uri = f'{base_sstore_uri}Info/'
sstore_namespace_uri = f'{base_sstore_uri}Namespace/'
sstore_batch_uri = f'{base_sstore_uri}Batch/'
sstore_collection_uri = f'{base_sstore_uri}Collection/'

# StatsStore RAD/REST module JSON body template
json_body_template = {
    'ssids': [],
    'range': {
        'range_type': 'RANGE_BY_TIME',
        'range_by_time': {
            'start_ts': -1,
            'end_ts': -1,
            'step': 1
        },   
        'show_unstable': True,
        'show_unbrowsable': True 
    }
}