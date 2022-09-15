import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import traceback
import base64
import PyPDF2, io
import re
from datetime import datetime
import config
import sys
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
import aiohttp


def connection():
    mail_pass = config.mail_pass
    username = config.username
    imap_server = "imap.mail.ru"
    imap = imaplib.IMAP4_SSL(imap_server)
    sts, res = imap.login(username, mail_pass)
    if sts == "OK":
        return imap
    else:
        return False


def encoded_words_to_text(encoded_words):
    # encoded_words=encoded_words.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "")
    encoded_word_regex = r"=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}="
    charset, encoding, encoded_text = re.match(
        encoded_word_regex, encoded_words
    ).groups()
    if encoding == "B":
        byte_string = base64.b64decode(encoded_text)
    elif encoding == "Q":
        byte_string = quopri.decodestring(encoded_text)
    return byte_string.decode(charset)


def get_attaches(msg):
    attaches = list()
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            if "pdf" in part.get_content_type():
                attaches.append(pdf_to_str(part.get_payload(decode=True)))
    if attaches:
        return attaches
    else:
        return [False]


def date_parse(msg_date):
    dt_obj = "".join(str(msg_date[:6]))
    dt_obj = dt_obj.strip("'(),")
    dt_obj = datetime.strptime(dt_obj, "%Y, %m, %d, %H, %M, %S")
    return dt_obj


def pdf_to_str(pdf):
    all_doc = ""
    try:
        with io.BytesIO(pdf) as open_pdf_file:
            read_pdf = PyPDF2.PdfFileReader(open_pdf_file)
            num_pages = read_pdf.getNumPages()
            for page in read_pdf.pages:
                page_content = page
                all_doc += page_content.extractText()
            return all_doc
    except:
        return False

async def send_message(bot_token, message, chat, rpl=None, prv=None):
    bot = Bot(token=bot_token)
    await bot.get_session()
    obj = await bot.send_message(
        chat_id=chat,
        text=message,
        parse_mode="HTML",
        reply_to_message_id=rpl,
        disable_web_page_preview=prv,
    )
    await bot._session.close()
    return obj.message_id

def get_letter_text(body):   
    soup = BeautifulSoup(body, 'html.parser')
    paragraphs = soup.find_all('div')
    print(paragraphs)
    text=""
    for paragraph in paragraphs:
        text += paragraph.text + "\n"    
    return text.replace('\xa0', ' ')

def get_text_from_multipart(msg):
    payload = msg.get_payload()[0]
    
    print(payload["Content-Type"])
    
    if "text/plain" in payload["Content-Type"]:
        print('i')
        letter_text = (
            (base64.b64decode(payload.get_payload()).decode())
            .lstrip()
            .rstrip()
        )
        letter_text = letter_text.replace("<","").replace(">","")
        return letter_text
    
    if "text/html" in payload["Content-Type"]:
        letter_text = (
            (base64.b64decode(payload.get_payload()).decode())
            .lstrip()
            .rstrip()
        )        
        letter_text=get_letter_text(letter_text)
        print(letter_text)
        return letter_text
        
    if "multipart" in payload["Content-Type"]:#if msg.is_multipart()
        letter_text = (
            (
                base64.b64decode(
                    payload.get_payload()[0].get_payload()
                ).decode()
            )
            .lstrip()
            .rstrip()
        )
        return letter_text

def post_construct(msg_subj, msg_from, msg_email, letter_text, att_files):
    txt = ""
    txt += (
        "<b>"
        + str(msg_subj)
        + "</b>"
        + "\n\n"
        + str(msg_from)
        + "\n"
        + msg_email
        + "\n"
        + letter_text
        + "\n"
        + "вложения pdf: "
        + str(att_files)
    )
    return txt
