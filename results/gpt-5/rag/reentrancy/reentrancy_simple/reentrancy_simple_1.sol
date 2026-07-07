pragma solidity ^0.4.15;

contract Reentrance {
    mapping (address => uint) userBalance;

    function getBalance(address u) constant returns(uint){
        return userBalance[u];
    }

    function addToBalance() payable{
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance(){
        uint amount = userBalance[msg.sender];
        require(amount > 0);
        userBalance[msg.sender] = 0;
        msg.sender.Transfer(amount);
    }
}