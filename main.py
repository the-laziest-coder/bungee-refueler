import random
import time
import requests
import ua_generator

import multiprocessing as mp
from termcolor import cprint
from enum import Enum
from pathlib import Path
from datetime import datetime
from retry import retry
from web3 import Web3

from config import *
from vars import *

default_ua = ua_generator.generate(device='desktop', browser='chrome')
default_headers = {'User-Agent': default_ua.text}
proxies = {}
try:
    for proxy in open('files/proxies.txt').readlines():
        proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
        break
except Exception:
    pass


NATIVE_TOKEN = NATIVE_TOKENS[REFUEL_FROM]


def decimal_to_int(d, n):
    return int(d * (10 ** n))


def int_to_decimal(i, n):
    return i / (10 ** n)


def wait_next_tx():
    time.sleep(random.uniform(NEXT_TX_MIN_WAIT_TIME, NEXT_TX_MAX_WAIT_TIME))


class RunnerException(Exception):

    def __init__(self, message, caused=None):
        super().__init__()
        self.message = message
        self.caused = caused

    def __str__(self):
        if self.caused:
            return self.message + ": " + str(self.caused)
        return self.message


class Runner:
    class Status(Enum):
        ALREADY = 1
        SUCCESS = 2
        FAILED = 3

    @retry(tries=MAX_TRIES, delay=1.5, backoff=2, jitter=(0, 1))
    def runner_wrapper(self, msg, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise RunnerException(msg, e)

    def __init__(self, w3, private_key, refuel_chain_info):
        self.w3 = w3
        self.private_key = private_key
        self.refuel_chain_info = refuel_chain_info

        account = w3.eth.account.from_key(private_key)
        self.address = account.address

    def _tx_verification(self, tx_hash, action_print):
        transaction_data = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        if transaction_data.get('status') is not None and transaction_data.get('status') == 1:
            scan_link = tx_hash.hex()
            if REFUEL_FROM in SCANS:
                scan_link = SCANS[REFUEL_FROM] + '/tx/' + scan_link
            print(f'{self.address} | {action_print}Successful tx: {scan_link}')
        else:
            raise RunnerException(f'{action_print}Tx error: {transaction_data.get("transactionHash").hex()}')

    def tx_verification(self, tx_hash, action=None):
        action_print = action + ' - ' if action else ''
        return self.runner_wrapper(
            f'{action_print}Tx error: {tx_hash.hex()}',
            self._tx_verification, tx_hash, action_print
        )

    @classmethod
    def _get_refuel_quote(cls, from_chain_id, to_chain_id, amount):
        resp = requests.get(f'https://refuel.socket.tech/quote?'
                            f'fromChainId={from_chain_id}&'
                            f'toChainId={to_chain_id}&'
                            f'amount={amount}', headers=default_headers, proxies=proxies)
        if resp.status_code != 200:
            raise RunnerException(f'status_code = {resp.status_code}, response = {resp.text}')

        json_resp = resp.json()
        if not json_resp['success']:
            return False, '', ''

        return True, json_resp['result']['contractAddress'], json_resp['result']['estimatedTime']

    def get_refuel_quote(self, from_chain, to_chain, amount):
        return self.runner_wrapper('Get refuel quote failed', self._get_refuel_quote,
                                   CHAIN_IDS[from_chain], CHAIN_IDS[to_chain], amount)

    def get_limit(self, from_chain, to_chain):
        from_chain_id, to_chain_id = CHAIN_IDS[from_chain], CHAIN_IDS[to_chain]
        for limit in self.refuel_chain_info['limits']:
            if limit['chainId'] == to_chain_id:
                if limit['isEnabled']:
                    return int(limit['minAmount']), int(limit['maxAmount'])
                else:
                    return -1, -1
        return -1, -1

    def _refuel(self, contract_address, to_chain_id, amount_int):
        contract = self.w3.eth.contract(self.w3.to_checksum_address(contract_address), abi=REFUEL_CONTRACT_ABI)
        tx = contract.functions.depositNativeToken(to_chain_id, self.address).build_transaction({
            'from': self.address,
            'value': amount_int,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.address)
        })
        estimate = self.w3.eth.estimate_gas(tx)
        tx['gas'] = estimate

        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.tx_verification(
            tx_hash,
            action=f'Refuel of {int_to_decimal(amount_int, NATIVE_TOKEN_DECIMAL)} ${NATIVE_TOKEN} '
                   f'to {CHAIN_NAMES[to_chain_id]}'
        )

    def refuel(self, contract_address, to_chain, amount):
        to_chain_id = CHAIN_IDS[to_chain]
        return self.runner_wrapper(f'Refuel to {to_chain} failed', self._refuel, contract_address, to_chain_id, amount)

    def run(self, to_chain):
        balance_int = self.w3.eth.get_balance(self.address)
        balance = int_to_decimal(balance_int, NATIVE_TOKEN_DECIMAL)

        min_amount, max_amount = get_chain_amount_range(to_chain)

        valuable_decimals = NATIVE_TOKEN_VALUABLE_DECIMALS[REFUEL_FROM]

        if REFUEL_AMOUNT_PERCENTAGE == 0:
            if min_amount > balance:
                raise RunnerException(f'Insufficient balance for min amount refuel to {to_chain}')
            amount = random.uniform(min_amount, min(max_amount, balance))
        else:
            amount = balance * REFUEL_AMOUNT_PERCENTAGE / 100.0
            if min_amount > amount:
                raise RunnerException(f'Insufficient balance for min amount refuel to {to_chain}')

        amount = round(amount, random.randint(valuable_decimals, valuable_decimals + 2))
        amount_int = decimal_to_int(amount, NATIVE_TOKEN_DECIMAL)

        allowed, contract_address, estimated_time = self.get_refuel_quote(REFUEL_FROM, to_chain, amount_int)
        if not allowed:
            raise RunnerException(f'Refuel of {amount} ${NATIVE_TOKEN} is not allowed to {to_chain}')

        min_limit_int, max_limit_int = self.get_limit(REFUEL_FROM, to_chain)
        if min_limit_int == -1 and max_limit_int == -1:
            raise RunnerException(f'Refuel limits to {to_chain} error')

        random_tx = 0
        max_random_tx = random.randint(0, MAX_RANDOM_TX_COUNT)
        random_tx_min_amount = decimal_to_int(RANDOM_TX_MIN_REFUEL_AMOUNT, NATIVE_TOKEN_DECIMAL)
        while amount_int >= min_limit_int:
            if min_limit_int * 2 > amount_int:
                refuel_amount_int = amount_int
            elif random_tx < max_random_tx and random_tx_min_amount <= amount_int - min_limit_int:
                random_tx_max = min(amount_int - min_limit_int, max_limit_int)
                random_tx_min = min(random_tx_min_amount, random_tx_max)
                refuel_amount_int = random.randint(random_tx_min, random_tx_max)
                random_tx += 1
            elif amount_int > max_limit_int and amount_int - max_limit_int < min_limit_int:
                refuel_amount_int = amount_int - min_limit_int
            else:
                refuel_amount_int = min(amount_int, max_limit_int)
            self.refuel(contract_address, to_chain, refuel_amount_int)
            amount_int -= refuel_amount_int
            wait_next_tx()

        cprint(f'{self.address} | Refuel of {amount} ${NATIVE_TOKEN} to {to_chain} started, '
               f'estimated time = ~{estimated_time / 1000} seconds', 'green')

        return Runner.Status.SUCCESS


