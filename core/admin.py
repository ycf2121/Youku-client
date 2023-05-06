from lib import common
from TcpClient import tcpclient
import os
from conf import setting

admin_data={
    'session':None,
    # 'name':None,
}

send_dic = {'type': None, 'user_type': 'admin', 'session': None}


def admin_register(client):
    print('管理员注册')
    while True:
        name=input('请输入用户名:').strip()
        if name == 'q': break

        password=input('请输入密码：').strip()
        conf_password=input('请确认密码：').strip()
        if password == conf_password:
            send_dic={'type':'register','user_type':'admin','name':name,'password':common.make_md5(password)}
            back_dic=common.send_data(client,send_dic,None)
            if back_dic['flag']:
                print(back_dic['msg'])
                break
            else:
                print(back_dic['msg'])
        else:
            print('两次输入密码不一致')

def admin_login(client):
    print('管理员登录')
    while True:
        name=input('请输入用户名：').strip()
        if name == 'q': break

        password=input('请输入密码:').strip()
        send_dic={'type':'login','user_type': 'admin','name':name,'password':common.make_md5(password)}
        back_dic=common.send_data(client,send_dic,None)
        if back_dic['flag']:
            admin_data['session']=back_dic['session']
            print(back_dic['msg'])
            break
        else:
            print(back_dic['msg'])

def release_notice(client):
    if not admin_data['session']:
        print('请先登录')
        return
    print('发布公告')
    while True:
        notice_name = input('请输入公告标题：').strip()
        notice_content = input('请输入公告内容:').strip()
        if notice_name == 'q': break
        send_dic['type'] = 'release_notice'
        send_dic['session'] = admin_data['session']
        send_dic['notice_name'] = notice_name
        send_dic['notice_content'] = notice_content
        back_dic = common.send_data(client, send_dic, None)
        if back_dic['flag']:
            print(back_dic['msg'])
            break
        else:
            print(back_dic['msg'])

def delete_movie(client):
    '''
    1 先拿到视频列表，打印
    2 根据视频前数字，选择要删除的视频
    3 删除成功/失败，打印
    '''
    if not admin_data['session']:
        print('请先登陆')
        return
    print('删除视频')
    while True:
        send_dic['type'] = 'get_movie_list'
        send_dic['session'] = admin_data['session']
        send_dic['movie_type'] = 'all'
        back_dic = common.send_data(client, send_dic, None)
        if back_dic['flag']:
            for i, mo in enumerate(back_dic['movie_list']):
                print('%s : %s--%s' % (i, mo[0], mo[1]))
            choose = input('请输入要删除的电影（数字）：').strip()
            if choose == 'q': break
            if choose.isdigit():
                choose = int(choose)
                if choose >= len(back_dic['movie_list']):
                    print('请输入范围内的数字')
                    continue
                send_dic['type'] = 'delete_movie'
                # 回忆后台返回的数据是什么样的
                send_dic['movie_id'] = back_dic['movie_list'][choose][2]
                back_dic = common.send_data(client, send_dic, None)
                if back_dic['flag']:
                    print(back_dic['msg'])
                    break
                else:
                    print(back_dic['msg'])

            else:
                print('请输入数字')

        else:
            print(back_dic['msg'])
            break

def upload_movie(client):
    if not admin_data['session']:
        print('请先登录')
        return
    print('上传视频')
    while True:
        up_list=common.get_allfile_by_path(setting.BASE_MOVIE_UP)
        if not up_list:
            print('暂无可上传影片')
            return
        for i,movie in enumerate(up_list):
            print('%s:%s' %(i,movie))
        choice=input('请输入要上传的影片(数字):').strip()
        if choice == 'q': break
        if choice.isdigit():
            choice=int(choice)
            # 先把md5值传上去校验一下文件是否存在，在决定要不要上传
            if choice >= len(up_list):
                print('请输入范围内的数字')
                continue

            movie_path=os.path.join(setting.BASE_MOVIE_UP,up_list[choice])
            file_md5=common.get_bigfile_md5(movie_path)
            send_dic = {'type': 'check_movie',
                        'session': admin_data['session'],
                        'file_md5':file_md5,
                        }
            back_dic = common.send_data(client,send_dic,None)
            if back_dic['flag']:
                is_free = input('是否免费（y/n）>>:').strip()
                if is_free == 'y':
                    is_free = 1
                else:
                    is_free = 0
                file_size = os.path.getsize(movie_path)
                send_dic={'type':'upload',
                          'user_type': 'admin',
                          'session':admin_data['session'],
                          'is_free':is_free,
                          'file_md5':file_md5,
                          'file_name':up_list[choice],
                          'file_size':file_size,
                          }
                back_dic = common.send_data(client,send_dic,movie_path)
                if back_dic['flag']:
                    print(back_dic['msg'])
                    break
                else:
                    print(back_dic['msg'])
            else:
                print(back_dic['msg'])
        else:
            print('请输入数字')

func_dic={
    '1':admin_register,
    '2':admin_login,
    '3':upload_movie,
    '4':delete_movie,
    '5':release_notice,
}

def admin_view():
    client=tcpclient.client_conn()
    while True:
        print('''
        1   注册
        2   登陆
        3   上传视频
        4   删除视频
        5   发布公告
        ''')
        choice=input('请选择功能：').strip()
        if choice =='q':break
        if choice not in func_dic:continue
        func_dic[choice](client)
    client.close()