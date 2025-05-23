from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Tuple
import uuid

# Forward declaration for type hinting if Node references itself or other node types
# class Node;

@dataclass
class Socket:
    name: str
    node_id: str # ID of the node this socket belongs to
    socket_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_type: Any = Any # Could be more specific, e.g., using ParamTypePlaceholder from ir.py
    is_input: bool = True
    # Connection: Tuple[str, str] | None = None  # (connected_node_id, connected_socket_id)
    # For multiple connections (e.g. an input that can receive from multiple outputs, though less common)
    connections: List[Tuple[str, str]] = field(default_factory=list) 


@dataclass
class Node:
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Node"
    node_type: str = "BaseNode"
    inputs: Dict[str, Socket] = field(default_factory=dict)
    outputs: Dict[str, Socket] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict) # General properties like position, color, etc.
    
    # Callback for when the node's state might require an update of the graph/IR
    # on_update: Callable[[], None] | None = None 

    def __post_init__(self):
        # Ensure sockets know their node_id and whether they are input/output
        for socket_name, socket_obj in self.inputs.items():
            socket_obj.node_id = self.node_id
            socket_obj.is_input = True
            socket_obj.name = socket_name # Ensure name consistency
        for socket_name, socket_obj in self.outputs.items():
            socket_obj.node_id = self.node_id
            socket_obj.is_input = False
            socket_obj.name = socket_name # Ensure name consistency

    def add_input_socket(self, name: str, data_type: Any = Any) -> Socket:
        if name in self.inputs:
            raise ValueError(f"Input socket '{name}' already exists on node '{self.node_id}'.")
        socket = Socket(name=name, node_id=self.node_id, data_type=data_type, is_input=True)
        self.inputs[name] = socket
        return socket

    def add_output_socket(self, name: str, data_type: Any = Any) -> Socket:
        if name in self.outputs:
            raise ValueError(f"Output socket '{name}' already exists on node '{self.node_id}'.")
        socket = Socket(name=name, node_id=self.node_id, data_type=data_type, is_input=False)
        self.outputs[name] = socket
        return socket

    def get_input_socket(self, name: str) -> Socket | None:
        return self.inputs.get(name)

    def get_output_socket(self, name: str) -> Socket | None:
        return self.outputs.get(name)

    # Placeholder for processing logic, to be overridden by subclasses
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Processing Node: {self.name} ({self.node_id})")
        # Basic pass-through or specific logic
        return {}

    def __repr__(self):
        return f"{self.node_type}(id='{self.node_id}', name='{self.name}')"


@dataclass
class SourceNode(Node):
    node_type: str = "SourceNode"
    # This node might be directly linked to an EmitterProperties instance from ir.py
    emitter_id: str | None = None # Link to an EmitterProperties in the EffectIR

    def __post_init__(self):
        super().__post_init__()
        # Source nodes typically have outputs but no direct data inputs
        # Example output: particle data stream, or signal
        if not self.outputs: # Add a default output if none defined by instantiation
            self.add_output_socket(name="output_particles", data_type="ParticleStream") 

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # In a real system, this would fetch/generate data from its corresponding emitter
        print(f"Processing SourceNode: {self.name}. Emitter ID: {self.emitter_id}")
        # For now, let's imagine it outputs some mock data or a reference to itself/emitter
        return {"output_particles": f"data_from_{self.emitter_id or self.node_id}"}


@dataclass
class DisplayNode(Node):
    node_type: str = "DisplayNode"
    # This node might be responsible for triggering a render or showing final values

    def __post_init__(self):
        super().__post_init__()
        # Display nodes typically have inputs but no direct data outputs in the graph flow
        if not self.inputs: # Add a default input if none defined
            self.add_input_socket(name="input_data", data_type=Any)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Processing DisplayNode: {self.name}. Received data:")
        for input_name, data_value in input_data.items():
            socket = self.get_input_socket(input_name)
            if socket and socket.connections:
                print(f"  Input '{input_name}' (from {len(socket.connections)} connection(s)): {data_value}")
            else:
                print(f"  Input '{input_name}' (no connection): {data_value}")
        # Display nodes typically don't output data further into the graph
        return {}


if __name__ == '__main__':
    # Example Usage
    source1 = SourceNode(name="Particle Emitter A", emitter_id="emitter_001")
    source1.add_output_socket(name="color_profile", data_type="Color") # Additional output
    
    display1 = DisplayNode(name="Main Output")
    display1.add_input_socket(name="particles_in", data_type="ParticleStream")
    display1.add_input_socket(name="settings_in", data_type=dict)

    print(source1)
    print(source1.outputs)
    print(display1)
    print(display1.inputs)

    # --- Representing Connections ---
    # Let's say source1.output_particles is connected to display1.particles_in
    # This connection logic would typically be managed by a NodeGraph class
    
    # Simulate fetching data from a source node
    source_output_data = source1.process({})
    print(f"Source 1 produced: {source_output_data}")

    # Simulate providing data to a display node
    # The graph execution engine would map source_output_data["output_particles"] 
    # to display1_input_data["particles_in"] if they are connected.
    display1_input_data = {
        "particles_in": source_output_data.get("output_particles"),
        "settings_in": {"brightness": 0.8}
    }
    display1.process(display1_input_data)

    # --- Socket details ---
    out_particles_socket = source1.get_output_socket("output_particles")
    in_particles_socket = display1.get_input_socket("particles_in")

    if out_particles_socket and in_particles_socket:
        # Simulate a connection by populating the connections list
        # In a real graph, the NodeGraph would manage this.
        # A connection is (from_node_id, from_socket_name/id)
        # An input socket stores where it's connected FROM.
        in_particles_socket.connections.append((source1.node_id, out_particles_socket.socket_id))
        print(f"Socket '{in_particles_socket.name}' on node '{display1.name}' is_input: {in_particles_socket.is_input}, connected to: {in_particles_socket.connections}")
    
        # An output socket could also store where it connects TO, if needed for bi-directional traversal
        # out_particles_socket.connections.append((display1.node_id, in_particles_socket.socket_id)) 
        # print(f"Socket '{out_particles_socket.name}' on node '{source1.name}' is_input: {out_particles_socket.is_input}, connected to: {out_particles_socket.connections}")


    # Test a node without default sockets to ensure post_init adds them
    minimal_source = SourceNode(name="Minimal Source")
    print(minimal_source.outputs) # Should have 'output_particles'
    minimal_display = DisplayNode(name="Minimal Display")
    print(minimal_display.inputs) # Should have 'input_data'

    # Test adding sockets
    test_node = Node(name="Test Node")
    test_node.add_input_socket("alpha_in", data_type=float)
    test_node.add_output_socket("beta_out", data_type=int)
    print(test_node.inputs)
    print(test_node.outputs)

    # Test getting socket
    alpha_socket = test_node.get_input_socket("alpha_in")
    print(f"Fetched socket: {alpha_socket}")
    
    # Test that socket_id is unique and name is passed correctly
    s_out = minimal_source.get_output_socket("output_particles")
    d_in = minimal_display.get_input_socket("input_data")
    print(f"Source output socket: name='{s_out.name}', id='{s_out.socket_id}'")
    print(f"Display input socket: name='{d_in.name}', id='{d_in.socket_id}'")
    assert s_out.name == "output_particles"
    assert d_in.name == "input_data"
    assert s_out.socket_id != d_in.socket_id
    assert s_out.node_id == minimal_source.node_id
    assert d_in.node_id == minimal_display.node_id
    assert not s_out.is_input
    assert d_in.is_input 