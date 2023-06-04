# Update Hubitat

This script allows for the automation of keeping your Hubitat Elevation hub updated with the latest firmware. This is my own creation, and is not endorsed by Hubitat Inc. Use at your own risk.

### Usage
First you'll need to install the requests python module. 
`pip install requests`

Then create a cron job that calls 
`py updateHubitat.py` on a schedule to your liking. I run it nightly.

### License
I'm releasing this under the MIT license. 
