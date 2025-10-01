from setuptools import setup
from setuptools import find_packages

def read_requirements():
    with open('requirements.txt', 'r') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

setup(name='ai_toolkits',
      version='0.0.1',
      description='AI toolkits for LLM integrations and structured data extraction',
      author='The fastest man alive.',
      packages=find_packages(),
      install_requires=read_requirements())