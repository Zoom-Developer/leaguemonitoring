<h1>League Monitoring</h1>
<h3>A tool to keep track of your friends' games and post that information to your discord server.</h3>

***Bot-Setup***
*-  Create a discord application and generate a token (https://discord.com/developers/applications)*<br>
*-  Create a league of legens application and generate a token (https://developer.riotgames.com/)*<br>
*-  Download League Monitoring (git clone https://github.com/Zoom-Developer/leaguemonitoring)*<br>
*-  Open config.py and write discord token to DISCORD_TOKEN and riot api token to RIOT_TOKEN, and also write log channel id in your discord server to LOG_CHANNEL*<br>
*-  In config.py in USERS write a user dict of the format {"name": {"id": "USER_DISCORD_ID"}, "name2": {"id": "USER_DISCORD_ID2"}}*<br>
*-  Download python requirenmets and run the bot*

***Commands***
*!online  -   Current list of users in the game*<br>
*!free  -   Current List of Free Champions*<br>
*!top  -   Users top (unstable)*<br>

***Attention***
*Due to the small number of allowed requests to the league api per minute, sometimes, very rarely, the bot can stop working for about 1 minute, the !top command sends a huge number of requests, so its abuse can put the bot down for a while.*<br>

*The original bot was written for the Russian community, so it has Russian localization. You can do the translation yourself.*<br>

<h3>Initially, the bot was written for a small group of people, but I decided to open its source code for everyone, good luck in using it)</h3>
