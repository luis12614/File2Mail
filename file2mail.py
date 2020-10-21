# -*- coding: utf-8 -*-
import sys
from file_ops import GetFileList
from logger import log
from send_by_email import Email

__author__ = 'Sencer Hamarat'


class Main():
    def __init__(self):
        self.email = Email()
        self.email.send(attachments=GetFileList().filtered_list())


def main():
    # try:
        Main()
    # except Exception as e:
    #     print "An error occured! Please take a look at log file to see error."
    #     log.info(e.message)
    # finally:
        sys.exit()

if __name__ == "__main__":
    main()
	
	if _mail = "mailbox.maricopa.gov"
	
	
