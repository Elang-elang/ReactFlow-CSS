from setuptools import setup, find_packages

setup(
    name="ReactFlow-CSS",
    version="1.0.8",
    author="Elang Muhammad",
    author_email="elangmuhammad888@gmail.com",
    description="This is pkg to load styling (tailwindcss and bootstrap) for reactpy, backend reactpy or other html files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Elang-elang/tailwind-py",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: JavaScript",
       "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    keywords=["tailwind", "tailwindcss", "style", "reactpy", "tailwind-py", "bootstrap", "bootstrap-py", "reactflow", "css", "reactflow-css", "reactflow_css"],
    dependencies=["reactpy"],
    include_package_data=True,
    package_data={
        'reactflow_css': [
            'reactflow_css/icons/icons/filled/*',
            'reactflow_css/icons/icons/outlined/*',
            'reactflow_css/icons/icons/round/*',
            'reactflow_css/icons/icons/sharp/*',
            'reactflow_css/icons/icons/two-tone/*',
            'reactflow_css/icons/icons/**/*',
            'reactflow_css/icons/icons/*',
            'reactflow_css/icons/**/*',
            'reactflow_css/icons/*',
            'reactflow_css/modules/tailwindcss/*'
            'reactflow_css/modules/bootstrap/css/*'
            'reactflow_css/modules/bootstrap/js/*'
            'reactflow_css/modules/bootstrap/**/*'
            'reactflow_css/modules/bootstrap/*'
            'reactflow_css/modules/**/*',
            'reactflow_css/modules/*'
            'reactflow_css/**/*',
            'reactflow_css/*',
            ],
    },
)
