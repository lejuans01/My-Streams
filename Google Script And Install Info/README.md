# Pluto, Samsung, Stirr, Plex, PBS, Tubi and Roku Playlist (M3U8)

This script generates an m3u8 playlist from the channels provided by services such as Pluto, Samsung, Stirr, Plex, PBS, Tubi, and Roku. It is based on the original script created by matthuisman, which can be found at [matthuisman's GitHub repository](https://github.com/matthuisman/i.mjh.nz).

### Script Access URL

Use the following URL to access the hosted script. Replace the `ADD_REGION` and `ADD_SERVICE` placeholders with your desired values.

`https://bit.ly.com/multiservice21?region=ADD_REGION&service=ADD_SERVICE`

After customizing the URL by replacing the ADD_REGION and ADD_SERVICE placeholders with your desired region and service (e.g., us for the US region and Pluto for the service), copy the complete URL and paste it into the "Add Playlist" or "M3U8 URL" section of your IPTV application. Once added, the app will load both the channels and the guide information

**⚠️ Please note:** It is recommended to add the Google Apps Script to your own Google account or deploy the script to one of the other services, rather than relying on this publicly shared URL long-term.

### Available Service Parameter Values

Choose one of the following services to include in the `service` parameter:

- Plex
- Roku
- SamsungTVPlus
- PlutoTV
- PBS
- PBSKids
- Stirr
- Tubi

### Available Region Parameter Values

Use one of these region codes to specify the region in the `region` parameter:

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

### Available Sorting Parameter Values (optional)

Use one of the following options in the `sort` parameter to specify how you want to sort the channels:

- `name` (default):  
  Sorts the channels alphabetically by their name.

- `chno`:  
  Sorts the channels by their assigned channel number.

  # ⚠️ Host this on google scripts: [https://script.google.com](https://script.google.com)

### How to Add the Script to Your Google Account (code.gs)

Go <a href="https://script.google.com/home/start" target="_blank">here</a> and click the "New Project" button in the upper left corner. Then, copy the script from <a href="[https://github.com/BuddyChewChew/My-Streams/blob/main/Streaming%20App%20Scripts/code.gs](https://github.com/BuddyChewChew/My-Streams/blob/main/Google%20Script%20And%20Install%20Info/code.gs)" target="_blank">code.gs</a> and paste it into the script editor. Once done, deploy the script.

Follow this video tutorial to learn how to deploy a Google Apps Script:

[How to Deploy a Google Web App](https://www.youtube.com/watch?v=-AlstV1PAaA)

During the deployment process, make sure to select **"Anyone"** for the "Who has access" option, so the app can access the URL and load without requiring authentication.

Once deployed, you will get a URL similar to:

`https://script.google.com/macros/s/...gwlprM_Kn10kT7LGk/exec`

To use the script, you need to add the `region` and `service` parameters at the end of the URL. For example:

`https://script.google.com/macros/s/...gwlprM_Kn10kT7LGk/exec?region=us&service=Plex`

Simply replace `region=us` and `service=Plex` with the appropriate region and service values from the available parameters listed above.

**Tip:** For a cleaner and more concise URL, consider using a URL shortener like [bit.ly.com](https://bitly.com/) and appending the necessary parameters at the end.
