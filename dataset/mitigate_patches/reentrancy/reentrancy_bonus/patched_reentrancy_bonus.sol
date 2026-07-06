contract SmartFix {
  bool public _locked = false;

  modifier _nonReentrant() {
    require(!_locked);
    _locked = true;
    _;
    _locked = false;
  }
}

pragma solidity ^0.4.24;

contract Reentrancy_bonus is SmartFix {

    mapping (address => uint) private userBalances;
    mapping (address => bool) private claimedBonus;
    mapping (address => uint) private rewardsForA;

    function withdrawReward(address recipient) _nonReentrant 
 public {
        uint amountToWithdraw = rewardsForA[recipient];
        rewardsForA[recipient] = 0;
        (bool success, ) = recipient.call.value(amountToWithdraw)("");
        require(success);
    }

    function getFirstWithdrawalBonus(address recipient) public {
        require(!claimedBonus[recipient]); 

        rewardsForA[recipient] += 100;

        withdrawReward(recipient); 
        claimedBonus[recipient] = true;
    }
}
