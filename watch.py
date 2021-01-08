#!/usr/bin/env python

from web3 import Web3
import asyncio
import requests
import datetime
import time
import random
import os
import json
from dotenv import load_dotenv
from web3.logs import STRICT, IGNORE, DISCARD, WARN

# TWITTER STUFF
import getopt
import sys
import twitter
try:
  import configparser
except ImportError as _:
  import ConfigParser as configparser

load_dotenv(override=True)
# URLs
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
NODE_URL = os.getenv("NODE_URL")
# BOT BEHAVIOR
POST_TO_DISCORD = os.getenv("POST_TO_DISCORD")
START_BLOCK = int(os.getenv("START_BLOCK"))
LOOKBACK = os.getenv("LOOKBACK")
LOOKBACK_TRADES = os.getenv("LOOKBACK_TRADES")
LOOKBACK_HARVESTS = os.getenv("LOOKBACK_HARVESTS")
LOOKBACK_STRATEGIES = os.getenv("LOOKBACK_STRATEGIES")
WATCH = os.getenv("WATCH")
# CONTRACTS
CONTROLLER_ABI = os.getenv("CONTROLLER_ABI")
STRAT_ABI = os.getenv("STRAT_ABI")
VAULT_TIMELOCK_ABI = os.getenv("VAULT_TIMELOCK_ABI")
TOKEN_FARM_ABI = os.getenv("TOKEN_FARM_ABI")
TOKEN_FARM_ADDR = os.getenv("TOKEN_FARM_ADDR")
PROFITSHARE_V2_ADDR = os.getenv("PROFITSHARE_V2_ADDR")
PROFITSHARE_V3_ADDR = os.getenv("PROFITSHARE_V3_ADDR")
UNIPOOL_ABI = os.getenv("UNIPOOL_ABI")
UNIROUTER_ABI = os.getenv("UNIROUTER_ABI")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
# CONSTANTS
ONE_18DEC = 1000000000000000000

w3 = Web3(Web3.HTTPProvider(NODE_URL))

controller_addr = '0x222412af183BCeAdEFd72e4Cb1b71f1889953b1C'
unipool_usdc_farm_addr = '0x514906FC121c7878424a5C928cad1852CC545892'
unipool_weth_farm_addr = '0x56feAccb7f750B997B36A68625C7C596F0B41A58'
unirouter_addr = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'

