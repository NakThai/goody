"""Setup script for installing the application."""
from setuptools import setup, find_packages

setup(
    name="bot_manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'playwright>=1.39.0',
        'customtkinter>=5.2.0',
        'pillow>=10.0.0',
        'pyinstaller>=6.1.0',
        'python-dotenv>=1.0.0',
        'questionary>=2.0.1'
    ],
    entry_points={
        'console_scripts': [
            'bot_manager=src.main:main',
        ],
    },
    package_data={
        'src': ['assets/*', 'config/*'],
    },
    python_requires='>=3.8',
)