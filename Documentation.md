---
title: hytest Framework
---


## Introduction

`hytest` is suitable for black-box system test automation.

It has the following advantages:

- Very easy to get started

  hytest lets you write test cases directly in Python.

  If you have Python programming experience, you can get started in one hour and use it flexibly within one day.

- Intuitive and easy to understand

  Test cases are stored in a directory/file structure, which is clear and straightforward.

  The `setup and teardown` mechanism is clear and flexible.

  You can flexibly **select** the test cases you want to execute.

- Beautiful test reports


## Installation and Execution

Installing hytest is very simple. Run the following command:

```
pip install hytest 
```

Note: hytest requires Python 3.9 or later.

Before running hytest automation, create a new `project directory`, and then create a subdirectory named `cases` inside it to store test case code.

Running hytest automated tests is very simple. You only need to:

- Open a command-line window.

- Go to the root directory of the automation code, that is, the `parent directory of cases`.

- Run hytest.

The command `hytest` is actually equivalent to running the following command:

```
python -m hytest
```

If you are using macOS, you can run:

```
python3 -m hytest
```

After execution, the command-line window displays the result of each test case.

Running the automation will generate a `log` directory. It contains detailed `test logs` and a `test report`.

The `test log` is a txt file.

The `test report` is in HTML format and will be automatically opened in the browser. Through the floating menu in the upper-right corner, you can:

- Switch between compact and detailed modes.

  This makes it easier to browse the content.

- Jump to the next or previous error.

  This makes it easier to quickly locate the problem when an issue occurs.

By default, the language of the test report uses the operating system language. If you want to specify it explicitly, add the `--lang` parameter.

For example:

```py
hytest  --lang=en

or

python -m hytest  --lang=en
```

If you do not want the test report to open automatically after the test finishes, you can use the `--auto_open_report=no` parameter, as shown below:

```py
hytest --auto_open_report=no
```

The usage of hytest command-line parameters will be explained in detail later. If you forget a command parameter in the future, you can run `hytest -h` to view the parameter description.

When building real project automation later, you usually need to create some other directories, such as:

- `lib` directory

  Used to store shared code libraries needed by test cases.

- `doc` directory

  Used to store documentation.

You can use the command-line parameter `--new` to create a hytest automation project directory. It will contain a `cases` directory and a sample code file.

For example, running:

```py
hytest --new auto1
```

will create a project directory named `auto1` under the current directory.


## Test Case Directory Structure

First, let us understand the structure of the test case directory.

- A hytest `automated test case` is a Python class written in a Python file.

  It corresponds to a test case in a test case document.

- One code file can contain multiple test cases.

- Multiple code files can be organized using directories.

Every `directory` and `py` file under the `cases` directory is called a `test suite`.

A `test suite` is a `collection of test cases`. In simple terms, it is `a group of test cases`.

For easier management, we group functionally related test cases together into a test suite.

- A Python file that contains `test case classes` is called a `suite file`.

- A directory that contains suite files is called a `test suite directory`.


## Defining Test Case Classes

The test case file format is as follows:

Each class in the file corresponds to one test case.

- The class attribute `name` specifies the test case name.

  If there is no `name` attribute, the class name will be used as the test case name.

- The class method `teststeps` corresponds to the test step code.

  Test step code is the program that executes the test case step by step automatically.

  Therefore, a class **must have a teststeps method** before hytest treats it as a test case class.

For example:

```py
# Recommendation: use the test case ID as the class name
class UI_0101:
    # Test case name. It is also recommended to end with the test case ID,
    # so it can correspond to the test case document
    # and make it easier to select by test case name later.
    name = 'Admin Home Page - UI-0101'

    # Test case steps
    def teststeps(self):
```

To make the execution process shown in our test logs and reports clearer, we can call some hytest library functions to output execution steps, informational messages, and checkpoint information.

Add the following code at the beginning of the file to import commonly used functions from the hytest library:

