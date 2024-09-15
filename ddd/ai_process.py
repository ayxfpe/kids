import networkx as nx
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
import re

def process_concept_tree(file_path, progress_file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # Parse the markdown content
    lines = content.split('\n')
    root = Node("Concept Tree")
    current_nodes = {0: root}
    
    for line in lines[1:]:  # Skip the title
        if line.strip():
            level = len(re.match(r'\s*', line).group(0)) // 2
            name = line.strip().lstrip('- ')
            current_nodes[level] = Node(name, parent=current_nodes.get(level-1, root))

    # Load progress
    with open(progress_file_path, 'r') as f:
        progress = set(line.strip() for line in f)

    # Create a networkx graph
    G = nx.Graph()
    
    def add_nodes_edges(node, parent=None):
        G.add_node(node.name)
        if node.name in progress:
            G.nodes[node.name]['color'] = 'lightblue'
        else:
            G.nodes[node.name]['color'] = 'lightgreen'
        if parent:
            G.add_edge(parent.name, node.name)
        for child in node.children:
            add_nodes_edges(child, node)

    add_nodes_edges(root)

    # Generate the visual representation
    plt.figure(figsize=(20, 10))
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    nx.draw(G, pos, with_labels=True, node_color=[G.nodes[n]['color'] for n in G.nodes()],
            node_size=3000, font_size=8, font_weight='bold')
    
    plt.title("Concept Tree with Progress", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('ddd/concept_tree.png', dpi=300, bbox_inches='tight')
    plt.close()

# Example usage
process_concept_tree('ddd/concept_tree.md', 'ddd/progress.txt')