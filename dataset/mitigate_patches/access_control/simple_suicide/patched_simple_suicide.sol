contract SmartFix {
  address public smartfix_owner = msg.sender;
}

pragma solidity ^0.4.0;

contract SimpleSuicide is SmartFix {

  function sudicideAnyone() {
    require((smartfix_owner == msg.sender)); 

    selfdestruct(msg.sender);
  }

}
