#!/usr/bin/env python3
"""
SASS/SCSS to CSS Converter
Convert SASS/SCSS files to CSS without using argparse - pure sys implementation
"""

import os
import sys
import glob
from pathlib import Path
import sass

class SassConverter:
    def __init__(self):
        self.supported_extensions = ['.sass', '.scss']
    
    def compile_file(self, input_path, output_path=None, output_style='nested', 
                    source_map=False, include_paths=None, precision=5):
        """
        Compile single SASS/SCSS file to CSS
        
        Args:
            input_path (str): Path to input file
            output_path (str): Path to output file (optional)
            output_style (str): CSS output style ('nested', 'expanded', 'compact', 'compressed')
            source_map (bool): Generate source map
            include_paths (list): List of paths for @import
            precision (int): Decimal precision
        """
        try:
            input_path = Path(input_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"File not found: {input_path}")
            
            if input_path.suffix not in self.supported_extensions:
                raise ValueError(f"Unsupported extension: {input_path.suffix}")
            
            # Determine output path if not provided
            if output_path is None:
                output_path = input_path.with_suffix('.css')
            else:
                output_path = Path(output_path)
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup include paths
            if include_paths is None:
                include_paths = [str(input_path.parent)]
            
            # Compile SASS/SCSS
            result = sass.compile(
                filename=str(input_path),
                output_style=output_style,
                source_map_filename=str(output_path.with_suffix('.css.map')) if source_map else None,
                include_paths=include_paths,
                precision=precision
            )
            
            # Write result to file
            if isinstance(result, tuple):  # Has source map
                css_content, source_map_content = result
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                if source_map:
                    map_path = output_path.with_suffix('.css.map')
                    with open(map_path, 'w', encoding='utf-8') as f:
                        f.write(source_map_content)
                    print(f"Source map: {map_path}")
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
            
            print(f"Success: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def compile_directory(self, input_dir, output_dir=None, recursive=True, **kwargs):
        """
        Compile all SASS/SCSS files in directory
        
        Args:
            input_dir (str): Input directory
            output_dir (str): Output directory
            recursive (bool): Scan subdirectories
            **kwargs: Parameters for compile_file
        """
        input_dir = Path(input_dir)
        
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {input_dir}")
        
        if output_dir is None:
            output_dir = input_dir
        else:
            output_dir = Path(output_dir)
        
        # Find all SASS/SCSS files
        pattern = "**/*" if recursive else "*"
        files = []
        for ext in self.supported_extensions:
            files.extend(input_dir.glob(f"{pattern}{ext}"))
        
        if not files:
            print(f"No SASS/SCSS files found in: {input_dir}")
            return False
        
        success_count = 0
        for file_path in files:
            # Skip partial files (starting with underscore)
            if file_path.name.startswith('_'):
                continue
            
            # Determine output path
            relative_path = file_path.relative_to(input_dir)
            output_path = output_dir / relative_path.with_suffix('.css')
            
            if self.compile_file(str(file_path), str(output_path), **kwargs):
                success_count += 1
        
        print(f"\nCompleted: {success_count}/{len(files)} files compiled successfully")
        return success_count > 0
    
    def watch_directory(self, input_dir, output_dir=None, **kwargs):
        """
        Watch directory for file changes (requires watchdog)
        """
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            import time
            
            class SassHandler(FileSystemEventHandler):
                def __init__(self, converter, input_dir, output_dir, **compile_kwargs):
                    self.converter = converter
                    self.input_dir = Path(input_dir)
                    self.output_dir = Path(output_dir) if output_dir else self.input_dir
                    self.compile_kwargs = compile_kwargs
                
                def on_modified(self, event):
                    if event.is_directory:
                        return
                    
                    file_path = Path(event.src_path)
                    if file_path.suffix in self.converter.supported_extensions:
                        print(f"Detected change: {file_path}")
                        
                        if file_path.name.startswith('_'):
                            # Partial file changed, compile all main files
                            self.converter.compile_directory(
                                str(self.input_dir), 
                                str(self.output_dir),
                                **self.compile_kwargs
                            )
                        else:
                            # Main file changed
                            relative_path = file_path.relative_to(self.input_dir)
                            output_path = self.output_dir / relative_path.with_suffix('.css')
                            self.converter.compile_file(
                                str(file_path), 
                                str(output_path),
                                **self.compile_kwargs
                            )
            
            handler = SassHandler(self, input_dir, output_dir, **kwargs)
            observer = Observer()
            observer.schedule(handler, str(input_dir), recursive=True)
            observer.start()
            
            print(f"Watching directory: {input_dir}")
            print("Press Ctrl+C to stop...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                print("\nStopped watching.")
            
            observer.join()
            
        except ImportError:
            print("Error: 'watchdog' package required for watch mode")
            print("Install with: pip install watchdog")
            return False

class ArgumentParser:
    """Simple argument parser without argparse"""
    
    def __init__(self):
        self.args = {}
        self.flags = set()
        self.help_requested = False
        
    def parse_args(self, args=None):
        """Parse command line arguments"""
        if args is None:
            args = sys.argv[1:]
        
        # Initialize default values
        self.args = {
            'input': None,
            'directory': None,
            'glob': None,
            'output': None,
            'style': 'nested',
            'source_map': False,
            'include_paths': [],
            'precision': 5,
            'recursive': False,
            'watch': False,
            'verbose': False
        }
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # Help flags
            if arg in ['-h', '--help']:
                self.help_requested = True
                return self.args
            
            # Input options
            elif arg in ['-i', '--input']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['input'] = args[i + 1]
                i += 1
            
            elif arg in ['-d', '--directory']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['directory'] = args[i + 1]
                i += 1
            
            elif arg == '--glob':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['glob'] = args[i + 1]
                i += 1
            
            # Output options
            elif arg in ['-o', '--output']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['output'] = args[i + 1]
                i += 1
            
            # Style options
            elif arg in ['-s', '--style']:
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                style = args[i + 1]
                if style not in ['nested', 'expanded', 'compact', 'compressed']:
                    raise ValueError(f"Invalid style: {style}. Must be one of: nested, expanded, compact, compressed")
                self.args['style'] = style
                i += 1
            
            # Boolean flags
            elif arg == '--source-map':
                self.args['source_map'] = True
            
            elif arg == '--recursive':
                self.args['recursive'] = True
            
            elif arg == '--watch':
                self.args['watch'] = True
            
            elif arg in ['-v', '--verbose']:
                self.args['verbose'] = True
            
            # Include path (can be used multiple times)
            elif arg == '--include-path':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                self.args['include_paths'].append(args[i + 1])
                i += 1
            
            # Precision
            elif arg == '--precision':
                if i + 1 >= len(args):
                    raise ValueError(f"Argument {arg} requires a value")
                try:
                    self.args['precision'] = int(args[i + 1])
                except ValueError:
                    raise ValueError(f"Precision must be an integer, got: {args[i + 1]}")
                i += 1
            
            else:
                raise ValueError(f"Unknown argument: {arg}")
            
            i += 1
        
        # Validate input options (mutually exclusive)
        input_count = sum(1 for x in [self.args['input'], self.args['directory'], self.args['glob']] if x is not None)
        if input_count == 0:
            raise ValueError("One input method required: -i/--input, -d/--directory, or --glob")
        elif input_count > 1:
            raise ValueError("Only one input method allowed: -i/--input, -d/--directory, or --glob")
        
        return self.args
    
    def print_help(self):
        """Print help message"""
        help_text = """
SASS/SCSS to CSS Converter - Convert SASS/SCSS files to CSS using Python and libsass

INPUT OPTIONS (choose one):
    -i, --input [FILE_INPUT]              Specify input SASS/SCSS file path
    -d, --directory [DIR_PATH]            Specify input directory containing SASS/SCSS files
    --glob [PATTERN]                      Use glob pattern to match multiple files (e.g., "./src/**/*.scss")

OUTPUT OPTIONS:
    -o, --output [PATH]                   Specify output path (can be file path or directory path)

COMPILATION OPTIONS:
    -s, --style [STYLE]                   Set CSS output formatting style:
            nested (default, indented like SASS)
            expanded (readable with separate lines)
            compact (one line per CSS rule)
            compressed (minified for production)
            
    --source-map                          Generate source map files (.css.map) for debugging
    --include-path [PATH]                 Add directory path for @import resolution (can be used multiple times)
    --precision [NUMBER]                  Set decimal precision for numeric values in CSS output (default: 5)

PROCESSING OPTIONS:
    --recursive                           Enable recursive scanning of subdirectories when processing directories
    --watch                               Enable watch mode for automatic recompilation on file changes (requires watchdog)
    -v, --verbose                         Enable verbose output with detailed information and error traces

OTHER OPTIONS:
    -h, --help                            Show this help message and exit

EXAMPLES:

    rf-css sass-convert -i style.scss -o style.css                           # Single file conversion
    
    rf-css sass-convert -i style.scss -o style.css -s compressed            # Single file with compressed output
    
    rf-css sass-convert -i style.scss -o style.css --source-map          # Single file with source map generation
    
    rf-css sass-convert -d ./sass -o ./css                                   # Process entire directory
    
    rf-css sass-convert -d ./sass -o ./css --recursive                       # Directory with recursive subdirectory scanning
    
    rf-css sass-convert -d ./sass -o ./css --watch                           # Watch mode for automatic recompilation (requires watchdog)
    
    rf-css sass-convert -i main.scss -o main.css --include-path ./vendors --include-path ./mixins              # With custom include paths for @import statements
    
    rf-css sass-convert --glob "./src/**/*.scss" -o ./dist                # Batch processing with glob patterns

OUTPUT STYLES:

    nested (default):
        .navbar {
          background: #333; }
          .navbar .nav-item {
            color: white; }

    expanded:
        .navbar {
          background: #333;
        }

        .navbar .nav-item {
          color: white;
        }

    compact:
        .navbar { background: #333; }
        .navbar .nav-item { color: white; }

    compressed:
        .navbar{background:#333}.navbar .nav-item{color:white}

        """
        print(help_text.strip())