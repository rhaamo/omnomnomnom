# OmNomNomNom

Manage your shelf of canned food. With OpenFoodFacts integration for products source only.

# Screenshots

Soon!

# Installation

Note: it does requires python 3.7 minimum ! And the latest or LTS nodejs for frontent.

```
useradd -m -s /bin/bash omnomnomnom
sudo su - omnomnomnom
git clone https://dev.sigpipe.me/dashie/omnomnomnom.git
python3 -m virtualenv venv
source venv/bin/activate
# API
cd api
pip install -r requirements.txt
pip install waitress
cp config/production_secret_sample.py config/production_secret.py
$EDITOR config/production_secret.py
export APP_SETTINGS='config.production_secret.Config'
export FLASK_ENV=production
flask db upgrade
flask db-datas 000-seeds

# Front
cd ../front
yarn install
$EDITOR src/main.js
# Change baseURL to
# "https://your.vhost"
yarn build

exit
```

VHost and service install, as root:
```
cp /home/omnomnomnom/omnomnomnom/dist/vhost.nginx /etc/nginx/sites-available/omnomnomnom
$EDITOR /etc/nginx/sites-available/omnomnomnom
# change what you need to change
cp /home/omnomnomnom/omnomnomnom/dist/omnomnomnom-web.service /etc/systemd/system/
$EDITOR /etc/systemd/system/
# change paths if needed
systemctl enable omnomnomnom-web
systemctl start omnomnomnom-web
```

Create an user:
```
sudo su - omnomnomnom
cd omnomnomnom
source venv/bin/activate
cd api
flask users create
# if needed:
flask users confirm
```

You should add to the `~/.bashrc` file of the `omnomnomnom` user the following:
```
export APP_SETTINGS='config.production_secret.Config'
export FLASK_ENV=production
```

So it ensures you always have the right production config when running commands.

# Update
Check changelog (if any) then:
```
sudo su - omnomnomnom
cd omnomnomnom
git pull
cd front
yarn install
yarn build
# if there is any db/api changes:
cd ~/omnomnomnom/api
flask db upgrade
# and run any seed if mentioned in changelog
```

Don't forget to restart the `omnomnomnom-web` service if there was any api change.
