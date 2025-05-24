import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

class GraphVisualizer:
    def __init__(self):
        self.G = nx.DiGraph()
        
    def create_graph(self, relationships_dict):
        """Create a directed graph from relationships dictionary"""
        print("\n=== Creating Graph ===")
        self.G.clear()
        print("Graph cleared")
        
        # First add all nodes
        for rel in relationships_dict:
            source = rel['node_start']
            self.G.add_node(source)
            print(f"Added node: {source}")
            
            # If there's a target node, add it too
            if rel['node_end']:
                target = rel['node_end']
                self.G.add_node(target)
                print(f"Added node: {target}")
                
                # Add edge only if there's a relationship
                if rel['relationship']:
                    self.G.add_edge(source, target, label=rel['relationship'])
                    print(f"Added edge: {source} --[{rel['relationship']}]--> {target}")
    
        print(f"\nGraph created with:")
        print(f"- {len(self.G.nodes())} nodes")
        print(f"- {len(self.G.edges())} edges")

    def show_graph(self):
        """Display the graph in a new window"""
        if len(self.G.nodes()) == 0:
            print("No nodes to display")
            return
            
        window = tk.Toplevel()
        window.title("Knowledge Graph Visualization")
        window.geometry("1200x800")  # Larger window
        
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # Use kamada_kawai_layout for better node distribution
        pos = nx.kamada_kawai_layout(self.G, scale=2.0)
        
        # Increase spacing between nodes
        pos = nx.spring_layout(self.G, pos=pos, k=1.5, iterations=50)
        
        # Draw nodes with larger size
        nx.draw_networkx_nodes(self.G, pos,
                             node_color='lightblue',
                             node_size=3000,
                             alpha=0.7)
        
        # Draw node labels with larger font
        nx.draw_networkx_labels(self.G, pos, font_size=10)
        
        # Draw edges with curves and larger arrows
        nx.draw_networkx_edges(self.G, pos,
                             edge_color='gray',
                             arrows=True,
                             arrowsize=20,
                             connectionstyle="arc3,rad=0.3",  # Increase curve
                             width=2)
        
        # Draw edge labels with offset
        edge_labels = nx.get_edge_attributes(self.G, 'label')
        nx.draw_networkx_edge_labels(self.G, pos,
                                   edge_labels=edge_labels,
                                   font_size=8,
                                   label_pos=0.6)  # Move labels away from edges
        
        # Add more space around the graph
        ax.margins(0.3)
        plt.axis('off')
        
        # Create canvas with scrollbars
        frame = tk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add zoom controls
        control_frame = tk.Frame(window)
        control_frame.pack(fill=tk.X)
        
        def zoom(factor):
            current_size = fig.get_size_inches()
            fig.set_size_inches(current_size[0]*factor, current_size[1]*factor)
            canvas.draw()
            
        tk.Button(control_frame, text="Zoom In", command=lambda: zoom(1.2)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Zoom Out", command=lambda: zoom(0.8)).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(control_frame, text="Close", command=window.destroy).pack(side=tk.RIGHT, padx=5, pady=5)