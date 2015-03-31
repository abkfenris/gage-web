import ipaddress
import json
import requests
from flask import Blueprint, request, abort, jsonify

hook = Blueprint('hook', __name__)


@hook.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return 'OK'
    elif request.method == 'POST':
        # Store the IP address of the requster
        request_ip = ipaddress.ip_address(u'{0}'.format(request.remote_addr))

        # Get the IPs for valid hook requests
        hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']

        # Check if the POST is from github
        for block in hook_blocks:
            if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
                break  # the remote address is in the range of github
        else:
            abort(403)

        # If it's a ping return hi
        if request.headers.get('X-GitHub-Event') == 'ping':
            return jsonify({'msg': 'Hi!'})
        # If it's anything but a push return wrong event type
        if request.headers.get('X-GitHub-Event') != 'push':
            return jsonify({'msg': 'wrong event type'})

        repos = {}

        payload = json.loads(request.data)
        repo_meta = {
            'name': payload['repository']['name'],
            'owner': payload['repository']['owner']['name'],
        }

        return 'OK'
