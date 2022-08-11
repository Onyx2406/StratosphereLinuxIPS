"""Unit test for modules/virustotal/virustotal.py"""
from ..modules.virustotal.virustotal import Module
import configparser
import random
import pytest
import time
import requests
import json

def do_nothing(*args):
    """Used to override the print function because using the self.print causes broken pipes"""
    pass


def get_vt_key():
    # get the user's api key
    try:
        with open('modules/virustotal/api_key_secret', 'r') as f:
            api_key = f.read()
    except FileNotFoundError:
        api_key = ''

    return api_key

def have_available_quota(api_key):
    """
    Check if the used has available VT quota
    """
    def get_allowed(quota):
        return res.get(quota, {}).get('user', {}).get('allowed', 0)

    url = f'https://www.virustotal.com/api/v3/users/{api_key}/overall_quotas'
    headers = {'Accept': 'application/json', 'x-apikey':api_key }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            res = json.loads(response.text)['data']
            api_requests_daily = get_allowed('api_requests_daily')
            api_requests_hourly = get_allowed('api_requests_hourly')
            api_requests_monthly = get_allowed('api_requests_monthly')
            quotas = (api_requests_daily, api_requests_hourly, api_requests_monthly)
            quotas = list(map(int, quotas))

            if not any(quotas):
                # one of the above is 0
                return f'Not enough quota.'
            return True
        else:
            error = json.loads(response.text)['error']
            code = error['code']
            msg = error['message']
            return f'{response.status_code}: {code}, {msg}'
    except (
        requests.exceptions.ReadTimeout,
        requests.exceptions.ConnectionError,
        json.decoder.JSONDecodeError,
    ):
        return False


# only run the following tests if an API key was found
API_KEY = get_vt_key()
enough_quota = have_available_quota(API_KEY)
error_msg = 'API key not found'
if enough_quota != True:
    error_msg = f"server response {enough_quota}"

pytestmark = pytest.mark.skipif(
    len(API_KEY) != 64 or enough_quota != True,
    reason=f'API KEY not found or you do not have quota. error: {error_msg}',
)


@pytest.fixture
def read_configuration():
    return


def create_virustotal_instance(outputQueue):
    """Create an instance of virustotal.py
    needed by every other test in this file"""
    config = configparser.ConfigParser()
    with open('slips.conf') as conf_file:
        config.read_file(conf_file)
    virustotal = Module(outputQueue, config, 6380)
    # override the self.print function to avoid broken pipes
    virustotal.print = do_nothing
    virustotal.__read_configuration = read_configuration
    virustotal.key_file = (
        '/media/alya/W/SLIPPS/modules/virustotal/api_key_secret'
    )
    return virustotal


def test_api_limit(outputQueue):
    virustotal = create_virustotal_instance(outputQueue)
    ip = (
        str(random.randint(0, 255))
        + '.'
        + str(random.randint(0, 255))
        + '.'
        + str(random.randint(0, 255))
        + '.'
        + str(random.randint(0, 255))
    )
    virustotal.api_query_(ip)
    # remember to set a key_file


@pytest.mark.parametrize('ip', ['8.8.8.8'])
def test_api_query_(outputQueue, ip):
    """
    This one depends on the available quota
    """
    virustotal = create_virustotal_instance(outputQueue)
    response = virustotal.api_query_(ip)
    # make sure response.status != 204 or 403
    assert response != {}, 'Server Error: Response code is not 200'
    assert response['response_code'] == 1


@pytest.mark.parametrize('ip', ['8.8.8.8'])
def test_interpret_rsponse(outputQueue, ip):
    virustotal = create_virustotal_instance(outputQueue)
    response = virustotal.api_query_(ip)
    for ratio in virustotal.interpret_response(response):
        assert type(ratio) == float


def test_get_domain_vt_data(outputQueue):
    virustotal = create_virustotal_instance(outputQueue)
    assert virustotal.get_domain_vt_data('google.com') != False


def test_scan_file(outputQueue, database):
    """
    This one depends on the available quota
    """

    virustotal = create_virustotal_instance(outputQueue)
    # test this function with a hash we know is malicious
    file_info = {
        'uid': 123,
        'daddr': '8.8.8.8',
        'saddr': '8.8.8.8',
        'size': 123,
        'profileid': 'profile_192.168.1.1',
        'twid': 'timewindow0',
        'md5': '7c401bde8cafc5b745b9f65effbd588f',
        'ts': time.time(),
    }
    virustotal.file_info = file_info
    assert virustotal.scan_file(file_info) == 'malicious', 'Server Error: Response code is not 200'
