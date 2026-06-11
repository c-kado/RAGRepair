pragma solidity ^0.4.24;

contract Reentrancy_bonus{

    mapping (address => uint) private userBalances;
    mapping (address => bool) private claimedBonus;
    mapping (address => uint) private rewardsForA;
    mapping (address => bool) private isWithdrawing;

    function withdrawReward(address recipient) public {
        require(!isWithdrawing[recipient]);
        isWithdrawing[recipient] = true;
        
        uint amountToWithdraw = rewardsForA[recipient];
        rewardsForA[recipient] = 0;
        recipient.transfer(amountToWithdraw);
        
        isWithdrawing[recipient] = false;
    }

    function getFirstWithdrawalBonus(address recipient) public {
        require(!claimedBonus[recipient]); 

        rewardsForA[recipient] += 100;

        withdrawReward(recipient); 
        claimedBonus[recipient] = true;
    }
}