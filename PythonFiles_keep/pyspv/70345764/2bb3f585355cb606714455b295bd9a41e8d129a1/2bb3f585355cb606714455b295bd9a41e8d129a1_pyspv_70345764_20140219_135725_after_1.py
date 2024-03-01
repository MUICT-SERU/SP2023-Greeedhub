import json
import pyspv
import sys
import time
import traceback

import xmlrpc.client 
from xmlrpc.server import SimpleXMLRPCServer

RPC_LISTEN_ADDRESS = '127.0.0.1'
RPC_LISTEN_PORT    = 18899

spv = None

def exception_printer(f):
    def f2(*args, **kwargs):
        nonlocal f
        try:
            return f(*args, **kwargs)
        except:
            traceback.print_exc()
            return traceback.format_exc()
    f2.__name__ = f.__name__
    return f2

@exception_printer
def getinfo():
    return {
        'balance': spv.coin.format_money(sum(v for v in spv.wallet.balance.values())),
        'blocks': spv.blockchain.best_chain['height'],
        'version': pyspv.VERSION,
        'platform': sys.platform,
        'python': sys.version,
        'user-agent': '',
        'app-name': spv.app_name,
        'testnet': spv.testnet,
        'coin': spv.coin.__name__,
    }

@exception_printer
def sendtoaddress(address, amount, memo=''):
    transaction_builder = spv.new_transaction_builder(memo=memo)
    transaction_builder.process_change(pyspv.PubKeyChange)

    # Determine the payment type based on the version byte of the address provided
    # (I don't think this is the proper long term solution to different payment types...)
    address_bytes = int.to_bytes(pyspv.base58.decode(address), spv.coin.ADDRESS_BYTE_LENGTH, 'big')
    k = len(spv.coin.ADDRESS_VERSION_BYTES)
    if address_bytes[:k] == spv.coin.ADDRESS_VERSION_BYTES:
        transaction_builder.process(pyspv.PubKeyPayment(address, spv.coin.parse_money(amount)))
    else:
        k = len(spv.coin.P2SH_ADDRESS_VERSION_BYTES)
        if address_bytes[:k] == spv.coin.P2SH_ADDRESS_VERSION_BYTES:
            transaction_builder.process(pyspv.ScriptHashPayment(address, spv.coin.parse_money(amount)))
        else:
            return "error: bad address {}".format(address)

    tx = transaction_builder.finish(shuffle_inputs=True, shuffle_outputs=True)

    if not tx.verify_scripts():
        raise Exception("internal error building transaction")

    spv.broadcast_transaction(tx)

    return {
        'tx': pyspv.bytes_to_hexstring(tx.serialize(), reverse=False),
        'hash': pyspv.bytes_to_hexstring(tx.hash()),
    }

@exception_printer
def getbalance():
    return dict((k, spv.coin.format_money(v)) for k, v in spv.wallet.balance.items())

@exception_printer
def getnewaddress(label='', compressed=0):
    compressed = bool(int(compressed))
    pk = pyspv.keys.PrivateKey.create_new()
    spv.wallet.add('private_key', pk, {'label': label})
    return pk.get_public_key(compressed).as_address(spv.coin)

@exception_printer
def listspends():
    spendable = []
    not_spendable = []
    for spend in spv.wallet.spends.values():
        if spend['spend'].is_spendable(spv):
            spendable.append(str(spend['spend']))
        else:
            not_spendable.append(str(spend['spend']) + ', confirmations={}'.format(spend['spend'].get_confirmations(spv)))
    return 'Spendable:\n' + '\n'.join(spendable) + '\nNot Spendable ({} confirmations required):\n'.format(spv.coin.TRANSACTION_CONFIRMATION_DEPTH) + '\n'.join(not_spendable)

@exception_printer
def dumppubkey(address):
    '''PubKeyPaymentMonitor has to be included for this to work'''
    metadata = spv.wallet.get_temp('address', address)
    if metadata is None:
        return 'error: unknown address'

    return metadata['public_key'].as_hex()

@exception_printer
def dumpprivkey(address_or_pubkey):
    '''PubKeyPaymentMonitor has to be included for this to work'''
    metadata = spv.wallet.get_temp('address', address_or_pubkey)
    if metadata is not None:
        public_key = metadata['public_key']
    else:
        public_key = pyspv.keys.PublicKey.from_hex(address_or_pubkey)

    metadata = spv.wallet.get_temp('public_key', public_key)
    if metadata is None:
        return 'error: unknown key'
    return metadata['private_key'].as_wif(spv.coin, public_key.is_compressed())

@exception_printer
def genmultisig(nreq, *pubkeys):
    nreq = int(nreq)
    assert 1 <= nreq <= len(pubkeys)

    pubkeys = [pyspv.keys.PublicKey.from_hex(pubkey) for pubkey in pubkeys]
    pubkeys.sort()

    # build the M-of-N multisig redemption script and add it to the wallet
    # (the p2sh monitor will notice that we added a redemption script to the 
    # wallet and start watching for transactions to it

    script = pyspv.script.Script()
    script.push_int(nreq)

    for pubkey in pubkeys:
        script.push_bytes(pubkey.pubkey)

    script.push_int(len(pubkeys))
    script.push_op(pyspv.script.OP_CHECKMULTISIG)

    redemption_script = script.program
    address = pyspv.base58_check(spv.coin, spv.coin.hash160(redemption_script), version_bytes=spv.coin.P2SH_ADDRESS_VERSION_BYTES)

    try:
        spv.wallet.add('redemption_script', redemption_script, {})
    except pyspv.wallet.DuplicateWalletItem:
        # No worries, we already have this redemption script
        pass

    return {
        'address': address,
        'redemption_script': pyspv.bytes_to_hexstring(redemption_script, reverse=False),
        'pubkeys': [ pubkey.as_hex() for pubkey in pubkeys ],
        'nreq': nreq,
    }

def server_main():
    global spv

    spv = pyspv.pyspv('pyspv-simple-wallet', logging_level=pyspv.DEBUG, peer_goal=4, testnet=True, listen=('0.0.0.0', 8336))
                #listen=None,
                #proxy=...,
                #relay_tx=False,

    rpc_server = SimpleXMLRPCServer((RPC_LISTEN_ADDRESS, RPC_LISTEN_PORT), allow_none=True)
    rpc_server.register_function(getnewaddress)
    rpc_server.register_function(getbalance)
    rpc_server.register_function(sendtoaddress)
    rpc_server.register_function(getinfo)
    rpc_server.register_function(listspends)
    rpc_server.register_function(dumppubkey)
    rpc_server.register_function(dumpprivkey)
    rpc_server.register_function(genmultisig)

    try:
        rpc_server.serve_forever()
    except KeyboardInterrupt:
        pass

    spv.shutdown() # Async shutdown
    spv.join()     # Wait for shutdown to complete

def rpc_call():
    s = xmlrpc.client.ServerProxy("http://{}:{}".format(RPC_LISTEN_ADDRESS, RPC_LISTEN_PORT))
    response = getattr(s, sys.argv[1])( *sys.argv[2:] )

    if isinstance(response, str) or response is None:
        print(response)
    else:
        print(json.dumps(response))

if __name__ == "__main__":
    if len(sys.argv) == 1 or all(x.startswith('-') for x in sys.argv[1:]):
        try:
            server_main()
        except:
            traceback.print_exc()
    else:
        rpc_call()

