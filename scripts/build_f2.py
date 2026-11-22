from pathlib import Path
import xml.etree.ElementTree as E
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'models/operational-bpmn/functionality-2'
B='http://www.omg.org/spec/BPMN/20100524/MODEL'
Z='http://camunda.org/schema/zeebe/1.0'
D='http://www.omg.org/spec/BPMN/20100524/DI'
C='http://www.omg.org/spec/DD/20100524/DC'
I='http://www.omg.org/spec/DD/20100524/DI'
for prefix,uri in [('bpmn',B),('zeebe',Z),('bpmndi',D),('dc',C),('di',I),('modeler','http://camunda.org/schema/modeler/1.0')]: E.register_namespace(prefix,uri)
def tag(n): return '{'+B+'}'+n
def add(parent,n,attrs={},text=None,ns=B):
    e=E.SubElement(parent,'{'+ns+'}'+n,attrs)
    e.text=text
    return e
def ext(e):
    x=e.find(tag('extensionElements'))
    if x is None:
        x=E.Element(tag('extensionElements'));e.insert(0,x)
    return x
def job(e,kind): add(ext(e),'taskDefinition',{'type':'f2-'+kind,'retries':'3'},ns=Z)
def write(tree,path):
    tree.getroot()[:]=sorted(tree.getroot(),key=lambda e:1 if e.tag.startswith('{'+D+'}') else 0)
    for scope in tree.getroot().iter():
        if scope.tag not in (tag('process'),tag('subProcess')):continue
        children={e.get('id'):e for e in scope if e.get('id')}
        for e in children.values():
            for ref in list(e):
                if ref.tag in (tag('incoming'),tag('outgoing')):e.remove(ref)
        for flow in list(scope):
            if flow.tag!=tag('sequenceFlow'):continue
            add(children[flow.get('sourceRef')],'outgoing',{},flow.get('id'))
            add(children[flow.get('targetRef')],'incoming',{},flow.get('id'))
    order={'documentation':0,'extensionElements':1,'incoming':2,'outgoing':3,'property':4,'ioSpecification':5,'dataInputAssociation':6,'dataOutputAssociation':7,'resourceRole':8,'multiInstanceLoopCharacteristics':9}
    for e in tree.getroot().iter():
        if any(c.tag in (tag('incoming'),tag('outgoing')) for c in e):
            e[:]=sorted(e,key=lambda c:order.get(c.tag.split('}')[-1],100))
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);E.indent(tree);tree.write(p,encoding='utf-8',xml_declaration=True)

tree=E.parse(SOURCE/'inventory-seasonal-availability.bpmn');root=tree.getroot();p=root.find(tag('process'))
p.set('isExecutable','true');p.set('name','F2 Inventory and Seasonal Availability')
nodes={e.get('id'):e for e in root.iter() if e.get('id')}
messages=[('Event_0yt42mz','f2-stock-update',None),('Event_0k7qpmm','f2-order-paid',None),('Event_0pab392','f2-stock-corrected','=updateId')]
for event,name,key in messages:
    mid='Message_'+event;add(root,'message',{'id':mid,'name':name});definition=nodes[event].find(tag('messageEventDefinition'));definition.set('messageRef',mid)
    if key:
        msg=root.find("bpmn:message[@id='%s']"%mid,{'bpmn':B});add(add(msg,'extensionElements'),'subscription',{'correlationKey':key},ns=Z)

conditions={
'Gateway_0jq1bif':('=updateValid','Flow_09arnco','Flow_0j8m4o5'),
'Gateway_0kucjyc':('=quantity > 0','Flow_0ishmbg','Flow_091vx6a'),
'Gateway_03r47f5':('=quantity = 0','Flow_09mj54y','Flow_07v7514'),
'Gateway_0lj5e6t':('=withinSeason','Flow_1fbf6pb','Flow_0wm8e9i'),
'Gateway_0k5t49x':('=quantity > 0 and quantity < lowStockThreshold','Flow_0fqqhb3','Flow_1muqdt7'),
'Gateway_0vqwqyu':('=quantity = 0','Flow_0oah0ri','Flow_1jxnw5h'),
'Gateway_1xw5u8e':('=withinSeason','Flow_030uhay','Flow_0wuzbao'),
'Gateway_19snyo8':('=quantity > 0 and quantity < lowStockThreshold','Flow_0eiv7vx','Flow_1uk5uq0'),
'Gateway_1a2lsu5':('=allowAnotherCorrection','Flow_15js0qm','Flow_0z9119x'),
'Gateway_00mph7y':('=correctionAttempts >= 3','Flow_1ybwghf','Flow_1gkpf8k')}
for gid,(expr,yes,no) in conditions.items():
    nodes[gid].set('default',no);add(nodes[yes],'conditionExpression',{'{http://www.w3.org/2001/XMLSchema-instance}type':'bpmn:tFormalExpression'},expr)

