from django.conf import settings
from django.db import models
import logging
import requests

log = logging.getLogger('genoome.twentythree.models')

class Token23(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField()
    scope = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class ClientError(Exception):
        pass

    def _api_get(self, url):
        headers = {
            'Authorization': 'Bearer %s' % self.access_token,
        }
        url = "https://api.23andme.com%s" % (url,)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            # https://api.23andme.com/docs/errors/ 
            log.warning('23andme error response: %s\nurl:%s', response.text, url)
            raise self.ClientError
        return response.json()

    @classmethod
    def get_by_code(klass, user, code):
        # https://api.23andme.com/docs/authentication/ 
        # curl https://api.23andme.com/token/
        #       -d client_id=xxx \
        #       -d client_secret=yyy \
        #       -d grant_type=authorization_code \
        #       -d code=zzz \
        #       -d "redirect_uri=https://localhost:5000/receive_code/"
        #       -d "scope=basic%20rs3094315"
        post_data = {
            'client_id': settings.CLIENT_ID23,
            'client_secret': settings.CLIENT_SECRET23,
            'scope': 'basic genomes',
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.COMEBACK_URL23,
        }
        response = requests.post('https://api.23andme.com/token/', data=post_data, timeout=30.00, verify=True)
        if response.status_code != 200:
            log.error('Problem fetching token %s %s', response.status_code, response.text)
            raise klass.ClientError
        data = response.json()
        initial = {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'scope': data['scope'],
        }
        instance, created = klass.objects.get_or_create(user=user, defaults=initial)
        if not created:
            log.warning('Updating initial token for %s', user)
            for key in initial:
                setattr(instance, key, initial[key])
            instance.save()
        log.debug('Token for %s ready!', user)
        return instance

    def refresh(self):
        post_data = {
            'client_id': settings.CLIENT_ID23,
            'client_secret': settings.CLIENT_SECRET23,
            'scope': self.scope,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'redirect_uri': settings.COMEBACK_URL23,
        }
        response = requests.post('https://api.23andme.com/token/', data=post_data, timeout=30.00, verify=True)
        if response.status_code != 200:
            log.error('Problem refreshing token %s %s', response.status_code, response.text)
            raise self.ClientError
        data = response.json()
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.scope = data['scope']
        self.save()

    def get_genome(self, profile_id23):
        # GET /1/genomes/profile_id/?unfiltered=...
        # curl https://api.23andme.com/1/genomes/c44.../ -H "..."
        # https://api.23andme.com/res/txt/snps.b4e00fe1db50.data 
        # scope required: genomes
        data = self._api_get('/1/genomes/%s/' % (profile_id23,))
        return data['genome']

    def get_profiles(self):
        # GET /1/user/
        # # JSON response:
        #{
        #    "id": "a42e94634e3f7683",
        #    "profiles": [
        #        {
        #            "genotyped": true,
        #            "id": "c4480ba411939067"
        #        }, ...
        #    ]
        #}
        # scope required: basic

        data = self._api_get('/1/user/')
        return data['profiles']


class CeleryTask23(models.Model):
    STATUS_CHOICES = (
        ('new', 'new'),
        ('fetching', 'fetching genome'),
        ('parsing', 'parsing genome'),
        ('error', 'error'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    chosen_profile = models.TextField()
    fetch_task_id = models.TextField()
    analyze_order = models.ForeignKey('disease.AnalyzeDataOrder', null=True)
    process_task_id = models.TextField(null=True)
    status = models.TextField(choices=STATUS_CHOICES, default='new')
