pragma solidity ^0.4.24;

contract MyContract {

    address public owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event Sent(address indexed to, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function MyContract() public {
        owner = msg.sender;
        emit OwnershipTransferred(address(0), owner);
    }

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0));
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    function sendTo(address receiver, uint amount) public onlyOwner {
        require(receiver != address(0));
        receiver.transfer(amount);
        emit Sent(receiver, amount);
    }

    function() public payable { }
}