def get_chain_amount_range(to_chain):
    if to_chain in REFUEL_AMOUNT_BY_CHAIN:
        min_amount, max_amount = REFUEL_AMOUNT_BY_CHAIN[to_chain]
    else:
        min_amount, max_amount = DEFAULT_MIN_REFUEL_AMOUNT, DEFAULT_MAX_REFUEL_AMOUNT
    return min_amount, max_amount


def ensure_refuel_limits():
    resp = requests.get('https://refuel.socket.tech/chains', headers=default_headers, proxies=proxies)
    if resp.status_code != 200:
        raise Exception(f'status_code = {resp.status_code}, response = {resp.text}')

    json_resp = resp.json()
    if not json_resp['success']:
        raise Exception(f'unsuccessful, response = {resp.text}')

    chain_info = None
    for chain in json_resp['result']:
        if chain['name'] == REFUEL_FROM:
            chain_info = chain
            break

    if chain_info is None:
        raise Exception(f'unsupported chain: {REFUEL_FROM}')

    for to_chain in REFUEL_TO:
        to_chain_id = CHAIN_IDS[to_chain]
        min_amount, max_amount = get_chain_amount_range(to_chain)
        if min_amount > max_amount:
            raise Exception(f'min amount > max amount for {to_chain} in config')
        min_amount = decimal_to_int(min_amount, NATIVE_TOKEN_DECIMAL)
        max_amount = decimal_to_int(max_amount, NATIVE_TOKEN_DECIMAL)
        random_tx_min_amount = decimal_to_int(RANDOM_TX_MIN_REFUEL_AMOUNT, NATIVE_TOKEN_DECIMAL)
        for limit in chain_info['limits']:
            if limit['chainId'] == to_chain_id:
                if not limit['isEnabled']:
                    raise Exception(f'refuel from {REFUEL_FROM} to {to_chain} is not enabled')
                min_limit, max_limit = int(limit['minAmount']), int(limit['maxAmount'])
                if random_tx_min_amount < min_limit:
                    raise Exception(f'random tx min amount is lower that refuel to {to_chain} min value '
                                    f'{round(int_to_decimal(min_limit, NATIVE_TOKEN_DECIMAL) + 0.00005, 4)} '
                                    f'${NATIVE_TOKEN}.\n'
                                    f'Check https://www.bungee.exchange/refuel to get correct limits')
                if min_amount < min_limit:
                    raise Exception(f'min amount for {to_chain} in config is lower than refuel min value '
                                    f'{round(int_to_decimal(min_limit, NATIVE_TOKEN_DECIMAL) + 0.00005, 4)} '
                                    f'${NATIVE_TOKEN}.\n'
                                    f'Check https://www.bungee.exchange/refuel to get correct limits')
                if max_amount > max_limit:
                    cprint(f'Max amount for {to_chain} in config is greater than refuel max value '
                           f'{round(int_to_decimal(max_limit, NATIVE_TOKEN_DECIMAL) - 0.00005, 4)} ${NATIVE_TOKEN}.\n'
                           f'You can continue to refuel with multiple transactions\n'
                           f'or stop and check https://www.bungee.exchange/refuel to get correct limits.\n'
                           f'Continue? (Y/n):',
                           'yellow', end=' ')
                    answer = input()
                    if answer != 'Y':
                        raise Exception(f'you aborted refuel with multiple transactions')
                break

    return chain_info


