# OmNomNomNom

Manage your shelf of canned food. With OpenFoodFacts integration for products source only.

# Installation

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