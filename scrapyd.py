import re
from urlparse import urljoin
import requests


class scrapyd_exception(Exception):
    def __init__(self, message=None):
        self.message = message
        # Exception.__init__(self, message)

    def __str__(self):
        return repr(self.message)


class scrapyd(object):
    def __init__(self, url, timeout=5):
        self.url = url
        self.timeout = timeout
        self.validate_server()

    def validate_server(self):
        if 'http:' not in self.url:
            self.url = 'http://%s' % self.url
        if self.url[-1] not in '/':
            self.url += '/'
        try:
            if not re.search('title[^>]*>[s|S]crapyd</title>', requests.get(self.url, timeout=self.timeout).text):
                raise scrapyd_exception
        except:
            raise scrapyd_exception

    def validate_response(self, response):
        if not isinstance(response, dict) and response['status'] == 'ok':
            raise scrapyd

    def list_projects(self):
        """
        @return list of projects or Raise an Exception
        """
        response = requests.get(url=urljoin(self.url, "listprojects.json"),
                                headers={'Content-Type': 'application/json'}, timeout=self.timeout)
        result = response.json
        self.validate_response(result)
        return result['projects']

    def list_version(self, project):
        """
        @return list of project version or Raise an Exception
        """
        if project in self.list_projects():
            response = requests.get(self.url + 'listversions.json?project=' + project,
                                    headers={'Content-Type': 'application/json'}, timeout=self.timeout)
            result = response.json
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
            result = response.json
            self.validate_response(result)
            return result['spiders']
        else:
            raise scrapyd_exception(' Project Not found Named %s' % project)

    def list_jobs(self, project):
        if project in self.list_projects():
            response = requests.get(self.url + 'listjobs.json?project=' + project,
                                    headers={'Content-Type': 'application/json'}, timeout=self.timeout)
            result = response.json
            self.validate_response(result)
            return result
        else:
            raise scrapyd_exception(' Project Not found Named %s' % project)

    def run_spider(self, project, spider_name, cache="False"):
        """
        if successful return job id , else Exception
        """
        if project in self.list_projects():
            if spider_name in self.list_spiders(project):

                jobs = self.list_jobs(project)
                for job in jobs['running']:
                    if job['spider'] == spider_name:
                        response={'error':"Crawler is Already Running , Please Stop the Previous One First"}
                        return response

                api_url = self.url + "schedule.json"
                data = {'project': project, 'spider': spider_name}
                if cache == 'True':
                    data['setting'] = 'HTTPCACHE_EXPIRATION_SECS=0'
                else:
                    data['setting'] = 'HTTPCACHE_EXPIRATION_SECS=1'

                response = requests.post(url=api_url, data=data)
                result = response.json
                self.validate_response(result)
                return {'result':result['jobid']}
            raise scrapyd_exception('no Spider Found')
        raise scrapyd_exception('no project Found')

    def stop_spider(self, project, job_id):
        if project in self.list_projects():
            api_url = self.url + "cancel.json"
            data = {'project': project, 'job': job_id}
            result = requests.post(url=api_url, data=data, timeout=self.timeout).json
            self.validate_response(result)
            return 'Crawler Stopped Successfully , Previous State of Spider was : %s' % result['prevstate']
        raise scrapyd_exception

    def delete_project(self, project):
        api_url = self.url + "delproject.json"
        data = {'project': project}
        result = requests.post(url=api_url, data=data, timeout=self.timeout).json
        if 'status' in result and 'ok' in result['status']:
            return 'Success'
        else:
            return result['message']

    def access_log(self, project, spider, job_id):

        api_url_log = self.url + 'logs/' + project + '/' + spider + '/' + job_id + '.log'
        result = requests.get(api_url_log)
        if result.status_code == 200:
            return result.text
        else:
            return "Log has been removed increase log list size in scrapyd config file"

    def access_items(self, project, spider, job_id):

        api_url_item = self.url + 'items/' + project + '/' + spider + '/' + job_id + '.jl'
        result = requests.get(api_url_item)
        if result.status_code == 200:
            return result.text
        else:
            return "Items have been removed increase log list size in scrapyd config file"

    def delete_version(self, project, version):
        api_url = self.url + "delversion.json"
        data = {'project': project, 'version': version}
        result = requests.post(url=api_url, data=data)
        if result.json['status'] == 'ok':
            return "Success"
        else:
            return "error"
