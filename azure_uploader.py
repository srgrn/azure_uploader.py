""" simple azure uploader script """
import sys
import argparse
import os
from azure.storage.blob import BlockBlobService

import logging


LOG_LEVEL = 'WARNING'

DEBUG = True
if DEBUG:
    import pdb
    LOG_LEVEL = 'DEBUG'

FORMAT = '%(asctime)-15s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


def print_humane_message(msg):
    seperator = "*"
    print((seperator * (len(msg) + 6)))
    print(("{}  {}  {}".format(seperator, " " * len(msg), seperator)))
    print(("{}  {}  {}".format(seperator, msg, seperator)))
    print(("{}  {}  {}".format(seperator, " " * len(msg), seperator)))
    print((seperator * (len(msg) + 6)))


def main():
    parser = argparse.ArgumentParser(description='upload a file azure')
    parser.add_argument('-f', '--file', help='file you want to upload', required=True)
    parser.add_argument('-c', '--container', help='Container name', required=True)
    parser.add_argument('--account', help='Specify account to user')
    parser.add_argument('--key', help='Specify what is the account key')
    parser.add_argument('-p', '--azure-path', help='give specific path on azure for the file')
    parser.add_argument('--report-endpoint',
                        help='allow giving an http endpoint to report to when the file has finished uploading')
    parser.add_argument('--contenttype', help='allow selecting content type')
    parser.add_argument('-d', '--dry-run', action='store_true',
                        help='test running the command without actually upload ')
    args = parser.parse_args()
    logging.debug("args=" + str(args))
    account = args.account
    key = args.key
    if account is None:
        logging.warning("No account given on command using environment")
        account = os.environ.get('AZURE_CONTAINER_ACCOUNT')
    if key is None:
        logging.warning("No key given on command using environment")
        key = os.environ.get('AZURE_CONTAINER_KEY')
    cloudpath = args.azure_path
    if cloudpath is None:
        cloudpath = os.path.dirname(args.file)
    logging.info("Uploading %s to container %s with path %s" % (args.file, args.container, cloudpath))
    if account is None or key is None:
        logging.error("Please specify blob credentials in the command line or using enviroment variables")
        sys.exit(1)
    if not args.dry_run:
        blob_service = BlockBlobService(account_name=account, account_key=key)
        if not cloudpath.endswith("/"):
            cloudpath += "/"
        cloudpath += os.path.basename(args.file)
        if args.contenttype is not None:
            blob_service.create_blob_from_path(args.container, cloudpath, args.file,
                                                  x_ms_blob_content_type=args.contenttype)
        else:
            blob_service.create_blob_from_path(args.container, cloudpath, args.file)
        url = "https://%s.blob.core.windows.net/%s/%s" % (account, args.container, cloudpath)
        print_humane_message(url)

if __name__ == '__main__':
    main()
