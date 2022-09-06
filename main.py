import os
import discord
import chess
import chess.svg
import chess.pgn
import io
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests

BOARD_VIEWER_OPTIONS = ["⬅️", "⏯️", "➡️"];
active_games = {};

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    print("Message received!")
    if message.author == client.user:
      return
    if 'chess.com/' in message.content:
      print(message.content)
      pgn = get_pgn(message.content)
      print(pgn)
      game = get_game(pgn)
      active_games[message.id] = game;
      sentMsg = await message.channel.send("hi", file=get_png(game.end().board()))
      for option in BOARD_VIEWER_OPTIONS:
        await sentMsg.add_reaction(option)

def get_game(pgn):
  return chess.pgn.read_game(io.StringIO(pgn))

def get_png(board):
  svg = chess.svg.board(board=board, size=1800)
  f = open('file.svg', 'w')
  f.write(svg)
  
  svg = svg2rlg("file.svg")
  renderPM.drawToFile(svg, "file.png", fmt="png")
  return discord.File('file.png')
      
def get_pgn(url):
  req = Request(url, headers={'User-Agent' : "Magic Browser"}) 
  page = urlopen(req)
  html = page.read().decode("utf-8")
  outputFile = open("output.html", "w")
  outputFile.write(html)
  soup = BeautifulSoup(html, "html.parser")
  whiteUser = soup.find_all("meta", {"name": "description"})[0].get('content').split()[0];
  print(whiteUser)
  archives = requests.get(f"https://api.chess.com/pub/player/{whiteUser}/games/archives").json()['archives']
  archives.reverse()
  for archive in archives:
    for game in requests.get(archive).json()['games']:
      if get_id(game['url']) == get_id(url):
        return game['pgn']

def get_id(url):
  return url.split('/')[-1];

client.run(os.environ['DISCORD_TOKEN'])