# coding=utf-8
import os
import sys

root_path = os.path.split(os.path.realpath(__file__))[0] + '/../'
sys.path.append(root_path)

try:
    import yaml
except ImportError:
    os.system('pip install pyyaml')
    import yaml


def load_yaml(yaml_path):
    if os.path.exists(yaml_path) is False:
        utils_common.exec_shell_cmd("touch " + yaml_path)
    yaml_file = open(yaml_path)
    return yaml.load(yaml_file, Loader=yaml.FullLoader)


if __name__ == '__main__':
    yaml_path = envs.get_out_dir() + "schduler.yaml"
    project = {
        'feizu_account': "",
        'feizu_password': "",
        'email_receiver': "",
        'sender_list': [
            {'email_sender_host': '',
             'email_sender_user': '',
             'email_sender_pwd': ''}]
    }
    f = open(yaml_path, 'w')
    yaml.dump(project, f)
    f.close()
