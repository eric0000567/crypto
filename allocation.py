from web3 import Web3
from eth_typing.evm import ChecksumAddress
from web3.contract import Contract
from decimal import Decimal
import time

# add check tokenDict function

class Allocation:
    def __init__(self, wallet,prvkey,gasBalance,
                tokenDict={},
                mainnet='https://bsc-dataseed3.binance.org/'):

        self.web3: Web3 = Web3(Web3.HTTPProvider(mainnet))
        self.wallet: ChecksumAddress = self.web3.toChecksumAddress(wallet)
        self.prvkey = prvkey
        self.tokenDict = tokenDict
        self.gasBalance = gasBalance

    def cakeEnterStaking(self,contract,amount,gasPrice=5):
        ct: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        #get estimate Gas fee
        estimateGas = ct.functions.enterStaking(amount).estimateGas({'from':self.wallet})
        if self.gasBalance <= estimateGas*2:
            return 'gas fail'
        # build transaction of pancakeswap pools and staking
        txn = ct.functions.enterStaking(amount).buildTransaction({
            'gas': estimateGas,
            'gasPrice': self.web3.toWei(gasPrice, 'gwei'),
            'from': self.wallet,
            'nonce': self.web3.eth.getTransactionCount(self.wallet)
        })
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.prvkey)
        txReport = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txReport.hex()

    def cakeLeaveStaking(self,contract,amount,gasPrice=5):
        ct: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        #get estimate Gas fee
        estimateGas = ct.functions.leaveStaking(amount).estimateGas({'from':self.wallet})
        if self.gasBalance <= estimateGas*2:
            return 'gas fail'
        txn = ct.functions.leaveStaking(amount).buildTransaction({
            'gas': estimateGas,
            'gasPrice': self.web3.toWei(gasPrice, 'gwei'),
            'from': self.wallet,
            'nonce': self.web3.eth.getTransactionCount(self.wallet)
        })
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.prvkey)
        txReport = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txReport.hex()

    def walletSendtoEX(self ,contract ,from_ ,to_ ,value_,gasPrice=5):
        value = self.web3.toWei(value_, 'ether')
        sendCt: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        estimateGas = sendCt.functions.transfer(to_,value).estimateGas({'from':from_ })
        if self.gasBalance <= estimateGas*2:
            return 'gas fail'
        txn = sendCt.functions.transfer(to_,value).buildTransaction({
            'gas': estimateGas,
            'gasPrice': self.web3.toWei(gasPrice, 'gwei'),
            'from': from_,
            'nonce': self.web3.eth.getTransactionCount(self.wallet)
        })
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.prvkey)
        txReport = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txReport.hex()

    def swapToken(self ,contract ,from_ ,tokenA ,tokenB ,amount ,minAmount,gasPrice=5):
        # swapExactTokensForTokens
        swapCt: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        path = [tokenA, tokenB]
        estimateGas = swapCt.functions.swapExactTokensForTokens(amount, minAmount, path, from_, (int(time.time()) + 15 * 60) ).estimateGas({'from':from_ })
        if self.gasBalance <= estimateGas*2:
            return 'gas fail'
        txn = swapCt.functions.swapExactTokensForTokens(amount, minAmount, path, from_, (int(time.time()) + 15 * 60) ).buildTransaction({
            'gas': estimateGas,
            'gasPrice': self.web3.toWei(gasPrice, 'gwei'),
            'from': from_,
            'nonce':  self.web3.eth.getTransactionCount(self.wallet)
        })
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.prvkey)
        txReport = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txReport.hex()

    def buyGas(self ,contract ,from_ ,tokenA ,tokenB ,amount ,minAmount,gasPrice=5):
        # swapExactTokensForETH
        swapCt: Contract = self.web3.eth.contract(contract[0], abi=contract[1])
        path = [tokenA,tokenB]
        estimateGas = swapCt.functions.swapExactTokensForETH(amount, minAmount, path, from_, (int(time.time()) + 15 * 60) ).estimateGas({'from':from_ })
        if self.gasBalance <= estimateGas*2:
            return 'gas fail'
        txn = swapCt.functions.swapExactTokensForETH(amount, minAmount, path, from_, (int(time.time()) + 15 * 60) ).buildTransaction({
            'gas': estimateGas,
            'gasPrice': self.web3.toWei(gasPrice, 'gwei'),
            'from': from_,
            'nonce':  self.web3.eth.getTransactionCount(self.wallet)
        })
        signed_txn = self.web3.eth.account.sign_transaction(txn, self.prvkey)
        txReport = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txReport.hex()
