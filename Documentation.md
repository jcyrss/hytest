## Introduction

`hytest` is a generic open source test-automation framework. It's mainly but not only used for QA system testing.

Maybe your first question is what's the difference comparing it with `pytest` or `Robot Framework`?

Well, I like the way of setup/teardown of Robot Framework over that of pytest.

The former is simpler and more intuitive than the latter. The order of multiple layer's setup/teardown is strictly obeyed, which is especially critical for system testing. But that of pytest is not very strict, [see this](https://github.com/pytest-dev/pytest/issues/7416)

But Robot Framework creates its own "language" to write test cases instead of using python directly. It's much less flexible to write test cases, and it makes it hard to deal with complex data structure. 

<br>

So, if you like Robot Framework's way of setup/teardown,  and want to write tests in python, you could try hytest.




##  Installation

hytest requires Python 3.8 or newer

simply run:

```py
pip install hytest
```


then, run the following command to create a test-automation project folder with name 'myauto'

```py
hytest --new myauto
```

Replace  `myauto` with your project name.

<br>

If error message pops up to tell you command  `hytest`  not found, run the following command instead

```py
python -m hytest.run --new myauto
```


<br>

Now, you will find the project folder is created, and there is a sub-folder called  `cases` in it.

As you could imagine, the test cases files should be put there, and there is a sample test cases file with its name 'case1.py'.

We will elaborate on how to write test cases later, now let run it to see what happen.

<br>

Just open a command line window, change current directory to path of the project folder.

In that path, run  `hytest`  or  `python -m hytest.run`, you should see the output like the following.

```
    *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *
    *       hytest 0.8.5            www.byhy.net       *
    *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *



===   [ collect test cases ]  ****  ===


== cases\case1.py



===   [ execute test cases ]  ===

Number of cases to run : 1



>>> cases\case1.py

* test case name - 0001
                          PASS


  ========= Duration Of Testing : 0.003 seconds =========


  number of cases to run : 1

  number of cases actually run : 1

  passed : 1

  failed : 0

  exception aborted : 0

  suite setup failed : 0

  suite teardown failed : 0

  cases setup failed : 0

  cases teardown failed : 0
```

Command line window show test execution info and result.

Besides, you will find a new folder call 'log' created in the project dir, within it there are test report and test log files.

By default, the test report will be open in browser automatically after testing. 

You could disable that by add argument `--auto_open_report no`  in command line.


<br>

You could run  `hytest -h`  to check command line arguments





## organization of test cases 


let's see how automation test cases are organized in hytest.

Here, we could call automation test cases  `hytest cases` 
  
- usually, every `hytest case`  is a class definition.

  Every one is related to a test cases in your test documentation.

- a python code file could contain multiple hytest cases.

  So that python code file is a  `test suite` containing hytest cases
  
  We also call that python code file  `hytest suite file` 
   
- a folder could contain multiple hytest suite files.
  
  So that folder is also a  `test suite` containing hytest cases.
  
  We also call that folder  `hytest suite folder` 

  a hytest suite folder could contain multiple other suite folders which could contain other folders recursively.

- by default, the folder with name  `cases` will be as root suite folder.
  
  That could be changed by set command line positional argument to other name, like

  ```py
  hytest anothercasesdir
  ```




## hytest case definition
 

usually, every `hytest case`  is a class definition, like 


```py
# better class name contains ID of the test case 
class UI_0101:
    name = 'administrator operations - UI-0101'

    def teststeps(self):
        
        openOurWebSite()

        getProductList()
```


- Value of class attribute `name` is the name of test case.  
 
  if name attribute is missing，the class name will be treat as the name of test case.

  Also better to put ID of the test case at the end of the name, that will facilitate filtering test cases to run later.

- `teststeps` method contains executing steps of the test cases
  
  So, hytest only think of those classes **with method teststeps** as a `hytest case class` when it collects test cases before run test.


<br>

We could add some information to make test report/log more clear and easy to track, like print test steps or other executing information.

To do that, call hytest library functions, like the following

<br>

