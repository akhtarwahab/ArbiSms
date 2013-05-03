from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from sms.forms import AuthenticateForm, UserCreateForm, ServerForm
from sms.models import Server
from django.template import RequestContext
from scrapyd import scrapyd

wrapper = None

def main(request, auth_form=None, user_form=None):
    # User is logged in
    if request.user.is_authenticated():
        user = request.user
        if request.method == "POST" and request.is_ajax():
            server_name = request.POST['name']
            server_address = request.POST['address']
            server_to_delete = Server.objects.filter(user_id=user.id, server_address=server_address,
                                                     server_name=server_name)
            server_to_delete.delete()
            servers_list = []
            servers = Server.objects.filter(user_id=user.id)
            for server in servers:
                dict_server = {'server_name': server.server_name, 'server_address': server.server_address}
                servers_list.append(dict_server)
            ctx = {'servers': servers_list}
            return render_to_response('server_table.html', ctx)

        else:
            server_form = ServerForm()
            servers = Server.objects.filter(user_id=user.id)
            servers_list = []
            for server in servers:
                dict_server = {'server_name': server.server_name, 'server_address': server.server_address}
                servers_list.append(dict_server)

            return render(request,
                          'servers.html',
                          {'server_form': server_form, 'user': user,
                           'next_url': '/', 'servers': servers_list})
    else:
        # User is not logged in
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or UserCreateForm()

        return render(request,
                      'home.html',
                      {'auth_form': auth_form, 'user_form': user_form, })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Success
            return redirect('/')
        else:
            # Failure
            return main(request, auth_form=form)
    return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    user_form = UserCreateForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            username = user_form.clean_username()
            password = user_form.clean_password2()
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return main(request, user_form=user_form)
    return redirect('/')


@login_required
def server_errors(request, server_form=None):
    user = request.user
    servers = Server.objects.filter(user_id=user.id)
    servers_list = []

    for server in servers:
        dict_server = {'server_name': server.server_name, 'server_address': server.server_address}
        servers_list.append(dict_server)

    return render(request,
                  'servers.html',
                  {'server_form': server_form, 'user': user,
                   'next_url': '/', 'servers': servers_list})


@login_required
def add_server(request):
    if request.method == "POST":
        server_form = ServerForm(data=request.POST)
        next_url = request.POST.get("next_url", "/")
        if server_form.is_valid():
            server = server_form.save(commit=False)
            server.user = request.user
            server.save()
            if not next_url:
                next_url = "/"
            return redirect(next_url)
        else:
            return server_errors(request, server_form)
    return redirect('/')


def projects(request):
    server_form = ServerForm()
    if request.method == 'POST':
        if request.POST['action'] == 'latest_version':

            list_version = wrapper.list_version(request.POST['project'].replace('\n', '').strip())
            ctx = {'version': list_version[-1], 'versions': [], 'project': request.POST['project'],
                   'id': request.POST['project'].replace('\n', '').strip() + "_versions"}
            return render_to_response('versions.html', ctx, context_instance=RequestContext(request))

        elif request.POST['action'] == 'all_versions':

            list_version = wrapper.list_version(request.POST['project'].replace('\n', '').strip())
            ctx = {'version': "", 'versions': list_version[:-1], 'project': request.POST['project']}
            return render_to_response('versions.html', ctx, context_instance=RequestContext(request))

        elif request.POST['action'] == 'projects':
            global wrapper
            wrapper = scrapyd(url=request.POST['address'])
            projects = wrapper.list_projects()
            ctx = {'server_form': server_form, 'projects': projects}

            return render_to_response('projects.html', ctx, context_instance=RequestContext(request))

        elif request.POST['action'] == 'delete':

            if request.POST['type'] == 'project':
                result = wrapper.delete_project(request.POST['project'])
            elif request.POST['type'] == 'version':
                result = wrapper.delete_version(request.POST['project'], request.POST['version'])

            if result == 'Success':
                projects = wrapper.list_projects()
                ctx = {'projects': projects}
                return render_to_response('projects_table.html', ctx, context_instance=RequestContext(request))
    else:
        return redirect('/')


def jobs(request):
    server_form = ServerForm()
    if request.method == "POST" and not request.is_ajax():

        project = request.POST['project']
        jobs = wrapper.list_jobs(project)
        ctx = jobs
        ctx['project'] = request.POST['project']
        ctx['server_form'] = server_form
        return render_to_response('jobs.html', ctx, context_instance=RequestContext(request))

    elif request.method == "POST" and request.is_ajax():
        if request.POST['action'] == 'log':
            log = wrapper.access_log(request.POST['project'], request.POST['spider'], request.POST['id'])
            if not log:
                log = "No Log Found"
            data = log.split('\n')
            ctx = {'item': 'log', 'data': data, 'job_id': request.POST['id']}
            return render_to_response('log_items.html', ctx, context_instance=RequestContext(request))

        elif request.POST['action'] == 'item':
            item = wrapper.access_items(request.POST['project'], request.POST['spider'], request.POST['id'])
            if not item:
                item = "No Item Found"
            data = item.split('\n')
            ctx = {'item': 'items', 'data': data, 'job_id': request.POST['id']}
            return render_to_response('log_items.html', ctx, context_instance=RequestContext(request))
    else:
        return redirect('/')


def spiders(request):
    server_form = ServerForm()
    if request.method == 'POST' and not request.is_ajax():
        spider = wrapper.list_spiders(request.POST['project'])
        ctx = {'server_form': server_form, 'spiders': spider, 'project': request.POST['project']}
        return render_to_response('spiders.html', ctx, context_instance=RequestContext(request))

    elif request.method == 'POST' and request.is_ajax():

        if request.POST['action'] == "schedule":
            schedule = wrapper.run_spider(request.POST['project'], request.POST['spider'], request.POST['cache'])
            if 'result' in schedule:
                msg = "Spider Scheduled Successfully, Job Id is :  " + schedule['result']
            if 'error' in schedule:
                msg = schedule['error']

            ctx = {'data': [msg]}
            return render_to_response('log_items.html', ctx, context_instance=RequestContext(request))

        elif request.POST['action'] == "stop":
            project = request.POST['project']
            spider = request.POST['spider']
            jobs = wrapper.list_jobs(project)
            spider_job = ''
            for job in jobs['running']:
                if job['spider'] == spider:
                    spider_job = job['id']
                    break

            if spider_job:
                response = wrapper.stop_spider(project, spider_job)
            else:
                response = "No Running Job For This Spider"
            ctx = {'data': [response]}
            return render_to_response('log_items.html', ctx, context_instance=RequestContext(request))

    else:
        return redirect('/')