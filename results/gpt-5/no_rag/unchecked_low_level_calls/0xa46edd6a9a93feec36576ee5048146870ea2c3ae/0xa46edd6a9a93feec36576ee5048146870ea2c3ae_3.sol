pragma solidity ^0.4.18;

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

contract EBU {

    function isContract(address _addr) internal view returns (bool) {
        uint256 size;
        assembly { size := extcodesize(_addr) }
        return size > 0;
    }

    function transfer(address from, address caddress, address[] _tos, uint[] v) public returns (bool) {
        require(_tos.length > 0);
        require(_tos.length == v.length);
        require(isContract(caddress));

        IERC20 token = IERC20(caddress);
        for (uint i = 0; i < _tos.length; i++) {
            require(token.transferFrom(from, _tos[i], v[i]));
        }
        return true;
    }
}