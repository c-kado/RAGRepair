pragma solidity ^0.4.18;

contract Reentrance {

  mapping(address => uint256) public balances;
  bool private reentrancyLock;

  modifier nonReentrant() {
    require(!reentrancyLock);
    reentrancyLock = true;
    _;
    reentrancyLock = false;
  }

  function donate(address _to) public payable {
    require(_to != address(0));
    balances[_to] += msg.value;
  }

  function balanceOf(address _who) public view returns (uint balance) {
    return balances[_who];
  }

  function withdraw(uint _amount) public nonReentrant {
    require(balances[msg.sender] >= _amount);
    balances[msg.sender] -= _amount; // effects first
    msg.sender.transfer(_amount);    // interaction after state change
  }

  function() public payable {}
}