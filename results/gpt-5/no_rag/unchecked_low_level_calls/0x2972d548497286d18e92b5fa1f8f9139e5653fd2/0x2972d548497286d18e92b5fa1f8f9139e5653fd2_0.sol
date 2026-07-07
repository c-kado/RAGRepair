pragma solidity ^0.4.25;

interface IERC20 {
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

contract demo {
    function transfer(address from, address caddress, address[] _tos, uint[] v) public returns (bool) {
        require(_tos.length > 0);
        require(_tos.length == v.length);

        for (uint i = 0; i < _tos.length; i++) {
            require(IERC20(caddress).transferFrom(from, _tos[i], v[i]));
        }
        return true;
    }
}