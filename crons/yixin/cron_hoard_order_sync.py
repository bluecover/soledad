# coding:utf-8

from core.models.hoard.profile import HoardProfile


def main():
    for id_ in HoardProfile.get_account_ids():
        HoardProfile.synchronize_in_worker(id_)


if __name__ == '__main__':
    main()
