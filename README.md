# Brikard server
Django + Postgre + Bootstrap (in development).

### HOWTO (docker)
1. [Install Docker Community Edition](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)    
2. Install docker-compose into python3, e.g. `pip3 install --user docker-compose`    
3. Add your user to the docker group. `sudo usermod -a -G docker username` ; you may have to reboot after this step for you to show up in the group.    
    
You can then use the `brikard-docker-compose` script as a drop in replacement for docker-compose. For example, to start the server you can run `brikard-docker-compose up --build`.    

Cleaning up after docker for a clean rebuild:     
1. `./cluspro-docker-compose rm` will remove the containers       
2. `docker volume prune`      
3. ssh into scc2 and remove you development jobs directory, likely by     
   `rm -rf /projectnb/cluspro/dev/${USER}/jobs/*`    
