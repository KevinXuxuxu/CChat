# CChat
- A command line tool for chatting.
- Basic P2P chatting is finished. More functions are to be added including
  - multi person chatting
  - better UI (considering `curses`)

### Usage

Basic commands:

- `name`: set current name to be displayed over conversation. (default `Host`)
- `port`: set current port for establishing host (default `9527`)
- `host`: host a conversation
	1. `waiting for connection`
	-  if anyone connects: `[127.0.0.1:54516] trying to connect`
	- enter `confirm` and start conversation
- `connect`: connect to a given host
	1. `where?` enter ip and port `localhost:9527`
	2. `waiting for acception`
	3. `confirmed` and start conversation
