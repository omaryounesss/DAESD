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
messages=[('Event_0yt42mz','f2-stock-update',None),('Event_0k7qpmm','f2-order-paid',None),
          ('Event_0ii4tpz','f2-season-start',None),('Event_0g3ep4s','f2-season-end',None)]
for event,name,key in messages:
    mid='Message_'+event;add(root,'message',{'id':mid,'name':name})
    definition=nodes[event].find(tag('messageEventDefinition'))
    if definition is None:
        definition=nodes[event].find(tag('timerEventDefinition'))
        definition.tag=tag('messageEventDefinition')
        for child in list(definition):definition.remove(child)
    definition.set('messageRef',mid)
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
review=nodes['Activity_07qa1zf'];add(ext(review),'formDefinition',{'formId':'f2-inventory-review','bindingType':'deployment'},ns=Z)
add(nodes['TimerEventDefinition_01m6b8r'],'timeDuration',{},'PT48H')
called=nodes['Activity_052zj9p'].find('.//{'+Z+'}calledElement');called.set('processId','check_product_stock_status');called.set('propagateAllChildVariables','true')

# Keep the original seasonal business routes. The executable receives a
# per-product scheduler message instead of using deployment-level fixed dates.
# Season boundaries are published by the persistent scheduler, not fixed timers.
nodes['Event_0g3ep4s'].find(tag('documentation')).text=(
    'Triggered by the persistent scheduler at 00:00 UTC on the day after the '
    'product\'s inclusive seasonal end date. The product becomes unavailable '
    'regardless of its remaining stock quantity.')
root.set('{http://camunda.org/schema/modeler/1.0}executionPlatformVersion','8.9.0')

# Executable-only producer interaction, documented against the operational source.
# Message-based update/order starts remain; corrections now use native Tasklist.
start=add(p,'startEvent',{'id':'Start_ProducerUpdate','name':'Producer starts inventory update'})
prepare=add(p,'serviceTask',{'id':'Task_PrepareProducerUpdate','name':'Load catalogue products'})
job(prepare,'prepare-update')
submit=add(p,'userTask',{'id':'Task_SubmitStockUpdate','name':'Update stock and seasonal availability'})
correction=nodes['Event_0pab392']
correction.tag=tag('userTask');correction.set('name','Correct stock and seasonal availability')
for child in list(correction):
    if child.tag==tag('messageEventDefinition'):correction.remove(child)
# Corrections arrive through the native form, not an incoming producer message.
# Remove both the old semantic message flow and its diagram connector.
for parent in root.iter():
    for child in list(parent):
        if child.get('id')=='Flow_0pg15sp' or child.get('bpmnElement')=='Flow_0pg15sp':
            parent.remove(child)
for task,fid,fields in [(submit,'f2-stock-update',('productId','quantity','availableFrom','availableUntil')),
                        (correction,'f2-stock-correction',('quantity','availableFrom','availableUntil'))]:
    x=ext(task);add(x,'userTask',ns=Z)
    add(x,'formDefinition',{'formId':fid,'bindingType':'deployment'},ns=Z)
    mapping=add(x,'ioMapping',ns=Z)
    for field in fields:add(mapping,'output',{'source':'='+field,'target':field},ns=Z)
for ident,source,target in [('Flow_ProducerPrepare','Start_ProducerUpdate','Task_PrepareProducerUpdate'),
                            ('Flow_ProducerSubmit','Task_PrepareProducerUpdate','Task_SubmitStockUpdate'),
                            ('Flow_ProducerValidate','Task_SubmitStockUpdate','Gateway_158vgre')]:
    add(p,'sequenceFlow',{'id':ident,'sourceRef':source,'targetRef':target})
lanes=p.find(tag('laneSet'))
platform=nodes['Lane_1w7vtzs']
platform.set('name','Marketplace operations')
for ident in ('Start_ProducerUpdate','Task_SubmitStockUpdate','Event_0pab392'):
    if not any(ref.text==ident for ref in platform.findall(tag('flowNodeRef'))):
        add(platform,'flowNodeRef',text=ident)