```py
from hytest import STEP, INFO, CHECK_POINT

class UI_0101:
      
    def teststeps(self):
        
        STEP(1, 'Open the browser')
        var1 = 'sdf'
        INFO(f'var1 is {var1}')
        CHECK_POINT('Opened successfully', var1.startswith('1sd') ) 

        
        STEP(2, 'Log in')        
        CHECK_POINT('Check whether login succeeded', True) 
    
        STEP(3, 'View the menu') 
        CHECK_POINT('Check whether the menu is correct', True)  
```

- The STEP function

  Used to declare each test step, making logs and reports clearer.

- The INFO function

  Used to print information in logs and reports, making it easier to locate issues.

  Of course, during development and debugging, you can also use `print` directly and view the output in the terminal.

- The CHECK_POINT function

  Used to declare each checkpoint in the testing process. If any checkpoint fails, the entire test case is considered failed.

  The first parameter is the checkpoint description.

  The second parameter is the checkpoint expression, such as `result["retcode"] == 0`.

  The third parameter indicates whether to continue executing the remaining code in the test case after the checkpoint fails.

  By default, if a checkpoint fails, the remaining test code after `teststeps` in that test case will not continue to execute.

  If you want the subsequent code in `teststeps` to continue even when a checkpoint fails, you can use the parameter `failStop=False`, as shown below:

  ```py   
    def teststeps(self):

        CHECK_POINT('Do not stop even if this fails 1', False, failStop=False)

        CHECK_POINT('Do not stop even if this fails 2', False, failStop=False)
  ```


## An Example

We use the `Baiyue SMS system` as the system under test.

There is now a batch of test cases for this system that need to be automated.

Let us first automate test case `UI-0101`. The test case is described as follows:

```
- Test case category
  
    Administrator login

- Preconditions

    An administrator exists in the system:

    Account: byhy
    Password: 88888888	


- Test steps

    1. Log in to the Baiyue SMS system with the correct administrator account and password.

    2. Check the left-side menu.


- Expected results

    1. Login succeeds.

    2. The first three menu item names are:
    
    Customers
    Medicines
    Orders
```

The corresponding hytest test case reference code is as follows:

```py
from hytest import *
from selenium import webdriver
from selenium.webdriver.common.by import By

class UI_0101:

    # Test case name
    name =  'Check operation menu UI_0101'

    # Test steps
    def teststeps(self):

        STEP(1, 'Log in to the website')

        wd = webdriver.Chrome()
        wd.implicitly_wait(10)

        wd.get('http://127.0.0.1/mgr/sign.html')

        wd.find_element(By.ID, 'username').send_keys('byhy')
        wd.find_element(By.ID, 'password').send_keys('88888888')

        wd.find_element(By.TAG_NAME, 'button').click()

        STEP(2, 'Get left-side menu information')

        eles = wd.find_elements(By.CSS_SELECTOR, '.sidebar-menu li span')

        menuText = [ele.text  for ele in eles]

        INFO(menuText)

        STEP(3, 'Check the menu bar')

        CHECK_POINT('Left-side menu check', menuText[:3] == ['Customers', 'Medicines', 'Orders'])

        wd.quit()
```


## Setup and Teardown

If we analyze carefully, the test case above needs to open a browser and log in.

If there are 100 such test cases, the login operation will be executed 100 times.

The focus of these test cases is actually not login, but the subsequent operations.

The subsequent operations require the same initial environment: an environment where the browser is `opened and logged in`.

Can the execution environment be shared?

That is, when these test cases begin execution, they are already in an environment where the browser has been opened and logged in.

In other words, when our test cases execute, they obtain a WebDriver object that corresponds to a browser already logged in with the administrator account. The later code can then use this WebDriver object directly to perform operations.

How can automated test cases have an `initial environment` where the browser has already been opened and logged in when they execute?

This requires an `initialization` operation, called `setup` in English.

Initialization means building the required data environment for one or more test cases before they execute.

The opposite operation of initialization is `cleanup`, called `teardown` in English.

Initialization creates the environment, and cleanup `restores or destroys` the environment.

Why do we need `cleanup` to restore the environment?

