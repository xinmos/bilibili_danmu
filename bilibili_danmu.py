import asyncio
import re
import time
import zlib

import requests
import websockets
import json
import struct

def getRealRoomId():
    room = input("请输入 url 中的 room 号：")
    response = requests.get(f"https://api.live.bilibili.com/room/v1/Room/room_init?id={room}")
    return response.json()["data"]["room_id"]

def getCertification():
    config = {
        'uid': 0,
        "roomid": getRealRoomId(),
        "protover": 1,
        "platform": "web",
        "clientver": "1.4.0"
    }
    b_config = json.dumps(config).encode("utf-8")
    str_bytes = struct.pack(f'>IHHII{len(b_config)}s', len(b_config) + 16, 16, 1, 7, 1, b_config)
    return str_bytes

def decodeMsg(msg):
    if msg['cmd'] == 'DANMU_MSG':
        print(msg["info"][2][1], ":", msg["info"][1])
    elif msg['cmd'] == "INTERACT_WORD":
        print("进入直播间:", msg["data"]["uname"])

async def hello():
    async with websockets.connect("wss://broadcastlv.chat.bilibili.com/sub") as ws:
        msg = getCertification()
        await ws.send(msg)
        start_time = int(time.time())
        while True:
            try:
                end_time = int(time.time())
                if end_time - start_time == 29:
                    beat = struct.pack(">IHHII", 0, 16, 1, 2, 1)
                    await ws.send(beat)
                    start_time = end_time
                res = await ws.recv()
                response = struct.unpack(f'>IHHII{len(res) - 16}s', res)
                if response[3] == 5:
                    if response[2] == 2:
                        # 数据被压缩过
                        for msg in re.findall(b'\x00({[^\x00]*})', zlib.decompress(response[-1])):
                            msg = json.loads(msg.decode('utf-8'))
                            decodeMsg(msg)
                    else:
                        msg = json.loads(response[-1].decode('utf-8'))
                        decodeMsg(msg)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(hello())
