#
# Copyright 2022 The Applied Research Laboratory for Intelligence and Security (ARLIS)
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import networkx as nx
import plotly.graph_objects as go

def createDiGraph(nodes, edges, *, drop_recursions: bool=False, node_labels=False):
    """
    Creates NetworkX Directed Graph Object (G) from defined node, edge list
    :param nodes: Series or List of Events, Elements
    :param edges: Series or List of Pairs
    :param drop_recursions: if True eliminates self:self pairs in edges
    :return: A NetworkX graph object
    """

    # Replace node names with the give node_labels if it is given as an argument
    if node_labels:
        nodes = [node if node not in node_labels else node_labels[node] for node in nodes]
        for i in range(len(edges)):
            edges[i] = tuple([node if node not in node_labels else node_labels[node] for node in edges[i]])

    # Remove self-to-self recursions
    if drop_recursions:
        edges = list(filter(lambda row: row[0] != row[1], edges))

    # Create a digraph with capacity attributes that represent the number of edges between nodes
    graph = nx.DiGraph((x, y, {'capacity': v}) for (x, y), v in collections.Counter(edges).items())
    graph.add_nodes_from(nodes)
    return graph

def sankey(edges, node_labels=False):
    """
    Creates Sankey Graph from defined edge list and optional user-provided labels
    :param edges_segmentN: List of Tuples
    :param node_labels: Optional Dictionary of Values; keys are originals, values are replacements
    :return: A Sankey graph
    """

    # Convert raw edges to a weighted digraph
    graph = createDiGraph(list(), edges, node_labels=node_labels)
    nodes = list(graph.nodes())
    edges = graph.edges(data=True)
    
    # Format weighted edge data for plotly Sankey function
    sources = [nodes.index(edge[0]) for edge in edges]
    targets = [nodes.index(edge[1]) for edge in edges]
    values = [edge[2]['capacity'] for edge in edges]
                                      
    return go.Figure(data=[go.Sankey(
        node=dict(label=nodes),
        link=dict(source=sources, target=targets, value=values))])

def funnel(edges, targets, node_labels=False, infer=True):
    """
    Creates Funnel Graph from defined edge list and optional user-provided labels
    :param edges: List of Tuples
    :param targets: String or list of strings representing elements of interest
    :param node_labels: Optional Dictionary of key default values, value replacements
    :param infer: Optional boolean, true = consider nondirect paths between targets and elements after the last target, false = only consider the provided elements    
    :return: A Funnel graph
    """
    
    # Convert raw edges to a weighted digraph
    graph = createDiGraph(list(), edges, drop_recursions=True, node_labels=node_labels)
    
    # Put raw strings into a list of one 
    if isinstance(targets, str):
        targets = [targets]
        
    target_edges = list()
    if infer:
        # Find a path through each provided target that maximizes flow
        for i in range(len(targets) - 1):
            path = max([path for path in nx.all_simple_paths(graph, targets[i], targets[i+1])],
                    key=lambda path: nx.path_weight(graph, path, "capacity"))
            target_edges.extend(nx.utils.pairwise(path))
        
        # Extend the path constructed above as much as possible without creating cycles
        dests = filter(lambda dest: dest not in targets, graph.nodes())
        paths = [path for path in nx.all_simple_paths(graph, targets[len(targets) - 1], dests)]
        targets = [edge[0] for edge in target_edges]
        path = max(filter(lambda path: not (set(path) & set(targets)), paths), key=len)
        target_edges.extend(nx.utils.pairwise(path))
        targets.extend(path)
    else:
        # Otherwise construct a path literally
        target_edges = distill.pairwiseSeq(targets)

    # Get the total outflow of the starting node
    counts = sum([graph.get_edge_data(*edge)['capacity'] for edge in graph.out_edges(target_edges[0][0])])
    
    # Get the flow at every other node in the path
    counts = [counts] + [graph.get_edge_data(*edge)['capacity'] for edge in target_edges]
    counts = [min(counts[0:i]) for i in range(1, len(counts)+1)]
    
    # Return a funnel representing the flow throughout the constructed path
    return go.Figure(go.Funnel(y=targets, x=counts))