```py
from hytest import STEP, INFO, CHECK_POINT

class UI_0101:
      
    def teststeps(self):
        
        STEP(1,'open our web site')        
        # imagine we get title bar string here
        websiteTitle = "Tom's Store  Jan 1st, 2023" 
        INFO(f'website title is {websiteTitle}')
        CHECK_POINT('home page title', websiteTitle.startswith("Tom's Store") ) 

        
        STEP(2,'login')        
        CHECK_POINT('login successfully', True) 
    
        STEP(3,'check menu') 
        CHECK_POINT('menu info correct', True)  
```

<br>

The output in test report looks like this

![image](https://github.com/jcyrss/hytest/assets/10496014/8319faba-8dd7-4326-baf8-81e541b3c3cc)


<br>


The output in test log looks like this

```
>>> cases\case1.py

* UI_0101  -  2023-06-02 11:21:35

  [ case execution steps ]

-- Step #1 -- open our web site 

website title is Tom's Store  Jan 1st, 2023

** checkpoint **  home page title ---->  pass


-- Step #2 -- login 


** checkpoint **  login successfully ---->  pass


-- Step #3 -- check menu 


** checkpoint **  menu info correct ---->  pass

  PASS 
```


- STEP  
   
  the function to print test steps in report/log.
  the first argument is the number of the step.

- INFO

  the function to show other info you want add in report/log.

  the only arguments could be any type. If it is not string, it will be convert to string first.

- CHECK_POINT
  
  the function to validate check points in test cases.

  
  ```py  
  def CHECK_POINT(desc:str, condition, failStop=True, failLogScreenWebDriver = None):
      """
      check point of testing.

      pass or fail of this check point depends on argument condition is true or false.
      it will print information about check point in log and report.

      Parameters
      ----------
      desc :    check point description, like check what.

      condition : usually it's a bool expression, like  `a==b`, 
          so actually, after evaluating the expression, it's a result bool object passed in .

      failStop : switch for whether continue this test cases when the condition is false 

      failLogScreenWebDriver : Selenium web driver object,
          when you want a screenshot image of browser in test report if current check point fail.
    """
  ```

  <br>

  Usually, execution of one test case will be terminated if one check failed.

  But if you want to continue execute for some reasons, set argument  `failStop`  to False, like this

   ```py   
    def teststeps(self):

        CHECK_POINT('not critical check', False, failStop=False)

        CHECK_POINT('critical check', False)
   ```



## setup and teardown


Setup and teardown in hytest is pretty much like that in Robot Framework.

There are 3 kinds of them, they are Setup/Teardown of

- hytest test case
- hytest suite file
- hytest suite folder


### setup/teardown of test case

We could add setup/teardown method to a hytest test case, like


```py
class c0101:
    name = 'administrator home page - 0101'

    def setup(self):
        open_browser()
        mgr_login()

    def teardown(self):
        wd = GSTORE['wd']
        wd.quit()

    def teststeps(self):        
```


<br>


When hytest execute the above test cases class, it will

- first,  run  `setup`  method

- then, run  `teststeps`  method

- at last, run  `teardown`  method


And,if setup failed, which means there is exception raised,  hytest will not run method teststeps or teardown any more。

If teststeps failed, which means there is exception raised,  hytest still will run teardown method.



### setup/teardown of suite file



If we need setup/teardown for all test cases in one  **hytest suite file** , we could add global functions  `suite_setup`  and  `suite_teardown`, like this


```py
from hytest  import *

def suite_setup():
    addProducts(100)

def suite_teardown():
    deleteProducts(100)

class c0101:
    name = 'administrator home page - 0101'

    def teststeps(self):
    # test steps code 


class c0102:
    name = 'administrator home page - 0102'

    def teststeps(self):
    # test steps code   
```

<br>


When hytest execute the above test cases class, it will

- first,  run  `suite_setup`  function

- then, run all the test cases in suite file

- at last, run  `suite_teardown`  function


If  suite_setup  failed, which means there is exception raised,  hytest will not run test cases or suite_teardown.

<br>

If both suite_setup、suite_teardown and cases setup、teardown methods existing in one suite file, like


```py
from hytest  import *

def suite_setup():
    INFO('suite_setup: add 100 products')
    addProducts(100)

def suite_teardown():
    INFO('suite_teardown: delete the 100 products added')
    deleteProducts(100)

class c0101:
    name = 'administrator home page - 0101'

    def setup(self):
        # case setup

    def teardown(self):
        # case teardown

    def teststeps(self):
    # test steps code 


class c0102:
    name = 'administrator home page - 0102'

    def setup(self):
        # case setup

    def teardown(self):
        wd = GSTORE['wd']
        wd.quit()

    def teststeps(self):
    # test steps code   
```

hytest will run them in the following order:

- suite_setup

- c0101 setup

- c0101 teststeps

- c0101 teardown
    
- c0102 setup

- c0102 teststeps

- c0102 teardown

- suite_teardown


Case c0101 has higher execution order priority than case c0102 because it appears earlier. 



### setup/teardown of suite folder



If we need setup/teardown for all test cases in one  **hytest suite folder** , we could create a python file with its name `__st__.py` in that suite folder, and add global functions  `suite_setup`  and  `suite_teardown` in it

That's setup/teardown for whole **hytest suite folder**.  

When we run testing, hytest will 

- first, execute suite_setup of folder 

- then, excute test suite file, including suite_setup of file and test cases and suite_teardown of file

- at last, execute suite_teardown of folder


<br>

Suite folder could be nested, I think you could easily figure out execution order.

If your are familiar with Robot Framework, it's easy to understand.


<br>

### default setup/teardown of test cases

We could define global function with name `test_setup`, then all the test cases without its own  `setup` method, will use global function  `test_setup` as its setup method. So that could be called default setup of all test cases in that suite file. 


We could define global function with name `test_teardown`, then all the test cases without its own  `teardown` method, will use global function  `test_teardown` as its setup method. So that could be called default teardown of all test cases in that suite file. 




## data sharing across setup/teardown/teststeps

In test automation, we often need to pass data created in setup to test steps and teardown method.

It's very easy for class level setup/teststeps/teardown. 

When hytest collecting test cases, it will create instance of hytest case classes, so we just need to assign those data to instance attributes, then other instance methods like teststeps/teardown could access them from those instance attributes.

Like this,


```py
class c0101:
    name = 'administrator home page - 0101'

    def setup(self):
        self.products = createProducts()

    def teardown(self):
        deleteProducts(self.products)

    def teststeps(self):  
        INFO(self.products)      
        ...
```



<br>

But how we share data created in setup functions of suite files or suite folders with test cases inside of them?

Hytest provides a global var  `GSTORE`, you could use it like a simple dictionary.

like this,

```py
from hytest import GSTORE

def suite_setup():
    GSTORE['env1 product id'] = createProduct()
    GSTORE['driver'] = webdriver.Chrome()

def suite_teardown():
    deleteProduct(GSTORE['env1 product id'])
    GSTORE['driver'].quit()


class c00303:
    name = 'create order - API-0303'

    def teststeps(self):
        createOrder(productid=GSTORE['env1 product id'])
```

<br>

We could also put/get data in the attribute way, like


```py
from hytest import GSTORE
def suite_setup():
    GSTORE.productId = createProduct()
    GSTORE.driver = webdriver.Chrome()

def suite_teardown():
    deleteProduct(GSTORE.productId)
    GSTORE.driver.quit()


class c00303:
    name = 'create order - API-0303'

    def teststeps(self):
        createOrder(productid=GSTORE.productId)
```



<br>

One disadvantage of using GSTORE is, IDE does not know the type of data in GSTORE, so it cannot provide editing helper functionalities like attributes prompt.

If you really need those IDE helps, you could define your own global shared data store.

You could create a python module file with name  `share.py`, the content is like 


```py
from selenium import webdriver
class gs:
    driver : webdriver.Chrome 
    productId : int
```

then in test suite file or `__st__.py` , you could use it like

```py
from share import gs

def suite_setup():
    gs.productId = createProduct()
    gs.driver = webdriver.Chrome()

def suite_teardown():
    deleteProduct(gs.productId)
    gs.driver.quit()


class c00303:
    name = 'create order - API-0303'

    def teststeps(self):
        createOrder(productid=gs.productId)
```

<br>

There are type hints in  `gs`  definition, so IDE could provides helps like attribute prompt/autocomplete.






## data driven

If a batch of test cases have almost the same test steps, just with different test data, we could separate test data out, and share the code the test steps. 

Usually we called that  `data-driven`  tests.



<br>

For example, we have 6 test cases about login functionality.

They are login with one account (username:byhy, password:888888) by inputting

- no user name, correct password
- correct user name, no password
- user name missing last char, correct password
- user name plus one extra char, correct password
- correct user name, password missing last char
- correct user name, password missing plus one extra char


<br>

hytest support data-driven by the follwowing way

```py
class LoginUI:
    # every item in ddt_cases is a dictionary and related to a test case, in the item:
    # name value is the name of the test case, 
    # para value is parameter of the test case.
    ddt_cases = [
        {
            'name': 'login UI_0001',
            'para': [None, '888888', 'please input user name']
        },
        {
            'name': 'login UI_0002',
            'para': ['byhy', None, 'please input password']
        },
        {
            'name': 'login UI_0003',
            'para': ['byh', '888888', 'wrong user name or password']
        },
        {
            'name': 'login UI_0003',
            'para': ['byhyy', '888888', 'wrong user name or password']
        },
        {
            'name': 'login UI_0001',
            'para': ['byhy', '88888', 'wrong user name or password']
        },
        {
            'name': 'login UI_0002',
            'para': ['byhy', '8888887', 'wrong user name or password']
        },
    ]

    
    def teststeps(self):
        # access test parameter data by 'self.para'
        username, password = self.para
        
        # the follwing a login test code
```

When executing test, hytest will create 6 instances of the above class,
and put each item of ddt_cases into those 6 instances in order as attribute  `para`, and call teststeps.

So in teststeps method, we could get test parameter data by  `self.para`.

<br>

For data-driven class, don't define class attribute 'name', because there are many test cases, and their names are in ddt_cases




<br>

Parameters of data-driven test cases could be created by dynamically, like 


```py
from hytest import *

class UI_000x:

    ddt_cases = []
    for i in range(10):
        ddt_cases.append({
            'name': f'Login UI_000{i+1}',
            'para': ['byhy', f'{i+1}'*8]
        })
 
    def teststeps(self):
        INFO(f'{self.para}')
```

<br>

When we run hytest, it will 

- First, collect test cases.

  It collect test case classes, and create instances of them. Every instance is one test cases object.
  
- Then, run automation by calling those instance methods


<br>

Collecting is before running. So we could not use those data which create when running in  `ddt_cases` .

The following code is wrong,

```py
from hytest import *
 
def suite_setup():
    GSTORE['data_1'] = 'some data'
  
class UI_000x:
    # the following code will be executed in collecting phase,
    # at that time GSTORE['data_1'] is not created, so it's wrong.
    ddt_cases = GSTORE['data_1']

    def teststeps(self):
        INFO(f'{self.para}')
```




## filter cases to run by name

When we execute testing, we often don't need to run all of them.

For example, we just need to run those cases for smoke-testing.

Or we just want to debug the one test case in developing.

Hytest let your pick which cases to run in the similar way with Robot Framework.

<br>


we could use command line switches  `--test`  or  `--suite`  to specify those cases to run. 

Like the following,

```py
--test testA              # run the cases with exact name 'testA'
--test "order list"       # run the cases with exact name 'order list'
--test testA --test testB # run the cases with exact name 'testA' or 'testB'
--test test*              # run the cases with name starting with 'test'

--suite orders            # run the suites with exact name 'orders', so all cases in that suite will be run
```

<br>

We suggest to put ID of test cases at the end of case name, like 'order list - 0101'

so we could pick that case to run by this way, save the trouble to write a long name.

```
hytest --test  *0101  
```


<br>

If you have a long list of test cases to run, like

```
UI-0301
UI-0302
UI-0303
UI-1401
UI-1402
# and more
```

We could run them in this way

```
hytest --test *0301  --test *0302 --test *0303 --test *1401 --test *1402 # and more 
```

That will make a very long command.


Hytest support argument file, we could put all arguments in one file with name like `args` , and put one argument each line, like the following

```
--test *0301
--test *0302
--test *0303
--test *1401
--test *1402
```

Then, we just need to run `hytest -A args` to run all the cases in list.



## filter cases to run by tags


Hytest supports  filter cases to run by  `tags` .

### add tags to test cases


To do that, first we need to add tags to test cases.

One cases could have multiple tags.

For example, a test cases of login functionality could have 3 tags: login functionality, smoke test, UI test



<br>

Hytest support adding tag to test cases in 2 different ways:

- by global var  `force_tags` 

  If we define a global var named  `force_tags`  in hytest suite file like this,

  ```py
  force_tags = ['login functionality','smoke test','UI test']
  ```

  All the test cases in that file will have those 3 tags.



  <br>

  As you could imaging, if we defined a  `force_tags` in  `__st__.py` in hytest suite folder, all the test cases in that folder will have those 3 tags.


- by the `tags` attribute of hytest case class
  
  If we define a `tags` attribute of hytest case class, like this

  ```py
  class Login00001:
      tags = ['login functionality','smoke test','UI test']
  ```

  That test case will have those 3 tags.



### filter cases by tags

When we run test, 2e could filter cases to run by tags.

Like,

```py
# run cases with 'smoke test' tag. Double quote is needed due to space char in tag. 
--tag "smoke test"  


# run cases without 'smoke test' tag.
--tagnot "smoke test"  


# run cases with both 'smoke test' and 'UITest' tags. Note how Double quote and single quote are used here
--tag "'smoke test' and 'UITest'"


# run cases with either 'smoke test' or 'UITest' tags
--tag "smoke test" --tag UITest


# run cases with tag name like A*B, like A5B， AB， A444B, etc
--tag A*B    
```


## debugging


When we run hytest, actually it is to run the following command

```
python -m hytest.run
```

So, when we debug code, we need to set IDE accordingly.


Take Pycharm for example, we need to set  `Debug Configurations` like the following

![image](https://github.com/jcyrss/hytest/assets/10496014/49338678-e5c5-4ca8-b4c4-8c5b1fe33782)






## set title of test report


We could use command line argument `--report_title` to set title of test report.

Like,


```py
hytest --report_title "Regression Test Round #2"
```



## add images into report

If you were developing UI automation with Selenium or Appium, you could use hytest function `SELENIUM_LOG_SCREEN` to save screenshot image to test report.


Like

```py
from hytest import *

class c1:
    name = 'web-lesson-0001'

    def teststeps(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://192.168.56.103/sign.html')

        # The first argument is webdriver object
        # argument 'width' is optional to specify the width of the image in web page.
        SELENIUM_LOG_SCREEN(driver, width='70%') 
```

<br>

You also could use hytest function `LOG_IMG` to put existing image file to test report.

Like

```py
from hytest import *

class c1:
    name = 'web-lesson-0001'

    def teststeps(self):

        # could be URL of an online image.
        LOG_IMG('http://www.byhy.net/xxx.png')

        # could be the relative path of a local image file relative to project root path.
        LOG_IMG('imgs/abc.png')

        # could be the absolute path of a local image.
        LOG_IMG('d:/car.png', width='70%')
```



## work with Jenkins



If we need to check test report from Jenkins, first we need to start an extra web server in the machine running hytest for viewing hytest report.

Since hytest is running in Python, we could use Python built-in library  `http`.

Enter hytest project root folder in commandline, and run the following command
  
```py
python -m http.server 80 --directory reports
```

It will start a web server serving static files with the folder `reports`  as content root.

Say the IP address of machine running hytest is  `192.168.5.156` , we could view all html files under the folder `reports` by url `http://192.168.5.156/xxxx.html`



<br>

How can we make hytest put test report file under the folder `reports`?

When we run hytest with argument  `--report_url_prefix`, like

```
hytest --report_url_prefix http://192.168.5.156
```

After testing finished, hytest will copy report file into a folder named `reports` under project root.

And the console output will end with the following

```
test report : http://192.168.5.156/report_20230108_180546.html
```

<br>



Say hytest running in a Windows machine, and automation project path here is `d:/myautomation` 

We could set `Jenkinsfile` of Jenkins Pipeline like this 


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
                dir("d://myautomation") {
                    bat "hytest --report_url_prefix http://192.168.5.156"
                }
            }
        }
    }    
    
}
```

<br>

After Jenkins finish this task, the result will include all the content hytest console outputs, including the last line like 


```
test report : http://192.168.5.156/report_20230108_180546.html
```
 
It's a link, we could just click it from Jenkins webpage to jump to the web site serving hytest report to view detail information of the test execution.


