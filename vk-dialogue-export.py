# -*- coding: utf-8 -*-

import codecs
import ConfigParser
import json
import sys
import urllib2
import os
from urllib import urlencode

Config = ConfigParser.ConfigParser()
Config.read("config.ini")

token = Config.get("auth", "access_token")
user_id = Config.get("auth", "user_id")
app_id = Config.get("application", "app_id")

def _api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    return json.loads(urllib2.urlopen(url).read())["response"]

def download_dialog(selector, messages_id, token):
    sys.stderr.write("Exporting: %s %s\n" % (selector, messages_id))

    fn = '{}_{}.json'.format(selector, messages_id)
    if os.path.exists(fn):
        return

    messages = _api("messages.getHistory", [(selector, messages_id)], token)

    mess = 0
    max_part = 200  # Due to vk.api

    cnt = messages[0]
    sys.stderr.write("Count of messages: %s\n" % cnt)

    messages = []
    users = set()

    while mess != cnt:
        # Try to retrieve info anyway

        while True:
            try:
                message_part = _api(
                    "messages.getHistory",
                    [
                        (selector, messages_id),
                        ("offset", mess),
                        ("count", max_part),
                        ("rev", 1)
                    ],
                    token
                )
            except Exception as e:
                sys.stderr.write('Got error %s, continue...\n' % e)
                continue
            break

        try:
            for i in range(1, 201):
                messages.append(message_part[i])
                users.add(message_part[i]["uid"])
        except IndexError:
            break

        result = mess + max_part
        if result > cnt:
            result = (mess - cnt) + mess
        mess = result
        sys.stderr.write("Exported %s messages of %s\n" % (mess, cnt))

    human_details = _api(
        "users.get",
        [("uids", ','.join(str(v) for v in users))],
        token
    )

    with codecs.open(fn, 'w+', "utf-8") as f:
        json.dump({
            "messages": messages,
            "users": human_details,
        }, f, indent=4)

    sys.stderr.write('Export done!\n')


dialogs = _api("messages.getDialogs", [("count", 200)], token)
with codecs.open('messages.json', 'w+', "utf-8") as f:
    json.dump({'dialogs': dialogs[1:]}, f, indent=4)

sys.stderr.write('%d chats!\n' % dialogs[0])
for dialog in dialogs[1:]:
    if 'chat_id' in dialog:
        download_dialog('chat_id', dialog['chat_id'], token)
    elif 'uid' in dialog:
        download_dialog('uid', dialog['uid'], token)