strats = {
  '0xCf5F83F8FE0AB0f9E9C1db07E6606dD598b2bbf5': 'Swerve CRVStrategyYCRVMainnet v1',
  '0x66B7611F35e48e311929e25D73428410C2335c34': 'CRVStrategySwerveUSDCMainnet',
  '0x892171EB51d56dc340E586652068cf758E5F798C': 'CRVStrategySwerveUSDTMainnet',
  '0xF60AFEBb76c43F636E4D1a099847Fc97dc8bDeD0': 'CRVStrategySwerveDAIMainnet',
  '0x01Fcb5Bc16e8d945bA276DCCFeE068231DA4cE33': 'CRVStrategySwerveUSDTMainnet',
  '0x18C4325Ae10FC84895C77C8310D6d98C748e9533': 'CRVStrategySwerveUSDCMainnet',
  '0xd75ffA16FFbCf4078d55fF246CfBA79Bb8cE3F63': 'USDC CRVStrategyStableMainnet',
  '0x2CE34b1bb247f242f1d2A33811E01138968EFBFF': 'USDT CRVStrategyStableMainnet',
  '0x394E653bbFC9A3497A0487Abee153CA6498F053D': 'DAI CRVStrategyStableMainnet',
  '0x810B83fC33E6f5dA9Be9AE5dd0F918338e980938': 'CRVStrategyStableMainnet',
  '0xCf5F83F8FE0AB0f9E9C1db07E6606dD598b2bbf5': 'CRVStrategyYCRVMainnet',
  '0x2427DA81376A0C0a0c654089a951887242D67C92': 'CRVStrategyYCRVMainnet',
  '0xe7048E7186cB6f12C566A6C8a818D9D41da6Df19': 'CRVStrategyWBTCMainnet',
  '0x2EADFb06f9D890EBA80e999eABa2D445bC70f006': 'CRVStrategyRENBTCMainnet',
  '0xaf2D2e5c5aF90c782c008b5b287f20334eEB308E': 'CRVStrategyWRenBTCMixMainnet',
  '0x6AC7575A340a3DAb2Ae9ca07c4DbFC6bf8E7E281': 'CRVStrategySwerveDAIMainnet',
  '0x0A7d74604b39229D444855eF294F287099774aC8': 'funi-eth-wbtc SNXRewardUniLPStrategy v1',
  '0xD3927f43D622e8BC9ce9a1111BeCd5d6d3cf3C90': 'funi-eth-wbtc SNXRewardUniLPStrategy v2',
  '0xb43aA2C44B99BaD346143Fb44e264213d412B6c2': 'funi-eth-usdt SNXRewardUniLPStrategy v1',
  '0x13627B75cf955eEe2d57Fc11a7082de5C36050c3': 'funi-eth-usdt SNXRewardUniLPStrategy v2',
  '0x50F1191F3059069888d9E16A327b96afdd26C6fD': 'funi-eth-usdc SNXRewardUniLPStrategy v1',
  '0x987A168E19F6F64D6AB08AE0e0FE77EA3D79BaaC': 'funi-eth-usdc SNXRewardUniLPStrategy v2',
  '0x2Fee56e039AcCceFA3cB1f3051aD00fe550a472c': 'funi-eth-dai SNXRewardUniLPStrategy v1',
  '0xA82660A0A468bBA63dB950532cdbDa47144c212c': 'funi-eth-dai SNXRewardUniLPStrategy v2',
  '0x4E015af8E1C5eB020f91063661CC5ce43719eBcF': 'WETHCreamNoFoldStrategy v1',
  '0xcF477F117cAa349Ca92dEdb3955481628D463bF1': 'WETHCreamNoFoldStrategy v2',
  '0x26D3e02999BEFFAEb07Af3A94438769DF0eE4150': 'WETH Cream Rescue Strategy',
  '0x53df6664b3ddE086DCe6315c317d1002b14B87E3': 'SushiMasterChefLPStrategy',
  '0x0fd7c77b473e3Efe3170536805a14b61050eFc6E': 'funi-eth-usdt SNXRewardUniLPStrategy',
  '0xC6E973B8Fe772C58AD0D20099D43D2b3f0AEF5c0': 'funi-eth-usdc SNXRewardUniLPStrategy',
  '0x2CF4cEB36172Fb2196a47490419D57584234Cbd4': 'funi-eth-dai SNXRewardUniLPStrategy',
  '0x46eC909099F9691b43b64413F1BC662edFbee00A': 'funi-eth-wbtc SNXRewardUniLPStrategy',
  '0x885D59830C1FdB120B54d62790dB7A6a1f534463': 'PickleStrategy3PoolMainnet',
  '0xD21C3b9aF9861b925c83046eA906FE933A50c977': 'CRVStrategyYCRVMainnet',
  '0xC4c0d58c11eC41CC0f1a5bE75296cf140Ca8dd87': 'NoopStrategyStable',
  '0xa23c6F2d85fe47e613ce6bBb40E74aCB49Ae281a': 'DEGOSimpleStrategy',
  '0x0a1aD1698f7487655821c0d42d6691Ec43276E08': 'NoopStrategyStable',
  '0x2059711f1cf4c215f48dBBbC4cf6aF5AC5131C82': 'NoopStrategyStable',
  '0x099a926E55D24392BA3817fE38caA9eFA8c7b06A': 'NoopStrategyStable',
  '0xE715458Cd3ba5377487822F748BE1a5b994Db436': 'NoopStrategyStable',
  '0xABcEa95e3603C0604C81c2d95ED3aBD91c013aE6': 'NoopStrategyStable',
  '0x3952555B3Be488F51f0b03315a85560a83c24E04': 'CRVStrategyWRenBTCMixMainnet',
}