Because after test cases finish executing, they may change the data environment. The changed data environment may affect the execution of other test cases.

Therefore, the principle is:

`Whoever` performs the `initialization` operation and makes `whatever change` to the environment

should perform the corresponding `restoration` in the `cleanup` operation.

hytest supports `three types` of setup/teardown:

- Setup and teardown for a single test case
- Setup and teardown for an entire test case file
- Setup and teardown for an entire test case directory


### Single Test Case

Let us look at the first type:

Setup and teardown for a single test case are implemented by adding `setup` and `teardown` methods to the class corresponding to the test case.

```py
class c0101:
    name = 'Admin Home Page - UI-0101'

    # Setup method
    def setup(self):
        open_browser()
        mgr_login()

    # Teardown method
    def teardown(self):
        wd = GSTORE['wd']
        wd.quit()

    # Test case steps
    def teststeps(self):        
```

When hytest executes a test case:

- It first executes the code inside `setup`.

- Then it executes the code inside `teststeps`.

- Finally, it executes the code inside `teardown`.

In addition:

If `setup` fails, meaning an exception occurs, hytest will not execute the code inside `teststeps` or `teardown`.

If `teststeps` fails, `teardown` will still be executed to ensure the environment is cleaned up.


### Test Case File

Sharp readers must have noticed that the setup and teardown for a **single test case** above do not solve the previously mentioned problem of sharing a data environment among **multiple test cases**.

In this situation, we can use `setup and teardown for the entire test case file`.

That means adding global functions `suite_setup` and `suite_teardown` to the file, as shown below:

```py
from hytest  import *
from lib.webui import  *
from time import sleep

def suite_setup():
    INFO('suite_setup')
    open_browser()
    mgr_login()

def suite_teardown():
    INFO('suite_teardown')
    wd = GSTORE['wd']
    wd.quit()

class c0101:
    # Test case name
    name = 'Admin Home Page - UI-0101'

    def teststeps(self):
    # Test case step code is omitted here    


class c0102:
    name = 'Admin Home Page - UI-0102'

    def teststeps(self):
    # Test case step code is omitted here    

```

If a test case file has both `suite_setup` and `suite_teardown`, and the test cases inside it also have `setup` and `teardown`, the execution order is:

- Execute the test case file's `suite_setup`.

- Execute each test case's `setup`, `teststeps`, and `teardown` in the file.

- Finally, execute the test case file's `suite_teardown`.


### Suite Directory

We have just made it possible for all test cases in a test case file to share setup and teardown operations.

What if the test cases in multiple test case files all need the same setup and teardown operations?

In this situation, we can use `setup and teardown for the entire test case directory`.

How do we set common setup for a directory?

Create a file named `__st__.py` under that directory.

As with suite files, setup and teardown for a suite directory are also implemented by adding global functions `suite_setup` and `suite_teardown` to the file.

If a suite directory has `suite_setup` and `suite_teardown`, the test case files also have `suite_setup` and `suite_teardown`, and the test cases themselves also have `setup` and `teardown`, the execution order is:

- Execute the suite directory's `suite_setup`.

- For each test case file under that directory:

  - Execute the test case file's `suite_setup`.

  - Execute each test case's `setup`, `teststeps`, and `teardown` in the file.

  - Execute the test case file's `suite_teardown`.

- Execute the suite directory's `suite_teardown`.


### Default Setup and Teardown

In addition to using `suite_setup` and `suite_teardown` to set up and clean up an entire suite, a `test case file` also supports another kind of setup and teardown: `default setup and teardown`.

This is done by defining global functions named `test_setup` and `test_teardown`.

If a global function `test_setup` is defined in a test case file, and a test case in that file `does not have its own setup` method, this `test_setup` will be used for initialization when the automation runs.

If a global function `test_teardown` is defined in a test case file, and a test case in that file `does not have its own teardown` method, this `test_teardown` will be used for cleanup when the automation runs.


## Data Association

### Basic Usage

In setup operations, we often create some data that will be used by test cases executed later.

