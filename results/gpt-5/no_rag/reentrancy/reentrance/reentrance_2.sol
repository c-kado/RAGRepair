pragma solidity ^0.4.18;

contract Reentrance {

  mapping(address => uint256) public balances;
  bool private locked;

  modifier nonReentrant() {
    require(!locked);
    locked = true;
    _;
    locked = false;
  }

  function donate(address _to) public payable {
    balances[_to] = balances[_to] + msg.value;
  }

  function balanceOf(address _who) public view returns (uint256 balance) {
    return balances[_who];
  }

  function withdraw(uint256 _amount) public nonReentrant {
    require(balances[msg.sender] >= _amount);
    balances[msg.sender] -= _amount;
    msg.sender.transfer(_amount);
  }

  function() public payable {}
}