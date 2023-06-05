from hytest import STEP, INFO, CHECK_POINT

def add_order(name):
    return {
        'ret': 0,
        'info': {
            'id': 100,
            'name': name
        }
    }


def rename_order(oid):
    return {'ret': 0}


def delete_order(oid):
    return {'ret': 0}


force_tags = ['优先级1']


def suite_setup():
    pass


def suite_teardown():
    pass


# 用例对应的类名，建议对应用例编号
class c00001:
    # 用例名，必填。 建议后面加上编号
    name = '添加订单 - API-0001'
    # 用例标签，可选   
    tags = ['本次不测', 'now']

    # 用例的初始化
    def setup(self):
        INFO('添加订单')
        ret = add_order('order name')

        # we could compare complicated data object easily,
        # but in Robot, that's hard
        assert ret == {
            'ret': 0,
            'info': {
                'id': 100,
                'name': 'order name'
            }
        }
        self.orderid = ret['info']['id']

    # 用例的清除
    def teardown(self):
        INFO('删除订单')
        delete_order(self.orderid)

    # 测试用例 具体操作步骤
    def teststeps(self):
        STEP(1, '再添加一个订单')
        CHECK_POINT('检查API接口返回值', True)

        STEP(2, '重命名订单')
        ret1 = rename_order(self.orderid)
        CHECK_POINT('检查API接口返回值', ret1 == {'ret': 0})

        STEP(3, '修改订单数据')
        INFO(ret1)
        CHECK_POINT('检查API接口返回值', ret1 == {'ret': 1})


class c00002:
    name = '添加订单 - API-0002'

    def teststeps(self):
        STEP(1, '添加一个客户不存在的订单')
        CHECK_POINT('检查API接口返回值', True)

        STEP(2, '添加一个客户id不存在的订单')
        ret = add_order('order name')
        CHECK_POINT('检查API接口返回值', ret['ret'] == 1)

    def teardown(self):
        delete_order(1)


# 没有定义 name 属性， 类名就是 用例的名字
class Test_function_3:

    def teststeps(self):
        CHECK_POINT('不通过但是也不中止1', False, failStop=False)


        CHECK_POINT('不通过但是也不中止2', False, failStop=False)

    def teardown(self):
        delete_order(1)

# 没有定义 teststeps，不是用例
class Test_function_nosteps:

    def teardown(self):
        delete_order(1)


# 数据驱动，多个用例
class c00003x:
    # ddt_cases 里面每个字典元素 定义一个用例的数据
    # 其中： name是该用例的名称， para是用例的参数
    ddt_cases = [
        {
            'name': '登录 - API-0031',
            'para': ['user001', '888888']
        },
        {
            'name': '登录 - API-0032',
            'para': ['user002', '8']
        },
        {
            'name': '登录 - API-0033',
            'para': ['user002', ''] 
        }
    ]

    # 用例的初始化
    def setup(self):
        pass

    # 每个用例调用时，该用例的参数在 self.para 中
    def teststeps(self):
        # 取出参数
        username, password = self.para
        print(username, password)
        # 下面是登录测试代码
        if not password:
            raise AssertionError(f'密码错误')

    def teardown(self):
        delete_order(1)