# Expand executable layout with one producer-interaction row. Source is untouched.
plane=root.find('.//{'+D+'}BPMNPlane')
for shape in plane.findall('{'+D+'}BPMNShape'):
    bounds=shape.find('{'+C+'}Bounds');ident=shape.get('bpmnElement')
    if ident=='Participant_041bi7k':bounds.set('height',str(float(bounds.get('height'))+180))
    elif ident=='Lane_1w7vtzs':bounds.set('height',str(float(bounds.get('height'))+180))
    elif float(bounds.get('y'))>=430:bounds.set('y',str(float(bounds.get('y'))+180))
    if ident=='Event_0pab392':
        bounds.set('x','1000');bounds.set('y','470');bounds.set('width','130');bounds.set('height','80')
        # A task displays its name internally; the old event's external label
        # would otherwise remain detached from the resized correction task.
        label=shape.find('{'+D+'}BPMNLabel')
        if label is not None:shape.remove(label)
for edge in plane.findall('{'+D+'}BPMNEdge'):
    for waypoint in edge.findall('{'+I+'}waypoint'):
        if float(waypoint.get('y'))>=430:waypoint.set('y',str(float(waypoint.get('y'))+180))
# External gateway/event/sequence-flow labels have independent DI bounds.
# Translate them with the geometry, including Yes/No labels on routed edges.
for label in plane.findall('.//{'+D+'}BPMNLabel'):
    bounds=label.find('{'+C+'}Bounds')
    if bounds is not None and float(bounds.get('y'))>=430:
        bounds.set('y',str(float(bounds.get('y'))+180))
# Reattach incoming/outgoing edges to the resized correction user task.
for edge in plane.findall('{'+D+'}BPMNEdge'):
    routes={'Flow_1lwoh2m':[(966,880),(980,880),(980,510),(1000,510)],
            'Flow_12vo3s4':[(1065,550),(1065,590),(230,590),(230,740),(320,740),(320,755)]}
    if edge.get('bpmnElement') in routes:
        for point in list(edge.findall('{'+I+'}waypoint')):edge.remove(point)
        for x,y in routes[edge.get('bpmnElement')]:add(edge,'waypoint',{'x':str(x),'y':str(y)},ns=I)
def shape(ident,x,y,width,height):
    s=add(plane,'BPMNShape',{'id':ident+'_di','bpmnElement':ident},ns=D)
    add(s,'Bounds',dict(x=str(x),y=str(y),width=str(width),height=str(height)),ns=C)
shape('Start_ProducerUpdate',242,482,36,36)
shape('Task_PrepareProducerUpdate',340,470,100,80)
shape('Task_SubmitStockUpdate',480,470,100,80)
for ident,points in [('Flow_ProducerPrepare',[(278,500),(310,500),(310,510),(340,510)]),
                     ('Flow_ProducerSubmit',[(440,510),(480,510)]),
                     ('Flow_ProducerValidate',[(530,550),(530,710),(320,710),(320,755)])]:
    edge=add(plane,'BPMNEdge',{'id':ident+'_di','bpmnElement':ident},ns=D)
    for x,y in points:add(edge,'waypoint',{'x':str(x),'y':str(y)},ns=I)
# Preparation is automated in the platform lane.
add(platform,'flowNodeRef',text='Task_PrepareProducerUpdate')
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
# Preserve the producer's exported date controls, IDs and layout. These source
# forms are canonical; edit them when saving later Modeler form changes.
for fid in ('f2-stock-correction','f2-stock-update'):
    source=ROOT/'source/forms'/f'{fid}.form'
    obj=json.loads(source.read_text(encoding='utf-8'))
    expected={'quantity','availableFrom','availableUntil'}
    if fid=='f2-stock-update':expected.add('productId')
    keyed={c['key']:c for c in obj['components'] if 'key' in c}
    if obj['id']!=fid or set(keyed)!=expected:
        raise ValueError('Producer form has incompatible variable keys: '+fid)
    for key in ('availableFrom','availableUntil'):
        if (keyed[key].get('type'),keyed[key].get('subtype'))!=('datetime','date'):
            raise ValueError('Producer season controls must be date-only: '+fid)
    (ROOT/'camunda/f2/forms'/f'{fid}.form').write_bytes(source.read_bytes())
print('Built two BPMN files and three forms with documented Tasklist refinements; operational sources untouched.')

