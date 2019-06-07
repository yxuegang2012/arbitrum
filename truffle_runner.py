# Copyright 2019, Offchain Labs, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import arbitrum as arb
import eth_utils
from collections import Counter
from arbitrum.instructions import OPS
import sys
from arbitrum.evm.contract import ArbContract, create_evm_vm


def run_until_halt(vm):
    log = []
    i = 0
    push_counts = Counter()
    while True:
        try:
            if vm.pc.op.get_op() == OPS["spush"]:
                push_counts[vm.pc.path[-1][5:-1]] += 1
            run = arb.run_vm_once(vm)
            if not run:
                print("Hit blocked insn")
                break
            i += 1
        except Exception as err:
            print("Error at", vm.pc.pc - 1, vm.code[vm.pc.pc - 1])
            print("Context", vm.code[vm.pc.pc - 6: vm.pc.pc + 4])
            raise err
        if vm.halted:
            break
    for log in vm.logs:
        vm.output_handler(log)
    vm.logs = []
    print("Ran VM for {} steps".format(i))
    # print(push_counts)
    return log


def run_n_steps(vm, steps):
    log = []
    i = 0
    while i < steps:
        log.append((vm.pc.pc, vm.stack[:]))
        try:
            # print(vm.pc, vm.stack[:])
            arb.run_vm_once(vm)
            i += 1
        except Exception as err:
            print("Error at", vm.pc.pc - 1, vm.code[vm.pc.pc - 1])
            print("Context", vm.code[vm.pc.pc - 6: vm.pc.pc + 4])
            raise err
        if vm.halted:
            break
    print("Ran VM for {} steps".format(i))
    return log

def make_msg_val(calldata):
    return arb.value.Tuple([calldata, 0, 0, 0])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception("Call as truffle_runner.py [compiled.json]")

    with open(sys.argv[1]) as json_file:
        raw_contracts = json.load(json_file)

    contracts = [ArbContract(contract) for contract in raw_contracts]
    vm = create_evm_vm(contracts)
    with open("code.txt", "w") as f:
        for instr in vm.code:
            f.write("{} {}".format(instr, instr.path))
            f.write("\n")

    channel = contracts[1]
    fib = contracts[0]

    test = fib.generateFib(20)
    test1 = test.set_tup_val(0, 949960771139723771144128610028553702292195488917)
    test2 = test.set_tup_val(1, test[1].set_tup_val(1, 25))
    vm.env.send_message([test1, 1234, 100000000, 0])
    vm.env.send_message([test2, 1234, 100000000, 0])
    print(arb.value.value_hash(100).hex())
    print(fib._generateFib(40))
    print(make_msg_val(fib.generateFib(2, 40)[0]))
    # print(arb.value.value_hash(fib.generateFib(2, 40)[0]).hex())
    vm.env.send_message([make_msg_val(fib.generateFib(2, 10 )), 1234, 100000000, 0])
    # vm.env.send_message([make_msg_val(fib.getFib(3, 19)), 2345, 0, 0])
    vm.env.deliver_pending()
    run_until_halt(vm)

    # person_a = '0x1000000000000000000000000000000000000000'
    # person_b = '0x2222222222222222222222222222222222222222'
    # person_a_int = eth_utils.to_int(hexstr=person_a)
    # person_b_int = eth_utils.to_int(hexstr=person_b)

    # vm.env.send_message([channel.deposit(), person_a_int, 10000, 0, 0])
    # vm.env.send_message([channel.getBalance(person_a), 0, 0, 0, 0])
    # vm.env.send_message([channel.getBalance(person_b), 0, 0, 0, 0])
    # vm.env.deliver_pending()
    # run_until_halt(vm)
    # vm.env.send_message(
    #     [channel.transferFib(person_b, 16), person_a_int, 0, 0, 0]
    # )
    # vm.env.send_message([channel.getBalance(person_a), 0, 0, 0, 0])
    # vm.env.send_message([channel.getBalance(person_b), 0, 0, 0, 0])
    # vm.env.deliver_pending()
    # run_until_halt(vm)
    # vm.env.send_message([channel.withdraw(10), person_b_int, 0, 0, 0])
    # vm.env.send_message([channel.getBalance(person_a), 0, 0, 0, 0])
    # vm.env.send_message([channel.getBalance(person_b), 0, 0, 0, 0])
    # vm.env.deliver_pending()
    # run_until_halt(vm)
    # print("Contract sent messages:", vm.sent_messages)
