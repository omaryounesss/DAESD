"""Duplicate the complete horizontal executable operational F2, activating ordering."""
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
B='http://www.omg.org/spec/BPMN/20100524/MODEL';Z='http://camunda.org/schema/zeebe/1.0';D='http://www.omg.org/spec/BPMN/20100524/DI';C='http://www.omg.org/spec/DD/20100524/DC';I='http://www.omg.org/spec/DD/20100524/DI'
for k,v in [('bpmn',B),('zeebe',Z),('bpmndi',D),('dc',C),('di',I),('modeler','http://camunda.org/schema/modeler/1.0')]:E.register_namespace(k,v)
def t(n):return '{'+B+'}'+n
def add(p,n,a=None,text=None,ns=B):
 e=E.SubElement(p,'{'+ns+'}'+n,a or {});e.text=text;return e
root=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn').getroot();p=root.find(t('process'));oldpid=p.get('id');p.set('id','f2_customer_ordering');p.set('name','Place an order - full operational F2 (simulated payment)')
coll=root.find(t('collaboration'));plane=root.find('.//{'+D+'}BPMNPlane')
for part in coll.findall(t('participant')):
 if part.get('processRef')==oldpid:part.set('processRef','f2_customer_ordering')
# Prevent this duplicate from consuming the producer/scheduler/payment messages
# owned by the original inventory deployment. All original paths remain visible.
for msg in root.findall(t('message')):msg.set('name','ordering-copy-'+msg.get('name'))
producerStart=p.find("./"+t('startEvent')+"[@id='Start_ProducerUpdate']")
if producerStart is not None:
 msg=add(root,'message',{'id':'OrderingInactiveProducerMessage','name':'ordering-copy-producer-update'})
 add(producerStart,'messageEventDefinition',{'id':'OrderingInactiveProducerDefinition','messageRef':msg.get('id')})
# Preserve the entire original horizontal geometry; make room on its left
# for customer entry and payment, and below it for compensation.
SHIFT=2200
poolids={e.get('id') for e in coll.findall(t('participant'))};laneids={e.get('id') for e in p.findall('.//'+t('lane'))}
for s in plane.findall('{'+D+'}BPMNShape'):
 bounds=s.find('{'+C+'}Bounds');ident=s.get('bpmnElement')
 if ident in poolids or ident in laneids:
  bounds.set('width',str(float(bounds.get('width'))+SHIFT+350))
  if ident in ('Participant_041bi7k','Lane_1w7vtzs'):bounds.set('height',str(float(bounds.get('height'))+400))
  elif ident in ('Participant_1dxapzq','Participant_1607470'):bounds.set('y',str(float(bounds.get('y'))+400))
 else:bounds.set('x',str(float(bounds.get('x'))+SHIFT))
for edge in plane.findall('{'+D+'}BPMNEdge'):
 for point in edge.findall('{'+I+'}waypoint'):
  point.set('x',str(float(point.get('x'))+SHIFT))
  if float(point.get('y'))>=1890:point.set('y',str(float(point.get('y'))+400))
for label in plane.findall('.//{'+D+'}BPMNLabel'):
 bounds=label.find('{'+C+'}Bounds')
 if bounds is not None:bounds.set('x',str(float(bounds.get('x'))+SHIFT))
# Original order entry becomes the only none start event in the ordering copy.
start=p.find("./"+t('startEvent')+"[@id='Event_0k7qpmm']");start.set('name','Customer starts order')
for c in list(start):
 if c.tag==t('messageEventDefinition'):start.remove(c)
for parent in (coll,plane):
 for c in list(parent):
  if c.get('id')=='Flow_0l1hzri' or c.get('bpmnElement')=='Flow_0l1hzri':parent.remove(c)
for f in list(p.findall(t('sequenceFlow'))):
 if f.get('sourceRef') in ('Event_0k7qpmm','Activity_0wf1ny8'):p.remove(f)
for edge in list(plane.findall('{'+D+'}BPMNEdge')):
 if not any(e.get('id')==edge.get('bpmnElement') for e in root.iter()):plane.remove(edge)
