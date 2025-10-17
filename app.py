import streamlit as st
import json
import os
from typing import Dict, List, Any
from streamlit_agraph import agraph, Node, Edge, Config
import subprocess
import sys
import time

# Import the registry to get functions
sys.path.append('/Users/liweikang/Code/gtool_registry_version')
from gtools.registry import list_all_modules, get_module_info, ConfigHandler, execute_start_sh, auto_import_functions_modules

# Auto import all functions
auto_import_functions_modules()

class StreamingOutput:
    """A file-like object that streams output to Streamlit in real-time"""
    def __init__(self, terminal_placeholder, terminal_content_key, node_name=None):
        self.terminal_placeholder = terminal_placeholder
        self.terminal_content_key = terminal_content_key
        self.node_name = node_name
        self.buffer = ""
        
    def write(self, text):
        self.buffer += text
        # Update the session state and display
        if hasattr(st, 'session_state') and hasattr(st.session_state, self.terminal_content_key):
            if self.node_name:
                # Update specific node's log
                if not hasattr(st.session_state, 'node_logs'):
                    st.session_state.node_logs = {}
                if self.node_name not in st.session_state.node_logs:
                    st.session_state.node_logs[self.node_name] = ""
                st.session_state.node_logs[self.node_name] += text
            else:
                # Update global log
                if not hasattr(st.session_state, self.terminal_content_key):
                    setattr(st.session_state, self.terminal_content_key, "")
                current_content = getattr(st.session_state, self.terminal_content_key, "")
                setattr(st.session_state, self.terminal_content_key, current_content + text)
            
            # Update display
            self.update_display()
    
    def update_display(self):
        # Get current selector value
        if hasattr(st.session_state, 'node_log_selector'):
            selected_node = getattr(st.session_state, 'node_log_selector')
            if selected_node == "📋 Global Log":
                display_content = getattr(st.session_state, self.terminal_content_key, "")
            else:
                display_content = st.session_state.node_logs.get(selected_node, "No logs available")
        else:
            display_content = getattr(st.session_state, self.terminal_content_key, "")
        
        # Update the display
        self.terminal_placeholder.code(display_content, language="text")
    
    def flush(self):
        pass

def load_config(config_path: str) -> Dict[str, Any]:
    return ConfigHandler.load_config(config_path)

def save_config(config: Dict[str, Any], config_path: str):
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def get_available_functions() -> List[str]:
    return list_all_modules()

def parse_argparse_for_ui(parser_func):
    """解析 argparse 参数，为 UI 生成控件配置"""
    import argparse
    
    # 调用解析器函数获取解析器
    try:
        parser = parser_func()
    except Exception as e:
        print(f"Error getting parser: {e}")
        return []
    
    params_config = []
    
    for action in parser._actions:
        if action.dest == 'help':
            continue
            
        param_config = {
            'dest': action.dest,
            'type': action.type,
            'default': action.default,
            'required': action.required,
            'nargs': action.nargs,
            'choices': action.choices,
            'help': action.help or '',
            'is_flag': isinstance(action, argparse._StoreTrueAction) or isinstance(action, argparse._StoreFalseAction),
            'is_positional': len(action.option_strings) == 0,
            'option_strings': action.option_strings
        }
        params_config.append(param_config)
    
    return params_config

