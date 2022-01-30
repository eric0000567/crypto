from eth_utils import address
from toolz.functoolz import return_none
from web3 import Web3
from eth_typing.evm import ChecksumAddress
from web3 import contract
from web3.contract import Contract
from decimal import Decimal
# coding: utf-8
import requests
import time
import hashlib
import hmac
import math


class WalletStatus:
    def __init__(self, wallet, pid_ = 0,
                tokenDict={},
                mainnet='https://bsc-dataseed3.binance.org/'):

        self.web3: Web3 = Web3(Web3.HTTPProvider(mainnet))
        self.wallet: ChecksumAddress = self.web3.toChecksumAddress(wallet)
        self.pid_ = pid_
        self.tokenDict = tokenDict
        

    #get cake token balanceOf
    def getTokenBalance(self,tokenName):
        if tokenName not in self.tokenDict:
            return False
        token = self.tokenDict[tokenName]
        tokenct = self.web3.eth.contract(address=token[0], abi=token[1]) 
        token_balance = tokenct.functions.balanceOf(self.wallet).call() # returns int with balance, without decimals
        # tokenBalance = self.web3.fromWei(token_balance, "ether")
        return token_balance

    #get account gas fee banlance
    def getGasBalance(self):
        banlance = self.web3.eth.get_balance(self.wallet)
        return banlance

    # get transaction times
    def getNonce(self):
        nonce = self.web3.eth.getTransactionCount(self.wallet)
        return nonce        

    # get staked and pending info
    def getCakePools(self,contract):
        cakeCt: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        pending: int = cakeCt.functions.pendingCake(self.pid_, self.wallet).call()
        staked: int = cakeCt.functions.userInfo(self.pid_, self.wallet).call()
        # # Convert to readable number
        # staked_balance: Decimal = self.web3.fromWei(staked[0], "ether")
        # pending_balance: Decimal = self.web3.fromWei(pending, "ether")
        return {'staked':staked[0],'pending':pending}

    # get pair
    def getPair(self,contract,tokenA,tokenB):
        ct: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        pair: str = ct.functions.getPair(tokenA,tokenB).call()
        priceCt: Contract = self.web3.eth.contract(pair, abi='[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"sync","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]')
        pairPrice = priceCt.functions.getReserves().call()

        return [self.web3.fromWei(pairPrice[0],'ether'),self.web3.fromWei(pairPrice[1],'ether')]
    
    #get tranasaction receipt
    #get_transaction
    def getTransactionReceipt(self,hash,waitingTimes):
        req = self.web3.eth.get_transaction(hash)
        print(req['blockHash'])
        if req['blockHash'] == None and waitingTimes<=10: return None
        req = self.web3.eth.get_transaction_receipt(hash)
        return req


    
# gate base code
host = "https://api.gateio.ws"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}


class GateStatus:        
    def __init__(self,gateKey,gateSecret):
        self.gateKey = gateKey
        self.gateSecret = gateSecret


    def gen_sign(self,method, url, query_string=None, payload_string=None):
        t = time.time()
        m = hashlib.sha512()
        m.update((payload_string or "").encode('utf-8'))
        hashed_payload = m.hexdigest()
        s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
        sign = hmac.new(self.gateSecret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
        return {'KEY': self.gateKey, 'Timestamp': str(t), 'SIGN': sign}

    def getBalance(self,currency='USDT',acc='spot'):
        # get Spot balance
        if acc == 'spot':
            url = '/spot/accounts'
        elif acc == 'futures':
            url = '/wallet/total_balance'

        query_param = ''
        sign_headers = self.gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)
        r = requests.request('GET', host + prefix + url, headers=headers)
        req = r.json()
        if acc == 'spot':
            spotAmount = [i for i in req if i['currency']==currency ][0]['available']
            return spotAmount
        elif acc == 'futures':
            futuresAmount = req['details']['futures']['amount']
            return futuresAmount

    def transfers(self,currency='USDT',from_='spot',to_='futures',amount=0):
        # transfers assets
        url = '/wallet/transfers'
        query_param = ''
        amount = str(math.floor(amount*1000)/1000)
        # from spot to futures
        body='{"currency":"'+currency+'","from":"'+from_+'","to":"'+to_+'","amount":'+amount+',"settle":"USDT"}'
        sign_headers = self.gen_sign('POST', prefix + url, query_param, body)
        headers.update(sign_headers)
        r = requests.request('POST', host + prefix + url, headers=headers, data=body)
        req = r.status_code
        return True if req == 204 else False


    def getFuturesPrice(self,pair='CAKE_USDT'):
        # get furtures info:  last_price, mark_price, funding_rate
        url = '/futures/usdt/contracts/'+pair
        r = requests.request('GET', host + prefix + url, headers=headers)
        req = r.json()
        ans = {'last_price':req['last_price'],'mark_price':req['mark_price'],'funding_rate':req['funding_rate']}
        return ans


    def orderFutures(self,contract,size,price):
        # order futures
        url = '/futures/usdt/orders'
        query_param = ''
        # size:order number , If size = 0 then close the positions
        if price ==0:
            # body='{"contract":"BTC_USDT","size":6024,"iceberg":0,"price":"3765","tif":"gtc","text":"t-my-custom-id"}'
            body='{"contract":"'+contract+'","size":'+str(size)+',"price":"0","tif":"ioc"}'
        else:
            body='{"contract":"'+contract+'","size":'+str(size)+',"price":"'+str(price)+'"}'
        sign_headers = self.gen_sign('POST', prefix + url, query_param, body)
        headers.update(sign_headers)
        r = requests.request('POST', host + prefix + url, headers=headers, data=body)
        req = r.json()
        return req

    def sendToken(self,currency,address,amount,chain):
        #send token to address
        url = '/withdrawals'
        query_param = ''
        body='{"currency":"'+currency+'","address":"'+address+'","amount":"'+amount+'","chain":"'+chain+'"}'
        sign_headers = self.gen_sign('POST', prefix + url, query_param, body)
        headers.update(sign_headers)
        r = requests.request('POST', host + prefix + url, headers=headers, data=body)
        print(r.json())
    
    def getLiqPrice(self,currency='CAKE_USDT'):
        url = '/futures/usdt/positions/'+currency
        query_param = ''
        sign_headers = self.gen_sign('GET', prefix + url, query_param)
        headers.update(sign_headers)
        r = requests.request('GET', host + prefix + url, headers=headers)
        req = r.json()
        return req




    
