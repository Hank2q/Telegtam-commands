import logging


def log():
    logger = logging.getLogger('Telegram-Bot')
    formatter = logging.Formatter(
        '[%(levelname)s]:[%(funcName)s]: %(message)s')

    file_handler = logging.FileHandler(filename='BotLog.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    logger.setLevel(logging.INFO)
    return logger


token = '1375525321:AAGMBUccTtTZ1MQ6TojACaCpLFBadzxyUec'
id = 1279697548
cloud = r'"C:\Users\HASSANIN\OneDrive\BotUpload"'
screenshots_dir = 'C:/Users/HASSANIN/Desktop/PythonProj/mobile-com/screenshots/'
short_help = '''\
Acceptable commands are:

/start
/quit
/sendfile [filename]
/upload [filename]
/screenshot
/help |[v]
>[command]
'''
help_msg = '''\
This bot is used to send commands to a python script that will be executed on a machine.

Acceptable commands are:

/start:
        Connect with the bot, can also be used to test whether the bot is running on the machine or not.

/quit:
        Closed the connection with the bot and kills the  script on the machine.

/sendfile [filename]:
        Sends the targeted file as a message.
        Compatable files are files that the telegram bot can send.
        Otherwise use /upload
        note:
            have to be in the directory of the file by using the 'cd' shell command.

/upload [filename]:
        Uploads the targeted file / directory to the specified cloud folder in the script.
        note:
            have to be in the directory of the file by using the 'cd' shell command.

/screenshot:
        Takes a screen shot of the machine's display and sends it.

/help |[v]:
        Displays this help message.
        Optional:
            v: display a shortened message of only available commands

>[command]:
        Execute shell command, every thing passed after the '>' will be executed in the shell and
        the result will be sent back as text.'''
