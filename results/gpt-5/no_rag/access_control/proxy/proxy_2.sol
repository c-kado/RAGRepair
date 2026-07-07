pragma solidity ^0.4.24;

contract Proxy {

  address public owner;

  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }

  constructor() public {
    owner = msg.sender;
  }

  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    owner = newOwner;
  }

  function forward(address callee, bytes _data) public onlyOwner {
    require(callee != address(0));
    require(callee.delegatecall(_data));
  }

}