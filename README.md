# DIGIBOXX-HACKATHON

## SETUP (Ubuntu)

- Install NGINX:
  ```bash
  sudo apt update
  
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

- Open bash profile:
  ```bash
  sudo nano ~/.bash_profile
  ```

- Append these lines inside bash profile (SAVE & EXIT):
  ```
  export SECRET_KEY="<your-secret-key(any random string)>"
  ```
  
- Execute commands from a bash_profile in current shell environment:
  ```bash
  source ~/.bash_profile
  ```

- Install virtualenv in global environment:
  ```bash
  pip install virtualenv
  ```
  
- Activate virtualenv and install the modules (use byobu):
  ```bash
  virtualenv <project-directory>
  cd <project-directory>
  source ~/.bash_profile
  source bin/activate
  pip install gunicorn gevent-websocket 
  pip install -r requirements.txt
  ```

- Run the server using:
  ```bash
  gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 -b 127.0.0.1:5001 app:app
  ```

## [LICENSE](LICENSE)


## About the Author
This repository is maintained by [shubhamistic](https://github.com/shubhamistic), a passionate programmer and web developer. Explore my projects and join me on my journey to create innovative solutions and push the boundaries of what's possible.


<p align="right">(<a href="#readme-top">back to top</a>)</p>
