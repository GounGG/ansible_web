#!/usr/bin/python
#coding:utf8

import os
import json
from collections import namedtuple
from ansible.inventory import Inventory
from ansible.vars import VariableManager
from ansible.parsing.dataloader import DataLoader
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.plugins.callback import CallbackBase
from ansible.errors import AnsibleParserError
from ansible.inventory.group import Group
from ansible.inventory.host import Host

class mycallback(CallbackBase):
    def __init__(self, *args):
        super(mycallback, self).__init__(display=None)
        self.status_ok = json.dumps({}, ensure_ascii=False)
        self.status_fail = json.dumps({}, ensure_ascii=False)
        self.status_unreachable = json.dumps({}, ensure_ascii=False)
        self.status_playbook = ''
        self.status_no_hosts = False
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}

    def v2_runner_on_ok(self, result):
        host = result._host.get_name()
        self.runner_on_ok(host, result._result)
        self.host_ok[host] = result

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        self.runner_on_failed(host, result._result, ignore_errors)
        self.host_failed[host] = result

    def v2_runner_on_unreachable(self, result):
        host = result._host.get_name()
        self.runner_on_unreachable(host, result._result)
        self.host_unreachable[host] = result

    def v2_playbook_on_no_hosts_matched(self):
        self.playbook_on_no_hosts_matched()
        self.status_no_hosts = True

    def v2_playbook_on_play_start(self, play):
        self.playbook_on_play_start(play.name)
        self.playbook_path = play.name

class MyInventory(Inventory):  
    """ 
    this is my ansible inventory object. 
    """  
    def __init__(self, resource, loader, variable_manager):  
        """ 
        resource的数据格式是一个列表字典，比如 
            { 
                "group1": { 
                    "hosts": [{"hostname": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...], 
                    "vars": {"var1": value1, "var2": value2, ...} 
                } 
            } 
 
        如果你只传入1个列表，这默认该列表内的所有主机属于my_group组,比如 
            [{"hostname": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...] 
        """  
        self.resource = resource  
        self.inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=[])  
        self.gen_inventory()  
  
    def my_add_group(self, hosts, groupname, groupvars=None):  
        """ 
        add hosts to a group 
        """  
        my_group = Group(name=groupname)  
  
        # if group variables exists, add them to group  
        if groupvars:  
            for key, value in groupvars.iteritems():  
                my_group.set_variable(key, value)  
  
        # add hosts to group  
        for host in hosts:  
            # set connection variables  
            hostname = host.get("hostname")  
            hostip = host.get('ip', hostname)  
            hostport = host.get("port")  
            username = host.get("username")  
            password = host.get("password")  
            ssh_key = host.get("ssh_key")  
            my_host = Host(name=hostname, port=hostport)  
            my_host.set_variable('ansible_ssh_host', hostip)  
            my_host.set_variable('ansible_ssh_port', hostport)  
            my_host.set_variable('ansible_ssh_user', username)  
            my_host.set_variable('ansible_ssh_pass', password)  
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)  
  
            # set other variables  
            for key, value in host.iteritems():  
                if key not in ["hostname", "port", "username", "password"]:  
                    my_host.set_variable(key, value)  
            # add to group  
            my_group.add_host(my_host)  
  
        self.inventory.add_group(my_group)  
  
    def gen_inventory(self):  
        """ 
        add hosts to inventory. 
        """  
        if isinstance(self.resource, list):  
            self.my_add_group(self.resource, 'default_group')  
        elif isinstance(self.resource, dict):  
            for groupname, hosts_and_vars in self.resource.iteritems():  
                self.my_add_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("vars"))

class ansible_playbook(object):
    # 初始化各项参数,根据需求修改
    def __init__(self, playbook, hosts,ansible_cfg=None, passwords={}):
        self.playbook_path = playbook
	self.hosts = hosts
        self.passwords = passwords
        Options = namedtuple('Options', 
			    ['listtags', 
		            'listtasks', 
                            'listhosts', 
                            'syntax', 
                            'connection',
                            'module_path',
                            'forks', 
                            'remote_user', 
                            'private_key_file', 
                            'ssh_common_args', 
                            'ssh_extra_args',
                            'sftp_extra_args', 
                            'scp_extra_args', 
                            'become', 
                            'become_method', 
                            'become_user',
                            'verbosity', 
                            'check'
                            ])
	self.options = Options(listtags=False, 
                               listtasks=False, 
                               listhosts=False, 
                               syntax=False, 
                               connection='smart',
                               module_path='/usr/lib/python2.6/site-packages/ansible/modules/', 
                               forks=100,remote_user='root', 
                               private_key_file=None, 
                               ssh_common_args=None, 
                               ssh_extra_args=None,
                               sftp_extra_args=None, 
                               scp_extra_args=None, 
                               become=False, 
                               become_method=None, 
                               become_user='root',
                               verbosity=None, 
                               check=False
                              )
        if ansible_cfg != None:
            os.environ["ANSIBLE_CONFIG"] = ansible_cfg
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        #self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager, host_list=host_list)
        self.inventory = MyInventory(self.hosts, self.loader, self.variable_manager).inventory 
  	self.variable_manager.set_inventory(self.inventory)	

    # 定义运行的方法和返回值
    def run(self):
        #判断playbook是否存在
        if not os.path.exists(self.playbook_path):
            code = 1000
            results = {'playbook': self.playbook_path, 
		       'msg': self.playbook_path + ' playbook is not exist',
                       'flag': False
		      }
        pbex = PlaybookExecutor(playbooks=[self.playbook_path],
                                inventory=self.inventory,
                                variable_manager=self.variable_manager,
                                loader=self.loader,
                                options=self.options,
                                passwords=self.passwords
				)
        self.results_callback = mycallback()
        pbex._tqm._stdout_callback = self.results_callback

        try:
            code = pbex.run()
        except AnsibleParserError:
            code = 1001
            results = {'playbook': self.playbook_path, 'msg': self.playbook_path + ' playbook have syntax error',
                       'flag': False}
            return code, results
        if self.results_callback.status_no_hosts:
            code = 1002
            results = {'playbook': self.playbook_path, 'msg': self.results_callback.status_no_hosts, 'flag': False,
                       'executed': False}
            return code, results

    def get_result(self):
        result_all = {'success': {}, 'failed': {}, 'unreachable': {}}

        for host, result in self.results_callback.host_ok.items():
            result_all['success'][host] = result._result

        for host, result in self.results_callback.host_failed.items():
	    if 'msg' in result._result:
                result_all['failed'][host] = result._result['msg']

        for host, result in self.results_callback.host_unreachable.items():
	    if 'msg' in result._result:
                result_all['unreachable'][host] = result._result['msg']
	
	return json.dumps(result_all, ensure_ascii=False,sort_keys=True, indent=2)

if __name__ == '__main__':
    hosts = {
             "group1": {
                    "hosts": [{"hostname": "192.168.30.141", "port": "22", "username": "root", "password": "oracle"}],
                    "vars": {"var1": "value1"}
             }
    }

    play_book = ansible_playbook(playbook='/etc/ansible/playbook_yaml/user.yml', hosts = hosts)
    play_book.run()
    print play_book.get_result()
