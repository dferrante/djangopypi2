import os
import json

AVAILABLE_SETTINGS = [
    dict(name='ADMINS'       , default=[]               , type='names_and_emails'),
    dict(name='DEBUG'        , default=False            , type='bool'),
    dict(name='TIME_ZONE'    , default='America/Chicago', type='timezone'),
    dict(name='WEB_ROOT'     , default='/'              , type='str'),
    dict(name='LANGUAGE_CODE', default='en-us'          , type='str'),
    dict(name='PKG_CACHE_USER_ID', default=1            , type='int'),
    dict(name='HTTP_PROXY'   , default=''               , type='str'),
]

def _filename(project_root):
    return os.path.join(project_root, 'settings.json')

def load(project_root):
    filename = _filename(project_root)
    if not os.path.exists(filename):
        save(project_root, dict((setting['name'], setting['default']) for setting in AVAILABLE_SETTINGS))
    return json.loads(open(filename, 'r').read())

def save(project_root, user_settings):
    fo = open(_filename(project_root), 'w')
    fo.write(json.dumps(user_settings, indent=4))
    fo.close()
