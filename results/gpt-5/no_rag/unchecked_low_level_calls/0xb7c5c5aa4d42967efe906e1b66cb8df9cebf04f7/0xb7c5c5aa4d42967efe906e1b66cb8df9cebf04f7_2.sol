pragma solidity ^0.4.23;

contract keepMyEther {
    mapping(address => uint256) public balances;

    function () payable public {
        balances[msg.sender] += msg.value;
    }

    function withdraw() public {
        uint256 amount = balances[msg.sender];
        require(amount > 0);

        // Effects
        balances[msg.sender] = 0;

        // Interaction with proper error handling
        msg.sender.transfer(amount);
    }
}