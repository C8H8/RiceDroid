#!/usr/bin/python3

import discord
import random
import asyncio
import datetime
import sys
import math
import re

motd = "There is currently no MOTD"
paydays = {}
balances = {}

lastred = datetime.date.today()
redeems = []

communism_level = -1

def i_getbal(uid):
	bal = 0
	if uid in balances:
		bal = balances[uid]
	return bal

def i_getup(uid):
	up = 1
	if uid in paydays:
		up = paydays[uid]
	return up

def uid_to_mention(uid):
	return "<@" + str(uid) + ">"

def show_leaderboard(channel, uid):
	print("[LEADERBOARD] " + str(uid) + " opened the leaderboard")
	total_msg = ""
	leaderboard = sorted(balances, key=balances.get, reverse=True)
	for i in range(0, 10):
		member = channel.guild.get_member(leaderboard[i])
		if member is None:
			total_msg+= "#" + str(i + 1) + ": (err: user not found)\n"
			if leaderboard[i] in balances:
				del balances[leaderboard[i]]
			if leaderboard[i] in paydays:
				del paydays[leaderboard[i]]
			continue
		total_msg+= "#" + str(i + 1) + ": " + member.name + ", " + str(i_getbal(leaderboard[i])) + " grains\n"
	total_msg+= "#" + str(leaderboard.index(uid) + 1) + ": " + channel.guild.get_member(uid).name + "\n"
	return total_msg

def set_motd(uid, new):
	global motd
	global balances
	up_cost = i_getup(uid) * 3
	print("[MOTD] " + str(uid) + " tried to set the motd")
	if(up_cost > i_getbal(uid)):
		return "You need " + str(up_cost) + " 🍚 to change the MOTD\n"
	balances[uid] = i_getbal(uid) - up_cost
	motd = new
	write_save()
	return "The new MOTD is: \"" + new + "\"\n"

def show_bal(uid, recipientuid):
	if recipientuid == 1:
		return "You have " + str(i_getbal(uid)) + " 🍚\nYou currently receive " + str(i_getup(uid)) + " 🍚 per day\n"

	else:
		recipientuid = recipientuid.split(" ", 2)
		recipientuid = int(re.search(r'\d+', recipientuid[0]).group())
		return "They have " + str(i_getbal(recipientuid)) + " 🍚\nThey currently receive " + str(i_getup(recipientuid)) + " 🍚 per day\n"

def seize(uid, uplevel):
	global communism_level
	if len(uplevel) < 1 or int(uplevel) < 1:
		return "Usage: seize [upgrade level]"
	print("[COMMUNISM] " + str(uid) + " tried to seize the means of production " + str(uplevel) + " times")
	if int(uplevel) > i_getbal(uid):
		return "You do not have enough 🍚 for that\n"
	communism_level+= int(uplevel)
	balances[uid] = i_getbal(uid) - int(uplevel)
	write_save()
	return uid_to_mention(uid) + " expanded the motherland with " + uplevel + " 🍚. Communism level is now " + str(communism_level)

def pillage(uid):
	global communism_level
	print("[COMMUNISM] " + str(uid) + " tried to pillage the motherland")
	balances[uid] = i_getbal(uid) + communism_level
	communism_level = 0
	write_save()
	return uid_to_mention(uid) + " stole all the 🍚; the communism level has reset to zero"

def payup(uid):
	global paydays
	global balances
	leaderboard = sorted(balances, key=balances.get, reverse=True)
	print("[PAYDAY] " + str(uid) + " tried to upgrade their payday")
	if leaderboard[0] == uid:
		return "You cannot use payup when you are #1\n"
	up_cost = i_getup(uid) * 3
	if i_getbal(uid) >= up_cost:
		balances[uid] = i_getbal(uid) - up_cost
		paydays[uid] = i_getup(uid) + 1
		write_save()
		return "You have increased your daily reward!\n"
	else:
		return "You do not have enough 🍚 for that\n"

def payday(uid):
	global lastred
	global balances
	global redeems
	
	# Reset payday
	if lastred != datetime.date.today():
		print("[PAYDAY] Reset payday")
		redeems = []
		lastred = datetime.date.today()
	
	print("[PAYDAY] " + str(uid) + " tried to redeem their payday")
	if uid in redeems:
		return "You have already redeemed your daily reward\n"
	payup_amnt = i_getup(uid)
	comm_amnt = min(math.floor(communism_level / 10), payup_amnt)
	balances[uid] = i_getbal(uid) + payup_amnt + comm_amnt
	redeems.append(uid)
	write_save()
	return "You have redeemed your daily reward\nYou also received " + str(comm_amnt) + " 🍚 courtesy of the motherland"

