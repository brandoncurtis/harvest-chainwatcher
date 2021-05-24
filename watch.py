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
WEBHOOK_URL_MATIC = os.getenv("WEBHOOK_URL_MATIC")
WEBHOOK_URL_BSC = os.getenv("WEBHOOK_URL_BSC")
NODE_URL = os.getenv("NODE_URL")
NODE_URL_MATIC = os.getenv("NODE_URL_MATIC")
NODE_URL_BSC = os.getenv("NODE_URL_BSC")
# BOT BEHAVIOR
POST_TO_DISCORD = os.getenv("POST_TO_DISCORD")
START_BLOCK_ETH = int(os.getenv("START_BLOCK_ETH"))
START_BLOCK_MATIC = int(os.getenv("START_BLOCK_MATIC"))
START_BLOCK_BSC = int(os.getenv("START_BLOCK_BSC"))
LOOKBACK = os.getenv("LOOKBACK")
LOOKBACK_TRADES = os.getenv("LOOKBACK_TRADES")
LOOKBACK_HARVESTS = os.getenv("LOOKBACK_HARVESTS")
LOOKBACK_STRATEGIES = os.getenv("LOOKBACK_STRATEGIES")
LOOKBACK_BURNS = os.getenv("LOOKBACK_BURNS")
LOOKBACK_MATIC = os.getenv("LOOKBACK_MATIC")
LOOKBACK_MATIC_BRIDGE = os.getenv("LOOKBACK_MATIC_BRIDGE")
LOOKBACK_MATIC_TRADES = os.getenv("LOOKBACK_MATIC_TRADES")
LOOKBACK_MINTER = os.getenv("LOOKBACK_MINTER")
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
MINTER_ABI = os.getenv("MINTER_ABI")
# CONSTANTS
ONE_18DEC = 1000000000000000000
ZERO_ADDR = "0x0000000000000000000000000000000000000000"
PRICEDELTA_PERCENT_THRESHOLD = 2.0
PRICEDELTA_PERCENT_THRESHOLD_MATIC = 0.1

# Activate networks
w3 = False
m3 = False
b3 = False
activenet = {
        'eth': False,
        'matic': False,
        'bsc': False,
        }
try: 
  provider = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={'timeout': 120}))
  print(f'ETH -- blockheight: {provider.eth.blockNumber}')
  w3 = provider
  activenet['eth'] = True
except Exception as e:
  print(f'ETH -- problem with node! support disabled')
  print(f'ETH -- {e}')

try: 
  provider = Web3(Web3.HTTPProvider(NODE_URL_MATIC, request_kwargs={'timeout': 120}))
  print(f'MATIC -- blockheight: {provider.eth.blockNumber}')
  m3 = provider
  activenet['matic'] = True
except Exception as e:
  print(f'MAT -- problem with node! support disabled')
  print(f'MAT -- {e}')

try: 
  provider = Web3(Web3.HTTPProvider(NODE_URL_BSC, request_kwargs={'timeout': 120}))
  print(f'BSC -- blockheight: {provider.eth.blockNumber}')
  b3 = provider
  activenet['bsc'] = True
except Exception as e:
  print(f'BSC -- problem with node! support disabled')
  print(f'BSC -- {e}')

CONTROLLER_ADDR = '0x222412af183BCeAdEFd72e4Cb1b71f1889953b1C'
UNIPOOL_FARM_USDC_ADDR = '0x514906FC121c7878424a5C928cad1852CC545892'
UNIPOOL_FARM_ETH_ADDR = '0x56feAccb7f750B997B36A68625C7C596F0B41A58'
UNIPOOL_USDC_ETH_ADDR = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'
UNIROUTER_ADDR = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
GRAIN_ADDR = '0x6589fe1271A0F29346796C6bAf0cdF619e25e58e'
GRAIN_SUPPLY = 30938628.224397507
MINTER_ADDR = '0x284D7200a0Dabb05ee6De698da10d00df164f61d'
IFARM_ADDR = '0x1571eD0bed4D987fe2b498DdBaE7DFA19519F651'
# MATIC
MATIC_ROOT_ADDR = os.getenv("MATIC_ROOT_ADDR")
MATIC_UNIROUTER_ADDR = '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'
MATIC_ROOT_ABI = os.getenv("MATIC_ROOT_ABI")
MATIC_ERC20_ADDR = '0x40ec5B33f54e0E8A33A975908C5BA1c14e5BbbDf'
MATIC_ERC20_ABI = os.getenv("MATIC_ERC20_ABI")
MATIC_UNIPOOL_IFARM_MATIC_ADDR = '0x2a574629CA405fA43A8F21FAa64ff73dD320f45b'
MATIC_UNIPOOL_IFARM_QUICK_ADDR = '0xD7668414BfD52DE6d59E16e5f647c9761992C435'
# BSC
BSC_UNIROUTER_ADDR = '0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F'
BSC_UNIPOOL_FARM_BUSD_ADDR = '0x8e1E53d73Be3A72d8c6108F8758069A54B4B564E'
LOOKBACK_BSC_TRADES = os.getenv("LOOKBACK_BSC_TRADES")

