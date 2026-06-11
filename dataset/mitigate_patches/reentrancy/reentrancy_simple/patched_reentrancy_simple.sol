/*
 * @source: https://github.com/trailofbits/not-so-smart-contracts/blob/master/reentrancy/Reentrancy.sol
 * @author: -
 * @vulnerable_at_lines: 24
 */

 pragma solidity ^0.4.15;

 contract Reentrance {
     mapping (address => uint) userBalance;

     function getBalance(address u) constant returns(uint){
         return userBalance[u];
     }

     function addToBalance() payable{
         require(((userBalance[msg.sender] + msg.value) >= userBalance[msg.sender])); /* <FIX> Insert:BC */
         userBalance[msg.sender] += msg.value;
     }

     function withdrawBalance(){
         // send userBalance[msg.sender] ethers to msg.sender
         // if mgs.sender is a contract, it will call its fallback function
         // <yes> <report> REENTRANCY
         uint256 tmp__1 = userBalance[msg.sender]; /* <FIX> Insert */
         userBalance[msg.sender] = 0; /* <FIX> Move */
         if( ! (msg.sender.call.value(tmp__1)() ) ){ /* <FIX> Replace: "userBalance[msg.sender]" => "tmp__1" */
             throw;
         }
         /* <FIX> Move: userBalance[msg.sender] = 0; */
     }
 }
