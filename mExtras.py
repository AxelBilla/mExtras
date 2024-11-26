#bot url

import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from private.config import token
from datetime import datetime

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
        open(path+"/data.txt","w")
        file = open(path+"/data.txt", "w")
        word=["[ROLE]: active\n"]
        file.writelines(word)
        file.close()

#syncs the commands
@bot.tree.command(name='sync', description='| BOT OWNER ONLY |')
async def sync(ctx):
    print(f"\n\n\n{ctx.user.name} is trying to access SYNC. [ID]: {ctx.user.id}, [SERVER]: {ctx.guild.name}")
    if ctx.user.id == owner_id:
        await bot.tree.sync()
        print("They're this bot's owner.\n")
        await ctx.response.send_message('synced.', ephemeral=True)
    else:
        print("They're not this bot's owner")
        await ctx.response.send_message('You do not have the permission(s) required to do this.', ephemeral=True)

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







#gives a default role to be given (if it doesn't exist)
@bot.tree.command(name='default_act', description='[ADMIN] Adds a default access role ("admin") to pre-existing servers.')
@app_commands.check(owner_admin)
async def default_role(ctx):
    print("[/default_role]")
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "r")
    wordList=file.readlines()
    file.close()
    if "[ROLE]: " not in wordList[0]:
        wordList.insert(0, "[ROLE]: active\n")
        fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "w")
        fileWrite.writelines(wordList)
        fileWrite.close()
        await ctx.response.send_message('"admin" was made the default access role.', ephemeral=True)
        print('They made "admin" the new default role')
    else:
        rolename=wordList[0].strip("\n").replace("[ROLE]: ", "")
        print(f'"{rolename}" was already the default role')
        await ctx.response.send_message(f'"{rolename}" has already been set up as the access role.', ephemeral=True)

#sets the role to be given
@bot.tree.command(name='role_act', description='[ADMIN] Setup a role to access advanced commands (i.e, "admin")')
@app_commands.check(owner_admin)
async def setupAllowedRole(ctx, role: str):
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "r")
    wordList=file.readlines()
    file.close()
    rolename=wordList[0].strip("\n").replace("[ROLE]: ", "")
    print(f'[/role_disk]\n[ORIGINAL ROLE]: "{rolename}"\n[NEW ROLE]: "{role}"')
    wordList[0]="[ROLE]: "+role+"\n"
    fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "w")
    fileWrite.writelines(wordList)
    fileWrite.close()
    await ctx.response.send_message(f"\"{role}\" has been made the server's only role with access to the advanced commands!", ephemeral=True)






#checks if user has sent at least once message in the last 7 days
@tasks.loop(hours=1)
async def hourlyCheck(ctx):
    addPath(ctx)
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "r")
    userList=file.readlines()
    file.close()
    for i in range(1, len(userList)-1):
        nowDate = datetime.datetime.now()
        content=userList[i].split
        userID=discord.utils.get(ctx.guild.members, id=content[0].strip("[]:"))
        savedDate=datetime.datetime.strptime(content[1], "%d/%m/%Y")
        timeGap = nowDate - savedDate
        if timeGap.days > 7:
            role=userList[0].split
            role=role[1]
            role=discord.utils.get(ctx.guild.roles, name=role)
            await userID.remove_roles(role)

#updates upon user message and gives them the role if they don't have it
#on message sent
async def onMessageUpdate(ctx):
    addPath(ctx)
    file = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "r")
    userList=file.readlines()
    file.close()
    for i in range(1, len(userList)-1):
        content=userList[i].split()
        userID=content[0].strip("[]:")
        if userID==ctx.user.id:
            content[1]=datetime.now().strftime("%d/%m/%Y")
            userList[i]=' '.join(content)+'\n'
            fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "w")
            fileWrite.writelines(userList)
            fileWrite.close()
            check=False
            break
    if check:
        nowDate=datetime.now().strftime("%d/%m/%Y")
        fileWrite = open(dir+"/serverData/" + str(ctx.guild.id) + "/" + "data.txt", "a")
        fileWrite.write(f"[{ctx.user.id}]: {nowDate}\n")
        fileWrite.close()
    role=userList[0].split
    role=role[1]
    role=discord.utils.get(ctx.guild.roles, name=role)
    await ctx.user.add_roles(role)

bot.run(token)
