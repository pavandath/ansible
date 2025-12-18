#!/usr/bin/env python3
# inventory/gcp-mig-mumbai.py

import os
from google.auth import compute_engine
from googleapiclient import discovery
import json

def get_instances(project, zones):
    """Fetch all instances matching our criteria"""
    credentials = compute_engine.Credentials()
    service = discovery.build('compute', 'v1', credentials=credentials)
    
    instances = []
    
    for zone in zones:
        result = service.instances().list(project=project, zone=zone).execute()
        if 'items' in result:
            for instance in result['items']:
                # Filter: running, http-server tag, web-instance-* name
                if (instance['status'] == 'RUNNING' and
                    'http-server' in instance.get('tags', {}).get('items', []) and
                    instance['name'].startswith('web-instance-')):
                    
                    instances.append(instance)
    
    return instances

def main():
    project = 'siva-477505'
    zones = ['asia-south1-a', 'asia-south1-b', 'asia-south1-c']
    
    instances = get_instances(project, zones)
    
    inventory = {
        '_meta': {
            'hostvars': {}
        },
        'all': {
            'hosts': [],
            'vars': {
                'ansible_user': 'ubuntu',
                'ansible_ssh_common_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null',
                'ansible_python_interpreter': '/usr/bin/python3'
            }
        }
    }
    
    for instance in instances:
        hostname = instance['name']
        
        # Get internal IP
        network_ip = instance['networkInterfaces'][0]['networkIP']
        
        inventory['all']['hosts'].append(hostname)
        inventory['_meta']['hostvars'][hostname] = {
            'ansible_host': network_ip,
            'zone': instance['zone'].split('/')[-1],
            'machine_type': instance['machineType'].split('/')[-1],
            'gcp_project': project
        }
    
    print(json.dumps(inventory))

if __name__ == '__main__':
    main()
