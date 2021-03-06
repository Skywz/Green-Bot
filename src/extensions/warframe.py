# Imports
import datetime as dt
from datetime import datetime
import operator
import discord
from discord.ext import commands
from ..functions.embeds import embedC
from ..functions.general import fetchAPI
from ..functions.date import Date

# CLass
class WarframeCog(commands.Cog):
	"""docstring for WarframeCog"""
	def __init__(self, bot):
		super(WarframeCog, self).__init__()
		self.bot = bot

	base_api = "https://api.warframestat.us/pc"
	api_extentions = {
		"cetus" : "/cetusCycle",
		"vallis" : "/vallisCycle",
		"cambion" : "/cambionCycle",
		"arbi" : "/arbitration",
		"kuva" : "/kuva",
		"sortie" : "/sortie",
		"fissures" : "/fissures",
		"invasions" : "/invasions",
		"events" : "/events"
	}
	relic_tiers = ["Lith", "Meso", "Neo", "Axi", "Requiem"]

	async def fetchWFAPI(self, extention = None):
		url = self.base_api 
		if extention is not None:
			url += self.api_extentions[extention]

		warframe_api = await fetchAPI(url)

		return warframe_api

	@commands.command(name="server-index", aliases=['server-list'])
	async def server_index(self, ctx):
		embed = embedC.quick_embed(f"Server Index", None, 0x98FB98)

		fields = [
			{"name" : "General Warframe Servers", "value" : "\
			[Official Warframe Server](https://discord.gg/cV6KV3G)\
			\n[Community Warframe Server](https://discord.gg/warframe)\
			\n[Warframe Trading Hub](https://discord.gg/EwD6J37)\
			\n[Warframe Blessings](https://discord.gg/3hHy5ygR4y)\
			\n[Warframe Giveaways](https://discord.com/invite/d8ZYADy)\
			\n[Endgame Community](https://discord.gg/2REYJrK)", "inline": True},
			{"name" : "Topical Warframe Servers", "value" : "\
			[Warframe University](https://discord.gg/ftfPKjP)\
			\n[Warframe Speedruns](https://discord.gg/7wtcKvv)\
			\n[Riven Info and Trading](https://discord.gg/S7aCrWx)\
			\n[Eidolon Zone](https://discord.gg/jDkrGf7)\
			\n[Warframe Arbitrations](https://discord.gg/ENRWGZr)\
			\n[Warframe Railjack](https://discord.gg/JvYVMNa)\
			\n[Warframe Conclave](https://discord.gg/asJsw6Q)\
			\n[Kubrow & Kavat Breeding and Trading](https://discord.gg/abzV2Cb)", "inline": True}
		]

		embedC().builder(embed, ctx.author, fields)

		await ctx.send(embed=embed)

	@commands.group(name="current", pass_context=True) # , invoke_without_command=False
	async def wf_current(self, ctx):
		if ctx.invoked_subcommand is None:
			pass

	@wf_current.command(brief="Returns the current arbi info.")
	async def arbi(self, ctx):
		info = await self.fetchWFAPI("arbi")

		embed = embedC.quick_embed("Current Arbitration", None, 0x98FB98)

		fields = [
			{"name" : "Enemy", "value" : info["enemy"], "inline" : True},
			{"name" : "Mission", "value" : info["type"], "inline" : True},
			{"name" : "Node", "value" : info["node"], "inline" : False}
		]

		if info["archwing"] == True:
			fields.append({"name" : "Archwing", "value" : info["archwing"], "inline" : False})

		embedC().add_fields(embed, fields)

		embed.set_footer(text="Expiry", icon_url=ctx.author.avatar_url_as(size=256))
		embed.timestamp = datetime.strptime(info["expiry"],"%Y-%m-%dT%H:%M:%S.%fZ")

		await ctx.send(content=None,embed=embed)

	@wf_current.command(brief="Returns the current sortie info.")
	async def sortie(self, ctx):
		info = await self.fetchWFAPI("sortie")

		embed = embedC.quick_embed("Current Sortie", None, 0x98FB98)

		fields = [
			#{"name" : "Boss", "value" : f'{sortie_info["boss"]}\
			#\nFaction - {sortie_info["faction"]}', "inline" : "False"},
			{"name" : f'Mission One - {info["variants"][0]["missionType"]}', "value" : f'Node: {info["variants"][0]["node"]}\
			\n{info["variants"][0]["modifier"]}\
			\n - {info["variants"][0]["modifierDescription"]}', "inline" : False},
			{"name" : f'Mission Two - {info["variants"][1]["missionType"]}', "value" : f'Node: {info["variants"][1]["node"]}\
			\n{info["variants"][1]["modifier"]}\
			\n - {info["variants"][1]["modifierDescription"]}', "inline" : False},
			{"name" : f'Mission Three - {info["variants"][2]["missionType"]}', "value" : f'Node: {info["variants"][2]["node"]}\
			\n{info["variants"][2]["modifier"]}\
			\n - {info["variants"][2]["modifierDescription"]}', "inline" : False},
		]

		embedC().add_fields(embed, fields)

		embed.set_footer(text="Expiry", icon_url=ctx.author.avatar_url_as(size=256))
		embed.timestamp = datetime.strptime(info["expiry"],"%Y-%m-%dT%H:%M:%S.%fZ")

		await ctx.send(content=None, embed=embed)

	@wf_current.command(brief="Returns the current fissures.")
	async def fissures(self, ctx, tier = None):
		"""
		Convert to use paginator
		"""
		info = await self.fetchWFAPI("fissures")
		fields = []

		if tier != None:
			if tier.capitalize() in self.relic_tiers:
				tier = tier.capitalize()
				embed = embedC.quick_embed(f"Current {tier} Fissures", None, 0x98FB98)

				for fissure in info:
					if fissure["tier"] == tier:
						fields.append({"name": f'Mission Type: {fissure["missionType"]}', 
										"value" : f'Node: {fissure["node"]}\
											\nEnemy: {fissure["enemy"]}\
											\nExpires in: **{fissure["eta"]}**', "inline" : False})

				embedC().builder(embed, ctx.author, fields)
		
				await ctx.send(content=None, embed=embed)
			else:
				await ctx.send(f"**{tier}** is not a relic type!")
		else:
			embed = embedC.quick_embed("Current Fissures", None, 0x98FB98)

			lis = {"Lith" : "", "Meso" : "", "Neo" : "", "Axi" : "", "Requiem" : ""}

			for fissure in info:
				lis[fissure["tier"]] += (f'**Mission Type: {fissure["missionType"]}**\
											\nNode: {fissure["node"]} - Enemy: {fissure["enemy"]}\
											\nExpires in: {fissure["eta"]}\n')
			
			for relic, value in lis.items():
				if value != "":
					fields.append({"name" : f'{relic} Fissures', "value" : value, "inline" : False})

			embedC().builder(embed, ctx.author, fields)
		
			await ctx.send(content=None, embed=embed)

	@wf_current.command(brief="")
	async def invasions(self, ctx):
		#info = await self.fetchWFAPI("invasions")

def setup(bot):
	bot.add_cog(WarframeCog(bot))