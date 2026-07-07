pragma solidity ^0.4.18;

contract Reentrance {

  mapping(address => uint) public balances;
  bool private locked;

  modifier nonReentrant() {
    require(!locked);
    locked = true;
    _;
    locked = false;
  }

  function donate(address _to) public payable {
    require(_to != address(0));
    uint newBalance = balances[_to] + msg.value;
    require(newBalance >= balances[_to]); // overflow check
    balances[_to] = newBalance;
  }

  function balanceOf(address _who) public view returns (uint balance) {
    return balances[_who];
  }

  function withdraw(uint _amount) public nonReentrant {
    require(_amount > 0);
    require(balances[msg.sender] >= _amount);

    // Effects
    balances[msg.sender] -= _amount;

    // Interaction
    msg.sender.transfer(_amount);
  }

  function() public payable {}
}