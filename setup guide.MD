More will appear in the future and this will be an MD

Create a discord bot and add sites to oauth 
you'll want to add all the sites to your redirect_uri in the oauth section of your application

1. redirect_url in the env is the general oauth that will also receive data that will be seen with /data
2. website_redirect_url is the env key value for the oauth page that will download your data with json and sqlite (will also have stats)
3. stats_redirect_url is the env value for stats only appearing, not everyone can read the json.
4. You will need to run a session of psql env value is PSQL_URL.
5. Run both systemd seperatetly (rpc will handle data transfer.)

To Setup the systemtcl:

```bash
systemctl --user enable --now OauthBot.service
systemctl --user enable --now OauthServer.service
```

To restart the Systemtcl (if the file is in .config/systemd/user):

```bash
systemctl --user restart OauthBot.service &&  # journalctl --user -u OauthBot.service Oauth Bot  
systemctl --user restart OauthServer.service && journalctl --user -u OauthServer.service # Oauth server
```

More coming soon.
