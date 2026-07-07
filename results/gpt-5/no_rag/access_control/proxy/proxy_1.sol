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

  function forward(address callee, bytes memory _data) public onlyOwner {
    require(callee != address(0));
    require(callee.delegatecall(_data));
  }

}