strats = {
  '0x7724844189CD0Bb08cAAD3d2F47d826EcB33aFe5': 'fUNI-COMFI:ETH StrategyProxy',
  '0x99F3157A9b96245a3c5a57A762C58474A06c3F7C': 'fUNI-MUSE:ETH StrategyProxy',
  '0x40D94AEFEC6ac00Fa80689A38135D83EeAa58999': 'StrategyProxy',
  '0xbdc7D6284BAD0D7243Bf3ca4DCeaE2A86DeEe37d': 'StrategyProxy',
  '0x7E33Ef42d0B7f2b25E27b49004cE79E1b11f2649': 'StrategyProxy',
  '0x991c40f931446321e3219a867a36B505b76E9522': 'IndexStrategyMainnet_MVI_ETH',
  '0xa03833A5Eef48fAd3295C11e6c1E5701C2817e16': 'Klondike2FarmStrategyMainnet_KXUSD_DAI',
  '0x170f77e70E488FB7d486aB916E305CA85D45364f': 'Klondike2FarmStrategyMainnet_WBTC_KLONX',
  '0x45D17d7C638A0ab6ec4eb736F87313d91EFFbBd5': 'OneInchStrategy_ETH_ONEINCH',
  '0x8d7dA935C449bE284B27D96B6F215d6Dba95d8d1': 'OneInchStrategy_1INCH_USDC',
  '0xb3fFE89b4f9e0b76980Ee06301409521CF6825Cc': 'OneInchStrategy_1INCH_WBTC',
  '0x405FE1198edABAE6a85C494dCF09f7be6a957b1D': 'StrategyProxy',
  '0x6Cb5e2fC7c258A1ec07f6a251f8E67A4e485812F': 'Klondike2FarmStrategyMainnet_WBTC_KBTCV2',
  '0x127BfdC843a35607B024781324311522907bCA66': 'CRVStrategyUSDPMainnet',
  '0x21546068903b82695C6CC26164b4CD15Ad906f60': 'StrategyProxy',
  '0xfdAF72D8B6E0F553c137A03F73C8ED210712f143': 'StrategyProxy',
  '0x32448D412e1821E5FB598291dC2de2aD91A78658': 'StrategyProxy',
  '0x7ce0c1E2985677743A789dC4B64E9230f8862395': 'StrategyProxy',
  '0x04b50373d4E190D4921bAbB9e874bB94E37EA045': 'XSushiStrategyMainnet',
  '0x4Cad48Bf9a362d3576d2aaCD5fD0DbD4F9e9FAB8': 'StrategyProxy',
  '0x33Fed4ccB4175484a692c83942D4374FcD1a3CD4': 'StrategyProxy',
  '0x8e8C911D46baDc3e69d781744d57884eEF6b4c43': 'StrategyProxy',
  '0x923ca6DCEF62030Bed25aA3EF854F39dc45DDa65': 'StrategyProxy',
  '0x18fe4B095dc23411857e174D8C561C860c6C7CD5': 'StrategyProxy',
  '0x97487C1F352a8076A738fbDcd316A10F01046567': 'MirrorMainnet_mNFLX_UST',
  '0x18fbE81e56133118669660A46d050546045aB9B3': 'MirrorMainnet_mTWTR_UST',
  '0xC4c0d58c11eC41CC0f1a5bE75296cf140Ca8dd87': 'NoopStrategyStable',
  '0xCf5F83F8FE0AB0f9E9C1db07E6606dD598b2bbf5': 'Swerve CRVStrategyYCRVMainnet v1',
  '0xd75ffA16FFbCf4078d55fF246CfBA79Bb8cE3F63': 'USDC CRVStrategyStableMainnet',
  '0x2CE34b1bb247f242f1d2A33811E01138968EFBFF': 'USDT CRVStrategyStableMainnet',
  '0x394E653bbFC9A3497A0487Abee153CA6498F053D': 'DAI CRVStrategyStableMainnet',
  '0x66B7611F35e48e311929e25D73428410C2335c34': 'CRVStrategySwerveUSDCMainnet',
  '0x892171EB51d56dc340E586652068cf758E5F798C': 'CRVStrategySwerveUSDTMainnet',
  '0xF60AFEBb76c43F636E4D1a099847Fc97dc8bDeD0': 'CRVStrategySwerveDAIMainnet',
  '0x01Fcb5Bc16e8d945bA276DCCFeE068231DA4cE33': 'CRVStrategySwerveUSDTMainnet',
  '0x18C4325Ae10FC84895C77C8310D6d98C748e9533': 'CRVStrategySwerveUSDCMainnet',
  '0x810B83fC33E6f5dA9Be9AE5dd0F918338e980938': 'CRVStrategyStableMainnet',
  '0xCf5F83F8FE0AB0f9E9C1db07E6606dD598b2bbf5': 'CRVStrategyYCRVMainnet',
  '0x2427DA81376A0C0a0c654089a951887242D67C92': 'CRVStrategyYCRVMainnet',
  '0xe7048E7186cB6f12C566A6C8a818D9D41da6Df19': 'CRVStrategyWBTCMainnet',
  '0x2EADFb06f9D890EBA80e999eABa2D445bC70f006': 'CRVStrategyRENBTCMainnet',
  '0xaf2D2e5c5aF90c782c008b5b287f20334eEB308E': 'CRVStrategyWRenBTCMixMainnet',
  '0x6AC7575A340a3DAb2Ae9ca07c4DbFC6bf8E7E281': 'CRVStrategySwerveDAIMainnet',
  '0xD21C3b9aF9861b925c83046eA906FE933A50c977': 'CRVStrategyYCRVMainnet',
  '0x3952555B3Be488F51f0b03315a85560a83c24E04': 'CRVStrategyWRenBTCMixMainnet',
  '0x0623cF5D4cD761E2C237fB02d1FA6424e03f5c8C': 'CRVStrategy3PoolMainnet',
  '0x6945F180b339825AC734649c12A1557e93b2b73A': 'CRVStrategyYCRVMainnet',
  '0x1825a0013E030DD668C5e4a00AE76Fb6E94687f6': 'CRVStrategyCompoundMainnet',
  '0x50f3cfb398A25A5918B27c77465e9C3EdE7888B7': 'CRVStrategyUSDNMainnet',
  '0x2b7CAA7D87c01152A82c266791AdA69CcFe64045': 'CRVStrategyBUSDMainnet',
  '0xE26d94dED203F5402882D19fEf92Ee04f6b73ef9': 'CRVStrategyTBTCMixedMainnet',
  '0x5E10a2A23393118306ccE080E3D3fc5447d0151b': 'CRVStrategyHBTCMainnet',
  '0x5905569D78ED1fA22299eab74ef0443D02B40000': 'CRVStrategyHUSDMainnet',
  '0xc55f8Be3cc55cae1BfBE5558D9E5b44906Ed248A': 'CRVStrategyUSTMainnet',
  '0x6d28d86ff925d2747D60a2b5C3E045F892f52285': 'CRVStrategyEURSMainnet',
  '0x52d8f04F071dD397C71514853A58664613B91192': 'CRVStrategySTETHMainnet',
  '0x807a637A1C82ca37d4bac0aB2684b33600c4a60A': 'CRVStrategyEURSV2Mainnet',
  '0xA505917C1326670451EfF9ea75FE0d49a3853acF': 'CRVStrategyGUSDMainnet',
  '0x2E916cF581547c1641BD259c01507136B4Ac6454': 'CRVStrategyOBTCMainnet',
  '0x0A7d74604b39229D444855eF294F287099774aC8': 'funi-eth-wbtc SNXRewardUniLPStrategy v1',
  '0xD3927f43D622e8BC9ce9a1111BeCd5d6d3cf3C90': 'funi-eth-wbtc SNXRewardUniLPStrategy v2',
  '0xb43aA2C44B99BaD346143Fb44e264213d412B6c2': 'funi-eth-usdt SNXRewardUniLPStrategy v1',
  '0x13627B75cf955eEe2d57Fc11a7082de5C36050c3': 'funi-eth-usdt SNXRewardUniLPStrategy v2',
  '0x50F1191F3059069888d9E16A327b96afdd26C6fD': 'funi-eth-usdc SNXRewardUniLPStrategy v1',
  '0x987A168E19F6F64D6AB08AE0e0FE77EA3D79BaaC': 'funi-eth-usdc SNXRewardUniLPStrategy v2',
  '0x2Fee56e039AcCceFA3cB1f3051aD00fe550a472c': 'funi-eth-dai SNXRewardUniLPStrategy v1',
  '0xA82660A0A468bBA63dB950532cdbDa47144c212c': 'funi-eth-dai SNXRewardUniLPStrategy v2',
  '0x0fd7c77b473e3Efe3170536805a14b61050eFc6E': 'funi-eth-usdt SNXRewardUniLPStrategy',
  '0xC6E973B8Fe772C58AD0D20099D43D2b3f0AEF5c0': 'funi-eth-usdc SNXRewardUniLPStrategy',
  '0x2CF4cEB36172Fb2196a47490419D57584234Cbd4': 'funi-eth-dai SNXRewardUniLPStrategy',
  '0x46eC909099F9691b43b64413F1BC662edFbee00A': 'funi-eth-wbtc SNXRewardUniLPStrategy',
  '0x4E015af8E1C5eB020f91063661CC5ce43719eBcF': 'WETHCreamNoFoldStrategy v1',
  '0xcF477F117cAa349Ca92dEdb3955481628D463bF1': 'WETHCreamNoFoldStrategy v2',
  '0x26D3e02999BEFFAEb07Af3A94438769DF0eE4150': 'WETH Cream Rescue Strategy',
  '0x53df6664b3ddE086DCe6315c317d1002b14B87E3': 'SushiMasterChefLPStrategy',
  '0x885D59830C1FdB120B54d62790dB7A6a1f534463': 'PickleStrategy3PoolMainnet',
  '0xa23c6F2d85fe47e613ce6bBb40E74aCB49Ae281a': 'DEGOSimpleStrategy',
  '0x0a1aD1698f7487655821c0d42d6691Ec43276E08': 'NoopStrategyStable',
  '0x2059711f1cf4c215f48dBBbC4cf6aF5AC5131C82': 'NoopStrategyStable',
  '0x099a926E55D24392BA3817fE38caA9eFA8c7b06A': 'NoopStrategyStable',
  '0xE715458Cd3ba5377487822F748BE1a5b994Db436': 'NoopStrategyStable',
  '0xABcEa95e3603C0604C81c2d95ED3aBD91c013aE6': 'NoopStrategyStable',
  '0xFDE5dfb79d4A65913CB72ddd9148a768705e98D4': 'IdleStrategyDAIMainnet',
  '0x1a69F857103De1B531Ab7CF935Ffc6a46C2e488c': 'IdleStrategyTUSDMainnet',
  '0x93ceE333C690CB91c39AC7B3294740651DC79C3d': 'IdleStrategyUSDCMainnet',
  '0x49938D0E7Ab1F224Ac091058e8638e4b8DA08dA6': 'IdleStrategyUSDTMainnet',
  '0x6561E55A43545BCC9EAE3202F3075b3Dc5283E90': 'IdleStrategyWBTCMainnet',
  '0xa5F125c0D571FD67D564C05a234E9a6f4E5d0624': 'IdleStrategyUSDCMainnet',
  '0x5B96D6b56d4051Cb54269f3620C262dB22366194': 'IdleStrategyUSDTMainnet',
  '0xb8E9Db02262d37233442932E1A6626D88c649c6e': 'IdleStrategyWBTCMainnet',
  '0xC78589912C85B3c86055A244580629A8c6504695': 'IdleStrategyTUSDMainnet',
  '0x9a6dE10fc9B9D1CA9Df3caF306ED60Ef1C419774': 'IdleStrategyDAIMainnet',
  '0x180A71C5688AC7e2368890ef77B0036Af8e261b6': 'StrategyProxy',
  '0x895CC1b32Aa6f5FEdf0E113eAC556309Ad225322': 'StrategyProxy',
  '0xd5d2ADcb5e6ad20425B0650E4050c0eA9ec3cEC0': 'StrategyProxy',
  '0xdD1dFbB5A580e96C2723cCAF687227900F97F053': 'StrategyProxy',
  '0xA44ffa733f1d500Fd10C613Cf66C87320d87ebee': 'StrategyProxy',
  '0x1Dcaf36c8c4222139899690945f4382f298f8735': 'CompoundWETHFoldStrategyMainnet',
  '0x5DB1B2128bCCC5B49f9cA7E3086b14fd4cf2ef64': 'CompoundNoFoldStrategyUSDCMainnet',
  '0xDA9A3F634eDE5DE46ea3B7BBFc6a811C4AeBe737': 'CompoundNoFoldStrategyUSDTMainnet',
  '0x180c496709023CE8952003A9FF385a3bBEB8b2C3': 'CompoundNoFoldStrategyDAIMainnet',
  '0x7f522f8619018F6D905A670830800903bCee544d': 'SNXRewardUniLPStrategy',
  '0xa81363950847aC250A2165D9Fb2513cA0895E786': 'SNXRewardUniLPStrategy_MIC_USDT',
  '0x940db279d149de71FDa27fA057936265A92d8d7e': 'SNXRewardUniLPStrategy_MIS_USDT',
  '0xA9cA706797702a50ea76aC9920774c8E982E4436': 'SNXRewardUniLPStrategy_DAI_BAS',
  '0xa89CBbE676562EbD0728E6cFA431DeBe77184090': 'SNXRewardUniLPStrategy_BAC_DAI',
  '0xb5480a276C49B5e3a1bC13659030b4E94018a817': 'MirrorMainnet_mTSLA_UST',
  '0x0a6ADe7348598E42Da381B03C1c40c9bA1c7747D': 'MirrorMainnet_mGOOG_UST',
  '0x0c3d0B5910b0603d68be29a647c0F6187A8c3D36': 'MirrorMainnet_mAMZN_UST',
  '0xA5a091fd156FF5e44f22Bef544923CDc850d9D46': 'MirrorMainnet_mAAPL_UST',
  '0x636A37802dA562F7d562c1915cC2A948A1D3E5A0': 'MithCash2FarmStrategyMainnet_MIS_USDT',
  '0xe12C4bB7b88b3CFe2d44a8e49037392B06bfaE72': 'MithCash2FarmStrategyMainnet_MIC_USDT',
  '0x65fEFAB5ebeB38cBdE82C4C20E226834db15eD9F': 'Basis2FarmStrategyMainnet_BAC_DAI',
  '0x61Ecfe8eB3522EC685C70f4732cf32c39CFd7d36': 'Basis2FarmStrategyMainnet_DAI_BAS',
  '0x185F97Af588c0D416Da1Bc3828234F94F4681810': 'BasisGoldStrategyMainnet_DSD',
  '0x7e2a45Ea5223eD02fE80e5020Aa650121A7361ab': 'BasisGoldStrategyMainnet_ESD',
  '0xB075bA5DC253E39376AC044182BE13315e828AE2': 'BasisGoldStrategyMainnet_BAC',
  '0x3F37185399537e95686a66247514De55C8792eb3': 'BasisGold2FarmStrategyMainnet_DAI_BSGS',
  '0x8d640378C983C6aab076bdB5d86A58F9179055eD': 'BasisGold2FarmStrategyMainnet_DAI_BSG',
  '0x67729651D5B265b0AD3e009437A71396Ae33eb83': 'OneInchStrategy_ETH_USDT',
  '0x15aDA3630227a33751e986F3E77b0a073f77d17d': 'OneInchStrategy_ETH_WBTC',
  '0xb97fDc1C48aBc7F25605118E6b4842dc57e666aF': 'OneInchStrategy_ETH_DAI',
  '0x8eA2DB065F74064DAF96Ab1aF9637131D5Fa4D95': 'OneInchStrategy_ETH_USDC',
  '0x323C726C899Ca9fB7b747fF61bC30183BdeB3c09': 'KlondikeStrategyMainnet_renBTC',
  '0xCe2FA27AD136c6035f60e8cf2Ad605d805745972': 'OneInchStrategy_ETH_WBTC',
  '0x7fB83f9c82065e8aA2321b4D86BDE76F381A4b0D': 'OneInchStrategy_ETH_USDT',
  '0xab9f3C22A580E04fA20650fef7aEfD937FeCA833': 'OneInchStrategy_ETH_USDC',
  '0x39AD7127896DB44389B84C23Bfa325E4161C9dA3': 'OneInchStrategy_ETH_DAI',
  '0x8B6Bef8D373D959a5f20D959BC44ebcA876f5464': 'GamestopStrategyMainnet_DSD',
  '0x9B29FB315be3333281A6f7c62ebFf799A6B6dC80': 'GamestopStrategyMainnet_ESD',
  '0xF2004f64F71F110e9e50B5Ff36253fE8785b2BCc': 'iFarmStrategy',
  '0xdC9a3e8c6327c6Fea1780019e00F7b0558f638A5': 'CRVStrategyAAVEMainnet',
  '0x1adAfE68f46e0aEcd5364b85966C8C16D4079361': 'Basis2FarmStrategyMainnet_DAI_BASV2',
  '0x1a0B8b5c603CAc03b3B6B7a9679F5E2c1E98f248': 'Klondike2FarmStrategyMainnet_WBTC_KLON',
  '0x5334cf3a2006f05f879f8677a6a1fb94c6ba7861': 'Klondike2FarmStrategyMainnet_WBTC_KBTC',
  '0x1b8e2b4Ad303550d6872C08C5F6c024b68B2286D': 'OneInchStrategy_ETH_ONEINCH',
  '0x6b477831b8af02393f1FEDD36956418cE9927894': 'Basis2FarmStrategyMainnet_BAC_DAIV2',
  '0x3a0073726E60Fd202fD228a9C88288F331977d04': 'CRVStrategyLINKMainnet',
}

