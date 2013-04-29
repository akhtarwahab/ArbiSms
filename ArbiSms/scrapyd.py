import re
from urlparse import urljoin
import requests


class scrapyd_exception(Exception):
    def __init__(self, message=None,expt=None):
        self.message = message
        Exception.__init__(self, message)

    def __str__(self):
        return repr(self.message)


class scrapyd_wrapper(object):
    def __init__(self, url, timeout=5):
        self.url = url
        self.timeout = timeout
        self.validate_server()

    def validate_server(self):
        if 'http:' not in self.url:
            self.url = 'http://%s' % self.url
        if self.url[-1] not in '/':
            self.url += '/'
        if not re.search('title[^>]*>[s|S]crapyd</title>', requests.get(self.url, timeout=self.timeout).text):
            raise scrapyd_exception, Exception


    def validate_response(self, response):
        if not isinstance(response, dict) and response['status'] == 'ok':
            raise scrapyd_wrapper

    def list_projects(self):
        """
        @return list of projects or Raise an Exception
        """
        response = requests.get(url=urljoin(self.url, "listprojects.json"),
                                headers={'Content-Type': 'application/json'}, timeout=self.timeout)
        result = response.json()
        self.validate_response(result)
        return result['projects']

    def list_version(self, project):
        """
        @return list of project version or Raise an Exception
        """
        if project in self.list_projects():
            response = requests.get(self.url + 'listversions.json?project=' + project,
                                    headers={'Content-Type': 'application/json'}, timeout=self.timeout)
            result = response.json()
            self.validate_response(result)
            return result['versions']
        else:
            raise scrapyd_exception(' Project Not found Named %s' % project)

    def list_spiders(self, project):
        """
        @return list of spiders or Raise an Exception
        """
        if project in self.list_projects():
            response = requests.get(self.url + 'listspiders.json?project=' + project,
                                    headers={'Content-Type': 'application/json'}, timeout=self.timeout)
            result = response.json()
            self.validate_response(result)
            return result['spiders']
        else:
            raise scrapyd_exception(' Project Not found Named %s' % project)

    def list_jobs(self, project):
        if project in self.list_projects():
            response = requests.get(self.url + 'listjobs.json?project=' + project,
                                    headers={'Content-Type': 'application/json'}, timeout=self.timeout)
            result = response.json()
            self.validate_response(result)
            return result
        else:
            raise scrapyd_exception(' Project Not found Named %s' % project)

    def run_spider(self, project, spider_name):
        """
        if successful return job id , else Exception
        """
        if project in self.list_projects():
            if spider_name in self.list_spiders(project):
                api_url = self.url + "schedule.json"
                data = {'project': project, 'spider': spider_name}
                response = requests.post(url=api_url, data=data)
                result = response.json()
                self.validate_response(result)
                return result['jobid']
            raise scrapyd_exception('no Spider Found')
        raise scrapyd_exception('no project Found')

    def stop_spider(self, project, job_id):
        if project in self.list_projects():
            api_url = self.url + "cancel.json"
            data = {'project': project, 'job': job_id}
            result = requests.post(url=api_url, data=data, timeout=self.timeout).json()
            self.validate_response(result)
            return 'Success , Previous State of Spider was %s' % result['prevstate']
        raise scrapyd_exception

    def delete_project(self, project):
        api_url = self.url + "delproject.json"
        data = {'project': project}
        result = requests.post(url=api_url, data=data, timeout=self.timeout).json()
        if 'status' in result and 'ok' in result['status']:
            return 'Success'
        else:
            return result['message']

    def access_log(self, project, spider, job_id):
        if project in self.list_projects() and spider in self.list_spiders(project) and job_id in self.list_jobs(
                project):
            api_url_log = self.url + 'logs/' + project + '/' + spider + '/' + job_id + '.log'
            return requests.get(api_url_log).content

    def access_log(self, project, spider, job_id):
        if project in self.list_projects() and spider in self.list_spiders(project) and job_id in self.list_jobs(
                project):
            api_url_item = self.url + 'items/' + project + '/' + spider + '/' + job_id + '.jl'
            return requests.get(api_url_item).content


r = scrapyd_wrapper(url='http://192.168.233.133:6800/')
print r.list_projects()
print r.list_projects()[0]
print r.list_version(r.list_projects()[0])
print r.list_spiders(r.list_projects()[0])
print r.list_jobs(r.list_projects()[0])
print r.run_spider('nestle', 'everyday')
print r.delete_project('nestle')