For the `setup` method inside a test case class, this is simple, because the test steps and cleanup method belong to the same class.

When the hytest framework executes, it creates an instance of that class. Therefore, you only need to store the data in instance attributes.

For the setup function of a test case file or suite directory, how can data generated by the `suite_setup` function be used by the test cases inside it?

You can use hytest's built-in object `GSTORE`.

You can assign and retrieve elements using dictionary-style syntax. For example:

```py
from hytest import GSTORE

def suite_setup():
    GSTORE['environment1_product_id'] = createProduct()
    GSTORE['driver'] = webdriver.Chrome()

def suite_teardown():
    deleteProduct(GSTORE['environment1_product_id'])
    GSTORE['driver'].quit()


class c00303:
    name = 'Add Order - API-0303'

    def teststeps(self):
        createOrder(productid=GSTORE['environment1_product_id'])
```

GSTORE also supports assigning and retrieving values through attributes. For example:

```py
def suite_setup():
    GSTORE.productId = createProduct()
    GSTORE.driver = webdriver.Chrome()

def suite_teardown():
    deleteProduct(GSTORE.productId)
    GSTORE.driver.quit()


class c00303:
    name = 'Add Order - API-0303'

    def teststeps(self):
        createOrder(productid=GSTORE.productId)
```

This is simpler to write, but the attribute name must comply with Python variable naming rules. For example, it cannot contain spaces, plus signs, minus signs, and similar characters.


### Dependency Injection

If you think writing `GSTORE.data1` or `GSTORE['data1']` in the code is too cumbersome, you can solve this with **dependency injection**.

Directly pass the object name you need from GSTORE as a parameter to the `teststeps` method or to a `setup/teardown method/function`.

When hytest calls these methods, it checks the parameters and automatically assigns the object with the same name in GSTORE to that parameter.

For example:

```py
def suite_setup():
    GSTORE.productId = createProduct()
    GSTORE.driver = webdriver.Chrome()

# Dependency injection of GSTORE.driver 
def suite_teardown(driver):
    deleteProduct(GSTORE.productId)
    driver.quit()


class c00303:
    name = 'Add Order - API-0303'

    # Dependency injection of GSTORE.productId 
    def teststeps(self, productId):
        createOrder(productid=productId)    
```


## Data-Driven Testing

For example:

A system has a batch of test cases for the login function. Their execution steps are almost the same, but the test parameters are different.

For example:

- Do not enter a username, and enter the correct password.

- Enter a username that is one character shorter at the end than the correct username, and enter the correct password.

- Enter a username that is one character longer at the end than the correct username, and enter the correct password.

- Enter a username that is one character shorter at the beginning than the correct username, and enter the correct password.

- Enter a username that is one character longer at the beginning than the correct username, and enter the correct password.

- Enter the correct username, and do not enter a password.

- Enter the correct username, and enter a password that is one character longer at the end than the correct password.

In this case, you can use hytest's data-driven test case format. You only need to define it as follows:

```py
class c00003x:
    # Each dictionary element in ddt_cases defines the data for one test case.
    # Here, name is the test case name, and para is the test case parameter.
    ddt_cases = [
        {
            'name' : 'Login - 000031',
            'para' : ['user001','888888']
        },
        {
            'name' : 'Login - 000032',
            'para' : ['user0012','888888']
        },
        {
            'name' : 'Login - 000033',
            'para' : ['ser001','888888']
        }
    ]
    
    # When the hytest framework executes, it automatically creates 3 test case instances.
    # When calling teststeps, it sets the parameters of each test case in self.para.
    # Test case code can directly get parameters from self.para.
    def teststeps(self):
        # Get parameters
        username, password = self.para
        
        # The login test code is below
```

In this way, we do not need to define so many test case classes, and the test data can also be stored centrally.

Special note: once you define test cases using data-driven testing, the names of these test cases are no longer the class name, such as `UI_000x` in the code above. Instead, they are the names defined in the driver data, such as `Login UI_0001`, `Login UI_0002`, and `Login UI_0003`.

