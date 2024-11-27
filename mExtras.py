#https://discord.com/oauth2/authorize?client_id=1311068031384027167

import os
import discord #pip install discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from private.config import token
from datetime import datetime #pip install datetime

owner_id=
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, owner_id = owner_id)
dir = os.path.dirname(__file__)

#Create server file if it doesn't exist
def addPath(ctx):
    path = dir+"/serverData/" + str(ctx.guild.id)
    if not os.path.exists(path):
        os.makedirs(path)
        open(path+"/activity.txt","w")
        file = open(path+"/activity.txt", "w")
        word=["[ROLE]: none\n"]
        file.writelines(word)
        file.close()

#checks if admin or bot owner (debug purposes)
@bot.event
async def owner_admin(ctx): #Allows me to debug stuff at will.
    print(f"\n\n\n{ctx.user.name} is trying to access a reserved ADMIN command.\n[ID]: {ctx.user.id}, [SERVER]: {ctx.guild.name}")
    addPath(ctx)
    async def predicate(ctx):
        if ctx.user.guild_permissions.administrator == True:
            print("They have administrator permissions.\n")
            return True
        else:
            if ctx.user.id == owner_id:
                print("They're this bot's owner.\n")
                return True
            else:
                print("They do not have an allowed role nor are they this bot's owner\n\n\n")
                await ctx.response.send_message('You do not have the permission(s) required to do this.', ephemeral=True)
                raise MissingPermissions(missing_permissions=['administrator'])
    a=await predicate(ctx)
    return app_commands.check(a) 

#syncs the commands
@bot.tree.command(name='sync_act', description='| BOT OWNER ONLY |')
@app_commands.check(owner_admin)
async def sync(ctx):
    print(f"\n\n\n{ctx.user.name} is trying to access SYNC. [ID]: {ctx.user.id}, [SERVER]: {ctx.guild.name}")
    if ctx.user.id == owner_id:
        await bot.tree.sync()
        print("They're this bot's owner.\n")
        await ctx.response.send_message('synced.', ephemeral=True)
    else:
        print("They're not this bot's owner")
        await ctx.response.send_message('You do not have the permission(s) required to do this.', ephemeral=True)

#gives a default role to be given (if it doesn't exist)
@bot.tree.command(name='default_act', description='[ADMIN] Adds a default access role ("admin") to pre-existing servers.')
@app_commands.check(owner_admin)
async def default_role(ctx):
    print("[/default_role]")
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "r")
    wordList=file.readlines()
    file.close()
    if "[ROLE]: " not in wordList[0]:
        wordList.insert(0, "[ROLE]: active\n")
        fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "w")
        fileWrite.writelines(wordList)
        fileWrite.close()
        await ctx.response.send_message('"active" was made the default activity role.', ephemeral=True)
        print('They made "active" the new default role\n---\n')
    else:
        rolename=wordList[0].strip("\n").replace("[ROLE]: ", "")
        print(f'"{rolename}" was already the default role.\n---\n')
        await ctx.response.send_message(f'"{rolename}" has already been set up as the activity role.', ephemeral=True)
    await hourlyCheck.start(ctx)

#sets the role to be given
@bot.tree.command(name='role_act', description='[ADMIN] Setup a role to be given/removed upon activity or lack thereof.')
@app_commands.check(owner_admin)
async def setupAllowedRole(ctx, role: str):
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "r")
    wordList=file.readlines()
    file.close()
    rolename=wordList[0].strip("\n").replace("[ROLE]: ", "")
    print(f'[/role_act]\n[ORIGINAL ROLE]: "{rolename}"\n[NEW ROLE]: "{role}"')
    wordList[0]="[ROLE]: "+role+"\n"
    fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "w")
    fileWrite.writelines(wordList)
    fileWrite.close()
    await ctx.response.send_message(f"\"{role}\" has been made the server's activity role!", ephemeral=True)
    await hourlyCheck.start(ctx)


#checks if user has sent at least once message in the last 7 days
@tasks.loop(hours=1)
async def hourlyCheck(ctx):
    print("[checking]\n")
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "r")
    userList=file.readlines()
    file.close()
    roleCheck=userList[0].split()
    roleCheck=roleCheck[1]
    if roleCheck != "none":
        for i in range(1,len(userList)):
            now=datetime.now()
            nowDate = now.strptime(now.strftime("%d/%m/%Y"), "%d/%m/%Y")
            content=userList[i].split()
            savedDate= now.strptime(content[1], "%d/%m/%Y")
            timeGap = nowDate - savedDate
            if timeGap.days > 7:
                print(f'{content[0].strip("[]:")} has been inactive for over 7 days and lost their role\n---\n')
                role=userList[0].split()
                role=role[1]
                role=discord.utils.get(ctx.guild.roles, name=role)
                member = await ctx.guild.fetch_member(content[0].strip("[]:"))
                await member.remove_roles(role)

#updates upon user message and gives them the role if they don't have it
@bot.event
async def on_message(ctx):
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "r")
    userList=file.readlines()
    file.close()
    roleCheck=userList[0].split()
    roleCheck=roleCheck[1]
    check=True
    print("[NEW MESSAGE]\n")
    if roleCheck != "none":
        for i in range(len(userList)):
            content=userList[i].split()
            userID=content[0].strip("[]:")
            if userID==str(ctx.author.id):
                content[1]=datetime.now().strftime("%d/%m/%Y")
                userList[i]=' '.join(content)+'\n'
                fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "w")
                fileWrite.writelines(userList)
                fileWrite.close()
                print("[EDIT]\n")
                check=False
                break
        if check:
            print("[NEW]\n")
            nowDate=datetime.now().strftime("%d/%m/%Y")
            fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "activity.txt", "a")
            fileWrite.write(f"[{ctx.author.id}]: {nowDate}\n")
            fileWrite.close()
        role=userList[0].split()
        role=role[1]
        print(f'Added "{role}" to "{ctx.author.id}"\n---\n')
        role=discord.utils.get(ctx.guild.roles, name=role)
        member = await ctx.guild.fetch_member(ctx.author.id)
        await member.add_roles(role)

bot.run(token)
