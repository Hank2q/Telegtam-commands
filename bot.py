import mimetypes
import os
import signal
import settings as s
from datetime import datetime
from subprocess import PIPE, Popen
from pyautogui import screenshot as take
from telegram.ext import CommandHandler, MessageHandler, Updater
from telegram.ext.filters import BaseFilter

logger = s.log()

updater = Updater(
    token=s.token, use_context=True)
dispatcher = updater.dispatcher


def launch():
    logger.info('BOT STARTED @ ' +
                datetime.now().strftime("%d-%m-%Y %H:%M:%S %p"))
    updater.start_polling()
    updater.idle()


def verified(id):
    return id == s.id


class CommandFilter(BaseFilter):
    def filter(self, msg):
        if msg.text.startswith('>'):
            return True
        else:
            logger.error(f'Invalid Command: "{msg.text}"')


def start(update, context):
    if not verified(update.effective_chat.id):
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="This bot is private\nLEAVE!")
        logger.warning(
            f'Unkown user connected to bot:\nid: {update.effective_user.id}\nname: {update.effective_user.name}')
        return
    update.message.reply_text('Welcom')
    logger.info('[CONNECTION ESTABLISHED]')


dispatcher.add_handler(CommandHandler('start', start))


def quit(update, context):
    if not verified(update.effective_chat.id):
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Closing Bot\nGood Bye!')
    logger.info('BOT DISSCONNECTED @ ' +
                datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    os.kill(os.getpid(), signal.SIGINT)


dispatcher.add_handler(CommandHandler('quit', quit))


def help(update, context):
    if not verified(update.effective_chat.id):
        return
    if context.args[0] == 'v':
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=s.short_help)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=s.help_msg)


dispatcher.add_handler(CommandHandler('help', help))


def screenshot(update, context):
    if not verified(update.effective_chat.id):
        return
    shot = take()
    logger.info('Screenshot Taken')
    name = s.screenshots_dir + \
        f'{datetime.now().strftime("%d-%m-%Y %H.%M.%S")}.png'
    shot.save(name)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Screenshot taken')
    context.bot.send_photo(
        chat_id=update.effective_chat.id, photo=open(name, 'rb'))


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
        logger.info(f'Sending File: {filename}')
        max_size = 52000000

        if is_type('image', filename):
            context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=open(filename, 'rb'))
            logger.info(f'File Sent')

        elif filename.endswith('mp4'):
            if os.path.getsize(filename) > max_size:
                update.message.reply_text(
                    'Video too larg to send\nTry the could')
                logger.error('Sending Failed: Video file too larg')
            else:
                context.bot.send_video(
                    chat_id=update.effective_chat.id, video=open(filename, 'rb'))
                logger.info(f'File Sent')

        elif is_type('audio', filename):
            if os.path.getsize(filename) > max_size:
                update.message.reply_text(
                    'Audio too larg to send\nTry the could')
                logger.error('Sending Failed: Audio file too larg')
            else:
                context.bot.send_audio(
                    chat_id=update.effective_chat.id, audio=open(filename, 'rb'))
                logger.info(f'File Sent')

        else:
            if os.path.getsize(filename) > max_size:
                update.message.reply_text(
                    'File too larg to send\nTry the could')
                logger.error('Sending Failed: File too larg')
            else:
                context.bot.send_document(
                    chat_id=update.effective_chat.id, document=open(filename, 'rb'))
                logger.info(f'File Sent')
    else:
        available = '\n'.join(
            [file for file in os.listdir() if os.path.isfile(file)])
        update.message.reply_text(
            f'File not found.\nAvaialble files:\n{available}')


dispatcher.add_handler(CommandHandler('sendfile', sendfile))


def upload(update, context):
    if not verified(update.effective_chat.id):
        return

    target = ' '.join(context.args) if len(
        context.args) > 1 else context.args[0]

    if target.lower() in [n.lower() for n in os.listdir()]:
        update.message.reply_text(f'Uploading {target} ...')
        logger.info(f'Uploading File: {target}')

        cmd = f'copy /Y "{target}" {s.cloud}'
        result = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

        if result.communicate()[1]:
            logger.error(
                f'Uploading Failed: {result.communicate()[1].decode()}')
            update.message.reply_text('Error uploading file')
        else:
            logger.info('File Uploaded')
            update.message.reply_text('File uploaded to cloud')
    else:
        available = '\n'.join(
            [file for file in os.listdir()])
        update.message.reply_text(
            f'File not found.\nAvaialble files:\n{available}')


dispatcher.add_handler(CommandHandler('upload', upload))


def command(update, context):
    if not verified(update.effective_chat.id):
        return

    cmd = update.message.text[1:]
    output = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

    if cmd.startswith('cd'):
        try:
            os.chdir(cmd[3:])
        except FileNotFoundError:
            available = '\n'.join(
                [folder for folder in os.listdir() if os.path.isdir(folder)])
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'ERROR: File not found\nAvailabe directories:\n{available}')
        else:
            cd = os.getcwd().replace('\\', '/') + '>'
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=cd)
        finally:
            return

    result, error = output.communicate()
    if error:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=f'Error:\n{error.decode()}')
        logger.error(f'Command Error: {cmd}:\n', error.decode())
    else:
        logger.info(f'Command Ran: {cmd}')
        if not result or result == b'\x0c':
            context.bot.send_message(
                chat_id=update.effective_chat.id, text='Command ran successfuly\nNo output')
        else:
            if len(result) <= 4000:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=result.decode())
            else:
                for chunk in range(0, len(result), 4000):
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=result[chunk:chunk + 4000].decode())


command_filter = CommandFilter()
dispatcher.add_handler(MessageHandler(command_filter, command))


if __name__ == "__main__":
    launch()