vaults = {
  '0x8e298734681adbfC41ee5d17FF8B0d6d803e7098': {'asset': 'fWETH-v0', 'decimals': 18,},
  '0xe85C8581e60D7Cd32Bbfd86303d2A4FA6a951Dac': {'asset': 'fDAI-v0', 'decimals': 18,},
  '0xc3F7ffb5d5869B3ade9448D094d81B0521e8326f': {'asset': 'fUSDC-v0', 'decimals': 6,},
  '0xc7EE21406BB581e741FBb8B21f213188433D9f2F': {'asset': 'fUSDT-v0', 'decimals': 6,},
  '0xF2B223Eb3d2B382Ead8D85f3c1b7eF87c1D35f3A': {'asset': 'FARM yDAI+yUSDC+yUSDT+yTUSD', 'decimals': 18,},
  '0xfBe122D0ba3c75e1F7C80bd27613c9f35B81FEeC': {'asset': 'fRenBTC-v0', 'decimals': 8,},
  '0xc07EB91961662D275E2D285BdC21885A4Db136B0': {'asset': 'fWBTC-v0', 'decimals': 8,},
  '0x192E9d29D43db385063799BC239E772c3b6888F3': {'asset': 'fCRVRenWBTC-v0', 'decimals': 18,},
  '0xb1FeB6ab4EF7d0f41363Da33868e85EB0f3A57EE': {'asset': 'fUNI-ETH-WBTC-v0', 'decimals': 18,},
  '0xB19EbFB37A936cCe783142955D39Ca70Aa29D43c': {'asset': 'fUNI-ETH-USDT-v0', 'decimals': 18,},
  '0x63671425ef4D25Ec2b12C7d05DE855C143f16e3B': {'asset': 'fUNI-ETH-USDC-v0', 'decimals': 18,},
  '0x1a9F22b4C385f78650E7874d64e442839Dc32327': {'asset': 'fUNI-ETH-DAI-v0', 'decimals': 18,},
  '0x01112a60f427205dcA6E229425306923c3Cc2073': {'asset': 'fUNI-ETH-WBTC', 'decimals': 18, 'type': 'timelock',},
  '0x7DDc3ffF0612E75Ea5ddC0d6Bd4e268f70362Cff': {'asset': 'fUNI-ETH-USDT', 'decimals': 18, 'type': 'timelock',},
  '0xA79a083FDD87F73c2f983c5551EC974685D6bb36': {'asset': 'fUNI-ETH-USDC', 'decimals': 18, 'type': 'timelock',},
  '0x307E2752e8b8a9C29005001Be66B1c012CA9CDB7': {'asset': 'fUNI-ETH-DAI', 'decimals': 18, 'type': 'timelock',},
  '0xF553E1f826f42716cDFe02bde5ee76b2a52fc7EB': {'asset': 'fSUSHI-WBTC-TBTC', 'decimals': 18, 'type': 'timelock',},
  '0x7674622c63Bee7F46E86a4A5A18976693D54441b': {'asset': 'fTUSD', 'decimals': 18, 'type': 'timelock',},
  '0xFE09e53A81Fe2808bc493ea64319109B5bAa573e': {'asset': 'fWETH', 'decimals': 18, 'type': 'timelock',},
  '0xab7FA2B2985BCcfC13c6D86b1D5A17486ab1e04C': {'asset': 'fDAI', 'decimals': 18, 'type': 'timelock',},
  '0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE': {'asset': 'fUSDC', 'decimals': 6, 'type': 'timelock',},
  '0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C': {'asset': 'fUSDT', 'decimals': 6, 'type': 'timelock',},
  '0x5d9d25c7C457dD82fc8668FFC6B9746b674d4EcB': {'asset': 'fWBTC', 'decimals': 8, 'type': 'timelock',},
  '0xC391d1b08c1403313B0c28D47202DFDA015633C4': {'asset': 'fRENBTC', 'decimals': 8, 'type': 'timelock',},
  '0x9aA8F427A17d6B0d91B6262989EdC7D45d6aEdf8': {'asset': 'fCRVRENWBTC', 'decimals': 18, 'type': 'timelock',},
  '0x71B9eC42bB3CB40F017D8AD8011BE8e384a95fa5': {'asset': 'f3CRV', 'decimals': 18, 'type': 'timelock',},
  '0x0FE4283e0216F94f5f9750a7a11AC54D3c9C38F3': {'asset': 'fYCRV', 'decimals': 18, 'type': 'timelock',},
}

CHADISMS = [
  'BRAH',
  'DUDE',
  'NICE',
  'OUCH',
  'SICK',
  'BOSS',
]

# TWITTER CONFIG

def GetConsumerKeyEnv():
  return os.environ.get("TWEETUSERNAME", None)

def GetConsumerSecretEnv():
  return os.environ.get("TWEETPASSWORD", None)

def GetAccessKeyEnv():
  return os.environ.get("TWEETACCESSKEY", None)

def GetAccessSecretEnv():
  return os.environ.get("TWEETACCESSSECRET", None)

