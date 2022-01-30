from asyncio import futures
from asyncio.windows_events import NULL
from decimal import Decimal
from hashlib import new
from unicodedata import decimal
from web3 import Web3
from status import WalletStatus, GateStatus
from allocation import Allocation
import baseInfo as bi
import time
import multiprocessing as mp
import math


'''
undone note:
0. send USDT to Gate or Wallet is undone!!!
1.check cake balance and choose use ord balance
2.rebalance function
3.append addHedging function
4.step 8 mp.Process
5.gas check function
'''

# wallet,
# prvkey, #alloctaion only
# pid_ = 0, #walletStatus only
# contractDice=[],
# tokenDict={},
# mainnet='https://bsc-dataseed3.binance.org/'

wallet = bi.wallet
gateWallet = bi.gateBepWallet
prvkey = bi.prvkey
pid_ = 0

cakePoolsContract = bi.contractDice['nomalCake']
cakeSwapContract = bi.contractDice['swapToken']
usdtContract = bi.contractDice['sendUSDT']
getPairContract = bi.contractDice['getPair']

tokenDict = bi.tokenDict
mainnet = bi.mainnet['bsc']

gateStatus = GateStatus(bi.gateKey, bi.gateSecret)
walletStatus = WalletStatus(wallet, pid_, tokenDict, mainnet)
allocation = Allocation(wallet, prvkey, walletStatus.getGasBalance(), tokenDict, mainnet)

def fromWei(wei,unit):
        return walletStatus.web3.fromWei(wei, unit)

def toWei(wei,unit):
        return walletStatus.web3.toWei(wei, unit)
def updateGasBalance():
    allocation.gasBalance = int(walletStatus.getGasBalance())

def totalBalanceInfo():
    gateSpotBalance = Decimal(gateStatus.getBalance('USDT','spot'))
    gateFuturesBalance = Decimal(gateStatus.getBalance('USDT','futures'))
    walletUSDTBalance = Decimal(fromWei(walletStatus.getTokenBalance('USDT'),'ether'))
    walletCAKEBalance = Decimal(fromWei(walletStatus.getTokenBalance('CAKE'),'ether'))
    walletGasBalance = Decimal(fromWei(walletStatus.getGasBalance(),'ether'))
    usingCake = walletStatus.getCakePools(cakePoolsContract)
    staked = Decimal(fromWei(usingCake['staked'],'ether'))
    pending = Decimal(fromWei(usingCake['pending'],'ether'))

    # print('Gate USDT balance: {},\nwallet USDT balance: {},\nstaked balance: {},\npending balance: {},\nfutures balance: {},\nGas balance: {}'\
    #         .format(gateSpotBalance,walletUSDTBalance, staked,pending, gateFuturesBalance,walletGasBalance))

    return {'gateSpotBalance':gateSpotBalance,'walletUSDTBalance':walletUSDTBalance,'walletCAKEBalance':walletCAKEBalance,
            'staked':staked,'pending':pending,'futuresBalance':gateFuturesBalance,'walletGasBalance':walletGasBalance}

def swapToken(tokenA,tokenB,amount,slip=0):
    #Swap token
    amountWei = toWei(amount,'ether')
    minWei = toWei(amount*slip,'ether')
    txnHash = allocation.swapToken(cakeSwapContract,wallet,tokenDict[tokenA][0],tokenDict[tokenB][0],amountWei,minWei)
    return txnHash

def buyGas(amount):
    usdtAmount = toWei(amount,'ether')
    txnHash = allocation.buyGas(cakeSwapContract,wallet,tokenDict['USDT'][0],tokenDict['BNB'][0],usdtAmount,0)
    return txnHash


def getTransactionReceipt(txnHash):
    waitingTimes = 0
    while True:
        # waiting for transaction receipt
        time.sleep(5)
        status = walletStatus.getTransactionReceipt(txnHash,waitingTimes)
        if status == None:
            print('waiting transaction...')
            waitingTimes += 1
            continue
        print('transaction done')
        return status



'''
1.get total balance
2.set hedging balance
3.balance USDT
4.transfer USDT to Gate futures
5.buy CAKE and sell CAKE_USDT at same time
6.check CAKE balance and Gas balance
7.stake cake in pools
8.check two account balance
/* for loop 8. */
if futures balance lost 75% then rebalance
'''

