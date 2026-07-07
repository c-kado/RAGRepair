pragma solidity ^0.4.19;

contract ReentrancyDAO {
    mapping (address => uint) credit;
    uint balance;

    function withdrawAll() public {
        uint amount = credit[msg.sender];
        require(amount > 0);

        // Effects
        credit[msg.sender] = 0;
        balance -= amount;

        // Interaction
        msg.sender.transfer(amount);
    }

    function deposit() public payable {
        credit[msg.sender] += msg.value;
        balance += msg.value;
    }
}