vaults = {
  '0x5EA74C6AbF0e523fdecFE218CCb3d2fDe2339613': {'asset': 'fUNI-MVI:ETH', 'decimals': 18, 'type': 'timelock',},
  '0xB89777534acCcc9aE7cbA0e72163f9F214189263': {'asset': 'fUNI-COMFI:ETH', 'decimals': 18, 'type': 'timelock',},
  '0xe6e0B4294eF6a518bB702402e9842Df2a2Abf1B1': {'asset': 'fUNI-ETH:GPUNKS', 'decimals': 18, 'type': 'timelock',},
  '0xd3093e3EfBE00f010E8F5Efe3f1cb5d9b7Fe0eb1': {'asset': 'f-ETHx5-1Jun21', 'decimals': 18, 'type': 'timelock',},
  #'': {'asset': '', 'decimals': 18, 'type': 'timelock',},
  '0x227A46266329767cEa8883BFC81d21f1Ea0EdbB3': {'asset': 'fUNI-MEME20:ETH', 'decimals': 18, 'type': 'timelock',},
  '0xBb1565072FB4f3244eBcE5Bc8Dfeda6baEb78Ad3': {'asset': 'fUNI-GPUNKS20:ETH', 'decimals': 18, 'type': 'timelock',},
  '0x4d3C5dB2C68f6859e0Cd05D080979f597DD64bff': {'asset': 'fUNI-MVI:ETH', 'decimals': 18, 'type': 'timelock',},
  '0x672C973155c46Fc264c077a41218Ddc397bB7532': {'asset': 'fUNI-KXUSD:DAI', 'decimals': 18, 'type': 'timelock',},
  # Harvest internal vaults
  '0x1571eD0bed4D987fe2b498DdBaE7DFA19519F651': {'asset': 'iFARM', 'decimals': 18, 'type': 'timelock',},
  # Sushiswap liquidity incentives + do not sell SUSHI
  '0x274AA8B58E8C57C4e347C8768ed853Eb6D375b48': {'asset': 'xSUSHI HODL', 'decimals': 18, 'type': 'timelock',},
  '0x29EC64560ab14d3166222Bf07c3F29c4916E0027': {'asset': 'fSUSHI-DAI:ETH HODL', 'decimals': 18, 'type': 'timelock',},
  '0x5774260CcD87F4FfFc4456260857207fc8BCb89A': {'asset': 'fSUSHI-USDC:ETH HODL', 'decimals': 18, 'type': 'timelock',},
  '0x4D4B6f8EFb685b774234Fd427201b3a9bF36ffc8': {'asset': 'fSUSHI-ETH:USDT HODL', 'decimals': 18, 'type': 'timelock',},
  '0xB677bcA369f2523F62862F88d83471D892dD55B9': {'asset': 'fSUSHI-WBTC:ETH HODL', 'decimals': 18, 'type': 'timelock',},
   # Sushiswap liquidity incentives
  '0x5aDe382F38A09A1F8759D06fFE2067992ab5c78e': {'asset': 'fSUSHI-SUSHI:ETH', 'decimals': 18, 'type': 'timelock',},
  '0xF553E1f826f42716cDFe02bde5ee76b2a52fc7EB': {'asset': 'fSUSHI-WBTC:TBTC', 'decimals': 18, 'type': 'timelock',},
  '0x203E97aa6eB65A1A02d9E80083414058303f241E': {'asset': 'fSUSHI-WETH:DAI', 'decimals': 18, 'type': 'timelock',},
  '0x64035b583c8c694627A199243E863Bb33be60745': {'asset': 'fSUSHI-WETH:USDT', 'decimals': 18, 'type': 'timelock',},
  '0x01bd09A1124960d9bE04b638b142Df9DF942b04a': {'asset': 'fSUSHI-WETH:USDC', 'decimals': 18, 'type': 'timelock',},
  '0x5C0A3F55AAC52AA320Ff5F280E77517cbAF85524': {'asset': 'fSUSHI-WETH:WBTC', 'decimals': 18, 'type': 'timelock',},
  '0x6F14165c6D529eA3Bfe1814d0998449e9c8D157D': {'asset': 'fSUSHI-MIC:USDT', 'decimals': 18, 'type': 'timelock',},
  '0x145f39B3c6e6a885AA6A8fadE4ca69d64bab69c8': {'asset': 'fSUSHI-MIS:USDT', 'decimals': 18, 'type': 'timelock',},
  '0x4D4D85c6a1ffE6Bb7a1BEf51c9E2282893feE521': {'asset': 'fSUSHI-ETH:UST', 'decimals': 18, 'type': 'timelock',},
  # Uniswap liquidity incentives
  ### Uniswap - NFT stuff
  '0xc45d471c77ff31C39474d68a5080Fe1FfACDBC04': {'asset': 'fUNI-MUSE:ETH', 'decimals': 18, 'type': 'timelock',},
  '0xF2a671645D0DF54d2f03E9ad7916c8F7368D1C29': {'asset': 'fUNI-ETH:MASK20', 'decimals': 18, 'type': 'timelock',},
  '0x1E5f4e7127ea3981551D2Bf97dCc8f17a4ECEbEf': {'asset': 'fUNI-DUDES20:ETH', 'decimals': 18, 'type': 'timelock',},
  '0xAF9486E3DA0cE8d125aF9b256b3ecd104a3031B9': {'asset': 'fUNI-ROPE20:ETH', 'decimals': 18, 'type': 'timelock',},
  '0x0cA19915439C12B16C0A8C119eC05fA801365a15': {'asset': 'fUNI-MCAT20:ETH', 'decimals': 18, 'type': 'timelock',},
  ### Uniswap - Terra Mirror synthetic assets
  '0x11804D69AcaC6Ae9466798325fA7DE023f63Ab53': {'asset': 'fUNI-UST:mAAPL', 'decimals': 18, 'type': 'timelock',},
  '0x8334A61012A779169725FcC43ADcff1F581350B7': {'asset': 'fUNI-mAMZN:UST', 'decimals': 18, 'type': 'timelock',},
  '0x07DBe6aA35EF70DaD124f4e2b748fFA6C9E1963a': {'asset': 'fUNI-mGOOGL:UST', 'decimals': 18, 'type': 'timelock',},
  '0xC800982d906671637E23E031e907d2e3487291Bc': {'asset': 'fUNI-mTSLA:UST', 'decimals': 18, 'type': 'timelock',},
  '0xb37c79f954E3e1A4ACCC14A5CCa3E46F226038b7': {'asset': 'fUNI-UST:mTWTR', 'decimals': 18, 'type': 'timelock',},
  '0x99C2564C9D4767C13E13F38aB073D4758af396Ae': {'asset': 'fUNI-UST:mNFLX', 'decimals': 18, 'type': 'timelock',},
  ### Uniswap - Algorithmic Stablecoins
  '0x6Bccd7E983E438a56Ba2844883A664Da87E4C43b': {'asset': 'fUNI-BAC:DAI', 'decimals': 18, 'type': 'timelock',},
  '0xf8b7235fcfd5A75CfDcC0D7BC813817f3Dd17858': {'asset': 'fUNI-BAS:DAI', 'decimals': 18, 'type': 'timelock',},
  '0x633C4861A4E9522353EDa0bb652878B079fb75Fd': {'asset': 'fUNI-DAI:BSGS', 'decimals': 18, 'type': 'timelock',},
  '0x639d4f3F41daA5f4B94d63C2A5f3e18139ba9E54': {'asset': 'fUNI-DAI:BSG', 'decimals': 18, 'type': 'timelock',},
  ### Uniswap - Klondike Bitcoin Synthetic
  '0xB4E3fC276532f27Bd0F738928Ce083A3b064ba61': {'asset': 'fUNI-WBTC:KLON', 'decimals': 18, 'type': 'timelock',},
  '0x5cd9Db40639013A08d797A839C9BECD6EC5DCD4D': {'asset': 'fUNI-WBTC:KBTC', 'decimals': 18, 'type': 'timelock',},
  ### Uniswap - Everything Else
  '0xb1FeB6ab4EF7d0f41363Da33868e85EB0f3A57EE': {'asset': 'fUNI-ETH-WBTC-v0', 'decimals': 18,},
  '0xB19EbFB37A936cCe783142955D39Ca70Aa29D43c': {'asset': 'fUNI-ETH-USDT-v0', 'decimals': 18,},
  '0x63671425ef4D25Ec2b12C7d05DE855C143f16e3B': {'asset': 'fUNI-ETH-USDC-v0', 'decimals': 18,},
  '0x1a9F22b4C385f78650E7874d64e442839Dc32327': {'asset': 'fUNI-ETH-DAI-v0', 'decimals': 18,},
  '0x01112a60f427205dcA6E229425306923c3Cc2073': {'asset': 'fUNI-ETH-WBTC', 'decimals': 18, 'type': 'timelock',},
  '0x7DDc3ffF0612E75Ea5ddC0d6Bd4e268f70362Cff': {'asset': 'fUNI-ETH-USDT', 'decimals': 18, 'type': 'timelock',},
  '0xA79a083FDD87F73c2f983c5551EC974685D6bb36': {'asset': 'fUNI-ETH-USDC', 'decimals': 18, 'type': 'timelock',},
  '0x307E2752e8b8a9C29005001Be66B1c012CA9CDB7': {'asset': 'fUNI-ETH-DAI', 'decimals': 18, 'type': 'timelock',},
  '0x2a32dcBB121D48C106F6d94cf2B4714c0b4Dfe48': {'asset': 'fUNI-ETH-DPI', 'decimals': 18, 'type': 'timelock',},
  # 1INCH liquidity incentives
  '0xDdB4669f39c03A6edA92ffB5B78A9C1a74615F1b': {'asset': 'f1INCH-1INCH:WBTC', 'decimals': 18, 'type': 'timelock',},
  '0xF174DDDD9DBFfeaeA5D908a77d695a77e53025b3': {'asset': 'f1INCH-1INCH:USDC', 'decimals': 18, 'type': 'timelock',},
  '0xFCA949E34ecd9dE519542CF02054DE707Cf361cE': {'asset': 'f1INCH-ETH:1INCH', 'decimals': 18, 'type': 'timelock',},
  '0x8e53031462E930827a8d482e7d80603B1f86e32d': {'asset': 'f1INCH-ETH:DAI', 'decimals': 18, 'type': 'timelock',},
  '0x859222DD0B249D0ea960F5102DaB79B294d6874a': {'asset': 'f1INCH-ETH:WBTC', 'decimals': 18, 'type': 'timelock',},
  '0x4bf633A09bd593f6fb047Db3B4C25ef5B9C5b99e': {'asset': 'f1INCH-ETH:USDT', 'decimals': 18, 'type': 'timelock',},
  '0xD162395C21357b126C5aFED6921BC8b13e48D690': {'asset': 'f1INCH-ETH:USDC', 'decimals': 18, 'type': 'timelock',},
  # Curve liquidity incentives
  '0x7Eb40E450b9655f4B3cC4259BCC731c63ff55ae6': {'asset': 'fCRV-USDP', 'decimals': 18, 'type': 'timelock',},
  '0x24C562E24A4B5D905f16F2391E07213efCFd216E': {'asset': 'fCRV-LINK', 'decimals': 18, 'type': 'timelock',},
  '0x9aA8F427A17d6B0d91B6262989EdC7D45d6aEdf8': {'asset': 'fCRV-RENWBTC', 'decimals': 18, 'type': 'timelock',},
  '0x640704D106E79e105FDA424f05467F005418F1B5': {'asset': 'fCRV-TBTC', 'decimals': 18, 'type': 'timelock',},
  '0x71B9eC42bB3CB40F017D8AD8011BE8e384a95fa5': {'asset': 'fCRV-3POOL', 'decimals': 18, 'type': 'timelock',},
  '0x0FE4283e0216F94f5f9750a7a11AC54D3c9C38F3': {'asset': 'fCRV-YPOOL', 'decimals': 18, 'type': 'timelock',},
  '0x683E683fBE6Cf9b635539712c999f3B3EdCB8664': {'asset': 'fCRV-USDN', 'decimals': 18, 'type': 'timelock',},
  '0x4b1cBD6F6D8676AcE5E412C78B7a59b4A1bbb68a': {'asset': 'fCRV-BUSD', 'decimals': 18, 'type': 'timelock',},
  '0x998cEb152A42a3EaC1f555B1E911642BeBf00faD': {'asset': 'fCRV-COMP', 'decimals': 18, 'type': 'timelock',},
  '0x29780C39164Ebbd62e9DDDE50c151810070140f2': {'asset': 'fCRV-HUSD', 'decimals': 18, 'type': 'timelock',},
  '0xCC775989e76ab386E9253df5B0c0b473E22102E2': {'asset': 'fCRV-HBTC', 'decimals': 18, 'type': 'timelock',},
  '0xc3EF8C4043D7cf1D15B6bb4cd307C844E0BA9d42': {'asset': 'fCRV-AAVE', 'decimals': 18, 'type': 'timelock',},
  '0xB8671E33fcFC7FEA2F7a3Ea4a117F065ec4b009E': {'asset': 'fCRV-GUSD', 'decimals': 18, 'type': 'timelock',},
  '0xc27bfE32E0a934a12681C1b35acf0DBA0e7460Ba': {'asset': 'fCRV-stETH', 'decimals': 18, 'type': 'timelock',},
  '0x84A1DfAdd698886A614fD70407936816183C0A02': {'asset': 'fCRV-UST', 'decimals': 18, 'type': 'timelock',},
  '0x6eb941BD065b8a5bd699C5405A928c1f561e2e5a': {'asset': 'fCRV-EURS', 'decimals': 18, 'type': 'timelock',},
  '0x966A70A4d3719A6De6a94236532A0167d5246c72': {'asset': 'fCRV-OBTC', 'decimals': 18, 'type': 'timelock',},
  '0x192E9d29D43db385063799BC239E772c3b6888F3': {'asset': 'fCRV-RenWBTC-v0', 'decimals': 18,},
  '0xF2B223Eb3d2B382Ead8D85f3c1b7eF87c1D35f3A': {'asset': 'FARM yDAI+yUSDC+yUSDT+yTUSD', 'decimals': 18,},
  # Single Asset Vaults
  '0x8Bf3c1c7B1961764Ecb19b4FC4491150ceB1ABB1': {'asset': 'fDSD', 'decimals': 18, 'type': 'timelock',},
  '0x45a9e027DdD8486faD6fca647Bb132AD03303EC2': {'asset': 'fESD', 'decimals': 18, 'type': 'timelock',},
  '0x371E78676cd8547ef969f89D2ee8fA689C50F86B': {'asset': 'fBAC', 'decimals': 18, 'type': 'timelock',},
  '0x8e298734681adbfC41ee5d17FF8B0d6d803e7098': {'asset': 'fWETH-v0', 'decimals': 18,},
  '0xe85C8581e60D7Cd32Bbfd86303d2A4FA6a951Dac': {'asset': 'fDAI-v0', 'decimals': 18,},
  '0xc3F7ffb5d5869B3ade9448D094d81B0521e8326f': {'asset': 'fUSDC-v0', 'decimals': 6,},
  '0xc7EE21406BB581e741FBb8B21f213188433D9f2F': {'asset': 'fUSDT-v0', 'decimals': 6,},
  '0xfBe122D0ba3c75e1F7C80bd27613c9f35B81FEeC': {'asset': 'fRenBTC-v0', 'decimals': 8,},
  '0xc07EB91961662D275E2D285BdC21885A4Db136B0': {'asset': 'fWBTC-v0', 'decimals': 8,},
  '0x7674622c63Bee7F46E86a4A5A18976693D54441b': {'asset': 'fTUSD', 'decimals': 18, 'type': 'timelock',},
  '0xFE09e53A81Fe2808bc493ea64319109B5bAa573e': {'asset': 'fWETH', 'decimals': 18, 'type': 'timelock',},
  '0xab7FA2B2985BCcfC13c6D86b1D5A17486ab1e04C': {'asset': 'fDAI', 'decimals': 18, 'type': 'timelock',},
  '0xf0358e8c3CD5Fa238a29301d0bEa3D63A17bEdBE': {'asset': 'fUSDC', 'decimals': 6, 'type': 'timelock',},
  '0x053c80eA73Dc6941F518a68E2FC52Ac45BDE7c9C': {'asset': 'fUSDT', 'decimals': 6, 'type': 'timelock',},
  '0x5d9d25c7C457dD82fc8668FFC6B9746b674d4EcB': {'asset': 'fWBTC', 'decimals': 8, 'type': 'timelock',},
  '0xC391d1b08c1403313B0c28D47202DFDA015633C4': {'asset': 'fRENBTC', 'decimals': 8, 'type': 'timelock',},
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
controller_contract = w3.eth.contract(address=CONTROLLER_ADDR, abi=CONTROLLER_ABI)
unipool_eth_contract = w3.eth.contract(address=UNIPOOL_FARM_ETH_ADDR, abi=UNIPOOL_ABI)
unipool_usdc_contract = w3.eth.contract(address=UNIPOOL_FARM_USDC_ADDR, abi=UNIPOOL_ABI)
unipool_usdceth_contract = w3.eth.contract(address=UNIPOOL_USDC_ETH_ADDR, abi=UNIPOOL_ABI)
unirouter_contract = w3.eth.contract(address=UNIROUTER_ADDR, abi=UNIROUTER_ABI)
grain_contract = w3.eth.contract(address=GRAIN_ADDR, abi=TOKEN_FARM_ABI)
minter_contract = w3.eth.contract(address=MINTER_ADDR, abi=MINTER_ABI)
# Smart Contracts - MATIC
matic_root_contract = w3.eth.contract(address=MATIC_ROOT_ADDR, abi=MATIC_ROOT_ABI)
matic_erc20_contract = w3.eth.contract(address=MATIC_ERC20_ADDR, abi=MATIC_ERC20_ABI)
if activenet['matic']:
  matic_unirouter_contract = m3.eth.contract(address=MATIC_UNIROUTER_ADDR, abi=UNIROUTER_ABI)
  matic_unipool_ifarm_matic_contract = m3.eth.contract(address=MATIC_UNIPOOL_IFARM_MATIC_ADDR, abi=UNIPOOL_ABI)
  matic_unipool_ifarm_quick_contract = m3.eth.contract(address=MATIC_UNIPOOL_IFARM_QUICK_ADDR, abi=UNIPOOL_ABI)
# Smart Contracts - BSC
if activenet['bsc']:
  bsc_unirouter_contract = b3.eth.contract(address=BSC_UNIROUTER_ADDR, abi=UNIROUTER_ABI)
  bsc_unipool_farm_busd_contract = b3.eth.contract(address=BSC_UNIPOOL_FARM_BUSD_ADDR, abi=UNIPOOL_ABI)

txids_seen = []

def handle_event(event):
  txhash = event.transactionHash.hex()
  blocknum = event.blockNumber
  #sender = w3.eth.getTransaction(txhash)['from']
  #print(event)
  msg = ''
  tweet = False
  color = None
  net = 'ETH'

  # GRAIN BURN
  if event.address == GRAIN_ADDR:
    if txhash in txids_seen:
      return
    print(f'event: GRAIN burn')
    remaining_supply, total_supply = get_burn_stats(blocknum)
    burner_addr = event.args['from']
    color = 32768
    msg = (f':fire: At block `{blocknum}`, '
           f'`{int(event.args.value)*10**-18:,.3f}` <:grain:784594063499853904> GRAIN was [burned](<https://etherscan.io/tx/{txhash}>)\n'
           f'by [{burner_addr}](<https://etherscan.io/address/{burner_addr}>)!\n'
           f'`{total_supply-remaining_supply:,.3f}` of `{total_supply:,.3f}` burned (`{100*(total_supply-remaining_supply)/total_supply:.4f}%` :fire::fire::fire:)'
           )

  # UNISWAP TRADE, USDC
  elif event.address == UNIPOOL_FARM_USDC_ADDR:
    # trades with yield aggregators may contain multiple uniswap event logs
    #if txhash in txids_seen:
    #  return
    print(f'event: FARM trade in the FARM:USDC Uniswap pool')
    sender = w3.eth.getTransaction(txhash)['from']
    farmsell, farmbuy = int(event.args.amount0In)*10**-18, int(event.args.amount0Out)*10**-18
    usdcsell, usdcbuy = int(event.args.amount1In)*10**-6, int(event.args.amount1Out)*10**-6
    # get price information
    print(f'fetching pool reserves...')
    poolvals = unipool_usdc_contract.functions['getReserves']().call(block_identifier=blocknum)
    poolvals_eth = unipool_eth_contract.functions['getReserves']().call(block_identifier=blocknum)
    print(f'calculating price...')
    price = unirouter_contract.functions['quote'](ONE_18DEC, poolvals[0], poolvals[1]).call(block_identifier=blocknum)*10**-6
    print(f'price of FARM: ${price}')
    # build message
    if farmbuy > 0:
      color = 32768
      pricechange = 100 * farmbuy / ( poolvals_eth[0] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD:
        return
      msg = (f':chart_with_upwards_trend: At block `{blocknum}`, '
             f'`+{pricechange:.4f}%`:evergreen_tree: to `${price:,.2f}`; '
             f'`{farmbuy:,.2f}` FARM was [bought](<https://etherscan.io/tx/{txhash}>)\n'
             f'by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )
    if farmsell > 0:
      color = 16711680
      pricechange = 100 * farmsell / ( poolvals_eth[0] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD:
        return
      msg = (f':chart_with_downwards_trend: At block `{blocknum}`, '
             f'`-{pricechange:.4f}%`:small_red_triangle_down: to `${price:,.2f}`; '
             f'`{farmsell:,.2f}` FARM was [sold](<https://etherscan.io/tx/{txhash}>)\n'
             f'by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )

  # UNISWAP TRADE, ETH
  elif event.address == UNIPOOL_FARM_ETH_ADDR:
    # trades with yield aggregators may contain multiple uniswap event logs
    #if txhash in txids_seen:
    #  return
    print(f'event: FARM trade in the FARM:ETH Uniswap pool')
    sender = w3.eth.getTransaction(txhash)['from']
    farmsell, farmbuy = int(event.args.amount0In)*10**-18, int(event.args.amount0Out)*10**-18
    ethsell, ethbuy = int(event.args.amount1In)*10**-18, int(event.args.amount1Out)*10**-18
    # get price information
    print(f'fetching FARM pool reserves...')
    poolvals = unipool_eth_contract.functions['getReserves']().call(block_identifier=blocknum)
    print(f'calculating price...')
    price_farm_eth = unirouter_contract.functions['quote'](ONE_18DEC, poolvals[0], poolvals[1]).call(block_identifier=blocknum)*10**-18
    price_eth_usd = get_ethprice_usd(blocknum)
    price = price_farm_eth * price_eth_usd
    print(f'price of FARM: ${price}')
    # build message
    if farmbuy > 0:
      color = 32768
      pricechange = 100 * farmbuy / ( poolvals[0] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD:
        return
      msg = (f':chart_with_upwards_trend: At block `{blocknum}`, '
             f'`+{pricechange:.4f}%`:evergreen_tree: to `${price:,.2f}`; '
             f'`{farmbuy:,.2f}` FARM was [bought](<https://etherscan.io/tx/{txhash}>)\n'
             f'by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )
    if farmsell > 0:
      color = 16711680
      pricechange = 100 * farmsell / ( poolvals[0] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD:
        return
      msg = (f':chart_with_downwards_trend: At block `{blocknum}`, '
             f'`-{pricechange:.4f}%`:small_red_triangle_down: to `${price:,.2f}`; '
             f'`{farmsell:,.2f}` FARM was [sold](<https://etherscan.io/tx/{txhash}>)\n'
             f'by [{sender}](<https://etherscan.io/address/{sender}>)!'
             )

  # UNISWAP TRADE, MATIC, WMATIC
  elif event.address == MATIC_UNIPOOL_IFARM_MATIC_ADDR:
    net = 'MATIC'
    # trades with yield aggregators may contain multiple uniswap event logs
    #if txhash in txids_seen:
    #  return
    print(f'event: IFARM trade in the MATIC:IFARM Quickswap pool')
    sender = m3.eth.getTransaction(txhash)['from']
    farmsell, farmbuy = int(event.args.amount1In)*10**-18, int(event.args.amount1Out)*10**-18
    quotesell, quotebuy = int(event.args.amount0In)*10**-18, int(event.args.amount0Out)*10**-18
    # get price information
    print(f'fetching pool reserves...')
    poolvals = matic_unipool_ifarm_matic_contract.functions['getReserves']().call(block_identifier=blocknum)
    #poolvals_eth = unipool_eth_contract.functions['getReserves']().call(block_identifier=blocknum)
    print(f'calculating price...')
    price = matic_unirouter_contract.functions['quote'](ONE_18DEC, poolvals[1], poolvals[0]).call(block_identifier=blocknum)*10**-18
    print(f'price of FARM: {price} MATIC')
    # build message
    if farmbuy > 0:
      color = 32768
      pricechange = 100 * farmbuy / ( poolvals[1] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD_MATIC:
        return
      msg = (f':chart_with_upwards_trend: At block `{blocknum}`, '
             f'`{farmbuy:,.2f}` iFARM was [bought](<https://explorer-mainnet.maticvigil.com/tx/{txhash}>)'
             f' on [Matic Quickswap](https://quickswap.exchange/#/swap?outputCurrency=0xab0b2ddB9C7e440fAc8E140A89c0dbCBf2d7Bbff)\n'
             f'<:chadright:758033272101011622> by [{sender}](<https://explorer-mainnet.maticvigil.com/address/{sender}>)!\n'
             f':evergreen_tree: `+{pricechange:.4f}%` to `{price:,.2f} MATIC` per `FARM`'
             )
    if farmsell > 0:
      color = 16711680
      pricechange = 100 * farmsell / ( poolvals[1] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD_MATIC:
        return
      msg = (f':chart_with_downwards_trend: At block `{blocknum}`, '
             f'`{farmsell:,.2f}` iFARM was [sold](<https://explorer-mainnet.maticvigil.com/tx/{txhash}>)'
             f' on [Matic Quickswap](https://quickswap.exchange/#/swap?outputCurrency=0xab0b2ddB9C7e440fAc8E140A89c0dbCBf2d7Bbff)\n'
             f'<:chadright:758033272101011622> by [{sender}](<https://explorer-mainnet.maticvigil.com/address/{sender}>)!\n'
             f':small_red_triangle_down: `-{pricechange:.4f}%` to `{price:,.2f} MATIC` per `FARM`'
             )

  # UNISWAP TRADE, BSC, BUSD
  elif event.address == BSC_UNIPOOL_FARM_BUSD_ADDR:
    net = 'BSC'
    # trades with yield aggregators may contain multiple uniswap event logs
    #if txhash in txids_seen:
    #  return
    print(f'event: FARM trade in the FARM:BUSD Pancakeswap pool')
    sender = b3.eth.getTransaction(txhash)['from']
    farmsell, farmbuy = int(event.args.amount1In)*10**-18, int(event.args.amount1Out)*10**-18
    quotesell, quotebuy = int(event.args.amount0In)*10**-18, int(event.args.amount0Out)*10**-18
    # get price information
    #print(f'fetching pool reserves...')
    #poolvals = matic_unipool_ifarm_matic_contract.functions['getReserves']().call(block_identifier=blocknum)
    #poolvals_eth = unipool_eth_contract.functions['getReserves']().call(block_identifier=blocknum)
    #print(f'calculating price...')
    #price = matic_unirouter_contract.functions['quote'](ONE_18DEC, poolvals[1], poolvals[0]).call(block_identifier=blocknum)*10**-18
    print(f'price of FARM: {price} MATIC')
    # build message
    if farmbuy > 0:
      color = 32768
      #pricechange = 100 * farmbuy / ( poolvals[1] * 10**-18)
      #if pricechange < PRICEDELTA_PERCENT_THRESHOLD_MATIC:
      #  return
      msg = (f':chart_with_upwards_trend: At block `{blocknum}`, '
             f'`{farmbuy:,.2f}` FARM was [bought](<https://bscscan.com/tx/{txhash}>)'
             f' on [BSC Pancakeswap](https://exchange.pancakeswap.finance/#/swap?outputCurrency=0x4B5C23cac08a567ecf0c1fFcA8372A45a5D33743)\n'
             f'<:chadright:758033272101011622> by [{sender}](<https://bscscan.com/address/{sender}>)!\n'
      #       f':evergreen_tree: `+{pricechange:.4f}%` to `{price:,.2f} MATIC` per `FARM`'
             )
    if farmsell > 0:
      color = 16711680
      pricechange = 100 * farmsell / ( poolvals[1] * 10**-18)
      if pricechange < PRICEDELTA_PERCENT_THRESHOLD_MATIC:
        return
      msg = (f':chart_with_downwards_trend: At block `{blocknum}`, '
             f'`{farmsell:,.2f}` FARM was [sold](<https://bscscan.com/tx/{txhash}>)'
             f' on [BSC Pancakeswap](https://exchange.pancakeswap.finance/#/swap?outputCurrency=0x4B5C23cac08a567ecf0c1fFcA8372A45a5D33743)\n'
             f'<:chadright:758033272101011622> by [{sender}](<https://bscscan.com/address/{sender}>)!\n'
#             f':small_red_triangle_down: `-{pricechange:.4f}%` to `{price:,.2f} MATIC` per `FARM`'
             )


 # MATIC ROOT EVENT
  elif event.address == MATIC_ROOT_ADDR:
    net = 'MATIC'
    if txhash in txids_seen:
      return
    print(f'event: Matic root event')
    event_name = event.event
    header_height = event.args.headerBlockId
    header_proposer = event.args.proposer
    header_child_start = event.args.start
    header_child_end = event.args.end
    msg = (f':tools: At block `{blocknum}`, [Matic {event_name}](<https://etherscan.io/tx/{txhash}>) proposed!\n'
           #f'proposed by `{header_proposer}`!\n'
           f':world_map: header block `{header_height}` for Matic blocks `{header_child_start}` to `{header_child_end}`\n'
           f':bridge_at_night: Matic→ Ethereum transfers may now be ready to claim on [Matic Bridge](<https://wallet.matic.network/bridge/>)'
            )
  # MATIC ERC20 EVENT
  elif event.address == MATIC_ERC20_ADDR:
    net = 'MATIC'
    if txhash in txids_seen:
      return
    if event.args.amount < 400000000000000000:
      return
    print(f'event: Matic erc20 deposit event')
    event_name = event.event
    msg = (f':tools: At block `{blocknum}`, `{event.args.amount*10**-18:,.2f}` [iFARM deposited](<https://etherscan.io/tx/{txhash}>) to [Matic Bridge](<https://wallet.matic.network/bridge/>)!\n'
           f':tractor: by `{event.args.depositor}` ([Ethereum](<https://etherscan.io/address/{event.args.depositor}>), [Matic](<https://explorer-mainnet.maticvigil.com/address/{event.args.depositor}>))\n'
            )
  # FARM MINTING EVENT
  elif event.address == MINTER_ADDR:
    if txhash in txids_seen:
      return
    print(f'event: FARM minting event')
    event_name = event.event
    msg = (f':tools: At block `{blocknum}`, [FARM minting #{event.args.id}](<https://etherscan.io/tx/{txhash}>) announced!\n'
            f':moneybag: `{event.args._amount*10**-18:,.2f}` FARM minting '
            f'at `{datetime.datetime.utcfromtimestamp(event.args.timeActive).strftime("%Y-%m-%d %H:%M:%S")} GMT`\n'
            f':lock: for delivery to [{event.args.target}](https://etherscan.io/address/{event.args.target})'
            )
  # VAULT EVENT
  elif event.address in vaults.keys():
    if txhash in txids_seen:
      return
    print(f'event: vault strategy update')
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
    if txhash in txids_seen:
      return
    print(f'event: (probably) HARDWORK on a vault')
    color = 16776960
    try:
      shareprice_decimals = int(vaults.get(event.args.vault, {'decimals':'18'})['decimals'])
      shareprice = event.args.newSharePrice * ( 10 ** ( -1 * shareprice_decimals ) )
      shareprice_delta = (event.args.newSharePrice - event.args.oldSharePrice) / event.args.oldSharePrice
      asset = vaults.get(event.args.vault, {'asset':'a new vault'})['asset']
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
    except:
      return
  send_msg(msg, tweet, net, color)
  txids_seen.append(txhash)
  cache_blockheight(net, blocknum)

def send_msg(msg, tweet, net='ETH', color=None):
  data = {}
  data['embeds'] = []
  embed = {}
  #embed['title'] = ":chains::mag: On-chain event detected!"
  embed['description'] = msg
  if color: embed['color'] = color
  data['embeds'].append(embed)
  if POST_TO_DISCORD == 'True' and len(msg) > 0:
    if net == 'MATIC':
      requests.post(WEBHOOK_URL_MATIC, json.dumps(data), headers={"Content-Type": "Application/json"})
    elif net == 'BSC':
      requests.post(WEBHOOK_URL_BSC, json.dumps(data), headers={"Content-Type": "Application/json"})
    elif net == 'ETH':
      requests.post(WEBHOOK_URL, json.dumps(data), headers={"Content-Type": "Application/json"})
  if tweet:
    try:
      print(msg)
      status = api.PostUpdate(tweet)
    except:
      print('could not tweet')
  time.sleep(1)

def get_ethprice_usd(blocknum):
    print(f'fetching ETH:USDC oracle price...')
    poolvals_usdc_eth = unipool_usdceth_contract.functions['getReserves']().call(block_identifier=blocknum)
    price_eth_usdc = unirouter_contract.functions['quote'](ONE_18DEC, poolvals_usdc_eth[1], poolvals_usdc_eth[0]).call(block_identifier=blocknum)*10**-6
    print(f'price of ETH: {price_eth_usdc} USDC')
    return price_eth_usdc

def get_burn_stats(blocknum):
  total_supply = GRAIN_SUPPLY
  remaining_supply = grain_contract.functions['totalSupply']().call(block_identifier=blocknum)*10**-18
  return remaining_supply, total_supply

def log_lookback(event_filters):
  print(f'Starting log lookback at {START_BLOCK_ETH}...')
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

def cache_blockheight(net, blocknum):
  with open(f'blockcache_{net}', 'w') as f:
    f.write(str(blocknum))
    print(f'{net.upper()} -- cache blockheight {blocknum}')

def main():
  if LOOKBACK == 'True':
    # set up lookback
    lookback_filters = []
    if LOOKBACK_MINTER == 'True':
      lookback_filters.append(minter_contract.events.MintingAnnounced.createFilter(fromBlock=START_BLOCK_ETH))
    if LOOKBACK_HARVESTS == 'True':
      lookback_filters.append(controller_contract.events.SharePriceChangeLog.createFilter(fromBlock=START_BLOCK_ETH))
    if LOOKBACK_TRADES == 'True':
      lookback_filters.append(unipool_usdc_contract.events.Swap.createFilter(fromBlock=START_BLOCK_ETH))
      lookback_filters.append(unipool_eth_contract.events.Swap.createFilter(fromBlock=START_BLOCK_ETH))
    if LOOKBACK_BURNS == 'True':
      lookback_filters.append(grain_contract.events.Transfer.createFilter(fromBlock=START_BLOCK_ETH, argument_filters={"to":ZERO_ADDR}))
    if LOOKBACK_STRATEGIES == 'True':
      for vault in vaults:
        if vaults.get(vault).get('type', '') == 'timelock':
          vault_contract = w3.eth.contract(address=vault, abi=VAULT_TIMELOCK_ABI)
          lookback_filters.append(vault_contract.events.StrategyAnnounced.createFilter(fromBlock=START_BLOCK_ETH))
          lookback_filters.append(vault_contract.events.StrategyChanged.createFilter(fromBlock=START_BLOCK_ETH))
    # MATIC lookback
    if LOOKBACK_MATIC_BRIDGE == 'True':
      lookback_filters.append(matic_erc20_contract.events.LockedERC20.createFilter(fromBlock=START_BLOCK_ETH, argument_filters={"rootToken":IFARM_ADDR}))
    if LOOKBACK_MATIC == 'True':
      lookback_filters.append(matic_root_contract.events.NewHeaderBlock.createFilter(fromBlock=START_BLOCK_ETH))
    if activenet['matic']:
      if LOOKBACK_MATIC_TRADES == 'True':
        lookback_filters.append(matic_unipool_ifarm_matic_contract.events.Swap.createFilter(fromBlock=START_BLOCK_MATIC))
        lookback_filters.append(matic_unipool_ifarm_quick_contract.events.Swap.createFilter(fromBlock=START_BLOCK_MATIC))
    # BSC lookback
    if activenet['bsc']:
      if LOOKBACK_BSC_TRADES == 'True':
        lookback_filters.append(bsc_unipool_farm_busd_contract.events.Swap.createFilter(fromBlock=START_BLOCK_BSC))
    # run lookback
    log_lookback(lookback_filters)
  # set up the loop
  if WATCH == 'True':
    event_filters = []
    print('watching for new events...')
    loop = asyncio.get_event_loop()
    event_filters.append(controller_contract.events.SharePriceChangeLog.createFilter(fromBlock='latest'))
    event_filters.append(unipool_usdc_contract.events.Swap.createFilter(fromBlock='latest'))
    event_filters.append(unipool_eth_contract.events.Swap.createFilter(fromBlock='latest'))
    event_filters.append(grain_contract.events.Transfer.createFilter(fromBlock='latest', argument_filters={"to":ZERO_ADDR}))
    event_filters.append(minter_contract.events.MintingAnnounced.createFilter(fromBlock='latest'))
    # MATIC events
    event_filters.append(matic_root_contract.events.NewHeaderBlock.createFilter(fromBlock='latest'))
    event_filters.append(matic_erc20_contract.events.LockedERC20.createFilter(fromBlock='latest', argument_filters={"rootToken":IFARM_ADDR}))
    if activenet['matic']:
      event_filters.append(matic_unipool_ifarm_matic_contract.events.Swap.createFilter(fromBlock='latest'))
      # TODO create handler for ifarm:quick swaps
      #event_filters.append(matic_unipool_ifarm_quick_contract.events.Swap.createFilter(fromBlock='latest'))
      #event_filters.append(bsc_unipool_farm_busd_contract.events.Swap.createFilter(fromBlock='latest'))
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