def send(uid, second_split):
	second_split = second_split.split(" ", 2)
	amount = int(second_split[0])
	recipientuid = int(re.search(r'\d+', second_split[1]).group())
	global balances
	if amount < 0:
		return "Smh I patched that"
	elif i_getbal(uid) >= amount:
		balances[uid] = i_getbal(uid) - amount
		balances[recipientuid] = i_getbal(recipientuid) + amount
		write_save()
		return "You sent " + str(amount) + " rice."
	else:
		return "You don't have enough rice"

def lottery(uid, amount):
	global balances
	val = random.randint(1, 10)
	if amount < 0:
		return "I patched that smh"
	elif val < i_getbal(uid):
		if val == 1: # 1/21 chance of winning the lottery
			reward = amount * 2
			balances[uid] = i_getbal(uid) + reward
			return "Wowee you just won and got " + str(reward) + " rice."
		else:
			balances[uid] = i_getbal(uid) - amount
			return "You lost " + str(amount) + " rice. This is why you don't do the lottery."
	else:
		return "Not enough rice buddo"

def seemaxup(uid):
	global paydays
	global balances

	up_cost = i_getup(uid) * 3
	totalRice = i_getbal(uid)
	timesRiced = 0;
	
	while(totalRice >= up_cost):
		totalRice = totalRice - up_cost
		timesRiced = timesRiced + 1
		up_cost = up_cost + 3

	final = i_getup(uid) + timesRiced
	return "You would end with the payday of " + str(final) + " after " + str(timesRiced) + " payups"

def maxup(uid):
	global paydays
	global bal

	totalRice = i_getbal(uid)
	timesRiced = 0;
	x = 1
	
	leaderboard = sorted(balances, key=balances.get, reverse=True)
	print("[PAYDAY] " + str(uid) + " tried to upgrade their payday")
	if leaderboard[0] == uid:
		return "You cannot use max payup when you are #1\n"

	while(x == 1):
		up_cost = i_getup(uid) * 3
		if i_getbal(uid) >= up_cost:
			balances[uid] = i_getbal(uid) - up_cost
			paydays[uid] = i_getup(uid) + 1
			write_save()
			x = 1
			timesRiced = timesRiced + 1
		else:
			x = 0

	final = i_getup(uid) + timesRiced
	return "You ended up with a payday of " + str(final) + " after " + str(timesRiced) + " payups"
	
	

def read_save():
	global communism_level
	fd = open("currency.dat", "r")
	add_dict = paydays
	for line in fd:
		if communism_level == -1:
			communism_level = int(line)
			continue
		if(line == "\n"):
			add_dict = balances
			continue
		split_text = line.split(" ")
		add_dict[int(split_text[0])] = int(split_text[1])

def write_save():
	global paydays
	global balances
	fd = open("currency.dat", "w+")
	fd.write(str(communism_level) + "\n")
	for uid, up in paydays.items():
		fd.write(str(uid) + " " + str(up) + "\n")
	fd.write("\n")
	for uid, bal in balances.items():
		fd.write(str(uid) + " " + str(bal) + "\n")
def help():
	return "Commands are: `payday | payup | bal {person} | set_motd [message] | leaderboard | seize [uplevel] | lottery [gamble amount] | pillage | send [amount] [recipient] | seemaxup | maxup`"
client = discord.Client()

@client.event
async def on_ready():
	print("Logged into Discord as " + str(client.user.name))

@client.event
async def on_message(message):
	msg_uid = message.author.id
	msg_split = message.content.split(" ", 2)
	msg_channel = message.channel
	if msg_split[0] != "?rice":
		return
	total_msg = ""
	total_msg+= motd + '\n'
	if msg_split[1] == "payday":
		total_msg+= payday(msg_uid)
	elif msg_split[1] == "help":
		total_msg += help()
	elif msg_split[1] == "payup":
		total_msg+= payup(msg_uid)
	elif msg_split[1] == "bal":
		try:
			total_msg += show_bal(msg_uid, msg_split[2])
		except:
			total_msg += show_bal(msg_uid, 1)
	elif msg_split[1] == "set_motd":
		total_msg+= set_motd(msg_uid, msg_split[2])
	elif msg_split[1] == "leaderboard":
		total_msg+= show_leaderboard(msg_channel, msg_uid)
	elif msg_split[1] == "lb":
		total_msg+= show_leaderboard(msg_channel, msg_uid)		
	elif msg_split[1] == "seize":
		total_msg+= seize(msg_uid, msg_split[2])
	elif msg_split[1] == "lottery":
		total_msg += lottery(msg_uid, int(msg_split[2]))
	elif msg_split[1] == "pillage":
		total_msg+= pillage(msg_uid)
	elif msg_split[1] == "send":
		total_msg+= send(msg_uid,msg_split[2])
	elif msg_split[1] == "seemaxup":
		total_msg += seemaxup(msg_uid)
	elif msg_split[1] == "maxup":
		total_msg += maxup(msg_uid)
	else:
		await msg_channel.send("Unknown command")
		return
	await msg_channel.send(total_msg)

# Init
read_save()
client.run(sys.argv[1])
