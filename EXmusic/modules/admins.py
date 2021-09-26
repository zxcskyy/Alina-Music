# Copyright (C) 2021 EXMusicbot

import traceback
import asyncio
from asyncio import QueueEmpty
from EXmusic.config import que
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Chat, CallbackQuery, ChatPermissions

from EXmusic.function.admins import admins
from EXmusic.helpers.channelmusic import get_chat_id
from EXmusic.helpers.decorators import authorized_users_only, errors
from EXmusic.modules.play import cb_admin_check
from EXmusic.helpers.filters import command, other_filters
from EXmusic.services.callsmusic import callsmusic
from EXmusic.services.callsmusic import queues

@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text("❎ No song is playing!")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await client.send_message("▶️ **Music paused!**\n\n• For resuming the song, press the button below.",
        reply_markup=InlineKeyboardMarkup(
            [
               [
                  InlineKeyboardButton("Resume »", callback_data="play")
               ]
            ]
         ),
      )


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text("❎ Nothing is paused!")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text("⏸ **Music resumed!**\n\n• For end the song, use command » /end")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❎ Nothing is streaming!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("✅ **Streaming ended**\n\n• Assistant has been disconnected from voice chat group")

@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❎ Nothing is playing to skip!\n\n**Info Update** : @EXProjects")
    else:
        queues.task_done(chat_id)

        if queues.is_empty(chat_id):
            callsmusic.pytgcalls.leave_group_call(chat_id)
        else:
            callsmusic.pytgcalls.change_stream(
                chat_id, queues.get(chat_id)["file"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"**You jump to the next song queue..**\n\n• skipped : **{skip[0]}**\n• now playing : **{qeue[0][0]}**")
