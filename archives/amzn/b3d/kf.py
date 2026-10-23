import sys, time; sys.path.insert(0,'/home/claude/amzn/b3d')
import amz, math
t=time.time()
amz.warehouse(1); amz.camera((0.9,-3.5,1.7),(0,8,1.0),30); amz.render('/home/claude/amzn/b3d/kf_warehouse.png'); print('w',time.time()-t)
import os
if 0:
  amz.datacenter(2); amz.camera((0.2,-1.0,1.5),(0,10,1.3),26); pass
t=time.time()
amz.warehouse(3,conveyor=False,stacks=[(-0.85,1.6,10,0.42),(0.85,1.6,17,0.42)]); amz.camera((0,-7.5,2.0),(0,1.6,2.0),36); amz.render('/home/claude/amzn/b3d/kf_stacks.png'); print('s',time.time()-t)
