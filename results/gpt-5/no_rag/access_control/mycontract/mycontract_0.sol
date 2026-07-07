pragma solidity ^0.4.24;

contract MyContract {

    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function MyContract() public {
        owner = msg.sender;
    }

    function sendTo(address receiver, uint amount) public onlyOwner {
        require(receiver != address(0));
        require(amount <= address(this).balance);
        receiver.transfer(amount);
    }

    function() public payable {}
}