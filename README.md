# Ansible AP

**故障:**

1. Flask/Django+Ansible+Celery无数据返回，正常执行无影响。

   ```shell	
   有两种方法解决这个问题，就是关闭assert：
   1.在celery 的worker启动窗口设置export PYTHONOPTIMIZE=1或打开celery这个参数-O OPTIMIZATION
   2.注释掉python包multiprocessing下面process.py中102行，关闭assert

   -O       在执行前对解释器产生的字节码进行优化。同 PYTHONOPTIMIZE=1。
   ```

​	