reduce=p.find("./"+t('serviceTask')+"[@id='Activity_0wf1ny8']");reduce.find('.//{'+Z+'}taskDefinition').set('type','f2-commit-order')
positions={}
def shape(i,x,y,w,h):
 positions[i]=(x,y,w,h);s=add(plane,'BPMNShape',{'id':i+'_di','bpmnElement':i},ns=D);add(s,'Bounds',dict(x=str(x),y=str(y),width=str(w),height=str(h)),ns=C)
 if w<90:
  label=add(s,'BPMNLabel',ns=D);add(label,'Bounds',dict(x=str(x-25),y=str(y+h+4),width='100',height='35'),ns=C)
for s in plane.findall('{'+D+'}BPMNShape'):
 b=s.find('{'+C+'}Bounds');positions[s.get('bpmnElement')]=tuple(float(b.get(k)) for k in ('x','y','width','height'))
# Relocate only the purchase start; all other original nodes stay in place.
for s in plane.findall('{'+D+'}BPMNShape'):
 if s.get('bpmnElement')=='Event_0k7qpmm':
  plane.remove(s);break
shape('Event_0k7qpmm',242,1532,36,36)
def node(i,typ,name,x,y,job=None,form=None):
 n=add(p,typ,{'id':i,'name':name})
 if job or form:
  ext=add(n,'extensionElements')
  if job:add(ext,'taskDefinition',{'type':'f2-'+job,'retries':'3'},ns=Z)
  if form:add(ext,'userTask',ns=Z);add(ext,'formDefinition',{'formId':form,'bindingType':'deployment'},ns=Z)
 shape(i,x,y,50 if typ=='exclusiveGateway' else (36 if typ=='endEvent' else 140),50 if typ=='exclusiveGateway' else (36 if typ=='endEvent' else 80))
 lane=p.find('.//'+t('lane')+"[@id='Lane_1w7vtzs']");add(lane,'flowNodeRef',text=i)
 return n
for args in [
 ('Load','serviceTask','Load available products',330,1510,'prepare-order'),
 ('Order','userTask','Place order',530,1510,None,'f2-place-order'),
 ('Validate','serviceTask','Check stock and seasonal availability',730,1510,'validate-order'),
 ('Valid','exclusiveGateway','Order valid?',930,1525),
 ('PayChoice','userTask','Choose simulated payment outcome',1080,1510,None,'f2-demo-payment'),
 ('Authorize','serviceTask','Authorize simulated payment',1300,1510,'authorize-payment'),
 ('Paid','exclusiveGateway','Payment authorized?',1510,1525),
 ('Committed','exclusiveGateway','Stock committed?',2535,1660),
 ('Capture','serviceTask','Capture simulated payment',2680,1730,'settle-payment'),
 ('Void','serviceTask','Cancel simulated payment authorization',2310,1930,'settle-payment'),
 ('Reject','userTask','View rejected order',1910,1930,None,'f2-order-result'),
 ('Declined','endEvent','Order rejected',2130,1952),
 ('Result','userTask','View completed order',4210,1610,None,'f2-order-result')]:node(*args)
# Keep the original end event and all original stock-status gateways/tasks.
end=p.find("./"+t('endEvent')+"[@id='Event_03jyftw']")
for f in p.findall(t('sequenceFlow')):
 if f.get('targetRef')=='Event_03jyftw':f.set('targetRef','Result')
for s in plane.findall('{'+D+'}BPMNShape'):
 if s.get('bpmnElement')=='Event_03jyftw':
  b=s.find('{'+C+'}Bounds');b.set('x','4430');positions['Event_03jyftw']=(4430,float(b.get('y')),36,36)
count=0
def flow(src,dst,condition=None,default=False):
 global count
 count+=1;i='OrderAddedFlow'+str(count);a={'id':i,'sourceRef':src,'targetRef':dst}
 if condition:a['name']='Yes'
 if default:a['name']='No';next(n for n in p if n.get('id')==src).set('default',i)
 f=add(p,'sequenceFlow',a)
 if condition:add(f,'conditionExpression',text=condition)
 return f