def parameter_config_dialog(selected_func, mode="add", current_params=None, node_idx=None, modules=None):
    """Parameter configuration dialog"""
    dialog_key = f"dialog_{mode}_{selected_func}_{node_idx if node_idx is not None else 'new'}"
    
    # Initialize dialog state
    if dialog_key not in st.session_state:
        st.session_state[dialog_key] = False
    
    # Get module info and parse parameters
    module_info = get_module_info(selected_func)
    params_config = []
    if module_info['has_args']:
        params_config = parse_argparse_for_ui(module_info['args_parser'])
    
    # Get current dependencies if editing
    current_deps = []
    if mode == "edit" and modules and node_idx is not None:
        current_deps = modules[node_idx].get('depends_on', [])
    
    # Get current display name if editing
    current_display_name = ""
    if mode == "edit" and modules and node_idx is not None:
        current_display_name = modules[node_idx].get('name', modules[node_idx].get('module_name', ''))
    
    # Get available nodes for dependency selection (exclude current node if editing)
    available_nodes = []
    if modules:
        for i, module in enumerate(modules):
            if mode == "edit" and i == node_idx:
                continue  # Don't allow self-dependency
            available_nodes.append(module.get('name', module.get('module_name', f'module_{i}')))
    
    # Dialog content
    if st.session_state[dialog_key]:
        @st.dialog(f"{'Add' if mode == 'add' else 'Edit'} Parameters for {selected_func}")
        def show_dialog():
            # Display name input
            st.subheader("📝 Display Name")
            display_name = st.text_input(
                "Display Name (shown in graph)",
                value=current_display_name if mode == "edit" else selected_func,
                key=f"display_name_{mode}_{selected_func}_{node_idx if node_idx is not None else 'new'}"
            )
            
            st.write(f"Configure parameters for **{selected_func}**")
            
            param_values = {}
            
            if params_config:
                for param in params_config:
                    dest = param['dest']
                    param_type = param['type']
                    default = param['default']
                    nargs = param['nargs']
                    choices = param['choices']
                    help_text = param['help']
                    is_flag = param['is_flag']
                    is_positional = param.get('is_positional', False)
                    
                    # Use current value if editing
                    if mode == "edit" and current_params:
                        if is_positional and '_positional_args' in current_params:
                            current_value = current_params['_positional_args'].get(dest, default)
                        else:
                            current_value = current_params.get(dest, default)
                    else:
                        current_value = default
                    
                    label = dest.replace('_', ' ').title()
                    if help_text:
                        label += f" ({help_text})"
                    
                    key = f"{mode}_{selected_func}_{dest}_{node_idx if node_idx is not None else 'new'}"
                    
                    if is_flag:
                        # Boolean flag
                        value = st.checkbox(label, value=current_value if current_value is not None else False, key=key)
                    elif choices:
                        # Multiple choice
                        if nargs in ('+', '*'):
                            value = st.multiselect(label, choices, default=current_value if isinstance(current_value, list) else [], key=key)
                        else:
                            index = choices.index(current_value) if current_value in choices else 0
                            value = st.selectbox(label, choices, index=index, key=key)
                    elif param_type == int:
                        # Integer input
                        if nargs in ('+', '*'):
                            default_val = current_value if current_value and isinstance(current_value, list) else []
                            default_str = ','.join(str(x) for x in default_val) if default_val else ""
                            value = st.text_input(label, value=default_str, key=key, help="Enter comma-separated integers")
                        else:
                            value = st.number_input(label, value=current_value if current_value is not None else 0, step=1, key=key)
                    elif param_type == float:
                        # Float input
                        if nargs in ('+', '*'):
                            default_val = current_value if current_value and isinstance(current_value, list) else []
                            default_str = ','.join(str(x) for x in default_val) if default_val else ""
                            value = st.text_input(label, value=default_str, key=key, help="Enter comma-separated floats")
                        else:
                            value = st.number_input(label, value=current_value if current_value is not None else 0.0, step=0.1, key=key)
                    else:
                        # String input (positional args)
                        if nargs in ('+', '*'):
                            default_val = current_value if current_value and isinstance(current_value, list) else []
                            default_str = ','.join(str(x) for x in default_val) if default_val else ""
                            value = st.text_input(label, value=default_str, key=key, help="Enter comma-separated values")
                        else:
                            value = st.text_input(label, value=str(current_value) if current_value is not None else "", key=key)
                    
                    param_values[dest] = value
            else:
                st.write("No parameters required")
            
            # Dependencies section
            st.markdown("---")
            st.subheader("🔗 Dependencies")
            
            if available_nodes:
                selected_deps = st.multiselect(
                    "Select dependencies (nodes that must run before this one)",
                    available_nodes,
                    default=current_deps,
                    key=f"deps_{mode}_{selected_func}_{node_idx if node_idx is not None else 'new'}"
                )
            else:
                st.write("No other nodes available for dependency selection")
                selected_deps = []
            
            # Convert parameter values to proper format
            formatted_params = {}
            positional_args = {}
            
            for param in params_config:
                dest = param['dest']
                value = param_values.get(dest)
                is_positional = param.get('is_positional', False)
                
                # Get current value for editing mode
                if mode == "edit" and current_params:
                    if is_positional and '_positional_args' in current_params:
                        current_value = current_params['_positional_args'].get(dest, param['default'])
                    else:
                        current_value = current_params.get(dest, param['default'])
                else:
                    current_value = param['default']
                
                if is_positional:
                    # 位置参数直接存储为列表
                    if param['is_flag']:
                        positional_args[dest] = value if value is not None else current_value
                    elif param['type'] == int:
                        if param['nargs'] in ('+', '*'):
                            if isinstance(value, str) and value:
                                try:
                                    positional_args[dest] = [int(x.strip()) for x in value.split(',')]
                                except:
                                    positional_args[dest] = current_value if isinstance(current_value, list) else [1, 2, 3]
                            else:
                                positional_args[dest] = current_value if isinstance(current_value, list) else [1, 2, 3]
                        else:
                            positional_args[dest] = int(value) if value is not None else current_value
                    elif param['type'] == float:
                        if param['nargs'] in ('+', '*'):
                            if isinstance(value, str) and value:
                                try:
                                    positional_args[dest] = [float(x.strip()) for x in value.split(',')]
                                except:
                                    positional_args[dest] = current_value if isinstance(current_value, list) else [1.0, 2.0, 3.0]
                            else:
                                positional_args[dest] = current_value if isinstance(current_value, list) else [1.0, 2.0, 3.0]
                        else:
                            positional_args[dest] = float(value) if value is not None else current_value
                    else:
                        # 对于其他类型（包括None），按字符串处理
                        if param['nargs'] in ('+', '*'):
                            if isinstance(value, str) and value:
                                positional_args[dest] = [x.strip() for x in value.split(',')]
                            else:
                                positional_args[dest] = current_value if isinstance(current_value, list) else []
                        else:
                            positional_args[dest] = str(value) if value is not None else current_value
                else:
                    # 可选参数存储在formatted_params中
                    if param['is_flag']:
                        formatted_params[dest] = value if value is not None else current_value
                    elif param['type'] == int:
                        if param['nargs'] in ('+', '*'):
                            if isinstance(value, str) and value:
                                try:
                                    formatted_params[dest] = [int(x.strip()) for x in value.split(',')]
                                except:
                                    formatted_params[dest] = current_value if isinstance(current_value, list) else []
                            else:
                                formatted_params[dest] = current_value if isinstance(current_value, list) else []
                        else:
                            formatted_params[dest] = int(value) if value is not None else current_value
                    elif param['type'] == float:
                        if param['nargs'] in ('+', '*'):
                            if isinstance(value, str) and value:
                                try:
                                    formatted_params[dest] = [float(x.strip()) for x in value.split(',')]
                                except:
                                    formatted_params[dest] = current_value if isinstance(current_value, list) else []
                            else:
                                formatted_params[dest] = current_value if isinstance(current_value, list) else []
                        else:
                            formatted_params[dest] = float(value) if value is not None else current_value
                    else:
                        if param['nargs'] in ('+', '*'):
                            if isinstance(value, str) and value:
                                formatted_params[dest] = [x.strip() for x in value.split(',')]
                            else:
                                formatted_params[dest] = current_value if isinstance(current_value, list) else []
                        else:
                            formatted_params[dest] = str(value) if value is not None else current_value
            
            # 如果有位置参数，将它们添加到formatted_params中
            if positional_args:
                formatted_params['_positional_args'] = positional_args
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel", key=f"cancel_{mode}_{selected_func}"):
                    st.session_state[dialog_key] = False
                    st.rerun()
            
            with col2:
                if st.button(f"{'Add' if mode == 'add' else 'Update'} Node", key=f"confirm_{mode}_{selected_func}"):
                    st.session_state[dialog_key] = False
                    # Store result in session state
                    result_key = f"result_{dialog_key}"
                    st.session_state[result_key] = (formatted_params, selected_deps, display_name)
                    st.rerun()
        
        show_dialog()
    
    # Check for result
    result_key = f"result_{dialog_key}"
    if result_key in st.session_state:
        result = st.session_state[result_key]
        del st.session_state[result_key]
        return result
    
    return None, None, None

