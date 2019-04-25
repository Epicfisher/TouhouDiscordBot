# Heroku CACHE_DIR Purger

*This is not an actual Discord Bot! This Branch purely exists to be loaded into Heroku to force a purge of the CACHE_DIR folder. If you don't know what this is, return to the Master branch, where you'll be able to find the latest version of the bot.*

---

If you do host this bot on Heroku, here's a quick overview of how this branch works:

Deploying your Heroku project with this "cache-purge" branch removes all installed requirements, and since Heroku likes to cache it's requirements when you first download them, this will effectively force Heroku to redownload and upgrade to the latest versions, once you redeploy from the main branch.

TLDR: Deploy this branch and then the Main branch to upgrade your requirements.
