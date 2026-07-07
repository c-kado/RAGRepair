pragma solidity ^0.4.15;

contract Reentrance {
    mapping (address => uint) userBalance;
    bool private reentrancyLock = false;

    modifier nonReentrant() {
        require(!reentrancyLock);
        reentrancyLock = true;
        _;
        reentrancyLock = false;
    }

    function getBalance(address u) public constant returns(uint){
        return userBalance[u];
    }

    function addToBalance() public payable {
        require(msg.value > 0);
        userBalance[msg.sender] += msg.value;
    }

    function withdrawBalance() public nonReentrant {
        uint amount = userBalance[msg.sender];
        require(amount > 0);

        // Effects
        userBalance[msg.sender] = 0;

        // Interaction
        msg.sender.transfer(amount);
    }
}