"""Editable draw.io mxCells and vector exports from the exact same geometry.

This is a transparent local XML exporter, not a claim that a missing draw.io
desktop binary was launched. Nodes, connector routes and labels remain editable.
"""
from pathlib import Path
import json
import hashlib
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from task2.scripts.build_figures import P

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'task2/diagrams'


def export(name,title,nodes,edges,footer):
    OUT.mkdir(parents=True,exist_ok=True);W,H=1120,800
    graph=ET.Element('mxfile',host='app.diagrams.net');diagram=ET.SubElement(graph,'diagram',name=title)
    model=ET.SubElement(diagram,'mxGraphModel',dx=str(W),dy=str(H),page='1',pageWidth=str(W),pageHeight=str(H))
    root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
    nodes=[('title',title,35,15,1050,55,'none',25),*nodes,('footer',footer,35,720,1050,60,'none',17)]
    for ident,label,x,y,w,h,fill,fontsize in nodes:
        c=ET.SubElement(root,'mxCell',id=ident,value=label,vertex='1',parent='1',
             style=f'rounded=1;whiteSpace=wrap;html=0;fillColor={P.get(fill,fill)};strokeColor={P["Rule"]};fontColor={P["Ink"]};fontSize={fontsize};align=left;spacingLeft=14;')
        ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
    for k,(source,target,points,label,tx,ty,dashed) in enumerate(edges):
        c=ET.SubElement(root,'mxCell',id=f'e{k}',edge='1',parent='1',source=source,target=target,value=label,
             style=f'endArrow=block;html=0;strokeColor={P["C1"]};dashed={int(dashed)};fontSize=16;')
        g=ET.SubElement(c,'mxGeometry',relative='1',labelX=str(tx),labelY=str(ty),**{'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(points[0][0]),y=str(points[0][1]),**{'as':'sourcePoint'})
        a=ET.SubElement(g,'Array',**{'as':'points'})
        for x,y in points[1:-1]:ET.SubElement(a,'mxPoint',x=str(x),y=str(y))
        ET.SubElement(g,'mxPoint',x=str(points[-1][0]),y=str(points[-1][1]),**{'as':'targetPoint'})
    ET.indent(graph);path=OUT/(name+'.drawio');ET.ElementTree(graph).write(path,encoding='utf-8',xml_declaration=True)
    svg=ET.Element('svg',xmlns='http://www.w3.org/2000/svg',width=str(W),height=str(H),viewBox=f'0 0 {W} {H}')
    defs=ET.SubElement(svg,'defs');marker=ET.SubElement(defs,'marker',id='arrow',markerWidth='10',markerHeight='8',refX='9',refY='4',orient='auto')
    ET.SubElement(marker,'path',d='M0,0 L0,8 L9,4 z',fill=P['C1'])
    ET.SubElement(svg,'rect',width=str(W),height=str(H),fill=P['Paper'])
    fig,ax=plt.subplots(figsize=(11.2,8));fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
    ax.set(xlim=(0,W),ylim=(H,0),aspect='equal');ax.axis('off')
    for ident,label,x,y,w,h,fill,fontsize in nodes:
        if fill!='none':
            ET.SubElement(svg,'rect',x=str(x),y=str(y),width=str(w),height=str(h),rx='6',fill=P[fill],stroke=P['Rule'])
            ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=6',facecolor=P[fill],edgecolor=P['Rule'],lw=1))
        for k,line in enumerate(label.split('\n')):
            yy=y+28+k*(fontsize+7)
            t=ET.SubElement(svg,'text',x=str(x+14),y=str(yy),fill=P['Ink'],**{'font-family':'DejaVu Sans,sans-serif','font-size':str(fontsize)});t.text=line
            ax.text(x+14,yy,line,va='baseline',fontsize=fontsize*.72,color=P['Ink'])
    for source,target,points,label,tx,ty,dashed in edges:
        attrs={'points':' '.join(f'{x},{y}' for x,y in points),'fill':'none','stroke':P['C1'],'stroke-width':'2','marker-end':'url(#arrow)'}
        if dashed:attrs['stroke-dasharray']='7 5'
        ET.SubElement(svg,'polyline',attrs)
        ax.plot(*zip(*points),color=P['C1'],lw=1.3,ls='--' if dashed else '-')
        ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',color=P['C1'],mutation_scale=12,lw=0))
        t=ET.SubElement(svg,'text',x=str(tx),y=str(ty),fill=P['Muted'],**{'font-size':'16','font-family':'DejaVu Sans,sans-serif'});t.text=label
        ax.text(tx,ty,label,fontsize=11.52,color=P['Muted'],va='baseline',bbox={'facecolor':P['Paper'],'edgecolor':'none','pad':1})
    ET.indent(svg);ET.ElementTree(svg).write(path.with_suffix('.svg'),encoding='utf-8',xml_declaration=True)
    fig.savefig(path.with_suffix('.pdf'));fig.savefig(path.with_suffix('.png'),dpi=200);plt.close(fig)
    path.with_suffix('.json').write_text(json.dumps({'drawio_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'nodes':len(nodes),'edges':len(edges),'raster_embedded_in_drawio':False,
         'export':'local exporter from same mxGeometry; actual .drawio desktop unavailable',
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))


def main():
    nodes=[('scope','Approved task scope\nMain-thread coordination\nOne continuous Goal',410,90,300,115,'P1',20),
      ('R','research_data context\nTeacher/source/data audit\nV/O on evolution',40,285,300,110,'Panel',20),
      ('EA','evolution context\nNSGA / KM execution\nIndependent V on RL',410,285,300,110,'Panel',20),
      ('EB','reinforcement context\nQ-KM / extensions\nIndependent V on online',780,285,300,110,'Panel',20),
      ('ROOT','Main thread execution\nTBG / BB / exact checks\nIntegration and reports',40,520,300,115,'Panel',20),
      ('QA','Independent references\nRaw input + target hashes\nIssues -> fix -> rerun',410,520,300,115,'P4',20),
      ('PKG','Reviewable deliverables\nFigures / notebooks / PDF\nGit commit / review ZIP',780,520,300,115,'Panel',20)]
    edges=[('scope','R',[(410,147),(190,147),(190,285)],'source contract',205,225,False),
      ('scope','EA',[(560,205),(560,285)],'method contract',575,245,False),
      ('scope','EB',[(710,147),(930,147),(930,285)],'method contract',790,225,False),
      ('R','QA',[(190,395),(190,450),(460,450),(460,520)],'cross-context checks',225,440,False),
      ('EA','QA',[(560,395),(560,520)],'raw runs',575,485,False),
      ('EB','QA',[(930,395),(930,450),(660,450),(660,520)],'cross-context checks',735,440,False),
      ('ROOT','QA',[(340,575),(410,575)],'',0,0,False),
      ('QA','scope',[(710,570),(744,570),(744,240),(680,240),(680,205)],'issue / new hypothesis',755,495,True),
      ('QA','PKG',[(710,615),(780,615)],'',0,0,False)]
    export('research_verification_workflow','Research and verification: actual native contexts',nodes,edges,
      'Four real contexts cover six responsibilities; deterministic functions are numerical tools.\nExternal web-GPT review and human acceptance follow the internal workflow.')
    nodes=[('raw','Teacher / synthetic input\nImmutable sources',40,90,300,90,'Panel',20),
      ('split','Chronological contract\nInner / validate / test',410,90,300,90,'P1',20),
      ('instances','Common scoped instances\nArrivals / batch / day',780,90,300,90,'Panel',20),
      ('online','One-use online matching\nTBG / batch sum or max\nRecycle vs discard',40,300,300,115,'Panel',20),
      ('ea','Static optional matching\nNSGA-II/III / weighted KM\nCommon feasible edges',410,300,300,115,'Panel',20),
      ('rl','Reusable-driver dynamics\nQ / Double / KM / NSGA\nPhysical empty movement',780,300,300,115,'Panel',20),
      ('references','Exact independent checks\nEnumerate / LP / MILP\nHV union / manual TD',40,560,300,115,'P4',20),
      ('metrics','Separate quality measures\nCoverage / delay / income\nPickup / empty cost / HV',410,560,300,115,'Panel',20),
      ('artifacts','Valid runs -> figures\nReports / source / rerun\nNegative results retained',780,560,300,115,'Panel',20)]
    edges=[('raw','split',[(340,135),(410,135)],'',0,0,False),('split','instances',[(710,135),(780,135)],'',0,0,False),
      ('instances','online',[(930,180),(930,240),(190,240),(190,300)],'same scoped inputs',400,230,False),
      ('instances','ea',[(930,180),(930,240),(560,240),(560,300)],'',0,0,False),
      ('instances','rl',[(930,180),(930,300)],'',0,0,False),
      ('online','metrics',[(190,415),(190,490),(490,490),(490,560)],'matching logs',220,480,False),
      ('ea','metrics',[(560,415),(560,560)],'front + cost',575,500,False),
      ('rl','metrics',[(930,415),(930,490),(650,490),(650,560)],'day + movement logs',745,480,False),
      ('references','metrics',[(340,615),(410,615)],'',0,0,True),
      ('metrics','artifacts',[(710,615),(780,615)],'',0,0,False)]
    export('dispatch_runtime_and_evaluation','Dispatch models and independent evaluation',nodes,edges,
      'Static, single-use online and sequential fleet models keep separate definitions and units.\nArrows show data and control. Technical structure is separate from historical chat evidence.')
    print('Two editable draw.io diagrams and matching vector exports created.')


if __name__=='__main__':main()
