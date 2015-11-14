# Insomnia
Sleepless nights? Working on that one important project? Or just surfing the web
too much? Share your guilty feeling of I-Should-Have-Gone-To-Sleep-6-Hours-Ago.

Check it out: https://insomnist.herokuapp.com

## Quickstart

```
$ redis-server&
$ pip install -r requirements.txt
$ foreman start
```

## Requirements

+ python3 + python3pip
+ `pip install -r requirements.txt`
+ `gem install foreman`
+ Redis

## Environment
Copy `.env.template` over to `.env` and set a valid Redis URL in `R`.

## Starting the server
You can run the server by using the following command

```
foreman start
```

Automatic restart happens upon changes to the `app.py` file.
