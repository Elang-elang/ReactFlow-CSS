from setuptools import setup, find_packages

# Read the contents of your README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ReactFlow-CSS",
    version="1.9.0",  # Major version bump to indicate stable release
    author="Elang Muhammad",
    author_email="elangmuhammad888@gmail.com",
    description="A comprehensive Python package for seamless integration of CSS frameworks (Tailwind CSS, Bootstrap) with ReactPy applications and HTML projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Elang-elang/tailwind-py",
    project_urls={
        "Bug Tracker": "https://github.com/Elang-elang/tailwind-py/issues",
        "Documentation": "https://github.com/Elang-elang/tailwind-py#readme",
        "Source Code": "https://github.com/Elang-elang/tailwind-py",
    },
    packages=find_packages(),
    classifiers=[
        # Development Status - Changed from Beta to Production/Stable
        "Development Status :: 5 - Production/Stable",
        
        # Programming Language Support
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: JavaScript",
        
        # License Information
        "License :: OSI Approved :: MIT License",
        
        # Operating System Compatibility
        "Operating System :: OS Independent",
        
        # Topic Classifications
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Software Development :: User Interfaces",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        
        # Environment
        "Environment :: Web Environment",
        "Environment :: Console",
        
        # Framework Classification
        "Framework :: Django",
        "Framework :: Flask",
        
        # Development Mode
        "Development Status :: 4 - Beta"
    ],
    python_requires=">=3.8",
    keywords=[
        "tailwind", "tailwindcss", "css", "styling", "reactpy", 
        "bootstrap", "web-development", "frontend", "ui", "css-framework",
        "python-css", "reactflow", "material-icons", "google-icons",
        "css-compiler", "web-components", "responsive-design"
    ],
    
    # Dependencies - Fixed syntax and added install_requires
    install_requires=[
        "reactpy==1.1.0",
    ],
    
    # Optional dependencies for enhanced features
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    
    # Package data inclusion
    include_package_data=True,
    package_data={
        'reactflow_css': [
            # Icon files - Fixed syntax with proper comma separation
            'icons/icons/filled/*',
            'icons/icons/outlined/*',
            'icons/icons/round/*',
            'icons/icons/sharp/*',
            'icons/icons/two-tone/*',
            'icons/icons/**/*',
            'icons/icons/*',
            'icons/**/*',
            'icons/*',
            
            # Module files - Fixed syntax
            'modules/tailwindcss/*',
            'modules/bootstrap/css/*',
            'modules/bootstrap/js/*',
            'modules/bootstrap/**/*',
            'modules/bootstrap/*',
            'modules/**/*',
            'modules/*',
            
            # Root package files
            '**/*',
            '*',
        ],
    },
    
    # Entry points for command-line interfaces (if needed)
    entry_points={
        'console_scripts': [
            # Add console scripts here if your package provides CLI tools
            # 'reactflow-css=reactflow_css.cli:main',
        ],
    },
    
    # ZIP safety
    zip_safe=False,
)
