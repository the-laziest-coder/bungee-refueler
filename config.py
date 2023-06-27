RPCs = {
    'Ethereum':  'https://eth.llamarpc.com',
    'Optimism':  'https://rpc.ankr.com/optimism',
    'BSC':       'https://rpc.ankr.com/bsc',
    'Gnosis':    'https://rpc.gnosischain.com',
    'Polygon':   'https://polygon.llamarpc.com',
    'Fantom':    'https://rpc.fantom.network',
    'Arbitrum':  'https://arb1.arbitrum.io/rpc',
    'Avalanche': 'https://avalanche-c-chain.publicnode.com',
    'zkSync':    'https://mainnet.era.zksync.io',
    'zkEVM':     'https://rpc.ankr.com/polygon_zkevm',
}

###############################################################################################################

# Время ожидания между выполнением разных акков рандомное в указанном диапазоне
NEXT_ADDRESS_MIN_WAIT_TIME = 0.5  # В минутах
NEXT_ADDRESS_MAX_WAIT_TIME = 1.5    # В минутах

# Время ожидания между транзакциями одного аккаунта
NEXT_TX_MIN_WAIT_TIME = 6   # В секундах
NEXT_TX_MAX_WAIT_TIME = 12  # В секундах

# Максимальное кол-во попыток сделать запрос/транзакцию если они фейлятся
MAX_TRIES = 3

###############################################################################################################

# Кол-во потоков, в которых будет запускаться скрипт.
# В большинстве случаев можно оставить 1 поток и просто уменьшить время ожидания между акками
PROCESSES_NUM = 1

# Possible values: Ethereum, Optimism, BSC, Gnosis, Polygon, Fantom, Arbitrum, Avalanche, zkSync, zkEVM
REFUEL_FROM = 'Avalanche'
REFUEL_TO = ['Optimism', 'zkSync']

# Если стоит 0, то используются значения из диапазонов ниже.
# Если значение больше нуля, то рефуелится указанный процент от всего баланса
REFUEL_AMOUNT_PERCENTAGE = 95

# Amount of network native token
DEFAULT_MIN_REFUEL_AMOUNT = 0.35
DEFAULT_MAX_REFUEL_AMOUNT = 0.35

# Максимально возможное кол-во дополнительных рандомных refuel транзакции (итоговая сумма остается та же)
MAX_RANDOM_TX_COUNT = 2
RANDOM_TX_MIN_REFUEL_AMOUNT = 1

# <network>: (min_amount, max_amount)
# (in native token)
# Если для какой-то сети не указано, то для нее берутся значения DEFAULT_MIN_REFUEL_AMOUNT и DEFAULT_MAX_REFUEL_AMOUNT
REFUEL_AMOUNT_BY_CHAIN = {
    'Optimism': (0.3, 0.4),
    'zkSync': (0.4, 0.4),
}