for src,dst in [('Event_0k7qpmm','Load'),('Load','Order'),('Order','Validate'),('Validate','Valid'),('PayChoice','Authorize'),('Authorize','Paid'),('Activity_0wf1ny8','Committed'),('Capture','Gateway_03r47f5'),('Void','Reject'),('Reject','Declined'),('Result','Event_03jyftw')]:flow(src,dst)
for src,dst,cond,other in [('Valid','PayChoice','=orderValid','Reject'),('Paid','Activity_0wf1ny8','=paymentAuthorized','Reject'),('Committed','Capture','=orderAccepted','Void')]:flow(src,dst,cond);flow(src,other,default=True)
# Rebuild flow references; retain all original data stores and associations.
for scope in p.iter():
 if scope.tag not in (t('process'),t('subProcess')):continue
 index={e.get('id'):e for e in scope if e.get('id')}
 for n in index.values():
  for c in list(n):
   if c.tag in (t('incoming'),t('outgoing')):n.remove(c)
 for f in scope.findall(t('sequenceFlow')):add(index[f.get('sourceRef')],'outgoing',text=f.get('id'));add(index[f.get('targetRef')],'incoming',text=f.get('id'))
 for n in index.values():
  order={'documentation':0,'extensionElements':1,'incoming':2,'outgoing':3,'property':4,'dataInputAssociation':5,'dataOutputAssociation':6}
  n[:]=sorted(n,key=lambda c:order.get(c.tag.split('}')[-1],9))
# Draw only new or retargeted purchase flows, keeping existing routed geometry.
flowindex={f.get('id'):f for f in p.findall(t('sequenceFlow'))}
for edge in list(plane.findall('{'+D+'}BPMNEdge')):
 f=flowindex.get(edge.get('bpmnElement'))
 if f is not None and f.get('targetRef')=='Result':plane.remove(edge)
existing={e.get('bpmnElement') for e in plane}
for f in p.findall(t('sequenceFlow')):
 if f.get('id') in existing:continue
 sx,sy,sw,sh=positions[f.get('sourceRef')];dx,dy,dw,dh=positions[f.get('targetRef')]
 edge=add(plane,'BPMNEdge',{'id':f.get('id')+'_di','bpmnElement':f.get('id')},ns=D)
 points=[(sx+sw,sy+sh/2),(dx,dy+dh/2)]
 if abs(sy-dy)>70:points=[(sx+sw/2,sy+sh),(sx+sw/2,dy+dh/2),(dx,dy+dh/2)]
 for x,y in points:add(edge,'waypoint',{'x':str(x),'y':str(y)},ns=I)
# Payment message lines use the existing Payment Provider pool.
for i,src in [('OrderingAuthorizationRequest','Authorize'),('OrderingCaptureRequest','Capture'),('OrderingVoidRequest','Void')]:
 add(coll,'messageFlow',{'id':i,'sourceRef':src,'targetRef':'Participant_1607470'})
 sx,sy,sw,sh=positions[src];edge=add(plane,'BPMNEdge',{'id':i+'_di','bpmnElement':i},ns=D)
 for x,y in [(sx+sw/2,sy+sh),(sx+sw/2,2380)]:add(edge,'waypoint',{'x':str(x),'y':str(y)},ns=I)
for definition in root.findall('.//{'+Z+'}formDefinition'):
 definition.set('bindingType','latest')
# Widening the full model keeps producer, marketplace, payment and notification pools.
root[:]=sorted(root,key=lambda e:1 if e.tag.startswith('{'+D+'}') else 0)
E.indent(root);E.ElementTree(root).write(ROOT/'camunda/f2/processes/place-order.bpmn',encoding='utf-8',xml_declaration=True)
E.ElementTree(root).write(ROOT/'camunda/f2/processes/place-order-horizontal.bpmn',encoding='utf-8',xml_declaration=True)
print('Built complete horizontal operational duplicate; original inventory unchanged.')
