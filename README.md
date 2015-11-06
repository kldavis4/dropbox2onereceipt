# Dropbox 2 OneReceipt

This is a small web application written in Python and intended to run on the Google App Engine that will monitor a user-specified Dropbox folder for new items and email them to a configurable email address. It is intended to mostly automate uploading of receipts to OneReceipt but can be adapted to other purposes as well.

## Setup

### Step 1 - Install Dropbox App
  * Install the Dropbox [Android](https://www.dropbox.com/android) or [iOS](https://itunes.apple.com/us/app/dropbox/id327630330?mt=8) app on your smartphone
  * Login or Register
  * Enable [Camera Upload](https://www.dropbox.com/en/help/307)

### Step 2 - Create Dropbox App
  * Create a new [Dropbox App](https://www.dropbox.com/developers/apps/create)
   * Select the 'Dropbox API' option
   * Set access to 'App folder'
   * Give the app a name (like 'Receipts123') and click Create
   * In the section with App key & App Secret, copy and paste the key and secret and save it for later

### Step 3 - Get Dropbox App Access Token
  * Install the [Dropbox Python Library](https://www.dropbox.com/developers-v1/core/sdks/python)
  * Download and extract the Python SDK
  * Install the library
   * `pip install dropbox`
  * From the commandline, navigate to the extracted sdk and go to the `example` directory
  * Edit `cli_client.py` and update the values of `APP_KEY` and `APP_SECRET` to match the key and secret from step 2 above. Save the file.
  * Execute cli_client.py and at the prompt type `login`
  * Copy and paste the url in the instructions to a new browser window. Click the Allow button.
  * Copy the authorization code and paste it into the terminal and hit enter
  * Type `exit`. Open `token_store.txt` which contains your Dropbox app access token.
  * Copy the token after the `oauth2:` prefix and save it for later

### Step 4 - Get the Google App Engine
  * Download the [Python SDK](https://cloud.google.com/appengine/downloads?hl=en) and install it
  * Open the Google App Engine Launcher
  * Login to the [Developer Console](https://console.developers.google.com/project)
  * Create a new project and note the project id
  * Configure your email address in the Application Settings, under Compute/App Engine
   * Emails will not be sent if this is not configured
   * You can only configure sender emails associated with the account being using to access the developer console

### Step 5 - Checkout dropbox2onereceipt
  * `git clone git@github.com:kldavis4/dropbox2onereceipt.git`
  * Change to the project directory and copy `app_config.py.sample` to `app_config.py`
  * Edit `app_config.py` and replace the access token with the one from Step 3
  * Configure the `destination_email`, `sender_email`, and `sent_folder` as well
  * Edit app.yaml and set the application field to project id from Step 4

### Step 6 - Deploy the application to Google App Engine
 * In the App Engine Launcher, select Add Existing Project
 * Locate the project directory you checked out in Step 5 and select it
 * Hit Deploy (or test locally first at http://localhost:8080)

## Usage

### Step 1 - Get your receipts into Dropbox
  * Take some pictures of your receipts
  * Once the images have automatically uploaded to dropbox, open your browser and navigate to the [https://www.dropbox.com/home/Camera Uploads](Camera Uploads) folder
  * Select the receipt photos and move them to the folder under the Apps directory with the application that you created in Step 2 above

### Step 2 - Send your receipts to OneReceipt
  * Navigate to the `/scan` url on your Google App Engine application. This will scan the folder in Dropbox, download each file and email it to the configured address, and then move it to a sent folder.
   * It is possible to configure a cron job that will automatically trigger the scan periodically. See the [documentation](https://cloud.google.com/appengine/docs/python/config/cron?hl=en) for more details.

## Quotas
 * Depending on frequency of usage, number of receipts, and size of the images being uploaded, this application should be able to run under the free quotas. Check the App Engine Quotas to see how much the app is using. 
 * Current daily quotas
  * Recipient Emails: 100
  * Attachment Data: 97.7MB

## Logging
 * If somethings not working right, go to the Monitoring section and select Logs to view them
 * The app will log any unexpected errors
