import requests
import re
import os
from flask import Response, request, abort, render_template, url_for, Blueprint
from _config import basedir

import json
import sys

sys.path.insert(0, "/usr/local/bin/igv-flask/igvjs/modules")
from prepare_data import prepare_data as prep_data

seen_tokens = set()

igvjs_blueprint = Blueprint('igvjs', __name__)

# give blueprint access to app config
@igvjs_blueprint.record
def record_igvjs(setup_state):
    igvjs_blueprint.config = setup_state.app.config;

# routes
@igvjs_blueprint.route('/')
def show_vcf():
    project_id = request.args.get('project_id')
    pipeline_name = request.args.get('pipeline_name')
    config_file = "/usr/local/bin/igv-flask/igvjs/static/data/public" + \
      "/igv-data/config/" + pipeline_name + "/" + project_id + ".json"
    with open(config_file) as json_data:
        d = json.load(json_data)
    return render_template('igv.html', data = json.dumps(d))


@igvjs_blueprint.route('/PrepareData', methods = ['POST'])
def prepare_data():
    data = request.get_json(force = True)
    project_json = "/usr/local/bin/igv-flask/igvjs/static/data/public/igv-data/config/" + \
          data["pipeline_name"] + "/" + data["project_id"] + ".json"
    err = None
    if not os.path.exists(project_json):
      err = prep_data(data)
    if err:
        return json.dumps({
            "error": err,
            "message": err
        }), 500
    else:
        return json.dumps({
            "error": err,
            "message": "Success"
        }), 200
    

@igvjs_blueprint.before_app_request
def before_request():
    if igvjs_blueprint.config['USES_OAUTH'] and (not igvjs_blueprint.config['PUBLIC_DIR'] or \
            not os.path.exists('.'+igvjs_blueprint.config['PUBLIC_DIR']) or \
            not request.path.startswith(igvjs_blueprint.config['PUBLIC_DIR'])):
        auth = request.headers.get("Authorization", None)
	#print auth
        if auth:
            token = auth.split()[1]
            if token not in seen_tokens:
                google_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
                params = {'access_token':token}
                res = requests.get(google_url, params=params)
                email = res.json()['email']
                if email in allowed_emails():
                    seen_tokens.add(token)
                else:
                    abort(403)
        else:
            if "static/data" in request.path and "data/static/data" not in request.path:
                abort(401)
    return ranged_data_response(request.headers.get('Range', None), request.path[1:])

def allowed_emails():
    emails = []
    if os.path.isfile(app.config['ALLOWED_EMAILS']):
        with open(app.config['ALLOWED_EMAILS'], 'r') as f:
            for line in f:
                emails.append(line.strip())
    return emails

def ranged_data_response(range_header, rel_path):
    path = os.path.join(basedir, rel_path)
    if not range_header:
        return None
    m = re.search('(\d+)-(\d*)', range_header)
    if not m:
        return "Error: unexpected range header syntax: {}".format(range_header)
    size = os.path.getsize(path)
    offset = int(m.group(1))
    length = int(m.group(2) or size) - offset

    data = None
    with open(path, 'rb') as f:
        f.seek(offset)
        data = f.read(length)
    rv = Response(data, 206, mimetype="application/octet-stream", direct_passthrough=True)
    rv.headers['Content-Range'] = 'bytes {0}-{1}/{2}'.format(offset, offset + length-1, size)
    return rv
