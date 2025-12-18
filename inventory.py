#!/usr/bin/env python3
import json
import subprocess
import sys

def get_gcp_instances():
    """Get instances using gcloud CLI (no Python modules needed)"""
    cmd = [
        'gcloud', 'compute', 'instances', 'list',
        '--project=siva-477505',
        '--filter=tags.items=http-server AND status=RUNNING',
        '--format=json(name,networkInterfaces[0].networkIP,zone)',
        '--quiet'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"gcloud error: {result.stderr}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return []

def main():
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        instances = get_gcp_instances()
        
        inventory = {
            'web_servers': {
                'hosts': [],
                'vars': {
                    'ansible_user': 'ubuntu',
                    'ansible_ssh_common_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null',
                    'ansible_python_interpreter': '/usr/bin/python3'
                }
            },
            '_meta': {'hostvars': {}}
        }
        
        for instance in instances:
            hostname = instance['name']
            ip = instance['networkInterfaces'][0]['networkIP']
            
            inventory['web_servers']['hosts'].append(hostname)
            inventory['_meta']['hostvars'][hostname] = {
                'ansible_host': ip,
                'zone': instance['zone'].split('/')[-1]
            }
        
        print(json.dumps(inventory))
    else:
        print(json.dumps({}))

if __name__ == '__main__':
    main()
