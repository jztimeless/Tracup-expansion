import requests
import logging
from pprint import pprint


def flatten(a):
    for each in a:
        if not isinstance(each, list):
            yield each
        else:
            yield from flatten(each)


class TracupSDK(object):

    def __init__(self, api_key, user_key):
        self.__api_key = api_key
        self.__user_key = user_key
        self.__base_url = 'http://www.tracup.com'

        self.__logger = logging.getLogger('tracupSDK')
        self.__logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler('./logs/requests.log')
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)

    def __request(self, url, data, method='post'):
        '''请求函数，发送接口请求

        Arguments:
            url {[type]} -- 接口的路由地址
            data {[type]} -- 请求发送的数据

        Keyword Arguments:
            method {str} -- 请求方式 (default: {'post'})

        Raises:
            Exception -- 参数错误异常
        '''

        url = self.__base_url + url
        if method.lower() == 'post':
            response = requests.post(url, data, headers={
                'content-type': 'application/x-www-form-urlencoded'
            })
        elif method.lower() == 'get':
            response = requests.get(url, data)
        else:
            raise Exception('参数错误，不支持的请求类型')
        if response.status_code == 200:
            r = response.json()
            self.__logger.debug('请求接口：{}, 响应内容：{}'.format(url, response.text))
            if r['code'] == 0:
                return r['data']
            else:
                raise Exception('[{}] {}'.format(r['code'], r['message']))
        raise Exception('请求接口失败：%s' % response.status_code)
    # 项目模块

    def get_project_modules(self, p_key):
        '''获取模块列表

        Arguments:
            p_key {[str]} -- [项目的key]

        Returns:
            [type] -- [description]
        '''

        data = {
            '_api_key': self.__api_key,
            'uKey': self.__user_key,
            'pKey': p_key
        }
        return self.__request('/apiv1/project/getProjectModuleList', data)
    # 项目问题状态

    def get_qestion_status(self, p_key):
        data = {
            '_api_key': self.__api_key,
            'uKey': self.__user_key,
            'pKey': p_key
        }
        return self.__request('/apiv1/project/getStatusList', data)

    # 项目问题类型
    def get_qestion_type(self, p_key):
        data = {
            '_api_key': self.__api_key,
            'uKey': self.__user_key,
            'pKey': p_key
        }
        return self.__request('/apiv1/project/getProjectTypeList', data)

    # 项目问题列表

    def get_qestion_list(self, p_key, status, sort_name='i_no', sort='desc'):
        page = 1
        all_issues = []
        while True:
            data = {
                '_api_key': self.__api_key,
                'uKey': self.__user_key,
                'pKey': p_key,
                'sortName': sort_name,
                'sort': sort,
                'status': status,
                'page':page
            }
            result = self.__request('/apiv1/issue/listIssue', data)
            issues = result['list']
            if issues is None:
                break
            all_issues = all_issues + issues
            page = page + 1
        return all_issues 

    # 问题详情
    def get_question(self, p_key, i_no):
        data = {
            '_api_key': self.__api_key,
            'uKey': self.__user_key,
            'pKey': p_key,
            'iNo': i_no
        }
        return self.__request('/apiv1/issue/view', data)

    def get_all_project(self):
        data = {
            '_api_key': self.__api_key,
            'ukey': self.__user_key
        }
        return self.__request('/apiv1/project/getAllProjectList', data)

    # 获取备注
    def get_issue_comment(self, p_key, i_no):
        data = {
            '_api_key': self.__api_key,
            'uKey': self.__user_key,
            'pKey': p_key,
            'iNo': i_no
        }
        return self.__request('/apiv1/issue/getNoteList', data)


if __name__ == '__main__':
    sdk = TracupSDK(
        '6e238511179b6aeadf1e26fed1f6db07',
        '414a471ef24654e6b8413416a5048238'
    )
    sdk.get_project_modules('9df58763ae346255c4f3667bd8adf5bb','8ddc46d5aab32b4f18dedab6efffdc63')
