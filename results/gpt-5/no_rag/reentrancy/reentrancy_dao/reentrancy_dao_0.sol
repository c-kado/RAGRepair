pragma solidity ^0.4.19;

contract ReentrancyDAO {
    mapping (address => uint) credit;
    uint balance;
    bool private reentrancyLock;

    function withdrawAll() public {
        require(!reentrancyLock);
        reentrancyLock = true;

        uint oCredit = credit[msg.sender];
        require(oCredit > 0);

        // Effects
        credit[msg.sender] = 0;
        balance -= oCredit;

        // Interaction
        msg.sender.transfer(oCredit);

        reentrancyLock = false;
    }

    function deposit() public payable {
        credit[msg.sender] += msg.value;
        balance += msg.value;
    }
}