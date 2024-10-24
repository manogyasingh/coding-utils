import json
import sys

def convert_ipynb_to_py(ipynb_path, py_path=None):
    """
    Convert a Jupyter notebook (.ipynb) file to a Python (.py) file.
    
    Args:
        ipynb_path (str): Path to input .ipynb file
        py_path (str, optional): Path to output .py file. If None, uses the same name with .py extension
    """
    # Generate output path if not provided
    if py_path is None:
        py_path = ipynb_path.rsplit('.', 1)[0] + '.py'
    
    try:
        # Read the notebook file
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Open the output file
        with open(py_path, 'w', encoding='utf-8') as f:
            # Write a header comment
            f.write(f"# Converted from {ipynb_path}\n\n")
            
            # Process each cell
            for cell in notebook['cells']:
                # Only process code cells
                if cell['cell_type'] == 'code':
                    # Get the source code
                    source = cell['source']
                    
                    # Handle both string and list source formats
                    if isinstance(source, list):
                        source = ''.join(source)
                    
                    # Write the code with a newline after each cell
                    f.write(source)
                    f.write('\n\n')
                
                # Optionally include markdown cells as comments
                elif cell['cell_type'] == 'markdown':
                    source = cell['source']
                    if isinstance(source, list):
                        source = ''.join(source)
                    
                    # Convert markdown to comments
                    commented = '\n'.join(f"# {line}" if line.strip() else "#"
                                        for line in source.split('\n'))
                    f.write(commented)
                    f.write('\n\n')
        
        print(f"Successfully converted {ipynb_path} to {py_path}")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {ipynb_path}")
    except json.JSONDecodeError:
        print(f"Error: {ipynb_path} is not a valid Jupyter notebook file")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py input.ipynb [output.py]")
        sys.exit(1)
    
    ipynb_path = sys.argv[1]
    py_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_ipynb_to_py(ipynb_path, py_path)