def topological_sort(modules: List[Dict[str, Any]]) -> List[int]:
    """Perform topological sort on modules based on dependencies"""
    # Create adjacency list and indegree count
    adj_list = {}
    indegree = {}
    
    # Initialize
    for i, module in enumerate(modules):
        adj_list[i] = []
        indegree[i] = 0
    
    # Build graph
    name_to_idx = {module.get('name', module.get('module_name', f'module_{i}')): i for i, module in enumerate(modules)}
    
    for i, module in enumerate(modules):
        for dep in module.get('depends_on', []):
            if dep in name_to_idx:
                j = name_to_idx[dep]
                adj_list[j].append(i)  # j -> i (j must run before i)
                indegree[i] += 1
    
def topological_sort(modules: List[Dict[str, Any]]) -> List[int]:
    """Perform topological sort that prefers original order when possible"""
    # Create dependency tracking
    name_to_idx = {module.get('name', module.get('module_name', f'module_{i}')): i for i, module in enumerate(modules)}
    completed = set()
    result = []

    # Keep trying until all nodes are processed
    remaining = set(range(len(modules)))

    while remaining:
        progress_made = False

        for i in list(remaining):
            module = modules[i]
            deps = module.get('depends_on', [])

            # Check if all dependencies are satisfied
            deps_satisfied = all(
                dep in [modules[j].get('name', modules[j].get('module_name', f'module_{j}')) for j in completed]
                for dep in deps
            )

            if deps_satisfied:
                result.append(i)
                completed.add(i)
                remaining.remove(i)
                progress_made = True

        # If no progress was made, there's a cycle
        if not progress_made:
            # Return original order as fallback
            return list(range(len(modules)))

    return result

