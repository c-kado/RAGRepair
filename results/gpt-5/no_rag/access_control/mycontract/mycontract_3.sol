pragma solidity ^0.4.24;

contract MyContract {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    constructor() public {
        owner = msg.sender;
    }

    function sendTo(address receiver, uint amount) public onlyOwner {
        receiver.transfer(amount);
    }

    function() public payable {}
}