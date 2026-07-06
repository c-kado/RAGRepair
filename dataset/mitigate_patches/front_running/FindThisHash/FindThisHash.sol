

pragma solidity ^0.4.22;

contract FindThisHash {
    bytes32 constant public hash = 0x3ea2f1d0abf3fc66cf29eebb70cbd4e7fe762ef8a09bcc06c8edf641230afec0;

    constructor() public payable {} 

    function solve(string solution) public {

        require(hash == sha3(solution));
        msg.sender.transfer(1000 ether);
    }
}
