import datetime
import json
import os
import sys

import requests
import yaml

conf_file = open('config.yaml', "r", encoding='utf-8')
conf = yaml.safe_load(conf_file)
cdn = 'https://api.azzb.club/'
update_flag = False
commit = ""
linux_readme = android_readme = windows_readme = ""
cur_repo = ""
cur_version = ""
cur_filename = []


def get_conf(m):
    global cur_repo, cur_version, cur_filename
    cur_repo = m['repo']
    cur_version = m['version']
    cur_filename = m['filename']


def gen_readme(version):
    global linux_readme, android_readme, windows_readme
    for n in cur_filename:
        os_type = n.get('os')
        path_name = get_name(n.get('path_name'), version)
        full_name = n.get('full_name')
        url = cdn + 'https://github.com/' + cur_repo + '/releases/latest/download/' + path_name
        if os_type == 'windows':
            windows_readme += '\t- **%s**: [%s](%s)\n' % (full_name, path_name, url)
        elif os_type == 'linux':
            linux_readme += '\t- **%s**: [%s](%s)\n' % (full_name, path_name, url)
        elif os_type == 'android':
            android_readme += '\t- **%s**: [%s](%s)\n' % (full_name, path_name, url)
        else:
            print('readme err :', full_name, os_type)


def add_readme():
    global linux_readme, android_readme, windows_readme
    file_handle = open('README.md', mode='w')
    file_handle.write("# dist\n- **windows**\n%s\n- **linux**\n%s\n- **android**\n%s" %
                      (windows_readme, linux_readme, android_readme))
    file_handle.close()


def get_name(name, version):
    if name.count('%s'):
        name = name % version
    return name


def check_version(m):
    global commit, update_flag
    headers = {'Accept': 'application/vnd.github.v3+json',
               'Content-Type': 'application/json',
               'authorization': 'Bearer ' + sys.argv[1]}
    gh_api = requests.get('https://api.github.com/repos/' + cur_repo + '/releases/latest', headers=headers).text
    remote_version = str(json.loads(gh_api)['tag_name']).replace('v', '')
    if remote_version == cur_version:
        gen_readme(cur_version)
    else:
        gen_readme(remote_version)
        m['version'] = remote_version
        yaml_write = open('config.yaml', "w", encoding="utf-8")
        yaml.safe_dump(conf, yaml_write, sort_keys=False)
        commit_title = cur_repo.split('/')[1]
        commit += '**%s**: v%s -> v%s\n' % (commit_title, cur_version, remote_version)
        update_flag = True


if __name__ == "__main__":
    for i in conf:
        get_conf(i)
        check_version(i)
    if update_flag:
        add_readme()
        os.system('git config --local user.name "github-actions[bot]"')
        os.system('git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"')
        os.system('git add .')
        os.system('git commit -am "%s"' % (datetime.date.today().strftime('%Y%m%d')))
        os.system('git push')
        os.system('gh release delete new --cleanup-tag -y')
        os.system('gh release create tmp')
        os.system('gh release create new --title "%s" --notes "%s"' % ("update", commit.rstrip('\n')))
        os.system('gh release delete tmp --cleanup-tag -y')
