# Update this when new version is tagged.
import os
import subprocess


LAST_TAG = 'v1.1.0'


def _get_git_version():
    plugin_path = os.path.realpath(os.path.dirname(__file__))
    try:
        git_version = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=4', '--dirty=-*'],
            cwd=plugin_path)
        if isinstance(git_version, bytes):
            return git_version.decode('utf-8').rstrip()
        else:
            return git_version.rstrip()
    except subprocess.CalledProcessError:
        # print('Git 版本检查失败：' + str(e))
        pass
    except Exception:
        # print('无法启动 Git 进程：' + str(e))
        pass
    return None


version = _get_git_version() or LAST_TAG
