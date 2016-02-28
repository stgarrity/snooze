I've been using [Mailbox](http://www.mailboxapp.com) since it was distributed via TestFlight and my email load broke the servers more than once ... and it quickly became an absolutely integratl part of my daily life, workflow, :sob: my family even :sob:. So obviously I was super sad to see it shut down last week. Rather than attempt to write a thoughtful, sentimental, or funny tribute (none of which I'm good at), I chose to memorialize my love for Mailbox in code.

Aghast at having to live without snooze going forward (and yes, I played with all the other imitation clients, they just can't hold a candle to Mailbox), I hacked this together on a cab ride from Manhattan to Newark Airport. Enough people have asked me about it that I figured I'd share. It's still a work in progress (PRs welcome).

This in no way holds a candle to Mailbox. The UX is whatever second-rate email client you're using now (you just move the message to one of four labels, "Tonight", "Tomorrow", "This Weekend", "Next Week" (all nested under ".Snooze", and auto-created for you on first run), and it will pull it back into your inbox at the appropriate time), it doesn't allow custom scheduling, swipes don't work as well, there's no auto-swiping, etc. But at least it gives you snooze back!

All the credit here goes to the incredible team at Mailbox for changing the way so many of us looked at email, whether it was swipes, or unified inboxes, or snooze, or that [Violet Hour](http://www.markbernstein.org/Aug10/TheVioletHour.html) of the Inbox Zero image of the day. Thanks for all that you did, guys & gals!

## Setup:

1. copy email_snooze.py to a directory where you want it to live (preferrably on a server somewhere, we rely on cron to run this every day)

2. run "pip install -r requirements.txt" to install the needed dependencies

3. edit the users = line (~5th to last line in the file) to have your email addresses, or at least the right number of emails you'd like to use with this (the actual strings are all relative to issued OAuth tokens in the app, so only used for debugging)

4. create a Google API app using the wizard here: https://console.developers.google.com/start/api?id=gmail

5. create client credentials for that app of type "Other" and download the JSON into "client_secret.json" in the same directory as email_snooze.py

6. run "python email_snooze.py none --noauth_local_webserver" and follow the prompts to grant access to your email account(s)

7. copy the lines from "crontab_file" into your crontab (using "crontab -e"), and making sure to insert the correct path to email_snooze.py (and potentially update your times)

## Known issues:

- scheduling via cron is ghetto
- current scheduling doesn't handle DST well if your computer timezone is UTC
- very little error handling, and it won't tell you if it fails
- does not currently remove the snooze label, so if you just archive the message it will effectively snooze again. This is "by design" but I'm far from convinced it's the right design. If you'd like to change it, simply add 

```
"removeLabelIds": [search_label]
```

to the body dict of the thread .modify() call per https://developers.google.com/gmail/api/v1/reference/users/threads/modify