class TweetRc(object):
  def __init__(self):
    self._config = None

  def GetConsumerKey(self):
    return self._GetOption('consumer_key')

  def GetConsumerSecret(self):
    return self._GetOption('consumer_secret')

  def GetAccessKey(self):
    return self._GetOption('access_key')

  def GetAccessSecret(self):
    return self._GetOption('access_secret')

  def _GetOption(self, option):
    try:
      return self._GetConfig().get('Tweet', option)
    except:
            return None

  def _GetConfig(self):
    if not self._config:
      self._config = configparser.ConfigParser()
      self._config.read(os.path.expanduser('~/.tweetrc'))
    return self._config

# Twitter setup
consumer_keyflag = None
consumer_secretflag = None
access_keyflag = None
access_secretflag = None
rc = TweetRc()
consumer_key = consumer_keyflag or GetConsumerKeyEnv() or rc.GetConsumerKey()
consumer_secret = consumer_secretflag or GetConsumerSecretEnv() or rc.GetConsumerSecret()
access_key = access_keyflag or GetAccessKeyEnv() or rc.GetAccessKey()
access_secret = access_secretflag or GetAccessSecretEnv() or rc.GetAccessSecret()
api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                  access_token_key=access_key, access_token_secret=access_secret,
                  input_encoding="utf-8")

# Smart Contracts
token_farm_contract = w3.eth.contract(address=TOKEN_FARM_ADDR, abi=TOKEN_FARM_ABI)
controller_contract = w3.eth.contract(address=controller_addr, abi=CONTROLLER_ABI)
unipool_usdc_farm_contract = w3.eth.contract(address=unipool_usdc_farm_addr, abi=UNIPOOL_ABI)
unipool_weth_farm_contract = w3.eth.contract(address=unipool_weth_farm_addr, abi=UNIPOOL_ABI)
unirouter_contract = w3.eth.contract(address=unirouter_addr, abi=UNIROUTER_ABI)

txids_seen = []

