# ReactFlow CSS

ReactFlow CSS is a Python package that simplifies the integration of popular CSS frameworks like Tailwind CSS and Bootstrap into your ReactPy applications and other HTML projects. It provides a streamlined API for configuring, compiling, and serving CSS, making it easier to manage your styling directly from Python.

## Features

- **Tailwind CSS Integration**: Configure and compile Tailwind CSS seamlessly within your Python project
- **Bootstrap Integration**: Include Bootstrap CSS and JavaScript with minimal setup
- **ReactPy Compatibility**: Designed specifically for ReactPy components and workflows
- **Unified API**: A `Helper` class to manage both frameworks through a single interface
- **Template Management**: Built-in templates and default styles for rapid development

## Installation

Install ReactFlow CSS using pip:

```bash
pip install ReactFlow-CSS
```

## Quick Start

### Basic Configuration

First, create configurations for your preferred CSS framework:

```python
# For Tailwind CSS
from reactflow_css.tailwindcss import configure_tailwind
config_tailwind = configure_tailwind(__file__)

# For Bootstrap
from reactflow_css.bootstrap import configure_boots
config_boots = configure_boots(__file__)
```

### Getting Default Templates

Generate default CSS templates quickly:

```python
# Get default Tailwind CSS template
from reactflow_css.tailwindcss import default_tailwind
tailwind_css = default_tailwind(path_output="./styles/tailwind.css")

# Get default Bootstrap template
from reactflow_css.bootstrap import default_boots
bootstrap_css = default_boots(path_output="./styles/bootstrap.css")
```

**Parameters:**
- `path_output` (str, optional): File path to save the generated CSS content. If `None`, returns content as string only.

## Tailwind CSS Integration

### Step 1: Configure Tailwind

Set up your Tailwind configuration:

```python
from reactflow_css.tailwindcss import configure_tailwind

config_tailwind = configure_tailwind(__file__)

# Define Tailwind configuration
tailwind_config = {
    "content": ["./src/**/*.{js,ts,jsx,tsx,py}", "./templates/**/*.html"],
    "theme": {
        "extend": {
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#64748b"
            }
        }
    },
    "plugins": []
}

# Apply configuration
config_tailwind.config(tailwind_config)
```

### Step 2: Setup Templates

Generate the necessary Tailwind files:

```python
# Create tailwind.config.js and input.css files
config_tailwind.render_templates(
    path_config="./tailwind.config.js",
    path_index="./input.css"
)

# Or use default templates
config_tailwind.default_templates(path_output="./styles/")
```

### Step 3: Compile CSS

Compile your Tailwind CSS:

```python
# Compile with file paths
compiled_css = config_tailwind.compile(
    path_config="./tailwind.config.js",
    path_index="./input.css",
    path_output="./dist/styles.css"
)

# Or compile with inline styles
compiled_css = config_tailwind.compile(
    index="@tailwind base; @tailwind components; @tailwind utilities;",
    path_output="./dist/styles.css"
)
```

**Parameters:**
- `path_config` (str, optional): Path to tailwind.config.js file
- `path_index` (str, optional): Path to input CSS file
- `path_output` (str): Output path for compiled CSS (default: "output.css")
- `index` (str, optional): Inline CSS content instead of file
- `*args`: Additional flags for Tailwind CLI

## Bootstrap Integration

### Step 1: Setup Templates

Initialize Bootstrap templates:

```python
from reactflow_css.bootstrap import configure_boots

config_boots = configure_boots(__file__)

# Render templates from existing files
template_content = config_boots.render_templates(path_index="./styles/custom.css")
```

### Step 2: Configure Styles

Add custom styles and imports:

```python
# Configure with custom styles and imports
custom_css = """
.custom-button {
    background-color: #007bff;
    border: none;
    padding: 12px 24px;
    border-radius: 4px;
}
"""

bootstrap_css = config_boots.config(
    style=custom_css,
    path_output="./dist/bootstrap-custom.css",
    '@import "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css";',
    '@import "./additional-styles.css";',
    '@import "--/css/bootstrap.min.css";'
)
```

