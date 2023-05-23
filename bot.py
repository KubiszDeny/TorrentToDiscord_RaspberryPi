#sudo apt-get install transmission-cli
#sudo apt-get install python3 python3-pip
import discord #pip install discord
import subprocess
import time


DISCORD_TOKEN = 'your_discord_token'
DISCORD_CHANNEL_ID = 111222333444555666777888999

notification_interval = None
notification_active = False

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as', client.user.name)

def send_message_to_discord(message):
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    client.loop.create_task(channel.send(message))

def get_active_torrents():
    process = subprocess.Popen(['transmission-cli', '--list'], stdout=subprocess.PIPE)
    output, _ = process.communicate()
    output = output.decode('utf-8')

    # Parsing torrent information
    torrent_lines = output.split('\n')
    torrents = []
    for line in torrent_lines[1:-1]:
        parts = line.split()
        torrent = {
            'id': parts[0],
            'name': ' '.join(parts[1:-6]),
            'status': parts[-6],
            'size': parts[-5],
            'completed': parts[-4],
            'down_speed': parts[-3],
            'up_speed': parts[-2]
        }
        torrents.append(torrent)

    return torrents

def start_torrent(torrent_magnet):
    subprocess.call(['transmission-cli', torrent_magnet])

def send_torrent_status():
    while notification_active:
        torrents = get_active_torrents()
        if len(torrents) > 0:
            response = 'Active torrents:\n'
            for torrent in torrents:
                response += f"ID: {torrent['id']}\nName: {torrent['name']}\nStatus: {torrent['status']}\nSize: {torrent['size']}\nCompleted: {torrent['completed']}\nDownload Speed: {torrent['down_speed']}\nUpload Speed: {torrent['up_speed']}\n\n"
            send_message_to_discord(response)
        else:
            send_message_to_discord('No active torrents.')

        time.sleep(notification_interval * 60)

@client.event
async def on_message(message):
    global notification_interval
    global notification_active

    if message.author == client.user:
        return

    if message.content.lower() == '!download':
        send_message_to_discord('Torrent download initiated.')
        # Code for downloading torrent...

    if message.content.lower() == '!torrent show':
        torrents = get_active_torrents()
        if len(torrents) > 0:
            response = 'Active torrents:\n'
            for torrent in torrents:
                response += f"ID: {torrent['id']}\nName: {torrent['name']}\nStatus: {torrent['status']}\nSize: {torrent['size']}\nCompleted: {torrent['completed']}\nDownload Speed: {torrent['down_speed']}\nUpload Speed: {torrent['up_speed']}\n\n"
            send_message_to_discord(response)
        else:
            send_message_to_discord('No active torrents.')

    if message.content.lower().startswith('!torrent magnet'):
        magnet_code = message.content.split(' ', 2)[2]
        start_torrent(magnet_code)
        send_message_to_discord('Torrent download started.')

    if message.content.lower() == '!torrent pause':
        pause_torrents()
        send_message_to_discord('All active torrents paused.')

    if message.content.lower() == '!torrent start':
        start_torrents()
        send_message_to_discord('All active torrents started.')

    if message.content.lower().startswith('!torrent notification'):
        if notification_active:
            send_message_to_discord('Notifications are already active. Use `!torrent notification stop` to stop notifications.')
            return

        command_parts = message.content.split(' ')
        if len(command_parts) == 3:
            if command_parts[2].isdigit():
                interval = int(command_parts[2])
                if interval > 0:
                    notification_interval = interval
                    notification_active = True
                    send_message_to_discord(f'Notifications activated. You will be notified every {interval} minute(s).')
                    send_torrent_status()
                else:
                    send_message_to_discord('Invalid notification interval. Please provide a positive integer value.')
            else:
                send_message_to_discord('Invalid notification interval. Please provide a positive integer value.')
        else:
            send_message_to_discord('Invalid command. Please use `!torrent notification <interval>` to set notification interval.')

    if message.content.lower() == '!torrent notification stop':
        if notification_active:
            notification_active = False
            send_message_to_discord('Notifications stopped.')
        else:
            send_message_to_discord('Notifications are not active.')

client.run(DISCORD_TOKEN)