Therefore, when selecting all the test cases above through command-line parameters during execution, you should use `hytest --test Login*`, not `hytest --test UI_000x`.


### Dynamically Generating Driver Data

hytest driver data is usually fixed data, but of course it can also generate some dynamic data.

For example:

```py
from hytest import *

class UI_000x:

    ddt_cases = []
    for i in range(10):
        ddt_cases.append({
            'name': f'Login UI_000{i+1}',
            'para': [None, f'{i+1}'*8, 'Please enter the username']
        })
 
    def teststeps(self):
        INFO(f'{self.para}')
```

hytest runs in two phases:

- Collecting test cases

  In this phase, hytest searches for all test case classes in the code under the test case directories.

  It instantiates these classes, thereby creating `test case instance objects`.

- Executing test cases

  It executes the `test case instance objects` created in the previous step one by one.

Therefore, in the first step, **collecting and creating test case objects happens before executing test cases**.

Therefore, `ddt_cases` **cannot use data that is generated only at test runtime**.

For example:

```py
from hytest import *
 
# Suite setup
def suite_setup():
    GSTORE['ddt_cases_UI_000x'] = []    
    for i in range(10):
        GSTORE['ddt_cases_UI_000x'].append({
            'name': f'Login UI_000{i+1}',
            'para': [None, f'{i+1}'*8, 'Please enter the username']
        }) 
  
class UI_000x:
    # Want to use GSTORE data set by suite setup? This does not work ❌
    # Because ddt_cases is executed in the collection phase, and suite_setup()
    # has not been executed yet.
    # At this time, GSTORE is still empty, so an error will be reported.
    ddt_cases = GSTORE['ddt_cases_UI_000x']

    def teststeps(self):
        INFO(f'{self.para}')
```


## Selecting Test Cases to Execute - By Name

When executing automated tests, we often do not need to execute `all` test cases.

For example, smoke testing only needs to execute the smoke test cases.

Or when debugging the automation of a test case you wrote, you only need to execute that one test case.

hytest can flexibly select the test cases to execute.

We can use the `--test` or `--suite` command-line parameters to specify which test cases or suites to execute, and wildcard matching is also supported.

```py
--test testA               # Execute the test case named testA
--test testA --test testB  # Execute the test cases named testA and testB
--test test*               # Execute test cases whose names start with test
--suite OrderManagement    # Execute the suite named OrderManagement
```

For example, if we want to test only the `Medicine Management` suite:

```
hytest --suite  MedicineManagement  
```

For example, if we want to test only the `UI - UI-0101` test case:

```
hytest --test  "UI - UI-0101"  
```

Because the test case name contains spaces, it must be enclosed in double quotation marks.

Usually, our test case names include the test case ID at the end, making it very convenient to select test cases by ID.

For example:

```
hytest --test  *0101  
```

This selects and executes the test case named `UI - UI-0101` in our exercise.

Suppose your test leader requires smoke testing, and the selected test case IDs are as follows:

```
UI-0301
UI-0302
UI-0303
UI-1401
UI-1402
```

We can execute them like this:

```
hytest --test *0301  --test *0302 --test *0303 --test *1401 --test *1402
```

Naturally, you may wonder: if there are too many test cases to execute, such as 1,000 test cases, would the command-line parameters become too long?

In this case, we can use a parameter file. Put all parameters in a parameter file. For example, create a parameter file named `args` with the following content:

```
--test *0301
--test *0302
--test *0303
--test *1401
--test *1402
```

One parameter per line.

Then the command only needs to be `hytest -A args`.


## Selecting Test Cases to Execute - By Tag

hytest also provides another way to select test cases: selecting by **tag**.


### Adding Tags to Test Cases

We can add tags to test cases. Then, when running tests, we can specify tags to choose which test cases to run.

A tag is a description of a test case's attributes or characteristics.

A test case can have multiple tags describing its attributes. For example, a login test case can have three tags: login function, smoke test, and UI test.

hytest can choose whether to execute a test case according to the configured tags.

There are several ways to add tags to test cases:

- Global variable `force_tags`

