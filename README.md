Introduction
------------

[中文教程](http://www.byhy.net/tut/auto/hytest/01/)

`hytest` is a generic open source test-automation framework. It's mainly but not only used for QA system testing.

Maybe your first question is what's the difference comparing it with `pytest` or  `Robot Framework`?

Well, I like the way of setup/teardown of Robot Framework over that of pytest.

The former is simpler and more intuitive than the latter. The order of multiple layer's setup/teardown is strictly obeyed, which is especially critical for system testing. But that of pytest is not very strict, [see this](https://github.com/pytest-dev/pytest/issues/7416)

But Robot Framework creates its own "language" to write test cases instead of using python directly. It's much less flexible to write test cases, and it makes it hard to deal with complex data structure. 


So, if you like Robot Framework's way of setup/teardown,  and want to write tests in python, you could try hytest.




Documentation
------------

[Github Documentation](https://github.com/jcyrss/hytest/blob/main/Documentation.md)


    







