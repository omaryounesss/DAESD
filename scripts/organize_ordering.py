"""Organize DI only: preserve the full ordering BPMN semantics."""
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];B='http://www.omg.org/spec/BPMN/20100524/MODEL';D='http://www.omg.org/spec/BPMN/20100524/DI';C='http://www.omg.org/spec/DD/20100524/DC';I='http://www.omg.org/spec/DD/20100524/DI'
for k,v in [('bpmn',B),('zeebe','http://camunda.org/schema/zeebe/1.0'),('bpmndi',D),('dc',C),('di',I),('modeler','http://camunda.org/schema/modeler/1.0')]:E.register_namespace(k,v)
def t(n):return '{'+B+'}'+n
def add(p,n,a,ns):return E.SubElement(p,'{'+ns+'}'+n,a)
path=ROOT/'camunda/f2/processes/place-order-horizontal.bpmn';root=E.parse(path).getroot();original=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn').getroot();plane=root.find('.//{'+D+'}BPMNPlane');p=root.find(t('process'))
semantic_before=E.tostring(p)
oldshapes={s.get('bpmnElement'):s for s in original.findall('.//{'+D+'}BPMNShape')};shapes={s.get('bpmnElement'):s for s in plane.findall('{'+D+'}BPMNShape')}
purchase={'Activity_0kb95hx','Activity_0wf1ny8','Gateway_03r47f5','Gateway_0lj5e6t','Activity_121359a','Activity_02oic3k','Gateway_1j4xncw','Gateway_0k5t49x','Activity_0a0msio','Gateway_1tlh55r','Activity_0jcnufj','Activity_1knv4gv'}
# Put all unaffected operational rows back at their familiar original positions.
for ident,s in shapes.items():
 if ident not in oldshapes:continue
 b=s.find('{'+C+'}Bounds');ob=oldshapes[ident].find('{'+C+'}Bounds');b.attrib.update(ob.attrib)
 if ident in purchase and ident!='Activity_0wf1ny8':b.set('x',str(float(b.get('x'))+1750))
 for label in list(s.findall('{'+D+'}BPMNLabel')):s.remove(label)
 oldlabel=oldshapes[ident].find('{'+D+'}BPMNLabel')
 if oldlabel is not None:
  import copy
  label=copy.deepcopy(oldlabel);s.append(label)
  if ident in purchase:
   lb=label.find('{'+C+'}Bounds');lb.set('x',str(float(lb.get('x'))+1750))