If we define a global variable named `force_tags` in a test case file, in the following format:

```py
force_tags = ['LoginFunction', 'SmokeTest', 'UITest']
```

then all test cases in that file will have these tags.

Tags must be placed in a list, even if there is only one tag.

If `force_tags` is defined in the `__st__.py` file of a **test suite directory**, then **all test cases in that directory** will have the tags specified in `force_tags`.

- The `tags` attribute of a test case class

If we define an attribute named `tags` in a test case class, in the following format:

```py
class c00001:
    name = 'Add Order - 00001'
    # Test case tags, optional   
    tags = ['LoginFunction', 'SmokeTest', 'UITest']
```

then this test case will have these tags.


### Selecting by Tag

When executing automation, we can specify tags through command-line parameters to select test cases to execute.

For example:

```py
# Execute test cases that contain the tag 'SmokeTest'. 
--tag SmokeTest  


# Execute test cases that do not contain the tag 'SmokeTest'.
--tagnot SmokeTest 


# Execute test cases that have both the SmokeTest and UITest tags.
--tag "'SmokeTest' and 'UITest'"


# Execute test cases that have either the SmokeTest or UITest tag.
--tag SmokeTest   --tag UITest


# Execute test cases whose tag matches the pattern A*B, such as A5B, AB, or A444B.
--tag A*B    
```


## Selecting Test Cases to Execute - Specify Directories and Files

If we only want to execute test cases under a certain `test suite directory` or a specific test case file, what should we do?

We can directly specify the path of that directory or file:

```py
hytest cases/order cases/user
```

This executes all test cases in the files under the `cases/order` and `cases/user` directories.

We can also directly specify certain test case files:

```py
hytest cases/a/c/t1.py  cases/a/c/t2.py cases/a/b/t3.py
```

This executes all test cases in the three test case files: `cases/a/c/t1.py`, `cases/a/c/t2.py`, and `cases/a/b/t3.py`.

Of course, directories and files can also be mixed:

```py
hytest cases/a/c/t1.py  cases/f cases/a/b cases/a/c/t2.py
```

If the specified directory or file does not exist, hytest will report an error and exit.

<br>

If a specified directory contains another specified directory or file, the included directory or file will be directly removed from the execution target list.

For example:

```
hytest cases/a cases/a/c/t1.py
```

is equivalent to directly executing:

```
hytest cases/a
```

because the `cases/a` directory already contains the `cases/a/c/t1.py` file.


## Other Features

### Specifying the Test Report Title

Use the `--report_title` parameter to specify the test report title.

For example:

```py
hytest --report_title Regression_Test_Round_2_Report
```

<br>

If the title needs to contain spaces, enclose it in double quotation marks, as shown below:

```py
hytest --report_title "Regression Test Round 2 Report"
```

<br>

Note: this feature was newly added in `hytest v0.8.2`.


### Adding Images to the Report

When using Selenium for web automation or Appium for mobile automation, you can use the `SELENIUM_LOG_SCREEN` function in the hytest library to take screenshots and write them into the test report.

As shown below:

```py
from hytest import *

class c1:
    name = 'web-lesson-0001'

    def teststeps(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://192.168.56.103/sign.html')

        # The first parameter is the webdriver object.
        # The width parameter is optional and specifies the image display width.
        SELENIUM_LOG_SCREEN(driver, width='70%') 
```

<br>

If you want to directly insert an already generated image into the report, you can use the `LOG_IMG` function in the hytest library.

As shown below:

```py
from hytest import *

class c1:
    name = 'web-lesson-0001'

    def teststeps(self):

        # The first parameter is the image path, which can be a web URL.
        LOG_IMG('http://www.byhy.net/xxx.png')
        # It can also be a local path relative to the report file.
        LOG_IMG('imgs/abc.png')
        # The width parameter is optional and specifies the image display width.
        LOG_IMG('imgs/abc.png', width='70%')
```


### Triggering Execution in Jenkins

When hytest is executed with the `--report_url_prefix` parameter,

