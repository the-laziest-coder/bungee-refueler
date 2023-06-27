SCANS = {
    'Ethereum': 'https://etherscan.io',
    'BSC': 'https://bscscan.com',
    'Polygon': 'https://polygonscan.com',
    'Avalanche': 'https://snowtrace.io',
    'Fantom': 'https://ftmscan.com',
    'Optimism': 'https://optimistic.etherscan.io',
    'Arbitrum': 'https://arbiscan.io',
    'Gnosis': 'https://gnosisscan.io',
    'zkSync': 'https://explorer.zksync.io',
    'zkEVM': 'https://zkevm.polygonscan.com',
}

CHAIN_IDS = {
    'Ethereum': 1,
    'Optimism': 10,
    'BSC': 56,
    'Gnosis': 100,
    'Polygon': 137,
    'Fantom': 250,
    'Arbitrum': 42161,
    'Avalanche': 43114,
    'zkSync': 324,
    'zkEVM': 1101,
}

CHAIN_NAMES = {
    1: 'Ethereum',
    10: 'Optimism',
    56: 'BSC',
    100: 'Gnosis',
    137: 'Polygon',
    250: 'Fantom',
    42161: 'Arbitrum',
    43114: 'Avalanche',
    324: 'zkSync',
    1101: 'zkEVM',
}

NATIVE_TOKENS = {
    'Ethereum': 'ETH',
    'Optimism': 'ETH',
    'BSC': 'BNB',
    'Gnosis': 'xDAI',
    'Polygon': 'MATIC',
    'Fantom': 'FTM',
    'Arbitrum': 'ETH',
    'Avalanche': 'AVAX',
    'zkSync': 'ETH',
    'zkEVM': 'ETH',
}

NATIVE_TOKEN_VALUABLE_DECIMALS = {
    'Ethereum': 5,
    'Optimism': 5,
    'BSC': 4,
    'Gnosis': 2,
    'Polygon': 2,
    'Fantom': 2,
    'Arbitrum': 5,
    'Avalanche': 3,
    'zkSync': 5,
    'zkEVM': 5,
}

NATIVE_TOKEN_DECIMAL = 18

REFUEL_CONTRACT_ABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"destinationReceiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"destinationChainId","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Donation","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"GrantSender","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"RevokeSender","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"srcChainTxHash","type":"bytes32"}],"name":"Send","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawal","type":"event"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"internalType":"struct GasMovr.ChainData[]","name":"_routes","type":"tuple[]"}],"name":"addRoutes","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable[]","name":"receivers","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"bytes32[]","name":"srcChainTxHashes","type":"bytes32[]"},{"internalType":"uint256","name":"perUserGasAmount","type":"uint256"},{"internalType":"uint256","name":"maxLimit","type":"uint256"}],"name":"batchSendNativeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"chainConfig","outputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"destinationChainId","type":"uint256"},{"internalType":"address","name":"_to","type":"address"}],"name":"depositNativeToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"}],"name":"getChainData","outputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"internalType":"struct GasMovr.ChainData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"grantSenderRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"processedHashes","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"revokeSenderRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"srcChainTxHash","type":"bytes32"},{"internalType":"uint256","name":"perUserGasAmount","type":"uint256"},{"internalType":"uint256","name":"maxLimit","type":"uint256"}],"name":"sendNativeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"senders","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"_isEnabled","type":"bool"}],"name":"setIsEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"setPause","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"setUnPause","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdrawBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"}],"name":"withdrawFullBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
