from neo.Prompt.Commands.Invoke import InvokeContract
from neo.Prompt.Utils import get_asset_id
from neo.Fixed8 import Fixed8
from prompt_toolkit import prompt
from decimal import Decimal
import json


def token_send(wallet, args):

    if len(args) != 4:
        print("please provide a token symbol, from address, to address, and amount")
        return

    token = get_asset_id(wallet, args[0])
    send_from = args[1]
    send_to = args[2]
    amount = amount_from_string(token, args[3])

    return do_token_transfer(token, wallet, send_from, send_to, amount)


def token_send_from(wallet, args):
    if len(args) != 4:
        print("please provide a token symbol, from address, to address, and amount")
        return

    token = get_asset_id(wallet, args[0])
    send_from = args[1]
    send_to = args[2]
    amount = amount_from_string(token, args[3])

    allowance = token_get_allowance(wallet, args[:-1], verbose=False)

    if allowance and allowance >= amount:

        tx, fee, results = token.TransferFrom(wallet, send_from, send_to, amount)

        if tx is not None and results is not None and len(results) > 0:

            if results[0].GetBigInteger() == 1:
                print("\n-----------------------------------------------------------")
                print("Transfer of %s %s from %s to %s" % (
                    string_from_amount(token, amount), token.symbol, send_from, send_to))
                print("Transfer fee: %s " % (fee.value / Fixed8.D))
                print("-------------------------------------------------------------\n")

                passwd = prompt("[Password]> ", is_password=True)

                if not wallet.ValidatePassword(passwd):
                    print("incorrect password")
                    return

                return InvokeContract(wallet, tx, fee)

        print("Could not send tokens")
    else:

        print("Requestest transfer from is greater than allowance")


def token_approve_allowance(wallet, args):

    if len(args) != 4:
        print("please provide a token symbol, from address, to address, and amount")
        return

    token = get_asset_id(wallet, args[0])
    approve_from = args[1]
    approve_to = args[2]
    amount = amount_from_string(token, args[3])

    tx, fee, results = token.Approve(wallet, approve_from, approve_to, amount)

    if tx is not None and results is not None and len(results) > 0:

        if results[0].GetBigInteger() == 1:
            print("\n-----------------------------------------------------------")
            print("Approve allowance of %s %s from %s to %s" % (string_from_amount(token, amount), token.symbol, approve_from, approve_to))
            print("Transfer fee: %s " % (fee.value / Fixed8.D))
            print("-------------------------------------------------------------\n")

            passwd = prompt("[Password]> ", is_password=True)

            if not wallet.ValidatePassword(passwd):
                print("incorrect password")
                return

            return InvokeContract(wallet, tx, fee)

    print("could not transfer tokens")


def token_get_allowance(wallet, args, verbose=False):

    if len(args) != 3:
        print("please provide a token symbol, from address, to address")
        return

    token = get_asset_id(wallet, args[0])
    allowance_from = args[1]
    allowance_to = args[2]

    tx, fee, results = token.Allowance(wallet, allowance_from, allowance_to)

    if tx is not None and results is not None and len(results) > 0:
        allowance = results[0].GetBigInteger()
        if verbose:
            print("%s allowance for %s from %s : %s " % (token.symbol, allowance_to, allowance_from, allowance))

        return allowance
    else:
        if verbose:
            print("Could not get allowance for token %s " % token.symbol)

    return 0


def do_token_transfer(token, wallet, from_address, to_address, amount):

    if from_address is None:
        print("Please specify --from-addr={addr} to send NEP5 tokens")
        return

    tx, fee, results = token.Transfer(wallet, from_address, to_address, amount)

    if tx is not None and results is not None and len(results) > 0:

        if results[0].GetBigInteger() == 1:
            print("\n-----------------------------------------------------------")
            print("Will transfer %s %s from %s to %s" % (string_from_amount(token, amount), token.symbol, from_address, to_address))
            print("Transfer fee: %s " % (fee.value / Fixed8.D))
            print("-------------------------------------------------------------\n")

            passwd = prompt("[Password]> ", is_password=True)

            if not wallet.ValidatePassword(passwd):
                print("incorrect password")
                return

            return InvokeContract(wallet, tx, fee)

    print("could not transfer tokens")


def amount_from_string(token, amount_str):

    precision_mult = pow(10, token.decimals)
    amount = float(amount_str) * precision_mult

    return int(amount)


def string_from_amount(token, amount):

    precision_mult = pow(10, token.decimals)
    amount = Decimal(amount) / Decimal(precision_mult)
    formatter_str = '.%sf' % token.decimals
    amount_str = format(amount, formatter_str)

    return amount_str