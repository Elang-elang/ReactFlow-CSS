<p align="center">
    <img
    src="https://raw.githubusercontent.com/reactive-python/reactpy/main/branding/svg/reactpy-logo-square.svg"
    alt="ReactPy Icon"
    >
</p>

<h1 align="center">ReactFlow CSS (Py)</h1>

<p align="center">
    <a
    href="https://pypi.org/project/reactflow-css"
    >
        <img
        src="https://img.shields.io/pypi/v/reactflow-css.svg?label=PyPI"
        alt="PyPI Version"
        >
    </a>
    <a
    href="https://github.com/Elang-elang/ReactFlow-CSS?tab=License-1-ov-file"
    >
        <img
        src="https://img.shields.io/badge/license-MIT-blue.svg"
        alt="LICENSE MIT"
        >
    </a>
</p>

<hr></hr>

# Introduction

ReactFlow CSS is a Python package that simplifies the integration of popular CSS frameworks like Tailwind CSS and Bootstrap into your ReactPy applications and other HTML projects. It provides a streamlined API for configuring, compiling, and serving CSS, making it easier to manage your styles directly from Python.

## Features

- **Tailwind CSS Integration**: Configure and compile Tailwind CSS seamlessly within your Python projects.
- **Bootstrap Integration**: Include Bootstrap CSS and JavaScript with minimal setup.
- **Google SVG Icons**: Access and generate SVG icons from Google Material Icons directly in your projects.
- **ReactPy Compatibility**: Specifically designed for ReactPy components and workflows.
- **Unified API**: `Helper` class for managing multiple frameworks through a single interface.
- **Template Management**: Built-in templates and default styles for rapid development.
- **CLI Comment**: For `Setup and Build` your projects
- **SASS Converter**: Convert `SASS/SCSS` with cli complex
## Installation

Install ReactFlow CSS using pip:

```bash
pip install ReactFlow-CSS
```

## CLI Usage

Run the following command:

```bash
rf-css [command] [flags] [args]
```
The CLI simplifies the development process.

### Usage Examples:

```bash
rf-css tailwindcss init -default ./output.css
```
Creates default Tailwind CSS styles and output drop in output.css.

### Getting Help

```bash
rf-css --help
```

For more information, run the above command.

## Quick Start

### Basic Configuration

First, create a configuration for your preferred CSS framework:

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
- `path_output` (str, optional): File path to save the generated CSS content. If `None`, return content as string only.

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

### Step 2: Set Up Templates

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

## Bootstrap Integration

### Step 1: Set Up Templates

Initialize Bootstrap templates:

```python
from reactflow_css.bootstrap import configure_boots

config_boots = configure_boots(__file__)

# Render template from existing file
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
If you use this format `@import '--/...'` then it will import the css module from the main folder of this package.

## Google Icons Integration

Generate SVG icons from Google Material Icons:

```python
from reactflow_css.icons import generate_icons

# Generate single icon
icon_svg = generate_icons("home")
print(icon_svg)

# Generate multiple icons
icons = generate_icons("home", "settings", "account_circle")
for name, svg in icons.items():
    with open(f"./icons/{name}.svg", "w") as f:
        f.write(svg)
```

## API Reference

See the source documentation for complete API reference for each module:
- `reactflow_css.tailwindcss`
- `reactflow_css.bootstrap`
- `reactflow_css.icons`

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/Elang-elang/ReactFlow-CSS?tab=License-1-ov-file) file for details. The included Google icons are licensed under the Apache 2.0 License.
