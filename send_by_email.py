# -*- coding: utf-8 -*-
import smtplib
from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from file_ops import MoveSentFile, FSTools
from logger import log
from settings import SETTINGS

__author__ = 'Sencer Hamarat'


class Email():
    """
    Prepare and send files as attachment by e-mail
    """
    def __init__(self):
        log.debug("Email Class initiated")
        self.host = str()
        self.port = int()
        self.tls = False
        self.user = str()
        self.password = str()
        self.sender = str()
        self.recipients = list()
        self.composed = str()
        self.outer = None
        self.attachments = list()
        self.smtp = None

    def __attach_file(self, attachment):
        """
        Guess content type of the attachment, prepare header with this knowledge and attach file to message
        :param attachment:
        :return: None
        """
        log.debug(u"{attachment} file prepairing to attach...".format(attachment=attachment))
        fstools = FSTools(attachment=attachment)
        ctype, encoding = fstools.get_file_type()
        log.debug("File type and encoding is: {ctype} / {encoding}".format(ctype=ctype, encoding=encoding))
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            fp = open(attachment)
            # Not: charset hesaplamasını yapmalıyız.
            msg = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'image':
            fp = open(attachment, 'rb')
            msg = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(attachment, 'rb')
            msg = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(attachment, 'rb')
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
            fp.close()
            # Base64 Encoding kullanarak yükleme
            encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=attachment.split('\\')[-1])
        log.debug("File attached to message.")
        self.outer.attach(msg)

    def _prepare_email(self, attachment):
        """
        Prepare e-mail body and append attachments
        """
        log.debug("Mail prepairing to send...")
        self.outer = MIMEMultipart()
        self.outer['Subject'] = u'You have a new fax! ({attachment})'.format(attachment=attachment.split('\\')[-1])
        self.outer['To'] = ', '.join(recipient for recipient in self.recipients)
        self.outer['From'] = self.sender

        fstools = FSTools(attachment=attachment)
        filetype, fileenc = fstools.get_file_type()

        html = u"""<html>
            <head></head>
            <body>
                <p>
                    Hello!
                </p>
                <p>
                    You have a new fax: <span style="font-weight: bold;">{attachment}</span><br />
                    Please take a look at the attachment in this e-mail to see received fax.
                </p>
                <p>
                    Receive Date: {filedate}<br />
                    File Size: {filesize}<br />
                    File Type: {filetype}<br />
                    File Encoding = {fileenc}
                </p>
                <p style="float: right;">
                    File2Mail by Sencer Hamarat (C) 2015
                </p>
            </body>
        </html>
        """.format(attachment=attachment.split('\\')[-1], filedate=fstools.get_file_ctime(), filetype=filetype,
                   filesize=fstools.get_file_size(), fileenc=fileenc)
        self.outer.attach(MIMEText(html, 'html'))
        self.outer.preamble = attachment.split('\\')[-1]
        log.debug("Message added to mail.")
        self.__attach_file(attachment)

    def __prepare_connection(self):
        """
        Check and prepare connection variables with given kwargs
        :return:
        """
        # If port kwarg is None and tls kwarg is False than self.port is 25
        # If Port kwarg is None and tls kwarg is True than self.port is 587
        # Otherwise self.port is port kwarg
        if self.tls and not self.port:
            self.port = 587
        elif not self.port and not self.tls:
            self.port = 25
        else:
            pass
        log.debug(u"Port setted to {port}".format(port=self.port))

        if not self.host:
            raise Exception("Host not specified")

        if not self.user:
            raise Exception("User is not specified")

        if not self.sender:
            self.sender = self.user

        if not len(self.recipients):
            raise Exception("Recipient(s) not specified")

    def _connection(self, stop=False):
        """
        If stop kwarg True then start connection else stop connection
        :param stop: bool
        :return: None
        """
        if not stop:
            log.info(u"Connecting to {host} host...".format(host=self.host))
            self.smtp = smtplib.SMTP()
            self.__prepare_connection()
            try:
                self.smtp.connect(self.host, self.port)
                log.info(u"Connected to {host} host".format(host=self.host))
            except Exception as e:
                raise Exception(repr(e))

            if self.tls:
                log.info("Starting TLS...")
                try:
                    self.smtp.starttls()
                    log.info("TLS Started.")
                except Exception as e:
                    raise Exception(e)
            log.info("Logging in with user credentials...")
            try:
                self.smtp.login(self.user, self.password)
                log.info("Logged in.")
            except Exception as e:
                raise Exception(e)
        else:
            self.smtp.quit()
            log.info(u"Connection to {host} is now closed.".format(host=self.host))

    def send(self, attachments=list()):
        """
        Make SMTP connection and send mail per attachments and return sent attachments list
        :param attachments:
        :return: list()
        """
        self.host = SETTINGS["host"]
        self.port = SETTINGS["port"]
        self.tls = SETTINGS["tls"]
        self.user = SETTINGS["user"]
        self.password = SETTINGS["password"]
        self.sender = SETTINGS["sender"]
        self.recipients = SETTINGS["recipients"]
        if not len(SETTINGS["recipients"]):
            raise Exception("There is no recipient specified in configuration file")

        self.attachments = attachments
        self._connection()

        for attachment in attachments:
            self._prepare_email(attachment)
            self.composed = self.outer.as_string()
            log.debug(u"{file} is now sending".format(file=attachment))
            self.smtp.sendmail(self.sender, self.recipients, self.composed)
            log.info(u"{file} is sent".format(file=attachment))
            MoveSentFile(sent_file=attachment).do()

        self._connection(stop=True)