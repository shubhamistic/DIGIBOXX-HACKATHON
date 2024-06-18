<a name="readme-top"></a>

<div align="center">
  <h3 align="center">DIGIBOXX-HACKATHON</h3>
  Backend for Face Recognition System designed for the Digiboxx.com Hackathon
  <p align="center">
    <a href="https://github.com/shubhamistic/DIGIBOXX-HACKATHON"><strong>Explore the docs »</strong></a>
    <br />
    ·
    <a href="https://github.com/shubhamistic/DIGIBOXX-HACKATHON/issues">Report Bug</a>
    ·
    <a href="https://github.com/shubhamistic/DIGIBOXX-HACKATHON/issues">Request Feature</a>
    ·
  </p>
</div>

## SETUP (Ubuntu)

```bash
sudo apt update
```

- Install required packages for mysqlclient:
  ```bash
  sudo apt install pkg-config
  sudo apt install libmysqlclient-dev
  sudo apt-get install libpython3.9-dev default-libmysqlclient-dev build-essential
  ```

- Install NGINX:
  ```bash
  sudo apt install nginx
  ```

- Open nginx configuration file:
  ```bash
  sudo nano /etc/nginx/sites-available/default
  ```

  Clear the contents of the file and add the following lines (SAVE & EXIT):
  ```
  server {
    server_name <example.com> <vpc-ip-address>;
    location / {
        include proxy_params;
        proxy_pass http://localhost:5001;
    }

    location /socket.io {
      include proxy_params;
      proxy_http_version 1.1;
      proxy_buffering off;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "Upgrade";
      proxy_pass http://localhost:5001/socket.io;
    }
  }
  ```
  
- Make sure nginx is listening to port 80 and 443:
  ```bash
  sudo iptables -I INPUT -p TCP --dport 80 -j ACCEPT
  sudo iptables -I INPUT -p TCP --dport 443 -j ACCEPT
  ```

- Open bash profile:
  ```bash
  sudo nano ~/.bash_profile
  ```

- Append these lines inside bash profile (SAVE & EXIT):
  ```
  export SECRET_KEY="<your-secret-key(any random string)>"
  export DB_USER="<your mysql username>"
  export DB_PASS="<your mysql password>"
  ```
  
- Execute commands from a bash_profile in current shell environment:
  ```bash
  source ~/.bash_profile
  ```
  
- Install MySQL:
  ```bash
  sudo apt install mysql-server
  ```
  
- Change MySQL password:
  ```bash
  sudo mysql
  ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
  ```

- **DATABASE CONFIGURATION**
  - Run these [*commands*](/models/) in your mysql terminal

- Install virtualenv:
  ```bash
  sudo apt install virtualenv
  ```

- Install the repository:
  ```bash
  git clone https://github.com/shubhamistic/DIGIBOXX-HACKATHON.git
  ```

- Activate virtualenv and install the modules (use byobu):
  ```bash
  virtualenv DIGIBOXX-HACKATHON
  cd DIGIBOXX-HACKATHON
  source ~/.bash_profile
  source bin/activate
  pip install --no-cache-dir -r requirements.txt
  ```

- Run the server using:
  ```bash
  gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 127.0.0.1:5001 app:app
  ```

## [LICENSE](LICENSE)


## About the Author
This repository is maintained by [shubhamistic](https://github.com/shubhamistic), a passionate programmer and web developer. Explore my projects and join me on my journey to create innovative solutions and push the boundaries of what's possible.


<p align="right">(<a href="#readme-top">back to top</a>)</p>