results_path = 'results/' + datetime.now().strftime('%d-%m-%Y-%H-%M-%S')


def clear_results():
    for c in REFUEL_TO:
        Path(f'{results_path}/to_{c}').mkdir(parents=True, exist_ok=True)


def write_listener(q):
    while True:
        m = q.get()
        if m == 'Finished':
            break
        (row, to_chain, status) = m
        with open(f'{results_path}/to_{to_chain}/{status.name}.txt', 'a') as file:
            file.write(f'{row}\n')
            file.flush()


def log_run(q, _row, _to_chain, _status, msg=''):
    address = 'None' if _row.find(';') == -1 else _row.split(';')[0]
    print_msg = address + ' |'
    if _status == Runner.Status.ALREADY:
        cprint(f'{print_msg} Already done', 'yellow')
    elif _status == Runner.Status.SUCCESS:
        cprint(f'{print_msg} Run success', 'green')
    else:
        cprint(f'{print_msg} Run failed: {msg}', 'red')
    q.put((_row, _to_chain, _status))


def pool_worker(pid, q, batch, refuel_chain_info):
    w3 = Web3(Web3.HTTPProvider(RPCs[REFUEL_FROM]))

    random.shuffle(batch)

    first = True
    for idx, (account_row, to_chain) in enumerate(batch):
        if account_row[0] == '#':
            continue

        if not first:
            wait = random.randint(
                int(NEXT_ADDRESS_MIN_WAIT_TIME * 60),
                int(NEXT_ADDRESS_MAX_WAIT_TIME * 60)
            )
            cprint('\n#########################################\n#', 'cyan', end='')
            cprint(f'Process #{pid}. Done: {idx}/{len(batch)}'.center(39), 'magenta', end='')
            cprint('#\n#########################################\n# ', 'cyan', end='')
            cprint('Waiting for next run for {:.2f} minutes'.format(wait / 60), 'magenta', end='')
            cprint(' #\n#########################################\n', 'cyan')
            time.sleep(wait)
        first = False

        if account_row.find(';') == -1:
            current_key = account_row
        else:
            current_key = account_row.split(';')[1]

        try:
            runner = Runner(w3, current_key, refuel_chain_info)
            current_address = runner.address
            if account_row.find(';') == -1:
                account_row = current_address + ';' + current_key
            status = runner.run(to_chain)
            log_run(q, account_row, to_chain, status)
        except Exception as run_ex:
            log_run(q, account_row, to_chain, Runner.Status.FAILED, str(run_ex))


def main():
    clear_results()

    try:
        refuel_chain_info = ensure_refuel_limits()
    except Exception as _e:
        cprint(f'Check refuel limits failed: {str(_e)}', 'red')
        exit(1)

    random.seed(datetime.now().timestamp())

    with open('files/wallets.txt', 'r') as f:
        data = f.read().splitlines()

    random.shuffle(data)

    batches = [[] for _ in range(PROCESSES_NUM)]
    for i, row in enumerate(data):
        batches[i % PROCESSES_NUM] += [(row, c) for c in REFUEL_TO]

    manager = mp.Manager()
    queue = manager.Queue()
    pool = mp.Pool(PROCESSES_NUM + 1)

    watcher = pool.apply_async(write_listener, (queue,))

    jobs = []
    for i in range(PROCESSES_NUM):
        job = pool.apply_async(pool_worker, (i + 1, queue, batches[i], refuel_chain_info))
        jobs.append(job)

    for job in jobs:
        job.get()

    cprint('\n#########################################\n#', 'cyan', end='')
    cprint(f'Finished'.center(39), 'magenta', end='')
    cprint('#\n#########################################', 'cyan')

    queue.put('Finished')
    pool.close()
    pool.join()


if __name__ == '__main__':
    cprint('###########################################################', 'cyan')
    cprint('#######################', 'cyan', end='')
    cprint(' By @timfame ', 'magenta', end='')
    cprint('#######################', 'cyan')
    cprint('###########################################################\n', 'cyan')

    main()