def newHedging( hedgingBalance:Decimal,cryptocurrency='CAKE'):
    # step 1 & 2
    totalBalance = totalBalanceInfo()
    updateGasBalance()
    available = (totalBalance['gateSpotBalance']+totalBalance['walletUSDTBalance'])
    if hedgingBalance > available:
        print('available balance is not enough.')
        return False
    halfBalance = Decimal(hedgingBalance/2)
    walletDiff = totalBalance['walletUSDTBalance'] - (halfBalance)
    ExDiff =  totalBalance['gateSpotBalance'] - (halfBalance)
    # print(walletDiff,ExDiff)
    # step 3 
    if walletDiff < 0:
        # wallet balance not enough ,need transfer USDT to wallet
        # Gate to binance to wallet
        print('wallet USDT balance is not enough.')
        pass
    elif ExDiff < 0:
        # gate balance not enough ,need transfer USDT to gate
        print('Gate USDT balance is not enough.')
        pass
    
    #step 4
    isSuccess = gateStatus.transfers('USDT','spot','futures',halfBalance)
    if not isSuccess :
        print('Gate transfer fail.')
        return False
    print('transfer USDT to futures')
    #step 5 & 6
    # swap tokenA to tokenB
    txnHash = swapToken('USDT','CAKE',halfBalance)
    if txnHash == 'gas fail':
        print('gas balance is not enough.')
        return False
    updateGasBalance()
    print('swap hash: ',txnHash)
    # waiting for transaction receipt
    swapStatus = getTransactionReceipt(txnHash)
    if swapStatus['status'] == 0:
        print('Swap rejected.')
        isSuccess = gateStatus.transfers('USDT','futures','spot',halfBalance)
        if not isSuccess :
            print('Gate transfers back fail. please manual transfer balance')
        return False
    elif swapStatus['status'] == 1:
        print('Swap success')
    else:
        print('unkown error')
        return False
    # buy short CAKE_USDT
    futruesPrice = gateStatus.getFuturesPrice('CAKE_USDT')
    # choose market price or limit price (?
    size = halfBalance/Decimal(futruesPrice['mark_price'])
    size = math.floor(size*10)
    print('order size: ',-size)
    futuresOrder = gateStatus.orderFutures('CAKE_USDT',-size,0) # 0 is market price, limit price is futruesPrice['last_price']
    cake = walletStatus.getTokenBalance('CAKE')
    print('cake: {}\nfutures: {}\nGas: {}'.format(fromWei(cake,'ether'),gateStatus.getBalance(acc='futures'),walletStatus.getGasBalance()))

    #step 7
    gasPrice = 5
    while True:
        txnHash = allocation.cakeEnterStaking(cakePoolsContract,cake,gasPrice)
        if txnHash == 'gas fail':
            print('gas balance is not enough.')
            return False
        print('Staking hash: ',txnHash)
        stakeStatus = getTransactionReceipt(txnHash)
        if stakeStatus['status'] == 0:
            updateGasBalance()
            print('Staking rejected. boost gas try again gas price: '+gasPrice)
            if gasPrice >= 7 : 
                print('Gas too high. quit staking ,please manual staking')
                return False
            gasPrice  += 1
            continue
        elif stakeStatus['status'] == 1:
            print('staking success')
            break
        else:
            print('unkown error')
            return False
    return True

#step 8 monitor balance, close true: liquidation, false: rebalance
# use mp.Process(target = function, args = **args) make check function?
def monitor(close=True):
    while True:
        totalbalance = totalBalanceInfo()
        usingCAKE = totalbalance['staked']+totalbalance['pending']
        cakePrice = Decimal(gateStatus.getFuturesPrice('CAKE_USDT')['mark_price'])
        stakingUSDT = usingCAKE*cakePrice
        futuresUSDT = Decimal(totalbalance['futuresBalance'])
        liqPrice = Decimal(gateStatus.getLiqPrice('CAKE_USDT')['liq_price'])
        print('staking CAKE balance: {}\nstaking USDT balance: {}\nfutures USDT balance: {}\nlast CAKE price: {}\nliquidation price: {}\ntotal balance: {}'\
                .format(usingCAKE,stakingUSDT,futuresUSDT,cakePrice,liqPrice,stakingUSDT+futuresUSDT))
        if (cakePrice*Decimal(1.2)) > liqPrice:
            if close:
                #cancel function
                print('liquidation position')
                withdrawalHedging()
            else:
                #rebalance function
                print('rebalance')
        print('----'*10)
        time.sleep(5)

def withdrawalHedging(cryptocurrency='CAKE'):
    # withdrawal all balance
    stakedCake = walletStatus.getCakePools(cakePoolsContract)
    if stakedCake['staked'] != 0:
        txnHash = allocation.cakeLeaveStaking(cakePoolsContract,stakedCake['staked'])
        updateGasBalance()
        if txnHash == 'gas fail':
            print('gas balance is not enough.')
            return False
        print('leave hash: ',txnHash)
        leaveStatus = getTransactionReceipt(txnHash)
        if leaveStatus['status'] == 0:
            print('leaving rejected. please manual leaving')
            return False
        elif leaveStatus['status'] == 1:
            print('leaving success')
            time.sleep(5)
        else:
            print('unkown error')
            return False

    totalBalance = totalBalanceInfo()
    cake = totalBalance['walletCAKEBalance']
    print('leaving pools cake balance: ',cake)
    txnHash = swapToken('CAKE','USDT',cake)
    updateGasBalance()
    if txnHash == 'gas fail':
        print('gas balance is not enough.')
        return False
    print('swap hash: ',txnHash)
    swapStatus = getTransactionReceipt(txnHash)
    if swapStatus['status'] == 0:
        print('swap rejected. please manual swap or try again')
        return False
    elif swapStatus['status'] == 1:
        print('swap success')
    else:
        print('unkown error')
        return False

    totalBalance = totalBalanceInfo()
    liq = gateStatus.getLiqPrice()
    futuresOrder = gateStatus.orderFutures('CAKE_USDT',-liq['size'],0) # 0 is market price, limit price is futruesPrice['last_price']
    isSuccess = gateStatus.transfers('USDT','futures','spot',totalBalance['futuresBalance'])
    if not isSuccess :
        print('Gate transfer fail.please manual transfer balance')

    print('wallet CAKE balance: {}\nwallet USDT balance: {}\nGate.io futures balance: {}\n Gate.io spot balance: {}\norder status: {}'\
            .format(totalBalance['walletCAKEBalance'],
                    totalBalance['walletUSDTBalance'],
                    totalBalance['futuresBalance'],
                    totalBalance['gateSpotBalance'],
                    futuresOrder['status']))



monitor()