kinds={
'Activity_0hss1ef':'validate-quantity','Activity_0hj1gqm':'validate-season',
'Activity_0t8snic':'save-update','Activity_0wf1ny8':'reduce-stock',
'Activity_1aqxzi0':'available','Activity_048h4bm':'unavailable','Activity_1xtvtom':'unavailable',
'Activity_121359a':'unavailable','Activity_02oic3k':'available','Activity_0jcnufj':'unavailable',
'Activity_0qv6sqp':'unavailable','Activity_1ktonrk':'available','Activity_1kkhp7r':'unavailable',
'Activity_0a0msio':'notify-low','Activity_16idmkx':'notify-low',
'Activity_1knv4gv':'notify-zero','Activity_00kvide':'notify-zero',
'Activity_07ct9ds':'request-correction','Activity_0kb95hx':'save-final'}
for nid,kind in kinds.items():
    e=nodes[nid]
    if e.tag==tag('task'):e.tag=tag('serviceTask')
    job(e,kind)
review=nodes['Activity_07qa1zf'];add(ext(review),'formDefinition',{'formId':'f2-inventory-review','bindingType':'latest'},ns=Z)
add(nodes['TimerEventDefinition_01m6b8r'],'timeDuration',{},'PT48H')
called=nodes['Activity_052zj9p'].find('.//{'+Z+'}calledElement');called.set('processId','check_product_stock_status');called.set('propagateAllChildVariables','true')

# Timer starts cannot use a product variable: no product instance exists yet.
# Each timer scans the catalogue, then runs Zain's original route once per due product.
plane=root.find('.//{'+D+'}BPMNPlane')
for label,start,first,end,ids,flowids,y in [
('start','Event_0ii4tpz','Activity_052zj9p','Event_0eb6t8d',
 ['Activity_052zj9p','Gateway_0kucjyc','Activity_1aqxzi0','Activity_048h4bm','Gateway_18mlopo','Event_0eb6t8d'],
 ['Flow_0ccb63r','Flow_0qn1zef','Flow_0ishmbg','Flow_091vx6a','Flow_19nxo7i','Flow_11uqjse','Flow_1vhcup5'],820),
('end','Event_0g3ep4s','Activity_1xtvtom','Event_0s09mrn',
 ['Activity_1xtvtom','Event_0s09mrn'],['Flow_1klohxp','Flow_1drh37y'],1070)]:
    add(nodes[start].find(tag('timerEventDefinition')),'timeCycle',{},'R/PT1M')
    scanid='F2_Scan_'+label;subid='F2_Each_'+label;sid='F2_Start_'+label;eid='F2_End_'+label
    scan=add(p,'serviceTask',{'id':scanid,'name':'Find products due for season '+label});job(scan,'scan-'+label)
    sub=add(p,'subProcess',{'id':subid,'name':'Apply season '+label+' to each due product'})
    loop=add(sub,'multiInstanceLoopCharacteristics',{'isSequential':'true'})
    add(add(loop,'extensionElements'),'loopCharacteristics',{'inputCollection':'=dueProducts','inputElement':'seasonProduct'},ns=Z)
    s=add(sub,'startEvent',{'id':sid,'name':'Product season '+label+' check'});add(s,'outgoing',{},flowids[0])
    for nid in ids+flowids:
        e=nodes[nid];p.remove(e);sub.append(e)
    nodes[flowids[0]].set('sourceRef',sid)
    nodes[start].find(tag('outgoing')).text='F2_ToScan_'+label
    add(p,'sequenceFlow',{'id':'F2_ToScan_'+label,'sourceRef':start,'targetRef':scanid})
    add(p,'sequenceFlow',{'id':'F2_ToEach_'+label,'sourceRef':scanid,'targetRef':subid})
    add(p,'sequenceFlow',{'id':'F2_Done_'+label,'sourceRef':subid,'targetRef':eid})
    add(p,'endEvent',{'id':eid,'name':'Season '+label+' catalogue check complete'})
    # Retain original route drawing and surround it with the added batch scope.
    for drawing in list(plane):
        if drawing.get('bpmnElement') in ids+flowids:
            for point in drawing.iter():
                if point.get('x') is not None:point.set('x',str(float(point.get('x'))+450))
    shape=add(plane,'BPMNShape',{'id':subid+'_di','bpmnElement':subid,'isExpanded':'true'},ns=D)
    add(shape,'Bounds',{'x':'680','y':str(y-25),'width':'750','height':'210'},ns=C)
    for nid,x,yy,w,h in [(sid,710,y+22,36,36),(scanid,440,y,100,80),(eid,1500,y+22,36,36)]:
        shape=add(plane,'BPMNShape',{'id':nid+'_di','bpmnElement':nid},ns=D);add(shape,'Bounds',{'x':str(x),'y':str(yy),'width':str(w),'height':str(h)},ns=C)
    # Lane membership only lists nodes directly owned by the process.
    lane=p.find('.//'+tag('lane'))
    for ref in list(lane):
        if ref.tag==tag('flowNodeRef') and ref.text in ids:lane.remove(ref)
    for nid in [scanid,subid,eid]:add(lane,'flowNodeRef',{},nid)
    for fid,points in [('F2_ToScan_'+label,[(278,y+40),(440,y+40)]),('F2_ToEach_'+label,[(540,y+40),(680,y+40)]),('F2_Done_'+label,[(1430,y+40),(1500,y+40)])]:
        edge=add(plane,'BPMNEdge',{'id':fid+'_di','bpmnElement':fid},ns=D)
        for x,yy in points:add(edge,'waypoint',{'x':str(x),'y':str(yy)},ns=I)
