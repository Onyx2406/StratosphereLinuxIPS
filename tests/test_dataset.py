"""
This file tests all kinds of input in our dataset/
It checks a random evidence and the total number of profiles in every file
"""
import os
import pytest
import  shutil
alerts_file = 'alerts.json'

def is_evidence_present(log_file, expected_evidence):
    """ Function to read the log file line by line and returns when it finds the expected evidence """
    with open(log_file, 'r') as f:
        line = f.readline()
        while line:
            if expected_evidence in line:
                return True
            line = f.readline()
        # evidence not found in any line
        return False

def has_errors(output_file):
    """ function to parse slips_output file and check for errors """
    # we can't redirect stderr to a file and check it because we catch all exceptions in slips
    with open(output_file ,'r') as f:
        for line in f:
            if '<class' in line or 'error' in line:
                return True

    return False


@pytest.mark.parametrize("pcap_path,expected_profiles, output_dir, expected_evidence",
                         [('dataset/hide-and-seek-short.pcap',15,'pcap/', 'horizontal port scan to port  23'),
                          ('dataset/arp-only.pcap',3,'pcap2/','performing an arp scan')])
def test_pcap(pcap_path, expected_profiles, database, output_dir, expected_evidence):
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    output_file = f'{output_dir}slips_output.txt'
    command = f'./slips.py -I -f {pcap_path} -o {output_dir} > {output_file} 2>&1'
    # this function returns when slips is done
    os.system(command)
    assert has_errors(output_file) == False
    profiles = int(database.getProfilesLen())
    assert profiles > expected_profiles
    log_file = output_dir + alerts_file
    assert is_evidence_present(log_file, expected_evidence) == True
    shutil.rmtree(output_dir)

@pytest.mark.skipif( 'nfdump' not in shutil.which('nfdump'), reason="nfdump is not installed")
@pytest.mark.parametrize("binetflow_path, expected_profiles, expected_evidence, output_dir", [
     ('dataset/test2.binetflow', 1, 'Connection to unknown destination port 7275/TCP destination IP 64.233.167.192','test2/'),
    ('dataset/test3.binetflow', 20, 'horizontal port scan to port  3389','test3/'),
      ('dataset/test4.binetflow', 2, 'horizontal port scan to port  81','test4/'),
     ('dataset/test5.binetflow', 4, 'Long Connection','test5/')])
def test_binetflow(database, binetflow_path, expected_profiles, expected_evidence,  output_dir ):
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    output_file = f'{output_dir}slips_output.txt'
    command = f'./slips.py -I -o {output_dir} -f {binetflow_path}  >  {output_file} 2>&1'
    # this function returns when slips is done
    os.system(command)
    assert has_errors(output_file) == False
    profiles = int(database.getProfilesLen())
    assert profiles > expected_profiles
    log_file = output_dir + alerts_file
    assert is_evidence_present(log_file, expected_evidence) == True
    shutil.rmtree(output_dir)


@pytest.mark.parametrize("zeek_dir_path,expected_profiles, expected_evidence,  output_dir",
     [('dataset/sample_zeek_files', 4,

       ['SSL certificate validation failed with (certificate is not yet valid)',
        'performing bad SMTP login to 80.75.42.226',
        'performing SMTP login bruteforce to 80.75.42.226. 3 logins in 10 seconds',
        'multiple empty HTTP connections to bing.com',
        'Detected Possible SSH bruteforce by using multiple SSH versions 9_1 then 8_1'],

       'sample_zeek_files/'),

      ('dataset/sample_zeek_files-2', 20, 'horizontal port scan', 'sample_zeek_files-2/')])
def test_zeek_dir(database, zeek_dir_path, expected_profiles, expected_evidence, output_dir):
    import time
    time.sleep(3)
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    output_file = f'{output_dir}slips_output.txt'
    command = f'./slips.py -I -f {zeek_dir_path}  -o {output_dir} > {output_file} 2>&1'
    # this function returns when slips is done
    os.system(command)
    assert has_errors(output_file) == False
    profiles = int(database.getProfilesLen())
    assert profiles > expected_profiles
    log_file = output_dir + alerts_file
    if type(expected_evidence) == list:
        # make sure all the expected evidence are there
        for evidence in expected_evidence:
            assert is_evidence_present(log_file, evidence) == True
    else:
        assert is_evidence_present(log_file, expected_evidence) == True
    shutil.rmtree(output_dir)

@pytest.mark.parametrize("conn_log_path, expected_profiles, expected_evidence,  output_dir",
     [('dataset/sample_zeek_files/conn.log',4,
       'a connection without DNS resolution to IP: 185.33.223.203','conn_log/'),

      ('dataset/sample_zeek_files-2/conn.log',5,
       'connection without DNS resolution to IP: 2a04:4e42:41::223','conn_log-2/')])

def test_zeek_conn_log(database, conn_log_path, expected_profiles, expected_evidence,  output_dir):
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    output_file = f'{output_dir}slips_output.txt'
    command = f'./slips.py -I -f {conn_log_path}  -o {output_dir} > {output_file} 2>&1'
    # this function returns when slips is done
    os.system(command)
    assert has_errors(output_file) == False
    profiles = int(database.getProfilesLen())
    assert profiles > expected_profiles
    log_file = output_dir + alerts_file
    assert is_evidence_present(log_file, expected_evidence) == True
    shutil.rmtree(output_dir)

@pytest.mark.parametrize('suricata_path,  output_dir',[('dataset/suricata-flows.json','suricata/')])
def test_suricata(database, suricata_path,  output_dir):
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    output_file = f'{output_dir}slips_output.txt'
    command = f'./slips.py -I -f {suricata_path} -o {output_dir} > {output_file} 2>&1'
    # this function returns when slips is done
    os.system(command)
    profiles = int(database.getProfilesLen())
    expected_evidence = 'vertical port scan'
    assert has_errors(output_file) == False
    assert profiles > 90
    log_file = output_dir + alerts_file
    assert is_evidence_present(log_file, expected_evidence) == True
    shutil.rmtree(output_dir)

@pytest.mark.parametrize('nfdump_path,  output_dir',[('dataset/test.nfdump', 'nfdump/')])
def test_nfdump(database, nfdump_path,  output_dir):
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    output_file = f'{output_dir}slips_output.txt'
    command = f'./slips.py -I -f {nfdump_path}  -o {output_dir} > {output_file} 2>&1'
    # this function returns when slips is done
    os.system(command)
    profiles = int(database.getProfilesLen())
    expected_evidence = 'Connection to unknown destination port 902/TCP'
    assert has_errors(output_file) == False
    # make sure slips generated profiles for this file (can't the number of profiles exactly because slips doesn't generate a const number of profiles per file)
    assert profiles > 0
    log_file = output_dir + alerts_file
    assert is_evidence_present(log_file, expected_evidence) == True
    shutil.rmtree(output_dir)