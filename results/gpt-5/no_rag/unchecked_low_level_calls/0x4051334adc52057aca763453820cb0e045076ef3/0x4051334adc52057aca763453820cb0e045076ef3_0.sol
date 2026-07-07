pragma solidity ^0.4.24;

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

contract airdrop {

    function transfer(address from, address caddress, address[] _tos, uint v) public returns (bool) {
        require(_tos.length > 0);
        IERC20 token = IERC20(caddress);
        for (uint i = 0; i < _tos.length; i++) {
            require(token.transferFrom(from, _tos[i], v), "Token transfer failed");
        }
        return true;
    }
}