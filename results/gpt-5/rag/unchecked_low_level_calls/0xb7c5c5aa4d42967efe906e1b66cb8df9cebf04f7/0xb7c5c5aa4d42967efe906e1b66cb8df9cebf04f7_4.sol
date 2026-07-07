pragma solidity ^0.4.23;

contract keepMyEther {
    mapping(address => uint256) public balances;

    function () public payable {
        require(balances[msg.sender] + msg.value >= balances[msg.sender]);
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;
        require(msg.sender.call.value(amount)());
    }
}