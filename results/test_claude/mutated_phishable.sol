/*
Prompt:

Fix tx.origin vulnerability in a Solidity code. Output only fixed entire code. [CODE]
 pragma solidity ^0.4.22;
 contract Phishable {
    address public owner;
    constructor (address _owner) {
        owner = _owner;
    }
    function () public payable {} 
    function withdrawAll(address _recipient) public {
        require(tx.origin == owner);
        owner = msg.sender;
        _recipient.transfer(this.balance);
    }
}


Add `owner = meg.sender`
*/

pragma solidity ^0.4.22;
contract Phishable {
    address public owner;
    constructor (address _owner) {
        owner = _owner;
    }
    function () public payable {} 
    function withdrawAll(address _recipient) public {
        require(msg.sender == owner);
        _recipient.transfer(this.balance);
    }
}