for example: `hytest --report_url_prefix http://192.168.5.156`,

after the test finishes, the test report will be copied to the `reports` directory of the automation project.

The test will also print a line similar to the following when it finishes:

```
Test report: http://192.168.5.156/report_20230108_180546.html
```

<br>

Therefore, before execution, we should start a web service for viewing test reports.

For example, execute the following in the automation test project directory:

```py
python -m http.server 80 --directory reports
```

This uses the `reports` directory under the current directory as the web access root directory.

If the IP address of the test execution host is 192.168.5.156,

you can view the test report through `http://192.168.5.156`.

<br>

Assume the path of the hytest automation project directory to be executed is `d:/my/elife_autotest`.

In a Windows environment, if you want to directly execute a Pipeline containing hytest automated tests on the Jenkins controller host,

you can configure the Pipeline `Jenkinsfile` like this:

```java
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'build release'
            }
        }
        
        
        stage('Test') {
            steps {
                dir("d://my//elife_autotest") {
                    bat "hytest --report_url_prefix http://192.168.5.156"
                }
            }
        }
    }    
    
}
```

<br>
 
After Jenkins runs, the build result will include the console output of hytest, which includes the test results and report link. This makes it convenient to view them from the Jenkins UI.


### Integration with Other Systems

During test execution, hytest emits events such as `test execution starts`, `each test case execution result`, and `test execution finishes`.

Developers can write their own code to handle these events and integrate hytest with other systems used in testing.

For example, during the test process, you may want to write the test result to a test record system every time a test case finishes.

This test record system could be an Excel file, or it could be a test management system such as JIRA.

<br>

This code can be defined in the `__st__.py` file under the hytest test case root directory.

<br>

The code example below shows how to dynamically write test results to an Excel test case execution record file during the test process.

```py
class MySignalHandler:
    TEST_RET_COL_NO = 6 # Column number of the test result in the test case Excel file

    def __init__(self):
        self.caseNum2Row = {} # Test case ID -> row number mapping table
        self.getCaseNum2RowInExcel()
        
        # Run pip install pypiwin32 to ensure the library containing win32com is installed.
        import win32com.client
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.excel.Visible = True
        workbook = self.excel.Workbooks.Open(r"h:\tcs-api.xlsx")
        self.sheet = workbook.Sheets(1)

    def getCaseNum2RowInExcel(self):
        """
        Get the row number corresponding to each test case ID in Excel,
        so test results can be filled in conveniently.
        """
        import xlrd
        book = xlrd.open_workbook(r"h:\tcs-api.xlsx")
        sheet = book.sheet_by_index(0)
        caseNumbers = sheet.col_values(colx=1)
        print(caseNumbers)

        for row, cn in enumerate(caseNumbers):
            if '-' in cn:
                self.caseNum2Row[cn] = row + 1

        print(self.caseNum2Row)

    def case_result(self, case):
        """
        case_result is the function called after each test case finishes executing.

        @param case: test case class instance
        """
        
        # Find the row number of the corresponding test case in Excel.
        caseNo = case.name.split(' - ')[-1].strip()
        cell = self.sheet.Cells(self.caseNum2Row[caseNo], self.TEST_RET_COL_NO)
        # Scroll the window to ensure the current test result cell is visible.
        self.excel.ActiveWindow.ScrollRow = self.caseNum2Row[caseNo]-2

        if case.execRet == 'pass':
            cell.Value = 'pass'
            cell.Font.Color =  0xBF00 # Set to green
        else:
            cell.Font.Color =  0xFF   # Set to red
            if case.execRet == 'fail':
                cell.Value = 'fail'
            elif case.execRet == 'abort':
                cell.Value = 'abort'

    def test_end(self, runner):
        """
        test_end is the function called after the entire test execution finishes.

        @param runner: hytest runner object
               runner.case_list: a list containing all test case class instances
        """
        for case in runner.case_list:
            print(f'{case.name} --- {case.execRet}')

# Register an instance of this class as a hytest signal handler object.
from hytest import signal
signal.register(MySignalHandler())
```
