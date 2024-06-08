import datetime
import json
import os
import sys

import requests
import yaml

conf_file = open('config.yaml', "r", encoding='utf-8')
conf = yaml.safe_load(conf_file)
cdn = 'https://api.iristory.top/'
readme = '# dist\n'
update_flag = False
commit = ""


def check_name(name, black_list, white_list):
    for black_string in black_list:
        if black_string in name:
            return None
    for white_group in white_list:
        hit_count = 0
        for k in white_group:
            if k in name:
                hit_count += 1
        if len(white_group) == hit_count:
            return name


def check_version(m):
    global commit, update_flag, readme
    headers = {'Accept': 'application/vnd.github.v3+json',
               'Content-Type': 'application/json',
               'authorization': 'Bearer ' + sys.argv[1]}
    repo = m["repo"]
    version = m["version"]
    name = m['name']
    black_list = m["black_list"]
    white_list = m["white_list"]
    gh_api = requests.get('https://api.github.com/repos/' + repo + '/releases/latest', headers=headers).text
    remote_version = str(json.loads(gh_api)['tag_name']).replace('v', '')
    assets = json.loads(gh_api)['assets']
    readme += '- **%s**\n' % name
    for asset in assets:
        out = check_name(asset["name"], black_list, white_list)
        if out is not None:
            readme += '\t- [%s](%s)\n' % (asset["name"], cdn + asset["browser_download_url"])
    if remote_version != version:
        m['version'] = remote_version
        yaml_write = open('config.yaml', "w", encoding="utf-8")
        yaml.safe_dump(conf, yaml_write, sort_keys=False)
        commit_title = repo.split('/')[1]
        commit += '**%s**: v%s -> v%s\n' % (commit_title, version, remote_version)
        update_flag = True


if __name__ == "__main__":
    for i in conf:
        check_version(i)
    if update_flag:
        file_handle = open('README.md', mode='w')
        file_handle.write(readme)
        file_handle.close()
        os.system('git config --local user.name "github-actions[bot]"')
        os.system('git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"')
        os.system('git add .')
        os.system('git commit -am "%s"' % (datetime.date.today().strftime('%Y%m%d')))
        os.system('git push')
        os.system('gh release delete new --cleanup-tag -y')
        os.system('gh release create tmp')
        os.system('gh release create new --latest --title "%s" --notes "%s"' % ("update", commit.rstrip('\n')))
        os.system('gh release delete tmp --cleanup-tag -y')
