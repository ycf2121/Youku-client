from TcpClient import tcpclient
from lib import common
from conf import setting
import os
import time

user_data = {
    'session': None,
    # 'name': None,
    'is_vip': None
}

# send_dic = {'type': None, 'user_type': 'user', 'name': None, 'session': None}
send_dic = {'type': None, 'user_type': 'user','session': None}


def user_register(client):
    print('用户注册')
    while True:
        name = input('请输入手机号>>:').strip()
        password = input('请输入密码>>').strip()
        conf_password = input('请确认密码>>:').strip()
        if password == conf_password:
            send_dic = {'type': 'register', 'user_type': 'user', 'name': name, 'password': common.make_md5(password)}
            back_dic = common.send_data(client, send_dic, None)
            if back_dic['flag']:
                print(back_dic['msg'])
                break
            else:
                print(back_dic['msg'])

        else:
            print('两次密码不一致')


def user_login(client):
    print('用户登录')
    while True:
        name = input('用户名>>').strip()
        if name == 'q': break
        password = input('密码>>').strip()
        send_dic = {'type': 'login', 'user_type': 'user', 'name': name, 'password': common.make_md5(password)}

        back_dic = common.send_data(client, send_dic, None)
        if back_dic['flag']:
            # user_data['name'] = name
            user_data['session'] = back_dic['session']
            user_data['is_vip'] = back_dic['is_vip']
            print(back_dic['msg'])
            print(back_dic['last_notice'])
            break
        else:
            print(back_dic['msg'])


def buy_member(client):
    print('购买会员')
    # if not user_data['name']:
    if not user_data['session']:
        print('请先登录')
        return
    if user_data['is_vip'] == 1:
        print('您已经是会员了')
        return
    while True:
        buy = input('是否购买会员（y/n）q 退出').strip()
        if 'y' == buy:
            send_dic['type'] = 'buy_member'
            # send_dic['name'] = user_data['name']
            send_dic['session'] = user_data['session']
            back_dic = common.send_data(client, send_dic, None)
            if back_dic['flag']:
                user_data['is_vip'] = 1
                print(back_dic['msg'])
                break
            else:
                print(back_dic['msg'])

        elif 'q' == buy:
            break
        else:
            print('您没有购买')


def get_movie_list(client):
    # if not user_data['name']:
    if not user_data['session']:
        print('请先登录')
        return
    print('查看视频列表')
    while True:
        send_dic['type'] = 'get_movie_list'
        # send_dic['name'] = user_data['name']
        send_dic['movie_type'] = 'all'
        send_dic['session'] = user_data['session']
        back_dic = common.send_data(client, send_dic, None)
        if back_dic['flag']:
            for i, mo in enumerate(back_dic['movie_list']):
                print('%s : %s-->%s' % (i, mo[0],mo[1]))
            break
        else:
            print(back_dic['msg'])


def down_free_movie(client):
    # if not user_data['name']:
    if not user_data['session']:
        print('请先登录')
        return
    print('下载免费视频')
    '''
    先查询免费视频，打印出来，
    用户选择后，通过电影id去后台下载
    '''
    send_dic['type'] = 'get_movie_list'
    send_dic['movie_type'] = 'free'
    send_dic['session'] = user_data['session']
    back_dic = common.send_data(client, send_dic, None)
    if back_dic['flag']:
        for i, mo in enumerate(back_dic['movie_list']):
            print('%s : %s-->%s' % (i, mo[0], mo[1]))
    while True:
        choose = input('请输入要下载的电影名称：').strip()
        send_dic['type'] = 'download_movie'
        send_dic['name'] = user_data['name']
        send_dic['session'] = user_data['session']
        send_dic['movie_name'] = choose
        send_dic['movie_type'] = 'free'
        back_dic = common.send_data(client, send_dic, None)
        if back_dic['flag']:
            if back_dic['wait_time'] > 0:
                print('请等待 %s 秒' % back_dic['wait_time'])
                time.sleep(back_dic['wait_time'])
            recv_size = 0
            print('----->', back_dic['filename'])
            path = os.path.join(setting.BASE_MOVIE_DOWN, back_dic['filename'])
            with open(path, 'wb') as f:
                while recv_size < back_dic['file_size']:
                    recv_data = client.recv(1024)
                    f.write(recv_data)
                    recv_size += len(recv_data)
                    print('recv_size:%s file_size:%s' % (recv_size, back_dic['file_size']))
            print('%s :下载成功' % back_dic['filename'])
            break
        else:
            print(back_dic['msg'])


