#!/usr/bin/python
# coding:utf-8


from flask import Flask,request,jsonify,render_template,abort
import ansible_playbook
import ansible_task
import json
from celery import Celery,platforms
import db_controller

# 解困celery不能以root启动
platforms.C_FORCE_ROOT = True
app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret'
app.config['CELERY_BROKER_URL'] = 'redis://192.168.30.140:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://192.168.30.140:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task()
def run(module, command):
    res = ansible_task.Task(module, command)
    return res.get_result() 

@app.route('/playbook')
def hello_world():
    play_book = ansible_playbook.ansible_playbook(playbook='/etc/ansible/site.yml')
    play_book.run()
    result = play_book.get_result()
    return result
    
@app.route('/task/<command>')
def task(command):
    res=run.apply_async(('shell', command))
    context = {"id": res.task_id}
    d = db_controller.Main("INSERT INTO `t_task` ( `f_task_id`, `f_status`, `f_error`, `f_time`) VALUES ('%s', '10', NULL, NOW());" %(res.task_id))
    d.insert()
    return jsonify(context)    

@app.route('/taskresult/<task_id>')
def task_result(task_id):
    task = run.AsyncResult(task_id)
    if task.state == 'PENDING':
	d = db_controller.Main("UPDATE `ansible`.`t_task` SET `f_status`='1' WHERE (`f_task_id`='%s');" %(task_id)) 
        d.insert()
	response = {
	    'state': task.state,
	    'status': 'Pending...'
	}
    elif task.state != 'FAILURE':
	d = db_controller.Main("UPDATE `ansible`.`t_task` SET `f_status`='0' WHERE (`f_task_id`='%s');" %(task_id)) 
        d.insert()
        response = {
            'state': task.state,
            'status': task.info
        }
	if 'result' in task.info:
	    response['result'] = task.info['result']
    else:
	d = db_controller.Main("UPDATE `ansible`.`t_task` SET `f_status`='2' WHERE (`f_task_id`='%s');" %(task_id)) 
        d.insert()
	response = {
            'state': task.state,
            'status': task.info
        }
    return jsonify(response)

@app.route('/test')
def test():
    res = ansible_task.Task()
    result = res.get_result()
    return render_template('index.html', res=json.loads(result)['success'], res1=json.loads(result)['unreachable'], res2=json.loads(result)['failed'])
	
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
