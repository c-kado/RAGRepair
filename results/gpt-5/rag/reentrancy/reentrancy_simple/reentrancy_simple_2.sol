pragma solidity ^0.4.15;

contract Reentrance {
    mapping (address => uint) userBalance;

    function getBalance(address u) public constant returns(uint){
        return userBalance[u];
    }

    function addToBalance() public payable{
        require(msg.value > 0);
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance() public {
        uint amount = userBalance[msg.sender];
        require(amount > 0);

        // Effects
        userBalance[msg.sender] = 0;

        // Interaction with limited gas to prevent reentrancy
        msg.sender.transfer(amount);
    }
}