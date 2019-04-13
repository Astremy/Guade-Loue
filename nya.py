import discord
import asyncio
import json
import os

class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bg_task = self.loop.create_task(self.my_background_task())

	async def on_ready(self):
		print('Bot Connecté')
		print("Nom : ",self.user.name)
		print("ID : ",self.user.id)
		print("------------------------------")

	async def my_background_task(self):
		await self.wait_until_ready()
		chann = self.get_channel(565837453231915008)
		while not self.is_closed():
			load = open("images/images.json","r")
			envoyer = json.loads(load.read())
			load.close()
			if len(envoyer) == 0:
				await asyncio.sleep(1)
			else:
				result = []
				for i in envoyer:
					try:
						await chann.send(file=discord.File("images/"+i,"images/"+i))
						await asyncio.sleep(0.2)
						mess = chann.last_message
						result.append(mess.attachments[0].url)
						print(mess.attachments[0].url)
						os.remove("images/"+i)
					except: pass
				load = open("images/photos.json","r")
				donnees = json.loads(load.read())
				load.close()
				for i in result:
					donnees.append(i)
				load = open("images/photos.json","w")
				load.write(json.dumps(donnees,indent=4))
				load.close()
				load = open("images/images.json","w")
				load.write("[]")
				load.close()

client = MyClient()
client.run('NTY1Njk1OTM4MTE5ODYwMjcw.XK6LfA.dfjtmZPH1Dx1zVgab48wQBd1Crk')