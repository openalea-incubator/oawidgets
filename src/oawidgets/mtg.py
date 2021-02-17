from __future__ import absolute_import

from openalea.mtg import traversal
from pyvis.network import Network
try:
    import colorcet as cc
except ImportError:
    cc = None

def dict2html(args, properties=None):
    """Return a HTML element from a dictionary"""
    if properties is None:
        selection = ['index', 'parent', 'complex', 'label', 'edge_type', 'scale']
        properties =  []
        for k in args:
            if k not in selection:
                properties.append(k)
    elif isinstance(properties, str):
        properties = [properties]
    properties.sort()
    return '<br>'.join(['%s %s'%(k, args[k]) for k in properties])


def plot(g, properties=None, selection=None, hlayout=True, scale=None, labels=None, **kwds):
    """Plot a MTG in the Jupyter Notebook"""
    G = Network(notebook=True, directed=True,
                layout=hlayout,
                height='800px', width='900px')

    if hlayout:
        G.hrepulsion()
        G.options.layout.hierarchical.direction='DU'
        G.options.layout.hierarchical.parentCentralization=True
        G.options.layout.hierarchical.levelSeparation=150
    else:
    	G.repulsion()

    if scale is None:
        scale = g.max_scale()

    #Colors
    if cc is not None:
        colors = cc.glasbey_light
    else:
        colors = ['#6e6efd', '#fb7e81', '#ad85e4', '#7be141', '#ffff00', '#ffa807', '#eb7df4', '#e6ffe3', '#d2e5ff', '#ffd1d9']

    #Data
    vids = g.vertices(scale=scale)
    edges = [(g.parent(vid), vid, 6 if g.edge_type(vid) == '<' else 1)
             for vid in vids if g.parent(vid) is not None]#, 'black' if g.edge_type(vid) == '<' else None
    pos = g.property('position')

    #Level determination
    levels = {}
    root = next(g.component_roots_at_scale_iter(g.root, scale=scale))
    for vid in traversal.pre_order(g, root):
        levels[vid] = 0 if g.parent(vid) is None else levels[g.parent(vid)]+1

    #Component roots
    component_roots = {}
    component_roots[root] = True
    for vid in traversal.pre_order(g, root):
        pid = g.parent(vid)
        if pid is None:
            component_roots[vid] = True
        elif g.complex(pid) != g.complex(vid):
            component_roots[vid] = True

    #Groups
    groups = {}
    for count, vid in enumerate(traversal.pre_order(g, g.complex(root))):
        nc = len(colors)
        groups[vid] = colors[count%nc]
        pid = g.parent(vid)
        if pid:
            if groups[vid] == groups[pid]:
                groups[vid] = colors[(1789*count+17)%nc]

    #Nodes adding
    for vid in vids:
        shape = 'box' if vid in component_roots else 'circle'
    if labels is None:
            label_node = g.label(vid)
    else:
        label_node = labels[vid]
        level = levels[vid]
    if selection is None:
            color = groups[g.complex(vid)]
    else:
        color = '#fb7e81' if vid in selection else '#97c2fc'
        title = dict2html(g[vid], properties=properties)
        #gap, mult = max(pos[1])-min(pos[1]), 20
        #x = mult*pos[g.parent(vid)][0] if g.parent(vid) else pos[vid][0]
        # #y = mult*(gap - pos[vid][1]) #if g.parent(vid) else None
        #physics = False if ('edge_type' not in g[vid] or g[vid]['edge_type']=='<' or g.nb_children(vid)>0) else True
        G.add_node(vid, shape=shape,
                   label=label_node,
                   level=level,
                   color=color,
		   title=title,
                   borderWidth=3,
		   #x=x,
                   #y=y,
                   #physics=physics,
                   )

    #Cluster
    if False:
        for vid in traversal.pre_order(g, g.complex(root)):
            G.add_node(vid, hidden=True)
            if g.parent(vid):
                G.add_edge(g.parent(vid), vid, hidden=True)
            for cid in g.components(vid):
                G.add_edge(vid, cid, hidden=True)

    #Edges adding
    for edge in edges:
        label_edge = g.edge_type(edge[1])
        G.add_edge(edge[0], edge[1], label=label_edge, width=edge[2])

    return G.show('mtg.html')
