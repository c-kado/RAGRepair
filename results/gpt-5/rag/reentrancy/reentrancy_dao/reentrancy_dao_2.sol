pragma solidity ^0.4.19;

contract ReentrancyDAO {
    mapping (address => uint) credit;
    uint balance;

    function withdrawAll() public {
        uint oCredit = credit[msg.sender];
        require(oCredit > 0);

        // Effects
        credit[msg.sender] = 0;
        require(balance >= oCredit);
        balance -= oCredit;

        // Interaction
        msg.sender.transfer(oCredit);
    }

    function deposit() public payable {
        require(credit[msg.sender] + msg.value >= credit[msg.sender]);
        require(balance + msg.value >= balance);

        credit[msg.sender] += msg.value;
        balance += msg.value;
    }
}