# Same-size ordering tasks on a straight, evenly spaced row.
placements={'Event_0k7qpmm':(242,1532,36,36),'Load':(330,1510,140,80),'Order':(520,1510,140,80),'Validate':(710,1510,140,80),'Valid':(900,1525,50,50),'PayChoice':(1040,1510,140,80),'Authorize':(1230,1510,140,80),'Paid':(1420,1525,50,50),'Activity_0wf1ny8':(1600,1510,140,80),'Committed':(1790,1525,50,50),'Capture':(1940,1510,140,80),'Void':(1745,1870,140,80),'Reject':(1360,1870,140,80),'Declined':(1550,1892,36,36),'Result':(3540,1610,140,80),'Event_03jyftw':(3740,1632,36,36)}
for ident,(x,y,w,h) in placements.items():shapes[ident].find('{'+C+'}Bounds').attrib.update(x=str(x),y=str(y),width=str(w),height=str(h))
for ident,x,y,w,h in [('Participant_09s0n6r',160,92,3740,60),('Participant_041bi7k',160,200,3740,1830),('Lane_12fsm5f',190,200,3710,230),('Lane_1w7vtzs',190,430,3710,1600),('Participant_1dxapzq',160,2080,3740,60),('Participant_1607470',160,2200,3740,60)]:shapes[ident].find('{'+C+'}Bounds').attrib.update(x=str(x),y=str(y),width=str(w),height=str(h))
positions={i:tuple(float(s.find('{'+C+'}Bounds').get(k)) for k in ('x','y','width','height')) for i,s in shapes.items()}
# Restore routed edges of unaffected operational paths exactly, rather than
# retaining the oversized translation from the previous layout.
oldedges={e.get('bpmnElement'):e for e in original.findall('.//{'+D+'}BPMNEdge')};flows={e.get('id'):e for e in root.iter() if e.tag in (t('sequenceFlow'),t('messageFlow'))}
for edge in plane.findall('{'+D+'}BPMNEdge'):
 ident=edge.get('bpmnElement');flow=flows.get(ident)
 if flow is None:continue
 src,dst=flow.get('sourceRef'),flow.get('targetRef')
 ispurchase=src in purchase or dst in purchase or src in placements or dst in placements
 if not ispurchase and ident in oldedges:
  edge[:]=[E.fromstring(E.tostring(c)) for c in oldedges[ident]]
  # Connect notification messages to their newly aligned service pool.
  if flow.tag==t('messageFlow') and dst=='Participant_1dxapzq':
   points=edge.findall('{'+I+'}waypoint');points[-1].set('y','2080')
  continue
 if src not in positions or dst not in positions:continue
 sx,sy,sw,sh=positions[src];dx,dy,dw,dh=positions[dst]
 if flow.tag==t('messageFlow'):
  points=[(sx+sw/2,sy+sh),(sx+sw/2,dy)]
 elif src=='Committed' and dst=='Void':points=[(sx+sw/2,sy+sh),(sx+sw/2,dy)]
 elif dst=='Reject' and src in ('Valid','Paid'):
  channel=1815 if src=='Valid' else 1840
  points=[(sx+sw/2,sy+sh),(sx+sw/2,channel),(dx+30,channel),(dx+30,dy)]
 elif src=='Void' and dst=='Reject':points=[(sx,sy+sh/2),(dx+dw,dy+dh/2)]
 elif src=='Capture' and dst=='Gateway_03r47f5':points=[(sx+sw,sy+sh/2),(dx,dy+dh/2)]
 elif src in purchase and dst in purchase and ident in oldedges and src!='Activity_0wf1ny8':
  points=[(float(q.get('x'))+1750,float(q.get('y'))) for q in oldedges[ident].findall('{'+I+'}waypoint')]
 elif abs(sy+sh/2-dy-dh/2)<1:points=[(sx+sw,sy+sh/2),(dx,dy+dh/2)]
 else:
  mid=(sx+sw+dx)/2
  points=[(sx+sw,sy+sh/2),(mid,sy+sh/2),(mid,dy+dh/2),(dx,dy+dh/2)]
 for c in list(edge):edge.remove(c)
 for x,y in points:add(edge,'waypoint',dict(x=str(x),y=str(y)),I)
 if flow.get('name'):
  # Labels sit beside their outgoing segment, never on a task.
  label=add(edge,'BPMNLabel',{},D);x,y=points[0];add(label,'Bounds',dict(x=str(x+8),y=str(y-22),width='40',height='18'),C)
# Remove orphaned association artwork left by the earlier translation.
# Original upper-section data associations keep their original geometry;
# long purchase-to-catalogue associations stay semantic, without crossing
# the whole collaboration as detached artwork.
for edge in list(plane.findall('{'+D+'}BPMNEdge')):
 ident=edge.get('bpmnElement')
 if ident in flows:continue
 if ident in oldedges:
  association=next((e for e in root.iter() if e.get('id')==ident),None)
  owner=next((e for e in root.iter() if association is not None and association in list(e)),None)
  if owner is not None and owner.get('id') in purchase:plane.remove(edge)
  else:edge[:]=[E.fromstring(E.tostring(c)) for c in oldedges[ident]]
# Event/gateway labels follow their nodes; task labels remain inside the box.
nodeindex={e.get('id'):e for e in p.iter() if e.get('id')}
for ident in placements:
 s=shapes[ident];node=nodeindex[ident]
 for label in list(s.findall('{'+D+'}BPMNLabel')):s.remove(label)
 if node.tag in (t('startEvent'),t('endEvent'),t('exclusiveGateway')) and node.get('name'):
  x,y,w,h=positions[ident];label=add(s,'BPMNLabel',{},D);add(label,'Bounds',dict(x=str(x+w/2-50),y=str(y+h+5),width='100',height='36'),C)
assert E.tostring(p)==semantic_before,'Layout must not alter execution semantics'
E.indent(root)
for name in ('place-order-horizontal.bpmn','place-order.bpmn'):E.ElementTree(root).write(ROOT/'camunda/f2/processes'/name,encoding='utf-8',xml_declaration=True)
print('Organized full horizontal diagram; process semantics unchanged.')