def handle_event(event):
  txhash = event.transactionHash.hex()
  blocknum = event.blockNumber
  # print(event)
  msg = ''
  tweet = False
  color = None
  # UNISWAP USDC/FARM TRADE
  if event.address == unipool_usdc_farm_addr:
    print('================USDC/FARM pool============')
    if txhash in txids_seen:
      return
    farmsell, farmbuy = int(event.args.amount0In)*10**-18, int(event.args.amount0Out)*10**-18
    usdcsell, usdcbuy = int(event.args.amount1In)*10**-6, int(event.args.amount1Out)*10**-6
    # get price information
    print(f'fetching pool reserves...')
    poolvals = unipool_usdc_farm_contract.functions['getReserves']().call(block_identifier=blocknum)
    print(f'calculating price...')
    price = unirouter_contract.functions['quote'](ONE_18DEC, poolvals[0], poolvals[1]).call(block_identifier=blocknum)*10**-6
    sender = w3.eth.getTransaction(event.transactionHash.hex())['from']
    # build message
    if farmbuy > 0:
      color = 32768
      pricechange = 100 * farmbuy / ( poolvals[0] * 10**-18)
      if pricechange < 1.0:
        return
      msg = (f':hamburger: **USDC/FARM Pool**\n\n'
             f':chart_with_upwards_trend: At block `{blocknum}`, '
             f'`+{pricechange:.4f}%`:evergreen_tree: to `${price:,.2f}`; '
             f'`{farmbuy:,.2f}` FARM was [bought](<https://etherscan.io/tx/{txhash}>) by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )
    if farmsell > 0:
      color = 16711680
      pricechange = 100 * farmsell / ( poolvals[0] * 10**-18)
      if pricechange < 1.0:
        return
      msg = (f':hamburger: **USDC/FARM Pool**\n\n'
             f':chart_with_downwards_trend: At block `{blocknum}`, '
             f'`-{pricechange:.4f}%`:small_red_triangle_down: to `${price:,.2f}`; '
             f'`{farmsell:,.2f}` FARM was [sold](<https://etherscan.io/tx/{txhash}>) by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )
  # UNISWAP WETH/FARM TRADE
  elif event.address == unipool_weth_farm_addr:
    print('================WETH/FARM pool============')
    if txhash in txids_seen:
      return
    farmsell, farmbuy = int(event.args.amount0In)*10**-18, int(event.args.amount0Out)*10**-18
    wethsell, wethbuy = int(event.args.amount1In)*10**-18, int(event.args.amount1Out)*10**-18
    # get price information
    print(f'fetching pool reserves...')
    poolvals = unipool_weth_farm_contract.functions['getReserves']().call(block_identifier=blocknum)
    print(f'calculating price...')
    price = unirouter_contract.functions['quote'](ONE_18DEC, poolvals[0], poolvals[1]).call(block_identifier=blocknum)*10**-18
    sender = w3.eth.getTransaction(event.transactionHash.hex())['from']
    # build message
    if farmbuy > 0:
      color = 32768
      pricechange = 100 * farmbuy / ( poolvals[0] * 10**-18)
      if pricechange < 1.0:
        return
      response = requests.get(f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={ETHERSCAN_API_KEY}')
      data = response.json()
      ethUsd = data['result']['ethusd']
      priceString = ''
      if response.status_code != 200:
        priceString = f'`{price:,.2f} WETH`'
      else:
        price = price * float(ethUsd)
        priceString = f'`${price:,.2f}`'
      msg = (f':cheese: **WETH/FARM Pool**\n\n'
             f':chart_with_upwards_trend: At block `{blocknum}`, '
             f'`+{pricechange:.4f}%`:evergreen_tree: to `{priceString}`; '
             f'`{farmbuy:,.2f}` FARM was [bought](<https://etherscan.io/tx/{txhash}>) by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )
    if farmsell > 0:
      color = 16711680
      pricechange = 100 * farmsell / ( poolvals[0] * 10**-18)
      if pricechange < 1.0:
        return
      response = requests.get(f'https://api.etherscan.io/api?module=stats&action=ethprice&apikey={ETHERSCAN_API_KEY}')
      data = response.json()
      ethUsd = data['result']['ethusd']      
      priceString = ''
      if response.status_code != 200:
        priceString = f'`{price:,.2f} WETH`'
      else:
        price = price * float(ethUsd)
        priceString = f'`${price:,.2f}`'
      msg = (f':cheese: **WETH/FARM Pool**\n\n'
             f':chart_with_downwards_trend: At block `{blocknum}`, '
             f'`-{pricechange:.4f}%`:small_red_triangle_down: to `{priceString}`; '
             f'`{farmsell:,.2f}` FARM was [sold](<https://etherscan.io/tx/{txhash}>) by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )
  # VAULT EVENT
  elif event.address in vaults.keys():
    color = 16711680
    event_name = event.event
    new_strategy = event.args.newStrategy
    vault_name = vaults.get(event.address, {'asset':'asset'})['asset']
    if event_name == 'StrategyAnnounced':
      dt_activated = f'{datetime.datetime.utcfromtimestamp(event.args.time).strftime("%Y-%m-%d %H:%M:%S")} GMT'
      old_strategy = 'old strategy'
    elif event_name == 'StrategyChanged':
      dt_activated = 'this block'
      old_strategy = event.args.get('oldStrategy', 'old strategy')
    msg = (f':compass: At block `{blocknum}`, [{event_name}](<https://etherscan.io/tx/{txhash}>) '
           f'for {vault_name}!\n'
           f':crossed_swords: Old strategy: `{old_strategy}`\n'
           f':rocket: New strategy: `{new_strategy}`\n'
           f':alarm_clock: Earliest effective: `{dt_activated}`!'
            )
    tweet = f'🧭  {event_name} for @harvest_finance {vault_name}; earliest effective {dt_activated} https://etherscan.io/tx/{txhash}'
  # HARVEST
  else:
    color = 16776960
    shareprice_decimals = vaults.get(event.args.vault, {'decimals':'0'})['decimals']
    shareprice = event.args.newSharePrice * ( 10 ** ( -1 * int(shareprice_decimals) ) )
    shareprice_delta = (event.args.newSharePrice - event.args.oldSharePrice) / event.args.oldSharePrice
    asset = vaults.get(event.args.vault, {'asset':'assets'})['asset']
    strat_addr = event.args.strategy
    strat_name = strats.get(strat_addr, 'farming strategy')
    dt = datetime.datetime.utcfromtimestamp(event.args.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    farm_xfrs = ''
    receipt = w3.eth.getTransactionReceipt(txhash)
    token_farm_logs = token_farm_contract.events.Transfer().processReceipt(receipt, errors=DISCARD)
    for xfr in token_farm_logs:
      if xfr.address == TOKEN_FARM_ADDR and (xfr.args.to == PROFITSHARE_V2_ADDR or xfr.args.to == PROFITSHARE_V3_ADDR):
        farm_xfrs += (f'\n:farmer: FARM to profit share: `{xfr.args.value*10**-18}`')
    msg =  (f':tractor: At `{dt} GMT`, did `HardWork` on [{asset}](<https://etherscan.io/tx/{txhash}>)\n'
            f':tools: Using the [{strat_name}](<https://etherscan.io/address/{strat_addr}#code>)!\n'
            f':chart_with_upwards_trend: Share price changes `{round(100*shareprice_delta,4):.4f}%` to `{round(shareprice,6):.6f}`!'
            f'{farm_xfrs}'
            f' <:chadright:758033272101011622> {random.choice(CHADISMS)}.'
            )      
  send_msg(msg, tweet, color)
  txids_seen.append(txhash)

def send_msg(msg, tweet, color=None):
  data = {}
  data['embeds'] = []
  embed = {}
  #embed['title'] = ":chains::mag: On-chain event detected!"
  embed['description'] = msg
  if color: embed['color'] = color
  data['embeds'].append(embed)
  if POST_TO_DISCORD == 'True' and len(msg) > 0:
    requests.post(WEBHOOK_URL, json.dumps(data), headers={"Content-Type": "Application/json"})
  if tweet:
    try:
      print(msg)
      status = api.PostUpdate(tweet)
    except:
      print('could not tweet')
  time.sleep(1)

def log_lookback(event_filters):
  print(f'Starting log lookback at {START_BLOCK}...')
  for n, event_filter in enumerate(event_filters, 1):
    print(f'Starting log lookback on contract {n}...')
    for event in event_filter.get_all_entries():
      handle_event(event)
  print('Lookback complete!')

async def log_loop(event_filters, poll_interval):
  print('Starting watch for new logs...')
  while True:
    for event_filter in event_filters:
      for event in event_filter.get_new_entries():
        handle_event(event)
    await asyncio.sleep(poll_interval)

def main():
  # set up lookback
  lookback_filters = []
  if LOOKBACK_HARVESTS == 'True':
    lookback_filters.append(controller_contract.events.SharePriceChangeLog.createFilter(fromBlock=START_BLOCK))
  if LOOKBACK_TRADES == 'True':
    # lookback_filters.append(unipool_usdc_farm_contract.events.Swap.createFilter(fromBlock=START_BLOCK))
    lookback_filters.append(unipool_weth_farm_contract.events.Swap.createFilter(fromBlock=START_BLOCK))
  if LOOKBACK_STRATEGIES == 'True':
    for vault in vaults:
      if vaults.get(vault).get('type', '') == 'timelock':
        vault_contract = w3.eth.contract(address=vault, abi=VAULT_TIMELOCK_ABI)
        lookback_filters.append(vault_contract.events.StrategyAnnounced.createFilter(fromBlock=START_BLOCK))
        lookback_filters.append(vault_contract.events.StrategyChanged.createFilter(fromBlock=START_BLOCK))
  # run lookback
  if LOOKBACK == 'True':
    log_lookback(lookback_filters)
  # set up the loop
  if WATCH == 'True':
    event_filters = []
    print('watching for new events...')
    loop = asyncio.get_event_loop()
    event_filters.append(controller_contract.events.SharePriceChangeLog.createFilter(fromBlock='latest'))
    event_filters.append(unipool_usdc_farm_contract.events.Swap.createFilter(fromBlock='latest'))
    event_filters.append(unipool_weth_farm_contract.events.Swap.createFilter(fromBlock='latest'))
    for vault in vaults:
      if vaults.get(vault).get('type', '') == 'timelock':
        vault_contract = w3.eth.contract(address=vault, abi=VAULT_TIMELOCK_ABI)
        event_filters.append(vault_contract.events.StrategyAnnounced.createFilter(fromBlock='latest'))
        event_filters.append(vault_contract.events.StrategyChanged.createFilter(fromBlock='latest'))
    # run the loop
    try:
      loop.run_until_complete(
        asyncio.gather(
          log_loop(event_filters, 10),
        )
      )
    finally:
      loop.close()
  print('done with everything!')

if __name__ == '__main__':
    main()
