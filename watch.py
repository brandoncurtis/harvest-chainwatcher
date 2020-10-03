#!/usr/bin/env python

from web3 import Web3
import asyncio
import requests
import datetime
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
NODE_URL = os.getenv("NODE_URL")
START_BLOCK = int(os.getenv("START_BLOCK"))
LOOK_BACK = os.getenv("LOOK_BACK")
CONTROLLER_ABI = os.getenv("CONTROLLER_ABI")
STRAT_ABI = os.getenv("STRAT_ABI")

w3 = Web3(Web3.HTTPProvider(NODE_URL))

controller_addr = '0x222412af183BCeAdEFd72e4Cb1b71f1889953b1C'

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
}

vaults = {
  '0x8e298734681adbfC41ee5d17FF8B0d6d803e7098': {'asset': 'fWETH', 'decimals': 18,},
  '0xe85C8581e60D7Cd32Bbfd86303d2A4FA6a951Dac': {'asset': 'fDAI', 'decimals': 18,},
  '0xc3F7ffb5d5869B3ade9448D094d81B0521e8326f': {'asset': 'fUSDC', 'decimals': 6,},
  '0xc7EE21406BB581e741FBb8B21f213188433D9f2F': {'asset': 'fUSDT', 'decimals': 6,},
  '0xF2B223Eb3d2B382Ead8D85f3c1b7eF87c1D35f3A': {'asset': 'FARM yDAI+yUSDC+yUSDT+yTUSD', 'decimals': 18,},
  '0xfBe122D0ba3c75e1F7C80bd27613c9f35B81FEeC': {'asset': 'fRenBTC', 'decimals': 8,},
  '0xc07EB91961662D275E2D285BdC21885A4Db136B0': {'asset': 'fWBTC', 'decimals': 8,},
  '0x192E9d29D43db385063799BC239E772c3b6888F3': {'asset': 'fCRVRenWBTC', 'decimals': 18,},
  '0xb1FeB6ab4EF7d0f41363Da33868e85EB0f3A57EE': {'asset': 'fUNI-ETH-WBTC', 'decimals': 18,},
  '0xB19EbFB37A936cCe783142955D39Ca70Aa29D43c': {'asset': 'fUNI-ETH-USDT', 'decimals': 18,},
  '0x63671425ef4D25Ec2b12C7d05DE855C143f16e3B': {'asset': 'fUNI-ETH-USDC', 'decimals': 18,},
  '0x1a9F22b4C385f78650E7874d64e442839Dc32327': {'asset': 'fUNI-ETH-DAI', 'decimals': 18,},
}

CHADISMS = [
  'BRAH',
  'DUDE',
  'NICE',
  'OUCH',
]

def handle_event(event):
  print(event)
  time.sleep(3)
  shareprice_decimals = vaults.get(event.args.vault, {'decimals':'0'})['decimals']
  shareprice = event.args.newSharePrice * ( 10 ** ( -1 * shareprice_decimals ) )
  shareprice_delta = (event.args.newSharePrice - event.args.oldSharePrice) / event.args.oldSharePrice
  asset = vaults.get(event.args.vault, {'asset':'assets'})['asset']
  txhash = event.transactionHash.hex()
  strat_addr = event.args.strategy
  strat_name = strats.get(strat_addr, 'farming strategy')
  dt = datetime.datetime.utcfromtimestamp(event.args.timestamp).strftime('%Y-%m-%d %H:%M:%S')

  msg =  (f'\nAt `{dt} GMT`, harvested some [{asset}](<https://etherscan.io/tx/{txhash}>) '
  f'using the [{strat_name}](<https://etherscan.io/address/{strat_addr}#code>)!\n'
  f'Share price changes `{round(100*shareprice_delta,4):.4f}%` to `{round(shareprice,6):.6f}`! {random.choice(CHADISMS)}. :tractor:\n'
    )
  json_payload = {'content': msg, 'embeds': [],}
  print(msg)
  requests.post(WEBHOOK_URL, json_payload)
  # and whatever

def log_lookback(event_filter):
  print(f'Starting log lookback at {START_BLOCK}...')
  for event in event_filter.get_all_entries():
    handle_event(event)
  print('Lookback complete!')

async def log_loop(event_filter, poll_interval):
  print('Starting watch for new logs...')
  while True:
    for event in event_filter.get_new_entries():
      handle_event(event)
    await asyncio.sleep(poll_interval)

def main():
  controller_contract = w3.eth.contract(address=controller_addr, abi=CONTROLLER_ABI)
  if LOOK_BACK == 'True':
    controller_filter_lookback = controller_contract.events.SharePriceChangeLog.createFilter(fromBlock=START_BLOCK)
    log_lookback(controller_filter_lookback)
  loop = asyncio.get_event_loop()
  controller_filter = controller_contract.events.SharePriceChangeLog.createFilter(fromBlock='latest')
  try:
    loop.run_until_complete(
      asyncio.gather(
        log_loop(controller_filter, 10),
      )
    )
  finally:
    loop.close()

if __name__ == '__main__':
    main()
