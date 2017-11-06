# Ansible API

**故障:**

1. Flask/Django+Ansible+Celery无数据返回，正常执行无影响。

   ```shell	
   有两种方法解决这个问题，就是关闭assert：
   1.在celery 的worker启动窗口设置export PYTHONOPTIMIZE=1或打开celery这个参数-O OPTIMIZATION
   2.注释掉python包multiprocessing下面process.py中102行，关闭assert

   -O       在执行前对解释器产生的字节码进行优化。同 PYTHONOPTIMIZE=1。
   ```

**数据库结构**
```sql
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for t_task
-- ----------------------------
DROP TABLE IF EXISTS `t_task`;
CREATE TABLE `t_task` (
  `f_id` int(11) NOT NULL AUTO_INCREMENT,
  `f_task_id` varchar(40) NOT NULL,
  `f_status` varchar(255) DEFAULT NULL,
  `f_error` varchar(255) DEFAULT NULL,
  `f_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`f_id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8;
```
