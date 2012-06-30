import model
import staff_interface
import interboard
import urllib

from template import Template
from util import WakaError
from staff_interface import StaffInterface
from staff_tasks import StaffAction
from board import Board, NoBoard
from misc import get_cookie_from_request, kwargs_from_params

def no_task(environ, start_response):
    board = environ['waka.board']
    start_response('302 Found', [('Location', board.url)])
    return []

def init_database():
    model.metadata.create_all(model.engine)

# Cache building
def task_rebuild(environ, start_response):
    request = environ['werkzeug.request']
    params = {'cookies': ['wakaadmin']}
    
    kwargs = kwargs_from_params(request, params)
    kwargs['board'] = environ['waka.board']
    kwargs['action'] = 'rebuild'

    return StaffAction(**kwargs).execute()

def task_rebuildglobal(environ, start_response):
    request = environ['werkzeug.request']
    params = {'cookies': ['wakaadmin']}
    
    kwargs = kwargs_from_params(request, params)
    kwargs['action'] = 'rebuild_global'

    return StaffAction(**kwargs).execute()

# Posting
def task_post(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form':     ['parent', 'field1', 'email', 'subject', 'comment',
                           'password', 'nofile', 'captcha', 'no_captcha',
                           'no_format', 'sticky', 'lock', 'adminpost'],
              'cookies':  ['wakaadmin'],
              'file':     ['file']}
   
    kwargs = kwargs_from_params(request, params)
 
    kwargs['name'] = kwargs.pop('field1')
    kwargs['oekaki_post'] = kwargs['srcinfo'] = kwargs['pch'] = None
    kwargs['admin_post_mode'] = kwargs.pop('adminpost')
    if kwargs['no_format'] == '0':
        kwargs['no_format'] = False

    if kwargs['admin_post_mode']:
        kwargs['action'] = 'admin_post'
        kwargs['board'] = board
        return StaffAction(**kwargs).execute()
    
    del kwargs['admin']
    return board.post_stuff(**kwargs)

