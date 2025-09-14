# Weiz Moderator Bot 

Modern Discord moderator bot with slash commands, dropdown help,.
Works on hosts where only `main.py` and Python egg are allowed; token + emoji live in `config.py`.

## Features
- Help menu with dropdown categories
- General: /kick /ban /timeout /warn /unban /addrole /moverole /movetimeout
- Automod: /enableautomod (antilink, antispam, badword warn), /setbadword, /addlinkblacklist
- Logs: /setlogchannel (detailed embeds for joins/leaves/roles/channels/messages)
- Utility: /setwelcomechannel, /setboosterchannel, /addemoji (multi), /dmuser, /embedmaker, /autopost (title-desc-channel-role-interval)
- Rolesettings: /deleterole, /createrolereaction (Desc | @role | emoji | image optional), /autorolewelcome

## Setup (Orihost Free Plan, egg locked to Python, Startup locked to main.py)
1. Upload this project folder. Ensure `requirements.txt` is installed.
2. Open `config.py` and paste your bot token into `TOKEN`.
3. Make sure **Message Content Intent** and **Server Members Intent** are enabled in the Discord Developer Portal.
4. Start. The bot status shows *Watching moderation*.
5. Use `/help` to get started.

## Notes
- All embeds are CYAN and include `weiz` footer.
- Emojis are centralized in `config.py` (EMOJI dict).
- Guild settings are stored in `data/guilds/<guild_id>.json`.

## Permissions
Invite your bot with at least: `Manage Guild`, `Manage Roles`, `Kick Members`, `Ban Members`, `Moderate Members`, `Manage Emojis and Stickers`, `Read Message History`.

Enjoy! ✨
