# COMP3310 ASSIGNMENT3

# Install

```bash
sudo apt-get update
sudo apt-get install libmosquitto-dev
sudo apt-get install libpaho-mqtt-dev
sudo apt-get install libpaho-mqtt1.3

sudo apt update
sudo apt install mosquitto mosquitto-clients

```

# Configure

```bash
sudo systemctl enable mosquitto.service
```

```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

```bash
listener 1883
```

If you want to allow clients to connect without a username and password, make sure this line exists and is set to true:

```bash
allow_anonymous true
```

If you plan to use username and password authentication, set this to false:

```bash
allow_anonymous false
```

Mosquitto uses a password file for storing usernames and hashed passwords. You can create this with the mosquitto_passwd tool:

```bash
sudo touch /etc/mosquitto/passwd
sudo mosquitto_passwd -b /etc/mosquitto/passwd username password
```

Add the following lines to your mosquitto.conf file:

```bash
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Reload or Restart Mosquitto:

```bash
sudo systemctl restart mosquitto
```

You can test your setup using Mosquitto's client utilities:

```bash
mosquitto_sub -h localhost -t "test/topic" -u "username" -P "password"
```

```bash
mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT" -u "username" -P "password"
```

# Build the Project

```bash
mkdir build
cd build
cmake ..
make
```

# Run the project

```bash
./Publisher  # Runs the Publisher executable.
./Subscriber # Runs the Subscriber executable.
```