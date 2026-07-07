pragma solidity ^0.4.15;

contract Reentrance {
    mapping (address => uint256) private userBalance;

    function getBalance(address u) public constant returns (uint256) {
        return userBalance[u];
    }

    function addToBalance() public payable {
        require(msg.value > 0);
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance() public {
        uint256 amount = userBalance[msg.sender];
        require(amount > 0);
        userBalance[msg.sender] = 0;
        msg.sender.transfer(amount);
    }
}