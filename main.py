import json
import os
import sys

import requests
import yaml

conf_file = open('config.yaml', "r", encoding='utf-8')
conf = yaml.safe_load(conf_file)
cdn = 'https://api.azzb.club/'


def add_readme():
    android_readme = []
    windows_readme = []
    linux_readme = []
    for k in conf:
        filename = k['filename']
        version = str(k['version'])
        repo = k['repo']
        for n in filename:
            os_type = n.get('os')
            path_name = get_name(n.get('path_name'), version)
            name_str = os.path.splitext(path_name)[0]
            for files in os.listdir(os_type):
                if name_str + "." in files:
                    path_name = files
            full_name = n.get('full_name')
            url = cdn + 'https://github.com/' + repo + '/releases/latest/download/' + path_name
            if os_type == 'windows':
                windows_readme.append('  - **%s**: [%s](%s)\n' % (full_name, path_name, url))
            elif os_type == 'linux':
                linux_readme.append('  - **%s**: [%s](%s)\n' % (full_name, path_name, url))
            elif os_type == 'android':
                android_readme.append('  - **%s**: [%s](%s)\n' % (full_name, path_name, url))
            else:
                print('readme err :', full_name, os_type)
    file_handle = open('README.md', mode='w')
    file_handle.write("# dist\n- **windows**\n")
    file_handle.writelines(windows_readme)
    file_handle.write("- **linux**\n")
    file_handle.writelines(linux_readme)
    file_handle.write("- **android**\n")
    file_handle.writelines(android_readme)
    file_handle.close()


def get_name(name, version):
    if name.count('%') == 1:
        name = name % version
    return name


def check_version(repo, local_version, m):
    headers = {'Accept': 'application/vnd.github.v3+json',
               'Content-Type': 'application/json',
               'authorization': 'Bearer ' + sys.argv[1]}
    gh_api = requests.get('https://api.github.com/repos/' + repo + '/releases/latest', headers=headers).text
    remote_version = str(json.loads(gh_api)['tag_name']).replace('v', '')
    if remote_version == local_version:
        return local_version, 0
    else:
        m['version'] = remote_version
        yaml_write = open('config.yaml', "w", encoding="utf-8")
        yaml.safe_dump(conf, yaml_write, sort_keys=False)
        add_readme()
        return remote_version, 1


def main(m):
    repo = m['repo']
    local_version = str(m['version'])
    (version, update_code) = check_version(repo, local_version, m)
    if update_code == 0:
        return
    commit_title = repo.split('/')[1]
    commit = '"%s: v%s -> v%s "' % (commit_title, local_version, version)
    os.system('''cat version.json | tr -d '",{}' | grep -v "^$" > version''')
    os.system('git config --local user.name "github-actions[bot]"')
    os.system('git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"')
    os.system('git add .')
    os.system('git commit -am ' + commit.rstrip(' '))
    os.system('git push')


if __name__ == "__main__":
    for i in conf:
        main(i)
