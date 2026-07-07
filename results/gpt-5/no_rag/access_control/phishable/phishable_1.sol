pragma solidity ^0.4.22;

contract Phishable {
    address public owner;

    constructor(address _owner) public {
        owner = _owner;
    }

    function() public payable {}

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function withdrawAll(address _recipient) public onlyOwner {
        _recipient.transfer(address(this).balance);
    }
}