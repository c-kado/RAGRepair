pragma solidity ^0.4.19;

contract ReentrancyDAO {
    mapping (address => uint) credit;
    uint balance;

    function withdrawAll() public {
        uint oCredit = credit[msg.sender];
        if (oCredit > 0) {
            // Effects: update state before external interaction
            credit[msg.sender] = 0;
            balance -= oCredit;

            // Interaction: use transfer to prevent reentrancy
            msg.sender.transfer(oCredit);
        }
    }

    function deposit() public payable {
        require(credit[msg.sender] + msg.value >= credit[msg.sender]);
        credit[msg.sender] += msg.value;
        balance += msg.value;
    }
}