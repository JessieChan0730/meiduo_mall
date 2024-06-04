from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client, get_tracker_conf
from django.conf import settings


# 重写存储引擎方法
class FastDfsStroage(Storage):

    def __init__(self, base_url=None, client_conf=None):
        """
            初始化对象
            :param base_url:
            :param client_conf:
        """
        if base_url is None:
            base_url = settings.FDAS_URL
        self.base_url = base_url

        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
            # FDFS_CLIENT_CONF = os.path.join(BASE_DIR, 'client.conf')
        self.client_conf = client_conf

    def _open(self, name, mode='rb'):

        """
            打开文件
            :param name:
            :param mode:
            :return:
        """
        pass

    def _save(self, name, content):
        """
            保存文件
            :param name: 传入文件名
            :param content: 文件内容
            :return:保存到数据库中的FastDFSDE文件名
        """

        client = Fdfs_client(get_tracker_conf(settings.FDFS_CLIENT_CONF))
        ret = client.upload_by_buffer(content.read())
        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")
        file_name = ret.get("Remote file_id")
        # byte转str
        file_name = str(file_name, encoding="utf-8")
        return file_name

    def exists(self, name):
        """
            检查文件是否重复, FastDFS自动区分重复文件
            :param name:
            :return:
        """
        return False

    def url(self, name):
        """
            获取name文件的完整url
            :param name:
            :return:
        """
        return self.base_url + name
