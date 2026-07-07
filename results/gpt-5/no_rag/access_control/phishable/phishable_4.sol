pragma solidity ^0.4.22;

contract Phishable {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    constructor (address _owner) public {
        require(_owner != address(0));
        owner = _owner;
    }

    function () public payable {}

    function withdrawAll(address _recipient) public onlyOwner {
        require(_recipient != address(0));
        _recipient.transfer(address(this).balance);
    }
}