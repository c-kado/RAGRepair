pragma solidity ^0.4.24;

contract Proxy {

  address public owner;

  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

  constructor() public {
    owner = msg.sender;
    emit OwnershipTransferred(address(0), owner);
  }

  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }

  function transferOwnership(address newOwner) external onlyOwner {
    require(newOwner != address(0));
    emit OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

  function forward(address callee, bytes _data) external onlyOwner {
    require(callee != address(0));
    uint256 size;
    assembly { size := extcodesize(callee) }
    require(size > 0);
    require(callee.delegatecall(_data));
  }
}