yml文件
```yaml
---
- hosts: group1
  name: add user
  remote_user: root

  vars:
     - user: "fjp"

  tasks:
     - name: create {{user}} on zabbix
       shell: id "{{user}}"
```

host inventory
```python
    hosts = {
             "group1": {
                    "hosts": [{"hostname": "192.168.30.141", "port": "22", "username": "root", "password": "oracle"}],
                    "vars": {"var1": "value1"}
             }
    }
```

手动执行效果
![](https://note.youdao.com/yws/public/resource/b68036344acf7ba5061a8c33d5d27fd6/xmlnote/16858B3D0E8346B58525EC6CD41B4B9C/10514)
