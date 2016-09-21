#! /bin/bash
# Get the pem in tmp
echo "$(tput setaf 4)Validating following:$(tput sgr0)"
echo "================================="
echo " - Verify the PEM files
 - Validate the Cert
 - Check setup with Chef Server"
echo "================================="
echo "\n"
sudo scp -o stricthostkeychecking=no -i /cheflab/conf/keys/cheflab-server.pem vagrant@cheflab-server:/home/vagrant/*.pem /tmp > /dev/null 2>&1
server_md5=`md5sum /tmp/learnchef-validator.pem  | cut -f1 -d' '`
client_md5=`md5sum ${HOME}/.chef/learnchef-validator.pem  | cut -f1 -d' '`
if [ -f "/vagrant/.chef/learnchef-validator.pem" ] && [ $server_md5 == $client_md5 ];
then
  sudo scp -o stricthostkeychecking=no -i /cheflab/conf/keys/cheflab-server.pem vagrant@cheflab-server:/home/vagrant/*.pem .chef/
else
   echo "$(tput setaf 3)You already have right keys...Checking the SSL cert$(tput sgr0)"
fi

knife ssl check > /dev/null 2>&1

if [ $? -eq 0 ];
then
  echo "\n"
  echo "$(tput setaf 3)SSL Cert Validated$(tput sgr0)"
else
   echo "$(tput setaf 1)Wrong SSL Cert... Downloading the right one now$(tput sgr0)"
   knife ssl fetch
fi

knife client list > /dev/null 2>&1

if [ $? -eq 0 ]
then
	echo "\n"
	echo "$(tput setaf 2)Setup complete, start working on your Cheflab Receipes...n'joy!!$(tput sgr0)"
else
	echo "$(tput setaf 1)Please verify your knife config or check network connectivity to cheflab-server$(tput sgr0)"
fi


