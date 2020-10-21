# -*- coding: utf-8 -*-
import ast
import base64
import os
import uuid
from Crypto.Cipher import AES

__author__ = 'Sencer Hamarat'


class ConfigLoader():
    """
    Read and parse Configuration file.
    """
    def __init__(self):
        self.content = None
        self.config = dict()
        self.file_name = "file2mail.conf"
        self.file = "{root}/{file}".format(root=PROJECT_ROOT, file=self.file_name)
        # Prepare crypto method
        self.padding = '{'
        self.block_size = 32
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * self.padding
        self.EncodeAES = lambda c, s: base64.b64encode(c.encrypt(self.pad(s)))
        self.DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.padding)

    def __genkey(self):
        """
        Generates encryption key for hiding password written in config file.
        :return:
        """
        if "secret" not in self.config:
            try:
                config_file = open("log.txt", "a")
                try:
                    self.config["secret"] = str(uuid.uuid4().get_hex().upper()[0:16])
                    config_file.write("secret = {secret}".format(secret=self.config["secret"]))
                finally:
                    config_file.close()
            except IOError:
                pass

    def __encode_pass(self):
        """
        Encodes given string with secret
        :return:
        """
        self.__genkey()
        cipher = AES.new(self.config["secret"])
        return self.EncodeAES(cipher, self.config["password"])

    def _encrypt_password(self):
        """
        Does encryption on password
        :return:
        """
        try:
            return self.__encode_pass()
        except:
            return False
            # raise Exception("Unable to encode given string")

    def __decode_pass(self):
        """
        Decodes given string with secret
        :return:
        """
        self.__genkey()
        cipher = AES.new(self.config["secret"])
        return self.DecodeAES(cipher, self.config["password"])

    def _decrypt_password(self):
        """
        Does decryption on password
        :return:
        """
        try:
            return self.__decode_pass()
        except:
            return False
            # raise Exception("Unable to decode given string")

    def _check_password_encryption(self):
        try:
            self._decrypt_password()
        except Exception as e:
            print ("e")
            self._encrypt_password()
        finally:
            self._decrypt_password()

    def _control_config(self):
        """
        Control the entries in configuration files.
        :return:
        """
        self._check_password_encryption()

        if "target_directory" not in self.config or not self.config["target_directory"]:
            raise Exception("Target directory is not specified")
        else:
            self.config["target_directory"] = self.config["target_directory"].decode("utf-8")

        if "sent_directory" not in self.config or not self.config["sent_directory"]:
            raise Exception("Sent directory is not specified")
        else:
            self.config["sent_directory"] = self.config["sent_directory"].decode("utf-8")

        if "excluded_files" not in self.config or not self.config["excluded_files"]:
            self.config["excluded_files"] = []
        elif isinstance(self.config["excluded_files"], str):
            self.config["excluded_files"] = ast.literal_eval(self.config["excluded_files"])

        if "log_level" not in self.config:
            self.config["log_level"] = ''

        if self.config["port"]:
            self.config["port"] = int(self.config["port"])

        if "recipients" not in self.config:
            self.config["recipients"] = []
        try:
            self.config["recipients"] = ast.literal_eval(self.config["recipients"])
        except SyntaxError as e:
            self.config["recipients"] = []

    def read_config(self):
        """
        Reads settings from file2mail.conf file and applies evaluations to necessary values
        :return: dict()
        """
        if os.path.isfile(self.file):
            with open(self.file, mode='r') as _file:
                self.content = _file.readlines()
        else:
            raise Exception("Configuration file not found: {file}".format(file=self.file))

        try:
            for line in self.content:
                if (not line.startswith('#')) and ('=' in line):
                    line = line.replace('\r', '').replace('\n', '')
                    key, value = line.split('=')
                    self.config[key.strip()] = value.strip()
        except Exception as e:
            raise Exception(e.message.join("Error in configuration file: {file}".format(file=self.file)))

        self._control_config()

        return self.config

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
SETTINGS = ConfigLoader().read_config()
