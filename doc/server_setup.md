## Server setup

This will setup a Causeway server to support the Rein market and was tested on Ubuntu Server 14.04.3 x64.

### User setup

    adduser cw     
    
Choose a strong password of 12+ chars.
    
    sudo visudo

Then make a copy of the root "all all" line and change root to cw. [ref](https://www.vultr.com/docs/setup-a-non-root-user-with-sudo-access-on-ubuntu)

### Install pre-requisites

Login as user `cw` and install git, pip, and sqlite..

    su - cw
    sudo apt-get update && sudo apt-get install git python3-pip sqlite3
    
Clone the repo. Note we're using pip3 because this server is written for Python 3 (tested on version 3.4).
    
    git clone https://github.com/ReinProject/causeway.git
    cd causeway
    sudo pip3 install -r requirements.txt

Setup the causeway server itself (simplified version of what's in the Causeway README. Double check to see if anything changed).

    sqlite3 causeway.db < schema.sql

Then you'll need to copy default\_settings.py to settings.py. If you have installed to a different location or would like to place the db file elsewhere, change DATABASE to the full path where you created the database.

Finally we run the server, under a screen session:

    exit
    screen
    su - cw
    cd causeway
    python3 causeway-server.py

Now you can close the terminal window and the server will keep running on our server. Re-attach next time you login as root with screen -r.
