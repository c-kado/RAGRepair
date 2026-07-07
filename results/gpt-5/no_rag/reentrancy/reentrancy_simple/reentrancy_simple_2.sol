pragma solidity ^0.4.15;

contract Reentrance {
    mapping (address => uint256) userBalance;

    function getBalance(address u) public constant returns(uint256) {
        return userBalance[u];
    }

    function addToBalance() public payable {
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance() public {
        uint256 amount = userBalance[msg.sender];
        require(amount > 0);

        // Effects: update state before interaction to prevent reentrancy
        userBalance[msg.sender] = 0;

        // Interaction: use transfer which forwards limited gas and reverts on failure
        msg.sender.transfer(amount);
    }
}