if you use this format `@import '--/...' ` (better use `--/css/` is the module css styling from main folder of this pkg) then it will import the css module from the main folder of this pkg

### Step 3: Use in ReactPy Components

Convert CSS imports to HTML link elements:

```python
from reactpy import html, component
from reactflow_css.bootstrap import convert_imports_to_link

@component
def App():
    return html.div(
        convert_imports_to_link(style=bootstrap_css),
        html.h1("Hello, Bootstrap!", className="text-primary"),
        html.button("Click me!", className="btn btn-primary custom-button")
    )
```

## API Reference

### Main Package (`reactflow_css`)

The main package provides convenient aliases for common functions:

- `configure_boots`: Alias for `bootstrap.Configuration.configure`
- `configure_tailwind`: Alias for `tailwindcss.Configuration.configure`
- `default_boots`: Alias for `bootstrap.Configuration.default_css`
- `default_tailwind`: Alias for `tailwindcss.Configuration.default_css`
- `convert_imports_to_link`: Alias for `bootstrap.generate.Convert_style`

### Tailwind CSS Module (`reactflow_css.tailwindcss`)

#### Class: `configure`

Main class for handling Tailwind CSS configuration and compilation.

##### `__init__(self, __path__)`
- **Parameters**: `__path__` - Path to the main script for resolving relative paths
- **Purpose**: Initializes the configure class

##### `config(self, config_dict: Dict[str, Any] = None, **kwargs) -> str`
- **Parameters**: 
  - `config_dict` - Dictionary containing Tailwind CSS configuration
  - `**kwargs` - Additional configuration as keyword arguments
- **Returns**: String representation of tailwind.config.js content
- **Purpose**: Generates Tailwind configuration content

##### `render_templates(self, path_config: str = None, path_index: str = None) -> None`
- **Parameters**:
  - `path_config` - Path to tailwind.config.js (default: "./tailwind.config.js")
  - `path_index` - Path to input CSS file (default: "./input.css")
- **Purpose**: Loads Tailwind configuration and input CSS from files

##### `default_templates(self, path_output: str = None) -> str`
- **Parameters**: `path_output` - Optional path to write default CSS content
- **Returns**: Default CSS content as string
- **Purpose**: Returns default Tailwind CSS template

##### `compile(self, path_config: str = None, path_index: str = None, path_output: str = "output.css", index: str = None, *args) -> str`
- **Parameters**:
  - `path_config` - Path to tailwind.config.js file
  - `path_index` - Path to input CSS file
  - `path_output` - Output path for compiled CSS
  - `index` - Optional inline CSS content
  - `*args` - Additional Tailwind CLI arguments
- **Returns**: Generated CSS content as string
- **Purpose**: Compiles Tailwind CSS

#### Function: `default_css(path_output: str = None) -> str`
- **Parameters**: `path_output` - Optional path to write default CSS content
- **Returns**: Default Tailwind CSS content
- **Purpose**: Returns default CSS from package's output.css file

#### Exceptions

- `TailwindError(Exception)`: Base exception for Tailwind-related errors
- `ModuleNotFound(TailwindError, ImportError)`: Required module not found
- `ProcessError(TailwindError, RuntimeError)`: Process execution errors
- `ConfigurationError(TailwindError)`: Invalid Tailwind configuration
- `FileNotFoundError(TailwindError)`: Specified file not found
- `CompilationError(TailwindError)`: CSS compilation errors
- `ValidationError(TailwindError)`: Validation failures

### Bootstrap Module (`reactflow_css.bootstrap`)

#### Class: `configure`

Main class for handling Bootstrap configuration.

##### `__init__(self, __path__)`
- **Parameters**: `__path__` - Path to main script for resolving relative paths
- **Purpose**: Initializes the configure class

##### `render_templates(self, path_input: str) -> str`
- **Parameters**: `path_input` - Path to input file
- **Returns**: Content of rendered template
- **Purpose**: Renders templates from given input path

