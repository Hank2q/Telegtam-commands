import settings as s
from telegram.ext import MessageHandler
from telegram.ext.filters import BaseFilter
from telegram.ext import CommandHandler
from telegram.ext import Updater
import os
import signal
import mimetypes
from pyautogui import screenshot as take
from datetime import datetime
from subprocess import Popen, PIPE


def verified(id):
    return id == s.id


updater = Updater(
    token=s.token, use_context=True)
dispatcher = updater.dispatcher


class CommandFilter(BaseFilter):
    def filter(self, msg):
        if msg.text.startswith('cmd '):
            return True
        else:
            print("[INVALID COMMAND SYNTAX]")


def start(update, context):
    if not verified(update.effective_chat.id):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="This bot is private")
        return
    # context.bot.send_message(
        # chat_id=update.effective_chat.id, text="Welcom Hank!")
    update.message.reply_text('Welcom Hank!')


dispatcher.add_handler(CommandHandler('start', start))


def quit(update, context):
    if not verified(update.effective_chat.id):
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Closing bot\nGood Bye!')
    print('[DISCONNECTED]')
    os.kill(os.getpid(), signal.SIGINT)


dispatcher.add_handler(CommandHandler('quit', quit))


def screenshot(update, context):
    if not verified(update.effective_chat.id):
        return
    ss = take()
    name = f'{datetime.now().strftime("%d-%m-%Y %H.%M.%S")}.png'
    ss.save(f'screenshots/{name}')
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='screenshot taken')
    context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=open(f'C:/Users/HASSANIN/Desktop/PythonProj/mobile-com/screenshots/{name}', 'rb'))


dispatcher.add_handler(CommandHandler('screenshot', screenshot))


def is_type(filetype, file):
    kind, _ = mimetypes.guess_type(file)
    if kind != None:
        return filetype in kind
    return False


def sendfile(update, context):
    if not verified(update.effective_chat.id):
        return
    filename = ' '.join(context.args) if len(
        context.args) > 1 else context.args[0]
    if filename in os.listdir() and os.path.isfile(filename):
        update.message.reply_text(f'Sending {filename} ...')
        print(f'[SENDING FILE]: {filename}')
        if is_type('image', filename):
            context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=open(filename, 'rb'))
        elif filename.endswith('mp4'):
            if os.path.getsize(filename) > 52428800:
                update.message.reply_text(
                    'Video too larg to send\nTry the could')
            else:
                context.bot.send_video(
                    chat_id=update.effective_chat.id, video=open(filename, 'rb'))
        elif is_type('audio', filename):
            if os.path.getsize(filename) > 52428800:
                update.message.reply_text(
                    'Audio too larg to send\nTry the could')
            else:
                context.bot.send_audio(
                    chat_id=update.effective_chat.id, audio=open(filename, 'rb'))
        else:
            if os.path.getsize(filename) > 52428800:
                update.message.reply_text(
                    'File too larg to send\nTry the could')
            else:
                context.bot.send_document(
                    chat_id=update.effective_chat.id, document=open(filename, 'rb'))
    else:
        available = '\n'.join(
            [file for file in os.listdir() if os.path.isfile(file)])
        update.message.reply_text(
            f'File not found.\nAvaialble files:\n{available}')


dispatcher.add_handler(CommandHandler('sendfile', sendfile))


def command(update, context):
    if not verified(update.effective_chat.id):
        return
    cmd = update.message.text[4:]
    out = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if cmd.startswith('cd'):
        try:
            os.chdir(cmd[3:])
        except FileNotFoundError:
            available = '\n'.join(
                [folder for folder in os.listdir() if os.path.isdir(folder)])
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'ERROR FILE NOT FOUND\nAvailabe directories:\n{available}')
        else:
            cd = os.getcwd().replace('\\', '/') + '>'
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=cd)
        finally:
            return
    result, error = out.communicate()
    if error:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f'Error:\n{error.decode()}')
        print(f'[COMMAND ERROR]: {cmd}:\n', error.decode())
    else:
        print(f'[COMMAND RAN]: {cmd}')
        if not result or result == b'\x0c':
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='Command ran successfuly\nNo output')
        else:
            if len(result) <= 4000:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=result.decode())
            else:
                for chunk in result[0:len(result), 4000]:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=chunk.decode())


command_filter = CommandFilter()
dispatcher.add_handler(MessageHandler(command_filter, command))


updater.start_polling()
updater.idle()