def down_charge_movie(client):
    # if not user_data['name']:
    if not user_data['session']:
        print('请先登录')
        return
    print('下载收费视频')
    if user_data['is_vip']:
        charge = input('您是会员，收费5元（y 确认）').strip()
    else:
        charge = input('您不是会员，收费10元（y 确认）').strip()
    if not charge == 'y':  # 不是y，相当于没付钱，直接返回
        return
    send_dic['type'] = 'get_movie_list'
    send_dic['movie_type'] = 'charge'
    send_dic['session'] = user_data['session']
    back_dic = common.send_data(client, send_dic, None)
    if back_dic['flag']:
        for i, mo in enumerate(back_dic['movie_list']):
            print('%s : %s-->%s' % (i, mo[0], mo[1]))
        choose = input('请输入要下载的电影（数字）：').strip()
        if choose.isdigit():
            choose = int(choose)
            # 回忆后台返回的数据是什么样的
            send_dic['type'] = 'download_movie'
            send_dic['session'] = user_data['session']
            send_dic['movie_id'] = back_dic['movie_list'][choose][2]
            send_dic['movie_type'] = 'charge'
            back_dic = common.send_data(client, send_dic, None)
            if back_dic['flag']:
                recv_size = 0
                print('----->', back_dic['filename'])
                path = os.path.join(setting.BASE_MOVIE_DOWN, back_dic['filename'])
                with open(path, 'wb') as f:
                    while recv_size < back_dic['file_size']:
                        recv_data = client.recv(1024)
                        f.write(recv_data)
                        recv_size += len(recv_data)
                        print('recv_size:%s file_size:%s' % (recv_size, back_dic['file_size']))
                print('%s :下载成功' % back_dic['filename'])
            else:
                print(back_dic['msg'])
    else:
        print(back_dic['msg'])


def check_download_record(client):
    # if not user_data['name']:
    if not user_data['session']:
        print('请先登录')
        return
    print('查看观影记录')
    send_dic['type'] = 'check_download_record'
    # send_dic['name'] = user_data['name']
    send_dic['session'] = user_data['session']
    back_dic = common.send_data(client, send_dic, None)
    if back_dic['flag']:
        for re in back_dic['download_list']:
            print(re)
    else:
        print(back_dic['msg'])


def check_notice(client):
    # if not user_data['name']:
    if not user_data['session']:
        print('请先登录')
        return
    print('查看公告')
    send_dic['type'] = 'check_notice'
    send_dic['name'] = user_data['name']
    send_dic['session'] = user_data['session']
    back_dic = common.send_data(client, send_dic, None)
    if back_dic['flag']:
        for value in back_dic['notice_list']:
            print(value)
    else:
        print(back_dic['msg'])


fun_dic = {
    '1': user_register,
    '2': user_login,
    '3': buy_member,
    '4': get_movie_list,
    '5': down_free_movie,
    '6': down_charge_movie,
    '7': check_download_record,
    '8': check_notice
}


def user_view():
    client = tcpclient.client_conn()
    while True:
        print('''
        1 注册
        2 登录
        3 冲会员
        4 查看视频
        5 下载免费视频
        6 下载收费视频
        7 查看观影记录
        8 查看公告
        ''')

        choose = input('please choose>>:').strip()
        if 'q' == choose: break
        if choose not in fun_dic: continue
        fun_dic[choose](client)
    client.close()