##### `config(self, style: str = "", output: str = None, *args) -> str`
- **Parameters**:
  - `style` - CSS content string
  - `output` - Optional path to write configured CSS
  - `*args` - Additional import statements
- **Returns**: Final CSS content including imports
- **Purpose**: Configures Bootstrap styles with imports

#### Function: `default_css(path_output: str = None) -> str`
- **Parameters**: `path_output` - Optional path to write default CSS content
- **Returns**: Default Bootstrap CSS content
- **Purpose**: Returns default Bootstrap CSS from bootstrap.min.css

#### Component: `Convert_style(style: str)`
- **Parameters**: `style` - CSS string containing @import statements
- **Returns**: List of ReactPy html.link elements
- **Purpose**: Converts CSS @import rules to HTML link elements

#### Exceptions

- `BootsTrapError(Exception)`: Base exception for Bootstrap-related errors
- `ModuleNotFound(BootsTrapError, ImportError)`: Required module not found
- `ProcessError(BootsTrapError, RuntimeError)`: Process execution errors
- `ConfigurationError(BootsTrapError)`: Configuration errors
- `FileNotFoundError(BootsTrapError)`: Specified file not found
- `CompilationError(BootsTrapError)`: CSS compilation errors
- `ValidationError(BootsTrapError)`: Validation errors

## Advanced Usage Examples

### Custom Tailwind Configuration

```python
from reactflow_css.tailwindcss import configure_tailwind

config_tailwind = configure_tailwind(__file__)

# Advanced Tailwind configuration
advanced_config = {
    "content": ["./src/**/*.{js,ts,jsx,tsx,py}"],
    "theme": {
        "extend": {
            "fontFamily": {
                "sans": ["Inter", "sans-serif"]
            },
            "spacing": {
                "18": "4.5rem",
                "88": "22rem"
            }
        }
    },
    "plugins": ["@tailwindcss/forms", "@tailwindcss/typography"]
}

config_tailwind.config(advanced_config)
config_tailwind.render_templates()

# Compile with additional flags
compiled_css = config_tailwind.compile(
    "--minify",
    "--watch",
    path_output="./dist/tailwind.min.css"
)
```

### Bootstrap with Custom Imports

```python
from reactflow_css.bootstrap import configure_boots
from reactpy import html, component

config_boots = configure_boots(__file__)

# Configure with multiple imports
custom_bootstrap = config_boots.config(
    style="""
    .navbar-custom {
        background-color: #2c3e50;
    }
    .btn-custom {
        background-color: #e74c3c;
        border-color: #c0392b;
    }
    """,
    path_output="./dist/custom-bootstrap.css",
    '@import "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css";',
    '@import "https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap";'
)

@component
def CustomApp():
    return html.div(
        convert_imports_to_link(style=custom_bootstrap),
        html.nav(
            html.div(
                html.a("My App", href="#", className="navbar-brand"),
                className="container"
            ),
            className="navbar navbar-expand-lg navbar-custom"
        ),
        html.div(
            html.button("Custom Button", className="btn btn-custom"),
            className="container mt-4"
        )
    )
```

## Best Practices

1. **File Organization**: Keep your CSS files organized in a dedicated `styles/` or `assets/` directory
2. **Configuration Management**: Store Tailwind configurations in separate files for complex projects
3. **Performance**: Use minification flags for production builds
4. **Caching**: Cache compiled CSS to avoid unnecessary recompilation
5. **Error Handling**: Always wrap compilation calls in try-catch blocks

## Troubleshooting

### Common Issues

1. **Module Not Found**: Ensure all required dependencies are installed
2. **Compilation Errors**: Check your Tailwind configuration syntax
3. **File Not Found**: Verify file paths are correct and files exist
4. **Process Errors**: Ensure Node.js and npm are properly installed for Tailwind

### Debug Mode

Enable debug mode for detailed error information:

```python
try:
    compiled_css = config_tailwind.compile(
        path_config="./tailwind.config.js",
        path_index="./input.css",
        "--verbose"
    )
except Exception as e:
    print(f"Compilation failed: {e}")
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation for common solutions
- Review the API reference for detailed usage information