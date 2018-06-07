# Getting Started With Seele
## Setting Up a Node

#### Preparations: 
<p>
	&emsp;&emsp;Install go v1.7 or higher and the C compiler. 
</p>
<p>
	&emsp;&emsp;In seeleteam\go-seele\cmd\node, run: go build; if you are running this for the first time a node executable object will appear. 
</p>

#### Running a Node: 

##### &emsp;&emsp;On Windows:
<p>
	&emsp;&emsp;&emsp;&emsp;<b>Running a Singular Node</b>：
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;In the cmd window, run: node start -c <a href="#node1">./config/node1.json</a>
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;By default this will start the miner, not metrics. You can add flags -m "stop" to not start the miner, or -t true to start metrics.
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;<b>Running Multiple Nodes</b>：
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;In one cmd window, run: node start -c ./config/node1.json
</p>
<p>
        &emsp;&emsp;&emsp;&emsp;In a second cmd window, run: node start -c ./config/node2.json
</p>

##### &emsp;&emsp;On Linux & Mac:
<p>
	&emsp;&emsp;&emsp;&emsp;<b>Running a Singular Node</b>：
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;On terminal, run: ./node start -c ./config/node1.json
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;By default this will start the miner, not metrics. You can add flags -m "stop" to not start the miner, or -t true to start metrics.
</p>
<p>
	&emsp;&emsp;Note: in the config file under the seeleteam\go-seele\cmd\node path, there are 4 different module configurations that you can choose from to start your node. 
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;<b>Running Multiple Nodes</b>：
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;In one terminal window, run: ./node start -c ./config/node1.json
</p>
<p>
        &emsp;&emsp;&emsp;&emsp;In another terminal window, run: ./node start -c ./config/node2.json
</p>

#### Custom Configurations:
<p>
	&emsp;&emsp;You can choose your own custom module configurations and not use the default module configurations to start your node. The custom configurations are below:
</p>

<a name="node1">

	{
	  "basic":{
	    "name": "seele node1",
	    "version": "1.0",
	    "dataDir": "node1",
	    "address": "0.0.0.0:55027",
	    "coinbase": "0x010117ee8edfd14a1925e45e4cb698f195651b5a136e69ee9b394b7e8166cb1f"
	  },
	  "p2p": {
	    "privateKey": "0x8c5fe84f836732ae7935e70ed7f578851fabf533d327a36b4e9fc49b455aa721",
	    "staticNodes": [],
	    "address": "0.0.0.0:39007",
	    "networkID": 1
	  },
	  "log": {
	    "isDebug": true,
	    "printLog": false
	  },
	  "httpServer": {
	    "address": "127.0.0.1:65027",
	    "crosssorgins": [
	      "*"
	    ],
	    "whiteHost": [
	      "*"
	    ]
	  },
	  "wsserver": {
	    "address": "127.0.0.1:8080",
	    "pattern": "/ws"
	  },
	  "genesis": {
	    "accounts":{
	      "0x010171048615cfef6d03e10df133200a4266d3a8856795dd7e8873e300ecfbe4":100,
	      "0x01014a36b60fbd2bf80b1f9da08d98b11166075a595622fedca4435ec35533e0":200
	    },
	    "difficult":10000000,
	    "shard":1
	  }
	}

</a>

<table> <tbody>
<tr>
<th>Domain</th>
<th>Parameter</th>
<th>Explanation</th>
</tr>
<tr>
<th rowspan="5">basic</th>
<td>name</td>
<td>Name of node</td>
</tr>
<tr>
<td>version</td>
<td>Version of node</td>
</tr>
<tr>
<td>dataDir</td>
<td>System file path of node, used to store data</td>
</tr>
<tr>
<td>address</td>
<td>Address to start RPC server</td>
</tr>
<tr>
<td>coinbase</td>
<td>Coinbase used to mine</td>
</tr>


<tr>
<th rowspan="4">p2p</th>
<td>privateKey</td>
<td>Private key for the p2p module, not used as an account</td>
</tr>
<tr>
<td>staticNodes</td>
<td>A static node. When the node is started, it will be connected to search for more nodes.</td>
</tr>
<tr>
<td>address</td>
<td>The p2p server will listen on the TCP connection, which is used as the UDP address for the Kad protocol.</td>
</tr>
<tr>
<td>networkID</td>
<td>Used to indicate the network type. For example, 1 is testnet, 2 is mainnet.</td>
</tr>