# Post Deletion
def task_delpostwindow(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    kwargs = {}
    kwargs['post_num'] = request.values.get('num', '')

    return board.delete_gateway_window(**kwargs)

def task_delete(environ, start_response, archiving=False):
    # TODO review compatibility with wakaba or refactor
    request = environ['werkzeug.request']
    board = environ['waka.board']

    singledelete = (request.values.get("singledelete", '') == 'OK')

    params = {'form': ['password', 'file_only', 'from_window', 'admindelete'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)

    if singledelete:
        # NOTE: from_window parameter originates from pop-up windows
        #       brought up by clicking "Delete" without JS enabled.
        params_single = ['postpassword', 'postfileonly', 'from_window']
        for param, single in map(None, params['form'][:3], params_single):
            kwargs[param] = request.form.get(single, '')

        kwargs['posts'] = [request.values.get('deletepost', '')]
    else:
        kwargs['posts'] = request.form.getlist('num')
    kwargs['archiving'] = archiving

    if kwargs['admindelete']:
        kwargs['board'] = board
        kwargs['action'] = 'admin_delete'
        return StaffAction(**kwargs).execute()

    del kwargs['admin']
    return board.delete_stuff(**kwargs)

def task_deleteall_confirm(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['ip', 'mask', 'global'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.DELETE_ALL_CONFIRM

    return StaffInterface(**kwargs)

def task_deleteall(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['ip', 'mask', 'global'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)

    if kwargs.pop('global'):
        kwargs['action'] = 'delete_by_ip_global'
    else:
        kwargs['board'] = environ['waka.board']
        kwargs['action'] = 'delete_by_ip'

    # Perform action: returns nothing.
    StaffAction(**kwargs).execute()

    return task_mpanel(environ, start_response)

def task_archive(environ, start_response):
    return task_delete(environ, start_response, archiving=True)

# Post Editing
def task_edit(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form': ['num']}
   
    kwargs = kwargs_from_params(request, params)
    kwargs['post_num'] = kwargs.pop('num')

    return board.edit_gateway_window(**kwargs)

def task_editpostwindow(environ, start_response):
    # This is displayed in a "pop-up window" UI.
    environ['waka.fromwindow'] = True

    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form':    ['num', 'password', 'admineditmode'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['admin_edit_mode'] = kwargs.pop('admineditmode')
    kwargs['post_num'] = kwargs.pop('num')

    return board.edit_window(**kwargs)

def task_editpost(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form': ['num', 'field1', 'email', 'subject', 'comment',
                       'password', 'nofile', 'captcha', 'no_captcha',
                       'no_format', 'sticky', 'lock', 'adminedit', 'killtrip',
                       'postfix'],
              'cookies': ['wakaadmin'],
              'file':    ['file']}

    kwargs = kwargs_from_params(request, params)
    kwargs['name'] = kwargs.pop('field1')
    kwargs['post_num'] = kwargs.pop('num')
    kwargs['admin_edit_mode'] = kwargs.pop('adminedit')
    kwargs['oekaki_post'] = kwargs['srcinfo'] = kwargs['pch'] = None
    if kwargs['admin_edit_mode']:
        kwargs['board'] = board
        kwargs['action'] = 'admin_edit'
        return StaffAction(**kwargs).execute()

    del kwargs['admin']
    return board.edit_stuff(**kwargs)

def task_report(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    num = request.form.getlist('num')
    from_window = request.values.get('popupwindow', '')

    return board.make_report_post_window(num, from_window)

def task_confirmreport(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form': ['num', 'comment', 'referer']}

    kwargs = kwargs_from_params(request, params)
    kwargs['posts'] = kwargs.pop('num').split(', ')
    
    return board.report_posts(**kwargs)

def task_resolve(environ, start_response):
    request = environ['werkzeug.request']
    params = {'cookies': ['wakaadmin'], 'form': ['delete']}

    kwargs = kwargs_from_params(request, params)

    posts = {}
    for post in request.form.getlist('num'):
        (board_name, num) = post.split('-')
        try:
            posts[board_name].append(num)
        except KeyError:
            posts[board_name] = [num]
    kwargs['posts'] = posts
    kwargs['action'] = 'report_resolve'

    return StaffAction(**kwargs).execute()

def task_restorebackups(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form':    ['handle'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['posts'] = request.form.getlist('num')
    kwargs['restore'] = kwargs.pop('handle').lower() == 'restore'
    kwargs['board'] = board
    kwargs['action'] = 'backup_remove'

    return StaffAction(**kwargs).execute()

def _toggle_thread_state(environ, start_response, operation):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    kwargs = {}
    kwargs['num'] = request.values.get('thread', 0)
    kwargs['board'] = board
    kwargs['action'] = 'thread_' + operation
    try:
        kwargs['admin'] = get_cookie_from_request(request, 'wakaadmin')
    except KeyError:
        kwargs['admin'] = ''

    return StaffAction(**kwargs).execute()

def task_sticky(environ, start_response):
    return _toggle_thread_state(environ, start_response, 'sticky')

def task_unsticky(environ, start_response):
    return _toggle_thread_state(environ, start_response, 'unsticky')

def task_lock(environ, start_response):
    return _toggle_thread_state(environ, start_response, 'lock')

def task_unlock(environ, start_response):
    return _toggle_thread_state(environ, start_response, 'unlock')

# Panels

def task_entersetup(environ, start_response):
    request = environ['werkzeug.request']

    admin = request.values.get('berra', '')

    return staff_interface.make_first_time_setup_page(admin)

def task_setup(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['admin', 'username', 'password']}
    kwargs = kwargs_from_params(request, params)

    return staff_interface.do_first_time_setup(**kwargs)

def task_sql(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['sql', 'nuke'],
              'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.SQL_PANEL

    return StaffInterface(**kwargs)

def task_proxy(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.PROXY_PANEL

    return StaffInterface(**kwargs)

def task_security(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.SECURITY_PANEL

    return StaffInterface(**kwargs)

def task_loginpanel(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['nexttask', 'nexttask', 'berra', 'desu', 'savelogin'],
              'cookies': ['wakaadmin', 'wakaadminsave']}

    kwargs = kwargs_from_params(request, params)

    # Why are we doing this again?
    kwargs['username'] = kwargs.pop('desu')
    kwargs['password'] = kwargs.pop('berra')

    # Login saving.
    wakaadminsave = kwargs.pop('wakaadminsave')
    savelogin = kwargs.pop('savelogin')
    kwargs['save_login'] = wakaadminsave or savelogin

    return staff_interface.do_login(**kwargs)

task_admin = task_loginpanel

def task_logout(environ, start_response):
    request = environ['werkzeug.request']
    
    admin = ''
    try:
        admin = request.cookies['wakaadmin']
    except KeyError:
        pass

    return staff_interface.do_logout(admin)

def task_mpanel(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['page'], 'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.BOARD_PANEL

    return StaffInterface(**kwargs)

def task_bans(environ, start_response):
    request = environ['werkzeug.request']

    kwargs = {}
    kwargs['ip'] = request.values.get('ip', '')
    kwargs['admin'] = get_cookie_from_request(request, 'wakaadmin')
    kwargs['dest'] = staff_interface.BAN_PANEL

    return StaffInterface(**kwargs)

def task_baneditwindow(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['num'],
              'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.BAN_EDIT_POPUP

    return StaffInterface(**kwargs)

def task_banpopup(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['ip', 'delete'],
              'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.BAN_POPUP

    return StaffInterface(**kwargs)

def task_staff(environ, start_response):
    request = environ['werkzeug.request']

    kwargs = {}
    try:
        kwargs['admin'] = get_cookie_from_request(request, 'wakaadmin')
    except KeyError:
        kwargs['admin'] = ''
    kwargs['dest'] = staff_interface.STAFF_PANEL

    return StaffInterface(**kwargs)

def task_spam(environ, start_response):
    request = environ['werkzeug.request']

    kwargs = {}
    try:
        kwargs['admin'] = get_cookie_from_request(request, 'wakaadmin')
    except KeyError:
        kwargs['admin'] = ''
    kwargs['dest'] = staff_interface.SPAM_PANEL

    return StaffInterface(**kwargs)

def task_reports(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['page', 'perpage', 'sortby', 'order'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['sortby_type'] = kwargs.pop('sortby')
    kwargs['sortby_dir'] = kwargs.pop('order')
    kwargs['dest'] = staff_interface.REPORTS_PANEL

    return StaffInterface(**kwargs)

def task_resolvedreports(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['page', 'perpage', 'sortby', 'order'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['sortby_type'] = kwargs.pop('sortby')
    kwargs['sortby_dir'] = kwargs.pop('order')
    kwargs['dest'] = staff_interface.RESOLVED_REPORTS_PANEL

    return StaffInterface(**kwargs)

def task_postbackups(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['page'],
              'cookies': ['wakaadmin']}
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.TRASH_PANEL

    return StaffInterface(**kwargs)

def task_addip(environ, start_response):
    request = environ['werkzeug.request']
    
    params = {'form':    ['type', 'comment', 'ip', 'mask', 'total',
                          'expiration'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['option'] = kwargs.pop('type')
    kwargs['action'] = 'admin_entry'

    return StaffAction(**kwargs).execute()

def task_addipfrompopup(environ, start_response):
    request = environ['werkzeug.request']
    board = environ['waka.board']

    params = {'form':    ['ip', 'total', 'expiration', 'comment', 'delete',
                          'deleteall_confirm'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['action'] = 'admin_entry'
    kwargs['option'] = 'ipban'
    kwargs['caller'] = 'window'
    delete = kwargs.pop('delete')
    delete_all = kwargs.pop('deleteall_confirm')

    try:
        if delete_all:
            interboard.delete_by_ip(kwargs['admin'], kwargs['ip'])
        elif delete:
            board = environ['waka.board']
            board.delete_stuff([delete], '', False, False, admindelete=True,
                               admin=kwargs['admin'], from_window=True,
                               caller='internal')
    except WakaError:
        pass

    return StaffAction(**kwargs).execute()

def task_addstring(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['type', 'string', 'comment'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['action'] = 'admin_entry'
    kwargs['option'] = kwargs.pop('type')
    kwargs['sval1'] = kwargs.pop('string')

    return StaffAction(**kwargs).execute()

def task_adminedit(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['num', 'ival1', 'ival2', 'sval1', 'total', 'year',
                          'month', 'day', 'hour', 'min', 'sec', 'comment',
                          'noexpire'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['action'] = 'edit_admin_entry'

    return StaffAction(**kwargs).execute()

def task_removeban(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['num'], 'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['action'] = 'remove_admin_entry'

    return StaffAction(**kwargs).execute()

# Interboard management.

def task_updatespam(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['spam'], 'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['action'] = 'update_spam'

    return StaffAction(**kwargs).execute()

def task_deleteuserwindow(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['username']}

    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.DEL_STAFF_CONFIRM

    return StaffInterface(**kwargs)

def task_disableuserwindow(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['username']}

    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.DISABLE_STAFF_CONFIRM

    return StaffInterface(**kwargs)

def task_enableuserwindow(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['username']}

    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.ENABLE_STAFF_CONFIRM

    return StaffInterface(**kwargs)

def task_edituserwindow(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['username']}

    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.EDIT_STAFF_CONFIRM

    return StaffInterface(**kwargs)

def task_createuser(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'],
              'form':    ['mpass', 'usertocreate', 'passtocreate', 'account',
                          'reign']}

    kwargs = kwargs_from_params(request, params)
    kwargs['reign'] = kwargs.pop('reign').split(',')

    return staff_interface.add_staff_proxy(**kwargs)

def task_deleteuser(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['mpass', 'username']}

    kwargs = kwargs_from_params(request, params)

    return staff_interface.del_staff_proxy(**kwargs)

def task_disableuser(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['mpass', 'username']}

    kwargs = kwargs_from_params(request, params)
    kwargs['disable'] = True

    return staff_interface.edit_staff_proxy(**kwargs)

def task_enableuser(environ, start_response):
    request = environ['werkzeug.request']

    params = {'cookies': ['wakaadmin'], 'form': ['mpass', 'username']}

    kwargs = kwargs_from_params(request, params)
    kwargs['disable'] = False

    return staff_interface.edit_staff_proxy(**kwargs)

def task_edituser(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form': ['mpass', 'usernametoedit', 'newpassword', 'newclass',
                       'originalpassword'], 
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['username'] = kwargs.pop('usernametoedit')
    kwargs['reign'] = request.form.getlist('reign')

    return staff_interface.edit_staff_proxy(**kwargs)

def task_move(environ, start_response):
    request = environ['werkzeug.request']
    
    kwargs = {}
    kwargs['parent'] = request.values.get('num', '')
    try:
        kwargs['admin'] = get_cookie_from_request(request, 'wakaadmin')
    except KeyError:
        kwargs['admin'] = ''
    kwargs['src_brd_obj'] = environ['waka.board']
    kwargs['dest_brd_obj'] = Board(request.values.get('destboard', ''))
    kwargs['action'] = 'thread_move'

    return StaffAction(**kwargs).execute()

def task_searchposts(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['ipsearch', 'id', 'ip', 'caller'],
              'cookies': ['wakaadmin']}
    
    kwargs = kwargs_from_params(request, params)
    kwargs['dest'] = staff_interface.POST_SEARCH_PANEL

    return StaffInterface(**kwargs)

def task_stafflog(environ, start_response):
    request = environ['werkzeug.request']

    params = {'form':    ['sortby', 'order', 'iptoview', 'view', 'perpage',
                          'page', 'actiontoview', 'posttoview', 'usertoview'],
              'cookies': ['wakaadmin']}

    kwargs = kwargs_from_params(request, params)
    kwargs['sortby_name'] = kwargs.pop('sortby')
    kwargs['sortby_dir'] = kwargs.pop('order')
    kwargs['ip_to_view'] = kwargs.pop('iptoview')
    kwargs['post_to_view'] = kwargs.pop('posttoview')
    kwargs['action_to_view'] = kwargs.pop('actiontoview')
    kwargs['user_to_view'] = kwargs.pop('usertoview')

    kwargs['dest'] = staff_interface.STAFF_ACTIVITY_PANEL

    return StaffInterface(**kwargs)

# Error-handling

def fffffff(environ, start_response, error):
    start_response('200 OK', [('Content-Type', 'text/html')])

    mini = '_mini' if environ['waka.fromwindow'] else ''
    return Template('error_template' + mini, error=error.message)

MAIN_SITE_URL = 'http://www.desuchan.net'
def not_found(environ, start_response):
    '''Not found handler that redirects to desuchan
    Meant for the development server'''

    start_response('302 Found',
        [('Location', MAIN_SITE_URL + environ['PATH_INFO'])])
    return []

# Initial setup

def check_setup(environ, start_response):
    import os, config
    from template import TEMPLATES_DIR

    issues = []

    if ('DOCUMENT_ROOT' not in environ or 'SCRIPT_NAME' not in environ or
        'SERVER_NAME' not in environ):
        return ["CGI environment not complete\n"]

    full_board_dir = os.path.join(environ['DOCUMENT_ROOT'], config.BOARD_DIR)
    if not os.access(full_board_dir, os.W_OK):
        issues.append("No write access to DOCUMENT_ROOT+BOARD_DIR (%s)" %
            full_board_dir)

    include_dir = os.path.join(environ['DOCUMENT_ROOT'],
        config.BOARD_DIR, "include")
    if not os.access(include_dir, os.F_OK | os.R_OK):
        issues.append("No read access to includes dir (%s). Wrong BOARD_DIR?" %
            include_dir)

    script_name_dir = os.path.join(environ['DOCUMENT_ROOT'],
        os.path.dirname(environ['SCRIPT_NAME']).lstrip("/"))
    if not os.access(script_name_dir, os.W_OK):
        issues.append("No write access to DOCUMENT_ROOT+SCRIPT_NAME dir (%s)" %
            script_name_dir)

    templates_dir = os.path.abspath(TEMPLATES_DIR)
    if not os.access(templates_dir, os.W_OK):
        issues.append("No write access to templates dir (%s)" % templates_dir)

    if issues:
        return ["<p>Setup issues found:</p> <ul>"] + \
            ["<li>%s</li>\n" % x for x in issues] + ["</ul>"]
    elif model.Session().query(model.account).count() == 0:
        return Template("first_time_setup")
    else:
        return ["Nothing to do."]
