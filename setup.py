from setuptools import find_packages, setup
from os.path import join

from hytest.product import version


CLASSIFIERS = """
Development Status :: 4 - Beta
Intended Audience :: Developers
Topic :: Software Development :: Testing
License :: OSI Approved :: Apache Software License
""".strip().splitlines()

with open('README.md', encoding='utf8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name         = 'hytest',
    version      = version,
    author       = '白月黑羽 - Jiangchunyang',
    author_email = 'jcyrss@gmail.com',
    url          = 'https://github.com/jcyrss/hytest',
    download_url = 'https://pypi.python.org/pypi/hytest',
    license      = 'Apache License 2.0',
    description  = 'A generic automation framework for QA testing',
    long_description = LONG_DESCRIPTION,
    long_description_content_type = 'text/markdown',
    keywords     = 'hytest automation testautomation',
    
    python_requires = '>=3.8',
    
    classifiers  = CLASSIFIERS,
    
    # https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages  
    #   find_packages() 会从setup.py 所在的目录下面寻找所有 认为有效的python  package目录
    #   然后拷贝加入所有相关的 python 模块文件，但是不包括其他类型的文件
    # packages     = find_packages(),
    packages     = find_packages(
        include = ['hytest','hytest.*']
    ),
    
    # 参考  https://godatadriven.com/blog/a-practical-guide-to-using-setup-py/
    # https://docs.python.org/3/distutils/setupscript.html#installing-package-data
    #  其他类型的文件， 必须在 package_data 里面指定 package目录 和文件类型, 
    #  这里 package目录为空，我猜是表示 所有的package 里面包含 .css 和 .js 都要带上
    package_data = {'': ['*.css','*.js']},
    
    
    install_requires=[   
          'rich',
          'dominate',
      ],
    entry_points = {
        'console_scripts': 
            [
                'hytest = hytest.run:run',
            ]
    },

    # options={"bdist_wheel": {"python-tag": 'py3'}}
)