def execute_graph(modules: List[Dict[str, Any]]) -> str:
    """Execute the graph and return results"""
    results = []
    
    # Get execution order using topological sort
    execution_order = topological_sort(modules)
    
    for idx in execution_order:
        module = modules[idx]
        name = module.get('module_name', module.get('name', 'unknown'))
        params = module.get('params', {})
        try:
            # Import the module
            module_info = get_module_info(name)
            if not module_info['has_function']:
                results.append(f"{name}: Function not found")
                continue
            
            func = module_info['function']
            args_parser = module_info['args_parser']
            
            # Parse params into args
            parser = args_parser()
            # Convert params to command line args
            args_list = []
            for key, value in params.items():
                if key == '_positional_args':
                    for k, v in value.items():
                        if isinstance(v, list):
                            args_list.extend([str(x) for x in v])
                        else:
                            args_list.append(str(v))
                else:
                    args_list.append(f"--{key}")
                    if isinstance(value, bool):
                        if value:
                            pass  # flag
                        else:
                            args_list.pop()  # remove if false
                    elif isinstance(value, list):
                        args_list.extend([str(x) for x in value])
                    else:
                        args_list.append(str(value))
            
            args = parser.parse_args(args_list)
            
            # Capture output
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output = io.StringIO()
            with redirect_stdout(output), redirect_stderr(output):
                func(args)
            
            result = output.getvalue()
            results.append(f"{name}:\n{result}")
        except Exception as e:
            results.append(f"{name}: Error - {str(e)}")
    return "\n".join(results)

