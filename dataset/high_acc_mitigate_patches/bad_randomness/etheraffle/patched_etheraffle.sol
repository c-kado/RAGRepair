pragma solidity ^0.4.16;

contract Ethraffle_v4b {
    struct Contestant {
        address addr;
        uint raffleId;
    }

    event RaffleResult(
        uint indexed raffleId,
        uint winningNumber,
        address winningAddress,
        address seed1,
        address seed2,
        uint seed3,
        bytes32 randHash
    );

    event TicketPurchase(
        uint indexed raffleId,
        address contestant,
        uint number
    );

    event TicketRefund(
        uint indexed raffleId,
        address contestant,
        uint number
    );

    uint public constant prize = 2.5 ether;
    uint public constant fee = 0.03 ether;
    uint public constant totalTickets = 50;
    uint public constant pricePerTicket = (prize + fee) / totalTickets; 
    address feeAddress;

    bool public paused = false;
    uint public raffleId = 1;
    uint public blockNumber = block.number;
    uint nextTicket = 0;
    mapping (uint => Contestant) contestants;
    uint[] gaps;

    function Ethraffle_v4b() public {
        feeAddress = msg.sender;
    }

    function () payable public {
        buyTickets();
    }

    function buyTickets() payable public {
        if (paused) {
            msg.sender.transfer(msg.value);
            return;
        }

        uint moneySent = msg.value;

        while (moneySent >= pricePerTicket && nextTicket < totalTickets) {
            uint currTicket = 0;
            if (gaps.length > 0) {
                currTicket = gaps[gaps.length-1];
                gaps.length--;
            } else {
                currTicket = nextTicket++;
            }

            contestants[currTicket] = Contestant(msg.sender, raffleId);
            emit TicketPurchase(raffleId, msg.sender, currTicket);
            moneySent -= pricePerTicket;
        }

        if (nextTicket == totalTickets) {
            chooseWinner();
        }

        if (moneySent > 0) {
            msg.sender.transfer(moneySent);
        }
    }

    function chooseWinner() private {

        uint winningNumber = uint(keccak256(block.timestamp, block.difficulty)) % totalTickets;
        address winningAddress = contestants[winningNumber].addr;
        RaffleResult(raffleId, winningNumber, winningAddress, msg.sender, tx.origin, block.difficulty, keccak256(block.timestamp, block.difficulty));

        raffleId++;
        nextTicket = 0;
        blockNumber = block.number;

        winningAddress.transfer(prize);
        feeAddress.transfer(fee);
    }

    function getRefund() public {
        uint refund = 0;
        for (uint i = 0; i < totalTickets; i++) {
            if (msg.sender == contestants[i].addr && raffleId == contestants[i].raffleId) {
                refund += pricePerTicket;
                contestants[i] = Contestant(address(0), 0);
                gaps.push(i);
                emit TicketRefund(raffleId, msg.sender, i);
            }
        }

        if (refund > 0) {
            msg.sender.transfer(refund);
        }
    }

    function togglePause() public {
        if (msg.sender == feeAddress) {
            paused = !paused;
        }
    }

    function kill() public {
        if (msg.sender == feeAddress) {
            selfdestruct(feeAddress);
        }
    }
}