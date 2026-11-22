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

# Keep Zain's exact timer starts and routes. A timer start has no product
# variables: this demonstration binds the two starts to one configured product.
# No scanner, wrapper subprocess, helper process or diagram movement is added.
demo=json.loads((ROOT/'services/inventory-service/demo-product.json').read_text())
from datetime import date, timedelta
add(nodes['TimerEventDefinition_0k570q7'],'timeDate',{},demo['availableFrom']+'T00:00:00Z')
add(nodes['TimerEventDefinition_0m3fr1e'],'timeDate',{},str(date.fromisoformat(demo['availableUntil'])+timedelta(days=1))+'T00:00:00Z')
root.set('{http://camunda.org/schema/modeler/1.0}executionPlatformVersion','8.9.0')
write(tree,'camunda/f2/processes/inventory-seasonal-availability.bpmn')
t=E.parse(SOURCE/'check-product-stock-status.bpmn')
t.getroot().set('{http://camunda.org/schema/modeler/1.0}executionPlatformVersion','8.9.0')
job(t.getroot().find('.//'+tag('serviceTask')),'retrieve-stock')
write(t,'camunda/f2/processes/check-product-stock-status.bpmn')

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

print('Built two BPMN files and two forms; original graph and diagram retained.')
