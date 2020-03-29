import logging
import os.path

import urllib3
from urllib3.util.url import parse_url
from urllib3.exceptions import MaxRetryError
import tempfile

logger = logging.getLogger(__name__)


class RemoteDataFile():
    """Encapsulation of a remote data file"""

    def __init__(self, url, download_dir: str, file_name: str):
        super().__init__()
        self.download_dir = download_dir
        self.file_name = file_name
        try:
            self.url = parse_url(url)
        except ValueError as e:
            logger.error(
                f'Failed to create RemoteDataFile object. Invalid URL supplied {url}')
            raise ValueError("Invalid URL supplied")

    def get_url(self):
        return self.url.url

    def get_download_path(self):
        return os.path.join(self.download_dir, self.file_name)


class DataDownload():
    def __init__(self, default_dir=tempfile.mkdtemp()):
        super().__init__()
        self.default_dir = default_dir
        self.remote_data_files = []

    def add_download(self, url: str, file_name: str,
                     download_dir: str = None):
        """Add a url to the list of downloads

        Arguments:
            url {str} -- URL to download
            file_name {str} -- Destination file name

        Keyword Arguments:
            download_dir {str} -- The destination directory on disk where the
                downloaded file will be saved. If None, it assumes the default
                directory path.  (default: {None})
        """
        if download_dir is None:
            download_dir = self.default_dir
        remote_data_file = RemoteDataFile(url, download_dir, file_name)
        self.remote_data_files.append(remote_data_file)

    def download(self, remote_file: RemoteDataFile):
        """Download a remote file

        Arguments:
            remote_file {RemoteDataFile} -- The RemoteDataFile object that
                defines the URL and destination location

        Returns:
            (file_path {str}, success {boolean}) -- A tuple of the downloaded
                file path on disk and a boolean indicating if the download 
                succeeded. The file_path is None and success if False if the
                download fails.
        """
        if not os.path.exists(remote_file.download_dir):
            logger.debug(
                f'Creating download folder {remote_file.download_dir}')
            os.mkdir(remote_file.download_dir)

        dest_file_path = remote_file.get_download_path()
        dest_file_size = 0
        if os.path.exists(dest_file_path):
            dest_file_size = os.path.getsize(dest_file_path)
            logger.debug(
                f'File {dest_file_path} already exists with size {dest_file_size}')

        http = urllib3.PoolManager()
        try:
            req = http.request('GET', remote_file.get_url(),
                               preload_content=False,)
        except MaxRetryError as e:
            logger.error(f'Failed to download {remote_file.get_url()}')
            e.reason = f'Failed to download {remote_file.get_url()}'
            return None, False

        if 'Content-Length' not in req.headers or \
                dest_file_size != int(req.headers['Content-Length']):
            logger.debug(f'Writing remote data file to disk: {dest_file_path}')
            with open(dest_file_path, 'wb') as out:
                while True:
                    data = req.read(16384)
                    if not data:
                        break
                    out.write(data)
            req.release_conn()
        else:
            logger.info(
                f'Skipping file download because it is the same file on disk: {remote_file.get_url()}')

        return dest_file_path, True

    def download_all(self):
        """Download all files in the download list
        
        Returns:
            file_paths {list{str}} -- A list of the downloaded file paths on
                disk and a boolean indicating if the download succeeded. The
                file_path is None and success if False if the download fails.
        """        
        data_files = []
        for remote_data_file in self.remote_data_files:
            file_path, succeeded = self.download(remote_data_file)
            if succeeded:
                data_files.append(file_path)

        return data_files