def main():
    # st.title("GTool Registry Visual Builder")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        config_path = st.text_input("Config File Path", value="/Users/liweikang/Code/gtool_registry_version/system_config/config.json")
        
        # Initialize session state for config path
        if 'config_loaded' not in st.session_state:
            st.session_state.config_loaded = False
            st.session_state.config_path = None
        
        if st.button("Load/Create Config"):
            if not os.path.exists(config_path):
                # Create new config
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                save_config({"working_directory": "/Users/liweikang/Code/gtool_registry_version", "modules": []}, config_path)
                st.success(f"Created new config at {config_path}")
            else:
                st.success(f"Loaded config from {config_path}")
            
            # Update session state
            st.session_state.config_loaded = True
            st.session_state.config_path = config_path

    if not st.session_state.config_loaded:
        st.warning("Please load or create a config file first.")
        return

    # Load current config
    config = load_config(st.session_state.config_path)
    modules = config.get('modules', [])
    
    # Migrate old config format: if modules don't have module_name, add it
    for module in modules:
        if 'module_name' not in module and 'name' in module:
            # For old format, assume name was the module name
            module['module_name'] = module['name']
            # Keep the display name as is
        elif 'module_name' not in module:
            # If neither exists, set both to unknown
            module['module_name'] = 'unknown'
            module['name'] = 'unknown'

    # Sidebar for adding nodes
    with st.sidebar:
        st.header("Add Node")
    
        # Node selection box
        with st.container():
            st.subheader("📋 Function Selection")
            available_funcs = get_available_functions()
            
            if not available_funcs:
                st.error("No functions found. Please check if functions are properly registered.")
            else:
                selected_func = st.selectbox("Select Function", available_funcs, key="select_function")
                
                if st.button("⚙️ Configure Parameters", key="configure_params"):
                    dialog_key = f"dialog_add_{selected_func}_new"
                    st.session_state[dialog_key] = True
                    st.rerun()
                
                # Check for dialog result
                dialog_key = f"dialog_add_{selected_func}_new"
                params, deps, display_name = parameter_config_dialog(selected_func, mode="add", modules=modules)
                if params is not None:
                    # Add new module to config
                    new_module = {
                        "module_name": selected_func,
                        "name": display_name,
                        "params": params,
                        "depends_on": deps
                    }
                    modules.append(new_module)
                    config['modules'] = modules
                    save_config(config, st.session_state.config_path)
                    st.success(f"Added {display_name}")
                    # Remove st.rerun() to avoid issues

        # Edit existing nodes
        st.header("Edit Nodes")
        
        # Node selection box for editing
        with st.container():
            st.subheader("📝 Select Node to Edit")
            if modules:
                node_names = [m.get('name', m.get('module_name', f'module_{i}')) for i, m in enumerate(modules)]  # Use display name, fallback to module_name
                edit_node = st.selectbox("Select Node to Edit", node_names, key="edit_node")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔧 Edit Parameters", key="edit_params"):
                        idx = node_names.index(edit_node)
                        module = modules[idx]
                        current_params = module.get('params', {})
                        
                        dialog_key = f"dialog_edit_{module['module_name']}_{idx}"
                        st.session_state[dialog_key] = True
                        st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete Node", key="delete_node"):
                        idx = node_names.index(edit_node)
                        module = modules[idx]
                        display_name = module.get('name', module.get('module_name', f'module_{idx}'))
                        
                        # Store deletion info in session state
                        st.session_state.delete_node_info = {
                            'idx': idx,
                            'display_name': display_name
                        }
                        st.rerun()
                
                # Handle node deletion
                if 'delete_node_info' in st.session_state:
                    delete_info = st.session_state.delete_node_info
                    del st.session_state.delete_node_info
                    
                    @st.dialog(f"Delete Node: {delete_info['display_name']}")
                    def confirm_delete():
                        st.write(f"Are you sure you want to delete the node **{delete_info['display_name']}**?")
                        st.write("This action cannot be undone.")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("❌ Cancel", key="cancel_delete"):
                                st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Delete", key="confirm_delete"):
                                idx = delete_info['idx']
                                display_name = delete_info['display_name']
                                
                                # Remove the node
                                deleted_module = modules.pop(idx)
                                
                                # Remove dependencies to this node from other nodes
                                for other_module in modules:
                                    if display_name in other_module.get('depends_on', []):
                                        other_module['depends_on'] = [dep for dep in other_module['depends_on'] if dep != display_name]
                                
                                # Save config
                                config['modules'] = modules
                                save_config(config, st.session_state.config_path)
                                
                                st.success(f"Node '{display_name}' deleted successfully!")
                                st.rerun()
                    
                    confirm_delete()
                
                # Check for dialog result
                # We need to check all possible dialog keys since we don't know which one was triggered
                for i, module in enumerate(modules):
                    dialog_key = f"dialog_edit_{module['module_name']}_{i}"
                    result_key = f"result_{dialog_key}"
                    
                    # Check for result first
                    if result_key in st.session_state:
                        result = st.session_state[result_key]
                        del st.session_state[result_key]
                        params, deps, display_name = result
                        # Update module
                        old_display_name = modules[i].get('name', modules[i].get('module_name', f'module_{i}'))
                        modules[i]['params'] = params
                        modules[i]['depends_on'] = deps
                        modules[i]['name'] = display_name
                        
                        # Update dependencies that reference the old display name
                        if old_display_name != display_name:
                            for other_module in modules:
                                if old_display_name in other_module.get('depends_on', []):
                                    other_module['depends_on'] = [display_name if dep == old_display_name else dep for dep in other_module['depends_on']]
                        
                        config['modules'] = modules
                        save_config(config, st.session_state.config_path)
                        st.success("Updated")
                    
                    # Show dialog if active
                    if dialog_key in st.session_state and st.session_state[dialog_key]:
                        params, deps, display_name = parameter_config_dialog(module['module_name'], mode="edit", current_params=module.get('params', {}), node_idx=i, modules=modules)
                        # Result processing is handled above
            else:
                st.write("No nodes to edit")

    # Display current graph
    st.header("Current Graph")

    # Graph display mode selector
    graph_mode = st.selectbox(
        "Graph Display Mode",
        ["📈 计算顺序", "🔗 依赖关系"],
        index=0,  # Default to execution order
        help="📈 计算顺序: 显示节点执行顺序的箭头\n🔗 依赖关系: 显示依赖关系的箭头"
    )

    nodes = []
    edges = []

    # Get execution order (for display only)
    execution_order = list(range(len(modules)))  # Use config order instead of topological sort
    order_map = {idx: pos + 1 for pos, idx in enumerate(execution_order)}

    if graph_mode == "📈 计算顺序":
        # Show execution order with arrows pointing to next nodes in sequence
        for i, module in enumerate(modules):
            order_num = order_map.get(i, "?")
            node_type = "📊" if module.get('depends_on') else "🔄"
            label = f"{node_type} {order_num}. {module.get('name', module.get('module_name', f'module_{i}'))}"
            nodes.append(Node(id=str(i), label=label, size=25))

        # Add edges based on execution order (arrows point to next nodes)
        for pos, current_idx in enumerate(execution_order[:-1]):  # Exclude last node
            next_idx = execution_order[pos + 1]
            edges.append(Edge(source=str(current_idx), target=str(next_idx)))

    else:  # "🔗 依赖关系"
        # Show dependency relationships
        for i, module in enumerate(modules):
            order_num = order_map.get(i, "?")
            node_type = "📊" if module.get('depends_on') else "🔄"
            label = f"{node_type} {order_num}. {module.get('name', module.get('module_name', f'module_{i}'))}"
            nodes.append(Node(id=str(i), label=label, size=25))

        # Add edges based on depends_on (arrows point from dependency to dependent)
        for i, module in enumerate(modules):
            for dep in module.get('depends_on', []):
                for j, m in enumerate(modules):
                    if m.get('name', m.get('module_name', f'module_{j}')) == dep:
                        edges.append(Edge(source=str(j), target=str(i)))

    if nodes:
        config_agraph = Config(width=750,
                              height=400,
                              directed=True,
                              physics=False,
                              hierarchical=dict(
                                  direction='UD',  # Up-Down direction
                                  sortMethod='directed',  # Use directed sort
                                  nodeSpacing=200,
                                  levelSeparation=150
                              ))

        agraph(nodes=nodes, edges=edges, config=config_agraph)

    else:
        st.write("No nodes yet. Add some from the sidebar.")

    # Terminal-like output area at the bottom
    st.header("🖥️ Execution Terminal")
    
    # Initialize terminal content
    if 'terminal_content' not in st.session_state:
        st.session_state.terminal_content = "Terminal ready. Click 'Execute Graph' to run nodes.\n"
    
    if 'node_logs' not in st.session_state:
        st.session_state.node_logs = {}
    
    # Node selector for logs
    node_options = ["📋 Global Log"] + [module.get('name', module.get('module_name', f'module_{i}')) for i, module in enumerate(modules)]
    
    # Get current selection, default to Global Log
    current_selection = st.session_state.get('selected_node_log', "📋 Global Log")
    
    # Ensure the selection is valid
    if current_selection not in node_options:
        current_selection = "📋 Global Log"
        st.session_state.selected_node_log = current_selection
    
    selected_node = st.selectbox("Select Node Log", node_options, key="node_log_selector")
    
    # Update stored selection
    st.session_state.selected_node_log = selected_node
    
    if selected_node == "📋 Global Log":
        display_content = st.session_state.terminal_content
    else:
        display_content = st.session_state.node_logs.get(selected_node, "No logs available")
    
    # Create a scrollable container for terminal output
    with st.container(height=300):
        terminal_placeholder = st.empty()
        terminal_placeholder.code(display_content, language="text")

    # Execute button
    if st.button("Execute Graph"):
        # Reset terminal content and node logs
        st.session_state.terminal_content = "🚀 Starting graph execution...\n"
        st.session_state.node_logs = {}
        
        # Execute each node in the order they appear in config (not topological order)
        for idx in range(len(modules)):
            module = modules[idx]
            name = module.get('module_name', module.get('name', 'unknown'))
            display_name = module.get('name', name)
            params = module.get('params', {})

            # Update global terminal with current execution
            st.session_state.terminal_content += f"\n▶️ Executing: {display_name}\n"
            
            # Initialize node-specific log
            if display_name not in st.session_state.node_logs:
                st.session_state.node_logs[display_name] = ""
            
            st.session_state.node_logs[display_name] += f"▶️ Executing: {display_name}\n"
            st.session_state.node_logs[display_name] += f"Parameters: {params}\n"

            try:
                # Import the module
                module_info = get_module_info(name)
                if not module_info['has_function']:
                    error_msg = f"❌ Error: Function '{name}' not found\n"
                    st.session_state.terminal_content += error_msg
                    st.session_state.node_logs[display_name] += error_msg
                    continue

                func = module_info['function']
                args_parser = module_info['args_parser']
                
                # Get parameter configuration for correct option strings
                params_config = []
                if module_info['has_args']:
                    params_config = parse_argparse_for_ui(module_info['args_parser'])

                # Parse params into args
                parser = args_parser()
                args_list = []
                for key, value in params.items():
                    if key == '_positional_args':
                        for k, v in value.items():
                            if isinstance(v, list):
                                args_list.extend([str(x) for x in v])
                            else:
                                args_list.append(str(v))
                    else:
                        # 对于可选参数，使用正确的选项字符串
                        param_config = next((p for p in params_config if p['dest'] == key), None)
                        if param_config and 'option_strings' in param_config and param_config['option_strings']:
                            option_string = param_config['option_strings'][0]  # 使用第一个选项字符串
                            args_list.append(option_string)
                        else:
                            args_list.append(f"--{key}")
                        
                        if isinstance(value, bool):
                            if value:
                                pass  # flag
                            else:
                                args_list.pop()  # remove if false
                        elif isinstance(value, list):
                            args_list.extend([str(x) for x in value])
                        else:
                            args_list.append(str(value))

                st.session_state.node_logs[display_name] += f"Args list: {args_list}\n"

                args = parser.parse_args(args_list)

                # Use streaming output for real-time display
                streaming_output = StreamingOutput(terminal_placeholder, 'terminal_content', node_name=display_name)
                
                # Redirect stdout and stderr to our streaming output
                import io
                from contextlib import redirect_stdout, redirect_stderr

                with redirect_stdout(streaming_output), redirect_stderr(streaming_output):
                    func(args)

                # The output has already been streamed, so we don't need to add it again
                st.session_state.node_logs[display_name] += f"✅ Completed\n"
                
                # Add completion to global log
                st.session_state.terminal_content += f"✅ {display_name} completed\n"

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}\n"
                st.session_state.terminal_content += error_msg
                st.session_state.node_logs[display_name] += error_msg

        # Final completion message
        st.session_state.terminal_content += f"\n🎉 Graph execution completed!\n"

        # Reset node log selector to Global Log after execution
        st.session_state.selected_node_log = "📋 Global Log"

        st.success("Graph execution completed!")

if __name__ == "__main__":
    main()