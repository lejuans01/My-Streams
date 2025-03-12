> [!WARNING]
> DISCLAIMER: The scripts and links provided on this GitHub page are for informational and educational purposes only. I do not claim responsibility for any issues, damages, or losses that may arise from the use of these scripts or links. Users are advised to use them at their own risk and discretion. Always review and test any code or links before implementing them in your projects.


# Pluto, Samsung, Stirr, Plex & Tubi
> [!NOTE]
> I created a discussion thread [here](https://github.com/BuddyChewChew/My-Streams/issues/3).

This script generates an m3u8 playlist from the channels provided by services such as Pluto, Samsung, Stirr, Plex, and Tubi. It is based on the original script created by matthuisman, which can be found at [matthuisman's GitHub repository](https://github.com/matthuisman/i.mjh.nz). 

## Follow this video tutorial to learn how to deploy a Google Apps Script:

[How to Deploy a Google Web App](https://rumble.com/v6qaofu-streaming-apps-script-install-instructions.html?mref=z8mk6&mc=2335k)

<a href="https://rumble.com/v6qaofu-streaming-apps-script-install-instructions.html?mref=z8mk6&mc=2335k" title="PLAY VIDEO"><img src="https://github.com/BuddyChewChew/My-Streams/blob/main/Rumble_Thumb.png" width="480" height="280"></a>

## How to Add the Script to Your Google Account

- Go <a href="https://script.google.com/home/start" target="_blank">here</a> and click the "New Project" button in the upper left corner. Then, copy the script from <a href="https://github.com/BuddyChewChew/My-Streams/blob/main/Google%20Script%20And%20Install%20Info/google_apps_script" target="_blank">google_apps_script</a> and paste it into the script editor. Once done, deploy the script.

- During the deployment process, make sure to select **"Anyone"** for the "Who has access" option, so the app can access the URL and load without requiring authentication.

- Once deployed, you will get a URL similar to:

`https://script.google.com/macros/s/...gwlprM_Kn10kT7LGk/exec`

- To use the script, you need to add the `region` and `service` parameters at the end of the URL.

Example: `https://script.google.com/macros/s/...gwlprM_Kn10kT7LGk/exec?region=all&service=Plex`

- Simply replace `region=us` and `service=Plex` with the appropriate region and service values from the available parameters listed above.

> [!TIP]
> For a cleaner and more concise URL, consider using a URL shortener like [bit.ly.com](https://bitly.com/) and appending the necessary parameters at the end.


## Script Access URL

Use the following URL to access the hosted script. Replace the `ADD_REGION` and `ADD_SERVICE` placeholders with your desired values.

Example: `https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec?region=all&service=Plex`

After customizing the URL by replacing the ADD_REGION and ADD_SERVICE placeholders with your desired region and service (e.g., us for the US region and Pluto for the service), copy the complete URL and paste it into the "Add Playlist" or "M3U8 URL" section of your IPTV application. Once added, the app will load both the channels and the guide information

## Available Service Parameter Values

Choose one of the following services to include in the `service` parameter:

Working Playlists:

- SamsungTVPlus
- Plex
- PlutoTV
- Tubi
- Stirr

Non Working Playlists:

- ~~ ~~PBS~~ ~~
- ~~ ~~PBSKids~~ ~~

## Available Region Parameter Values

Use one of these region codes to specify the region in the `region` parameter:

> [!TIP]
> Not All region codes work with every stream. I would just use `all` or `us`.
>
> 
- `all` (for all regions)
- `ar` (Argentina)
- `br` (Brazil)
- `ca` (Canada)
- `cl` (Chile)
- `de` (Germany)
- `dk` (Denmark)
- `es` (Spain)
- `fr` (France)
- `gb` (United Kingdom)
- `mx` (Mexico)
- `no` (Norway)
- `se` (Sweden)
- `us` (United States)
  Sorts the channels by their assigned channel number

  If your looking for stand alone playlist for "Pluto, Samsung, Stirr, Plex & Tubi". Go here [iptv-streams](https://github.com/iptv-org/iptv/tree/master/streams) and here for EPGs [i.mjh.nz](https://github.com/matthuisman/i.mjh.nz).

> [!IMPORTANT]
> This repository does not host or store any video files. It simply hosts a script that you can copy&paste to self-host on GOOGLE APP SCRIPTS. To the best of our knowledge, the content was intentionally made publicly available by the copyright holders or with their permission and consent granted to these websites to stream and share the content they provide.
> 
> Please note that linking does not directly infringe copyright, as no copies are made on this repository or its servers. Therefore, sending a DMCA notice to GitHub or the maintainers of this repository is not a valid course of action. To remove the content from the web, you should contact the website or hosting provider actually hosting the material.


*Thanks [jeepcook](https://github.com/jeepcook) for editing some of the script and GROK AI for the rest.*