<tr>
<th rowspan="2">log</th>
<td>isDebug</td>
<td>If IsDebug is true, the log will be on the debug level, otherwise it will be on the info level.</td>
</tr>
<tr>
<td>printLog</td>
<td>If PrintLog is true, then all logs will be printed on the console, otherwise it will be written and stored in a file.</td>
</tr>


<tr>
<th rowspan="3">httpServer</th>
<td>address</td>
<td>HTTP RPC's service address.</td>
</tr>
<tr>
<td>crosssorgins</td>
<td>Sent to the client's cross-origin resource sharing origin. Note that CORS is a type of forced safety measure by the browser, which is irrelevant to the client's custom HTTP.</td>
</tr>
<tr>
<td>whiteHost</td>
<td>Whitelist of permitted hosts.</td>
</tr>


<tr>
<th rowspan="2">wsserver</th>
<td>address</td>
<td>Address of Websocket RPC server.</td>
</tr>
<tr>
<td>pattern</td>
<td>Pattern to request path.</td>
</tr>

<tr>
<th rowspan="3">genesis</th>
<td>accounts</td>
<td>Account information of the genesis block, used for testing.</td>
</tr>
<tr>
<td>difficult</td>
<td>Difficulty level: should be difficult near the beginning in order for easier block creation.</td>
</tr>
<tr>
<td>shard</td>
<td>Number of shards in the genesis block.</td>
</tr>
</table>


#### Help:
	To run：node -h

	use "node help [<command>]" for detailed usage

	Usage:
	  node [command]

	Available Commands:
	  help        Help about any command
	  key         generate a key pair with specified shard number
	  start       start the node of Seele
	  validatekey validate the private key and generate its public key

	Flags:
	  -a, --addr string   rpc address (default "127.0.0.1:55027")
	  -h, --help          help for node

	Use "node [command] --help" for more information about a command.

#### Others:
<p>
	&emsp;&emsp;To create a public and private key, run in the command window: node key
</p>
<p>
	&emsp;&emsp;To create a public key based on the private key, run in the command window: node validatekey -k PRIVATEKEY
</p>


## Create a Client Node:
		
#### Preparations:
<p>
	&emsp;&emsp;Install go v1.7 or higher and the C compiler. 
</p>
<p>
	&emsp;&emsp;In seeleteam\go-seele\cmd\client, run: go build. If you are running this for the first time, a client executable object will appear.
</p>

#### Running a Client Node:
<p>
	&emsp;&emsp;On Windows:
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;In the command window, run: client
</p>
<p>
	&emsp;&emsp;On Mac & Linux:
</p>
<p>
	&emsp;&emsp;&emsp;&emsp;In the command window, run: ./client  
</p>

#### Help:
	To run：client -h

	rpc client to interact with node process

	Usage:
	  client [command]

	Available Commands:
	  getbalance              get the balance of an account
	  getblockbyhash          get block info by block hash
	  getblockbyheight        get block info by block height
	  getblockheight          get block height of the chain head
	  getblockrlp             get block rlp hex by block height
	  getblocktxcountbyhash   get block transaction count by hash
	  getblocktxcountbyheight get block transaction count by height
	  getinfo                 get the miner info
	  getnetworkversion       get current network version
	  getpeercount            get count of connected peers
	  getpeersinfo            get seele peers info
	  getprotocolversion      get seele protocol version
	  gettransactionbyhash    get transaction count by hash
	  gettxbyhashandindex     get transaction by hash and index
	  gettxbyheightandindex   get transaction by block height and index
	  gettxpoolcontent        get content of the tx pool
	  gettxpooltxcount        get the number of all processable transactions contained within the transaction pool
	  help                    Help about any command
	  key                     generate a key pair with specified shard number
	  miner                   miner actions
	  printblock              get block pretty printed form by block height
	  savekey                 save the key
	  sendtx                  send a tx to the miner

	Flags:
	  -a, --addr string     rpc address (default "127.0.0.1:55027")
	  -h, --help            help for client
	  -w, --wsaddr string   websocket rpc address (default "ws://127.0.0.1:8080/ws")

	Use "client [command] --help" for more information about a command.