pragma solidity ^0.4.22;

contract Phishable {
    address public owner;

    constructor(address _owner) public {
        owner = _owner;
    }

    function () public payable {}

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function withdrawAll(address _recipient) public onlyOwner {
        require(_recipient != address(0));
        _recipient.transfer(this.balance);
    }
}