for shape in plane:
    if shape.get('bpmnElement')=='DataStoreReference_0as5i3t':
        bounds=shape.find('{'+C+'}Bounds');bounds.set('x','1700');bounds.set('y','1000')
write(tree,'camunda/f2/processes/inventory-seasonal-availability.bpmn')

t=E.parse(SOURCE/'check-product-stock-status.bpmn');job(t.getroot().find('.//'+tag('serviceTask')),'retrieve-stock');write(t,'camunda/f2/processes/check-product-stock-status.bpmn')

def form(fid,title,fields):
    components=[{'type':'text','text':'# '+title,'id':'heading'}]+fields
    obj={'schemaVersion':16,'id':fid,'type':'default','components':components,'executionPlatform':'Camunda Cloud','executionPlatformVersion':'8.9.0','exporter':{'name':'DaESD F2','version':'1.0'}}
    f=ROOT/'camunda/f2/forms'/f'{fid}.form';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(obj,indent=2))
form('f2-inventory-review','Review invalid stock update',[
 {'type':'text','text':'Validation errors: {{validationErrors}}','id':'errors'},
 {'type':'checkbox','key':'allowAnotherCorrection','label':'Allow another producer correction','id':'allow','defaultValue':False},
 {'type':'textarea','key':'reviewNotes','label':'Review notes','id':'notes','validate':{'required':True}}])
form('f2-stock-correction','Correct stock and season update',[
 {'type':'text','text':'Validation errors: {{validationErrors}}','id':'errors'},
 {'type':'number','key':'quantity','label':'Stock quantity','id':'quantity','validate':{'required':True,'min':0}},
 {'type':'textfield','key':'availableFrom','label':'Season start (YYYY-MM-DD)','id':'from','validate':{'required':True}},
 {'type':'textfield','key':'availableUntil','label':'Season end (YYYY-MM-DD, inclusive)','id':'until','validate':{'required':True}}])

# Small producer-side adapter supplies a Tasklist form without replacing the
# message catch in the original marketplace operational model.
r=E.Element(tag('definitions'),{'id':'F2_Correction_Definitions','targetNamespace':'https://uwe.ac.uk/daesd/f2','{http://camunda.org/schema/modeler/1.0}executionPlatform':'Camunda Cloud','{http://camunda.org/schema/modeler/1.0}executionPlatformVersion':'8.9.0'})
pr=add(r,'process',{'id':'f2-producer-correction','name':'F2 Producer correction form','isExecutable':'true'})
add(r,'message',{'id':'CorrectionRequested','name':'f2-correction-requested'})
s=add(pr,'startEvent',{'id':'CorrectionStart','name':'Correction requested'});add(s,'messageEventDefinition',{'messageRef':'CorrectionRequested'})
u=add(pr,'userTask',{'id':'F2_CorrectStock','name':'Submit corrected stock and season update'});add(ext(u),'userTask',ns=Z);add(ext(u),'formDefinition',{'formId':'f2-stock-correction','bindingType':'latest'},ns=Z)
send=add(pr,'sendTask',{'id':'F2_SendCorrection','name':'Return corrected stock update'});job(send,'send-correction')
add(pr,'endEvent',{'id':'CorrectionEnd','name':'Correction returned'})
for i,(a,b) in enumerate([('CorrectionStart','F2_CorrectStock'),('F2_CorrectStock','F2_SendCorrection'),('F2_SendCorrection','CorrectionEnd')]):add(pr,'sequenceFlow',{'id':f'CorrectionFlow{i}','sourceRef':a,'targetRef':b})
diag=add(r,'BPMNDiagram',{'id':'CorrectionDiagram'},ns=D);pl=add(diag,'BPMNPlane',{'id':'CorrectionPlane','bpmnElement':'f2-producer-correction'},ns=D)
for nid,x,w,h in [('CorrectionStart',100,36,36),('F2_CorrectStock',200,100,80),('F2_SendCorrection',360,100,80),('CorrectionEnd',520,36,36)]:
    sh=add(pl,'BPMNShape',{'id':nid+'_di','bpmnElement':nid},ns=D);add(sh,'Bounds',{'x':str(x),'y':str(100 if h==80 else 122),'width':str(w),'height':str(h)},ns=C)
for i,(x1,x2) in enumerate([(136,200),(300,360),(460,520)]):
    edge=add(pl,'BPMNEdge',{'id':f'CorrectionFlow{i}_di','bpmnElement':f'CorrectionFlow{i}'},ns=D)
    for x in [x1,x2]:add(edge,'waypoint',{'x':str(x),'y':'140'},ns=I)
write(E.ElementTree(r),'camunda/f2/processes/producer-stock-correction.bpmn')
print('Built three BPMN files and two forms from original F2 sources.')
